from database import get_connection


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
                if (
                    evaluation["publiee"]
                    and evaluation["statut"] == "note"
                    and evaluation["note"] is not None
                ):
                    notes_disponibles.append({
                        "moyenne": evaluation["note"],
                        "coefficient": evaluation["coefficient"],
                    })

            matiere["moyenne"] = moyenne_ponderee(
                notes_disponibles
            )

            matiere["provisoire"] = (
                not evaluations
                or len(notes_disponibles) < len(evaluations)
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
                        element["note"]
                        for element in equivalents_evaluations
                        if (
                            element["publiee"]
                            and element["statut"] == "note"
                            and element["note"] is not None
                        )
                    ]

                    evaluation["moyenne_classe"] = (
                        moyenne_simple(notes)
                    )

                    evaluation["classe_provisoire"] = (
                        len(notes) < len(inscriptions)
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