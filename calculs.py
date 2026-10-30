import math

from database import get_connection


def valeur_comptee(evaluation):
    """Valeur qui entre dans la moyenne, ou None si elle ne compte pas.

    - note publiée : la note ;
    - absence injustifiée : 0/20 ;
    - absence justifiée, note en attente ou non publiée : ne compte pas.
    """
    if not evaluation["publiee"]:
        return None

    if evaluation["statut"] == "note" and evaluation["note"] is not None:
        return evaluation["note"]

    if evaluation["statut"] == "absence_injustifiee":
        return 0.0

    return None


def a_venir(evaluation):
    """Note que l'enseignant n'a pas encore mise (ou pas encore publiée)."""
    return (
        not evaluation["publiee"]
        or evaluation["statut"] in (None, "en_attente")
    )


def moyenne_ponderee(elements):
    """Calcule une moyenne à partir des valeurs disponibles."""
    total = 0
    somme_coefficients = 0

    for element in elements:
        moyenne = element["moyenne"]
        coefficient = element["coefficient"]

        if moyenne is not None:
            total += moyenne * coefficient
            somme_coefficients += coefficient

    if somme_coefficients == 0:
        return None

    return total / somme_coefficients


def moyenne_simple(valeurs):
    """Calcule la moyenne des valeurs disponibles."""
    disponibles = [
        valeur for valeur in valeurs
        if valeur is not None
    ]

    if not disponibles:
        return None

    return sum(disponibles) / len(disponibles)


def calculer_moyennes_personnelles(ues):
    """Calcule les moyennes personnelles dans la structure."""
    for ue in ues:
        for matiere in ue["matieres"]:
            evaluations = matiere["evaluations"]
            notes_disponibles = []

            for evaluation in evaluations:
                valeur = valeur_comptee(evaluation)

                if valeur is not None:
                    notes_disponibles.append({
                        "moyenne": valeur,
                        "coefficient": evaluation["coefficient"],
                    })

            matiere["moyenne"] = moyenne_ponderee(
                notes_disponibles
            )

            matiere["provisoire"] = (
                not evaluations
                or any(a_venir(evaluation) for evaluation in evaluations)
            )

        ue["moyenne"] = moyenne_ponderee(ue["matieres"])

        ue["provisoire"] = (
            not ue["matieres"]
            or any(
                matiere["provisoire"]
                for matiere in ue["matieres"]
            )
        )

    return {
        "moyenne": moyenne_ponderee(ues),
        "provisoire": (
            not ues
            or any(ue["provisoire"] for ue in ues)
        ),
    }


def ajouter_moyennes_classe(ues, inscription_id):
    """Calcule les moyennes des étudiants du même groupe."""
    connection = get_connection()

    try:
        inscriptions = connection.execute(
            """
            SELECT id
            FROM inscriptions
            WHERE groupe_id = (
                SELECT groupe_id
                FROM inscriptions
                WHERE id = ?
            )
            ORDER BY id
            """,
            (inscription_id,),
        ).fetchall()

        # On prépare un arbre de résultats pour chaque étudiant.
        arbres_classe = []

        for inscription in inscriptions:
            arbre = []

            for ue in ues:
                ue_classe = {
                    "coefficient": ue["coefficient"],
                    "matieres": [],
                }

                for matiere in ue["matieres"]:
                    evaluations = connection.execute(
                        """
                        SELECT
                            ev.id,
                            ev.coefficient,
                            ev.publiee,
                            CASE
                                WHEN ev.publiee = 1
                                THEN r.note
                                ELSE NULL
                            END AS note,
                            CASE
                                WHEN ev.publiee = 1
                                THEN r.statut
                                ELSE NULL
                            END AS statut
                        FROM evaluations AS ev
                        LEFT JOIN resultats AS r
                            ON r.evaluation_id = ev.id
                            AND r.inscription_id = ?
                        WHERE ev.matiere_id = ?
                        ORDER BY ev.date_evaluation, ev.id
                        """,
                        (inscription["id"], matiere["id"]),
                    ).fetchall()

                    ue_classe["matieres"].append({
                        "coefficient": matiere["coefficient"],
                        "evaluations": evaluations,
                    })

                arbre.append(ue_classe)

            calculer_moyennes_personnelles(arbre)
            arbres_classe.append(arbre)

        for index_ue, ue in enumerate(ues):
            equivalents_ue = [
                arbre[index_ue]
                for arbre in arbres_classe
            ]

            ue["moyenne_classe"] = moyenne_simple([
                element["moyenne"]
                for element in equivalents_ue
            ])

            ue["classe_provisoire"] = (
                not equivalents_ue
                or any(
                    element["provisoire"]
                    for element in equivalents_ue
                )
            )

            for index_matiere, matiere in enumerate(ue["matieres"]):
                equivalents_matieres = [
                    element["matieres"][index_matiere]
                    for element in equivalents_ue
                ]

                matiere["moyenne_classe"] = moyenne_simple([
                    element["moyenne"]
                    for element in equivalents_matieres
                ])

                matiere["classe_provisoire"] = (
                    not equivalents_matieres
                    or any(
                        element["provisoire"]
                        for element in equivalents_matieres
                    )
                )

                evaluations_affichage = []

                for index_eval, evaluation in enumerate(
                    matiere["evaluations"]
                ):
                    evaluation = dict(evaluation)

                    equivalents_evaluations = [
                        element["evaluations"][index_eval]
                        for element in equivalents_matieres
                    ]

                    notes = [
                        valeur_comptee(element)
                        for element in equivalents_evaluations
                    ]

                    evaluation["moyenne_classe"] = (
                        moyenne_simple(notes)
                    )

                    evaluation["classe_provisoire"] = any(
                        a_venir(element)
                        for element in equivalents_evaluations
                    )

                    evaluations_affichage.append(evaluation)

                matiere["evaluations"] = evaluations_affichage

    finally:
        connection.close()


def calculer_resultats(ues, inscription_id=None):
    """Calcule les résultats personnels et ceux de la classe."""
    bilan = calculer_moyennes_personnelles(ues)

    if inscription_id is not None:
        ajouter_moyennes_classe(ues, inscription_id)

    return bilan

def note_necessaire(evaluations, cible=10):
    """Note à obtenir aux évaluations à venir pour atteindre la cible.

    Évaluations à venir : non publiées ou en attente de note.
    Une absence injustifiée compte 0 ; une absence justifiée ne compte
    pas. On suppose la même note à chaque évaluation restante.
    """
    total = 0
    coefficients_acquis = 0
    restantes = []

    for evaluation in evaluations:
        valeur = valeur_comptee(evaluation)

        if valeur is not None:
            total += valeur * evaluation["coefficient"]
            coefficients_acquis += evaluation["coefficient"]
        elif a_venir(evaluation):
            restantes.append(evaluation)

    if not restantes:
        return None

    coefficients_restants = sum(
        evaluation["coefficient"] for evaluation in restantes
    )

    besoin = (
        cible * (coefficients_acquis + coefficients_restants) - total
    ) / coefficients_restants

    # Arrondi au dixième supérieur : on ne promet jamais trop peu.
    besoin = math.ceil(round(besoin * 10, 6)) / 10

    if besoin <= 0:
        etat = "assuree"
    elif besoin > 20:
        etat = "impossible"
    else:
        etat = "possible"

    return {
        "note": besoin,
        "etat": etat,
        "cible": cible,
        "evaluations": [evaluation["nom"] for evaluation in restantes],
    }


def ajouter_objectifs(ues):
    """Ajoute à chaque matière la note nécessaire pour avoir la moyenne."""
    for ue in ues:
        for matiere in ue["matieres"]:
            matiere["objectif"] = note_necessaire(matiere["evaluations"])
