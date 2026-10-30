from math import ceil

from calculs import moyenne_ponderee
from database import get_connection


def calculer_classement(etudiant, semestre):
    """Compare la filière sur les mêmes évaluations disponibles."""
    connection = get_connection()

    try:
        inscriptions = connection.execute(
            """
            SELECT i.id
            FROM inscriptions AS i
            JOIN groupes AS g ON g.id = i.groupe_id
            WHERE g.filiere_id = ?
              AND g.niveau = ?
              AND g.annee_scolaire = ?
            ORDER BY i.id
            """,
            (
                etudiant["filiere_id"],
                etudiant["niveau"],
                etudiant["annee_scolaire"],
            ),
        ).fetchall()

        evaluations = connection.execute(
            """
            SELECT
                ev.id,
                ev.coefficient,
                ev.publiee,
                m.id AS matiere_id,
                m.coefficient AS coefficient_matiere,
                u.id AS ue_id,
                u.coefficient AS coefficient_ue
            FROM evaluations AS ev
            JOIN matieres AS m ON m.id = ev.matiere_id
            JOIN ues AS u ON u.id = m.ue_id
            JOIN semestres AS s ON s.id = u.semestre_id
            WHERE u.filiere_id = ?
              AND s.annee_scolaire = ?
              AND (? = 0 OR s.numero = ?)
            ORDER BY ev.id
            """,
            (
                etudiant["filiere_id"],
                etudiant["annee_scolaire"],
                semestre,
                semestre,
            ),
        ).fetchall()

        notes = {}

        for inscription in inscriptions:
            lignes = connection.execute(
                """
                SELECT
                    evaluation_id,
                    CASE
                        WHEN statut = 'absence_injustifiee' THEN 0
                        ELSE note
                    END AS note
                FROM resultats
                WHERE inscription_id = ?
                  AND (
                    (statut = 'note' AND note IS NOT NULL)
                    OR statut = 'absence_injustifiee'
                  )
                """,
                (inscription["id"],),
            ).fetchall()

            notes[inscription["id"]] = {
                ligne["evaluation_id"]: ligne["note"]
                for ligne in lignes
            }

    finally:
        connection.close()

    # Mêmes règles que la moyenne affichée à l'étudiant : toutes les
    # évaluations publiées ; une absence injustifiée compte 0, une
    # absence justifiée ne compte pas pour l'étudiant concerné.
    communes = [
        evaluation
        for evaluation in evaluations
        if evaluation["publiee"] and inscriptions
    ]

    resultat = {
        "rang": None,
        "effectif": len(inscriptions),
        "top": None,
        "moyenne": None,
        "nombre_evaluations": len(communes),
        "total_evaluations": len(evaluations),
        "provisoire": len(communes) < len(evaluations),
    }

    if not communes:
        return resultat

    moyennes = {}

    for inscription in inscriptions:
        ues = {}

        for evaluation in communes:
            ue = ues.setdefault(
                evaluation["ue_id"],
                {
                    "coefficient": evaluation["coefficient_ue"],
                    "matieres": {},
                },
            )

            matiere = ue["matieres"].setdefault(
                evaluation["matiere_id"],
                {
                    "coefficient": evaluation["coefficient_matiere"],
                    "evaluations": [],
                },
            )

            matiere["evaluations"].append({
                "moyenne": notes[inscription["id"]].get(evaluation["id"]),
                "coefficient": evaluation["coefficient"],
            })

        for ue in ues.values():
            for matiere in ue["matieres"].values():
                matiere["moyenne"] = moyenne_ponderee(
                    matiere["evaluations"]
                )

            ue["moyenne"] = moyenne_ponderee(
                ue["matieres"].values()
            )

        moyennes[inscription["id"]] = moyenne_ponderee(
            ues.values()
        )

    moyenne = moyennes.get(etudiant["inscription_id"])

    if moyenne is None:
        return resultat

    # Les égalités à deux décimales partagent le même rang.
    moyenne_comparaison = round(moyenne, 2)

    rang = 1 + sum(
        round(valeur, 2) > moyenne_comparaison
        for valeur in moyennes.values()
    )

    resultat.update({
        "rang": rang,
        "top": ceil(100 * rang / len(inscriptions)),
        "moyenne": moyenne,
    })

    return resultat