import csv
import random
from datetime import date, timedelta

from werkzeug.security import generate_password_hash

from database import DATABASE_PATH, get_connection, init_database


ANNEE = "2026-2027"
MOT_DE_PASSE_DEMO = "Demo2026!"

# Générateur indépendant : mêmes données à chaque génération.
rng = random.Random(42)

FILIERES = {
    "DSIA": {
        "nom": "Data Science et Intelligence Artificielle",
        1: [
            "Python",
            "Algorithmique",
            "Bases de données",
            "Statistiques",
            "Machine Learning",
            "Data Engineering",
        ],
        2: [
            "Deep Learning",
            "Analyse d'images",
            "Traitement du langage",
            "Visualisation de données",
            "Données massives",
            "Projet IA",
        ],
    },
    "CYBER": {
        "nom": "Cybersécurité",
        1: [
            "Réseaux",
            "Linux",
            "Programmation sécurisée",
            "Cryptographie",
            "Sécurité des systèmes",
            "Analyse de vulnérabilités",
        ],
        2: [
            "Sécurité web",
            "Investigation numérique",
            "Sécurité réseau",
            "Gestion des incidents",
            "Audit de sécurité",
            "Projet cybersécurité",
        ],
    },
    "EMB": {
        "nom": "Systèmes embarqués",
        1: [
            "Programmation C",
            "Électronique numérique",
            "Microcontrôleurs",
            "Capteurs",
            "Architecture des processeurs",
            "Traitement du signal",
        ],
        2: [
            "Systèmes temps réel",
            "Robotique",
            "Objets connectés",
            "Communication embarquée",
            "Conception FPGA",
            "Projet embarqué",
        ],
    },
    "ENER": {
        "nom": "Énergie",
        1: [
            "Électrotechnique",
            "Thermodynamique",
            "Conversion d'énergie",
            "Automatique",
            "Réseaux électriques",
            "Énergies renouvelables",
        ],
        2: [
            "Stockage de l'énergie",
            "Efficacité énergétique",
            "Réseaux intelligents",
            "Électronique de puissance",
            "Modélisation énergétique",
            "Projet énergie",
        ],
    },
}

PRENOMS = [
    "Lina", "Adam", "Inès", "Hugo", "Sarah",
    "Lucas", "Jade", "Yanis", "Emma", "Nathan",
    "Chloé", "Amir", "Léa", "Noah", "Manon",
    "Louis", "Nora", "Gabriel", "Alice", "Rayan",
    "Zoé", "Paul", "Maya", "Arthur", "Camille",
    "Sami", "Clara", "Ethan", "Louise", "Ilyes",
]

NOMS = [
    "Morel", "Laurent", "Bernard", "Martin",
    "Petit", "Robert", "Richard", "Durand",
    "Dubois", "Simon", "Michel", "Lefebvre",
    "Leroy", "Roux", "David", "Bertrand",
    "Moreau", "Fournier", "Girard", "Bonnet",
]

PROFILS = [
    "regulier",
    "projet",
    "examen",
    "progression",
    "fragile",
]


def ajouter(connection, table, **valeurs):
    """Insère une ligne et renvoie son identifiant."""
    colonnes = ", ".join(valeurs)
    parametres = ", ".join("?" for _ in valeurs)

    curseur = connection.execute(
        f"INSERT INTO {table} ({colonnes}) "
        f"VALUES ({parametres})",
        tuple(valeurs.values()),
    )

    return curseur.lastrowid



def formats_evaluations(nom_matiere):
    """Formats pédagogiques fictifs adaptés à chaque enseignement."""
    formats_specifiques = {
        "Python": [
            ("TP 1 — Fonctions", "TP", 1),
            ("TP 2 — Données", "TP", 1),
            ("Projet Python", "Projet", 3),
            ("Contrôle pratique", "Examen", 2),
        ],
        "Algorithmique": [
            ("QCM 1", "Examen", 1),
            ("QCM 2", "Examen", 1),
            ("Contrôle final", "Examen", 3),
        ],
        "Bases de données": [
            ("TP SQL", "TP", 1),
            ("Projet de modélisation", "Projet", 2),
        ],
        "Statistiques": [
            ("Contrôle continu", "Examen", 1),
            ("Examen final", "Examen", 2),
        ],
        "Machine Learning": [
            ("TP — Classification", "TP", 1),
            ("TP — Régression", "TP", 1),
            ("Projet de prédiction", "Projet", 3),
        ],
        "Data Engineering": [
            ("TP — Pipeline de données", "TP", 1),
            ("Projet ETL", "Projet", 3),
            ("Soutenance", "Projet", 1),
        ],
        "Anglais": [
            ("Compréhension orale", "Examen", 1),
            ("Présentation orale", "Projet", 1),
            ("Examen final", "Examen", 2),
        ],
        "Gestion de projet": [
            ("Dossier de groupe", "Projet", 2),
            ("Soutenance", "Projet", 1),
        ],
        "Management d'équipe": [
            ("Étude de cas", "Projet", 2),
            ("Présentation collective", "Projet", 1),
        ],
    }

    if nom_matiere in formats_specifiques:
        return formats_specifiques[nom_matiere]

    if nom_matiere.startswith("Projet"):
        return [
            ("Livrable intermédiaire", "Projet", 1),
            ("Rapport final", "Projet", 3),
            ("Soutenance finale", "Projet", 2),
        ]

    if nom_matiere in {
        "Réseaux", "Linux", "Sécurité réseau",
        "Microcontrôleurs", "Capteurs", "Robotique",
        "Objets connectés", "Électronique numérique",
        "Électronique de puissance", "Conception FPGA",
    }:
        return [
            ("TP 1", "TP", 1),
            ("TP 2", "TP", 1),
            ("Contrôle pratique", "Examen", 2),
        ]

    if nom_matiere in {
        "Cryptographie", "Thermodynamique",
        "Architecture des processeurs", "Traitement du signal",
        "Automatique", "Modélisation énergétique",
    }:
        return [
            ("Interrogation écrite", "Examen", 1),
            ("Examen final", "Examen", 3),
        ]

    return [
        ("TP d'application", "TP", 1),
        ("Étude de cas", "Projet", 2),
        ("Contrôle final", "Examen", 2),
    ]


def creer_programme(connection, filiere_id, programme, semestres):
    """Crée les UE, matières et évaluations d'une filière."""
    evaluations = []

    for semestre in (1, 2):
        blocs = [
            (
                "Sciences et techniques — Fondamentaux",
                10,
                programme[semestre][:3],
            ),
            (
                "Sciences et techniques — Spécialité",
                10,
                programme[semestre][3:],
            ),
            (
                "Management et sciences humaines",
                5,
                [
                    "Gestion de projet"
                    if semestre == 1
                    else "Management d'équipe"
                ],
            ),
            (
                "Langues vivantes",
                5,
                ["Anglais"],
            ),
        ]

        debut = (
            date(2026, 9, 14)
            if semestre == 1
            else date(2027, 2, 1)
        )

        for nom_ue, coefficient_ue, matieres in blocs:
            ue_id = ajouter(
                connection,
                "ues",
                nom=nom_ue,
                filiere_id=filiere_id,
                semestre_id=semestres[semestre],
                coefficient=coefficient_ue,
            )

            for nom_matiere in matieres:
                matiere_id = ajouter(
                    connection,
                    "matieres",
                    nom=nom_matiere,
                    ue_id=ue_id,
                    coefficient=1,
                )

                formats = formats_evaluations(nom_matiere)

                for position, (nom, type_eval, coef) in enumerate(formats):
                    # Exemple volontaire de résultats non publiés.
                    publiee = not (
                        semestre == 2
                        and nom_matiere == "Anglais"
                        and type_eval == "Examen"
                    )

                    evaluation_id = ajouter(
                        connection,
                        "evaluations",
                        nom=nom,
                        type_evaluation=type_eval,
                        matiere_id=matiere_id,
                        date_evaluation=(
                            debut + timedelta(days=21 + position * 28)
                        ).isoformat(),
                        coefficient=coef,
                        publiee=int(publiee),
                    )

                    evaluations.append({
                        "id": evaluation_id,
                        "semestre": semestre,
                        "type": type_eval,
                        "matiere_id": matiere_id,
                    })

    return evaluations


def creer_resultat(base, profil, semestre, type_eval, aisance):
    """Produit une note plausible ou un statut sans note."""
    tirage = rng.random()

    if tirage < 0.02:
        return None, "absence_justifiee"

    if tirage < 0.035:
        return None, "absence_injustifiee"

    if tirage < 0.06:
        return None, "en_attente"

    bonus = 0

    if profil == "projet":
        bonus = 2 if type_eval == "Projet" else -1

    elif profil == "examen":
        bonus = 2 if type_eval == "Examen" else -0.5

    elif profil == "progression" and semestre == 2:
        bonus = 2

    note = base + aisance + bonus + rng.gauss(0, 1.3)
    note = round(min(20, max(0, note)) * 2) / 2

    return note, "note"


def exporter_csv(connection):
    """Exporte les tables utiles, sans les mots de passe hachés."""
    dossier = DATABASE_PATH.parent / "exports"
    dossier.mkdir(parents=True, exist_ok=True)

    tables = [
        "filieres", "groupes", "etudiants", "inscriptions",
        "semestres", "ues", "matieres", "evaluations", "resultats",
    ]

    for table in tables:
        colonnes = (
            "id, numero, prenom, nom, email, statut"
            if table == "etudiants"
            else "*"
        )

        curseur = connection.execute(
            f"SELECT {colonnes} FROM {table} ORDER BY id"
        )

        with (dossier / f"{table}.csv").open(
            "w", encoding="utf-8-sig", newline=""
        ) as fichier:
            writer = csv.writer(fichier, delimiter=";")
            writer.writerow(
                colonne[0] for colonne in curseur.description
            )
            writer.writerows(curseur.fetchall())


def main():
    init_database()
    connection = get_connection()

    try:
        nombre = connection.execute(
            "SELECT COUNT(*) FROM filieres"
        ).fetchone()[0]

        if nombre:
            print(
                "La base contient déjà des données. "
                "Aucune donnée n'a été modifiée."
            )
            return

        with connection:
            semestres = {
                numero: ajouter(
                    connection,
                    "semestres",
                    numero=numero,
                    annee_scolaire=ANNEE,
                )
                for numero in (1, 2)
            }

            compteur = 0

            for code, programme in FILIERES.items():
                filiere_id = ajouter(
                    connection,
                    "filieres",
                    code=code,
                    nom=programme["nom"],
                )

                groupes = [
                    ajouter(
                        connection,
                        "groupes",
                        nom=f"{code}-{lettre}",
                        filiere_id=filiere_id,
                        niveau="E4",
                        annee_scolaire=ANNEE,
                    )
                    for lettre in ("A", "B")
                ]

                evaluations = creer_programme(
                    connection, filiere_id, programme, semestres
                )

                for position in range(30):
                    compteur += 1
                    profil = PROFILS[position % len(PROFILS)]

                    base = (
                        rng.uniform(7, 10)
                        if profil == "fragile"
                        else rng.uniform(10, 16)
                    )

                    etudiant_id = ajouter(
                        connection,
                        "etudiants",
                        numero=f"ETU{compteur:04d}",
                        prenom=PRENOMS[position],
                        nom=rng.choice(NOMS),
                        email=f"etudiant{compteur:04d}@example.com",
                        mot_de_passe_hash=generate_password_hash(
                            MOT_DE_PASSE_DEMO
                        ),
                        statut=(
                            "apprentissage"
                            if position % 3 == 0
                            else "initial"
                        ),
                    )

                    inscription_id = ajouter(
                        connection,
                        "inscriptions",
                        etudiant_id=etudiant_id,
                        groupe_id=groupes[position // 15],
                    )

                    # Une aisance propre à chaque matière.
                    aisances = {}

                    for index, evaluation in enumerate(evaluations):
                        matiere_id = evaluation["matiere_id"]

                        if matiere_id not in aisances:
                            aisances[matiere_id] = rng.uniform(-2, 2)

                        note, statut = creer_resultat(
                            base,
                            profil,
                            evaluation["semestre"],
                            evaluation["type"],
                            aisances[matiere_id],
                        )

                        # Cas limites garantis pour la démonstration.
                        if compteur == 1:
                            cas = {
                                0: (0, "note"),
                                1: (20, "note"),
                                2: (None, "absence_justifiee"),
                                3: (None, "absence_injustifiee"),
                                4: (None, "en_attente"),
                            }

                            if index in cas:
                                note, statut = cas[index]

                        ajouter(
                            connection,
                            "resultats",
                            inscription_id=inscription_id,
                            evaluation_id=evaluation["id"],
                            note=note,
                            statut=statut,
                        )

        exporter_csv(connection)

        print("Jeu de données fictives créé.")
        print("4 filières, 8 groupes et 120 étudiants.")
        nombre_resultats = connection.execute(
            "SELECT COUNT(*) FROM resultats"
        ).fetchone()[0]
        print(f"2 semestres et {nombre_resultats} résultats.")
        print("Exports CSV disponibles dans data/exports.")
        print(f"Mot de passe des comptes de démonstration : {MOT_DE_PASSE_DEMO}")

    finally:
        connection.close()


if __name__ == "__main__":
    main()