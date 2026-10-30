import csv
import random
from datetime import date, timedelta

from werkzeug.security import generate_password_hash

from database import DATABASE_PATH, get_connection, init_database


ANNEE = "2026-2027"
MOT_DE_PASSE_DEMO = "Demo2026!"

# Générateur indépendant : mêmes données à chaque génération.
rng = random.Random(42)

# Programme réel E4 2026-2027 (document « Organisation des programmes
# E4 », V1 du 13/04/2026). Le semestre 1 de l'application correspond
# au S3 de l'école, le semestre 2 au S4.
# Les cours au choix (management, ouvertures) sont fixés par filière
# pour simplifier : dans la réalité, chaque étudiant choisit les siens.
FILIERES = {
    "DSIA": {
        "nom": "Data Science et Intelligence Artificielle",
        "approfondissement_1": [
            "Python 1 : programmation avancée",
            "Algorithm Design",
            "Python 2 : manipulation de données",
        ],
        "approfondissement_2": [
            "Apprentissage automatique 1",
            "DevOps Data",
            "Data Engineering",
            "Optimisation pour les systèmes intelligents",
        ],
        "management_s1": ["UX Design", "Management de l'innovation"],
        "ouvertures_s1": [
            "Theoretical Foundations of Deep Learning",
            "Développement Web Front-End",
        ],
        "approfondissement_3": [
            "Machine Learning 2",
            "Exposure to Research: Data Science and AI",
            "Deep & Reinforcement Learning",
        ],
        "management_s2": "Droit des affaires",
        "ouverture_s2": "Initiation au langage Rust",
    },
    "CYBER": {
        "nom": "Cybersécurité",
        "approfondissement_1": [
            "Normes ISO et IAM",
            "Sécurité système Windows/Linux",
            "Advanced Linux Operating System",
        ],
        "approfondissement_2": [
            "Sécurité des systèmes d'information",
            "Sécurité des systèmes virtualisés et matérialités",
            "Sécurité des réseaux locaux",
            "Active Directory",
        ],
        "management_s1": ["Sociologie du numérique", "Risk Management"],
        "ouvertures_s1": [
            "Cryptographie et sécurité des communications",
            "Architecture des ordinateurs",
        ],
        "approfondissement_3": [
            "Cyber Defense and Attack",
            "Virtualized OS Security",
            "Exposition à la recherche : réseaux et méthode EBIOS RM",
        ],
        "management_s2": "International Management",
        "ouverture_s2": "Rétro-ingénierie",
    },
    "EMB": {
        "nom": "Systèmes embarqués",
        "approfondissement_1": [
            "Architectures numériques embarquées",
            "Systèmes à événements discrets / SysML",
            "Robotique mobile et navigation autonome",
        ],
        "approfondissement_2": [
            "Filtrage adaptatif",
            "Temps réel",
            "Intelligence artificielle embarquée",
            "SysML pour les systèmes embarqués",
        ],
        "management_s1": [
            "Management d'équipe et leadership",
            "Veille technologique",
        ],
        "ouvertures_s1": [
            "Système d'aide à la conduite automobile (ADAS)",
            "Introduction to Robotics",
        ],
        "approfondissement_3": [
            "Temps réel distribué",
            "Contrôle et optimisation des systèmes",
            "Électronique pour les systèmes embarqués",
        ],
        "management_s2": "Diriger et décider",
        "ouverture_s2": "IA embarquée avec les architectures NPU",
    },
    "ENER": {
        "nom": "Énergie",
        "approfondissement_1": [
            "Machines thermiques",
            "Distribution de l'énergie électrique",
            "Exposition à la recherche : transferts de chaleur I",
        ],
        "approfondissement_2": [
            "Énergies renouvelables pour la production d'électricité",
            "Électronique de puissance pour les ENR",
            "Énergétique du bâtiment",
            "Transferts de chaleur II",
        ],
        "management_s1": [
            "Management de la RSE",
            "Politiques énergétiques et environnementales",
        ],
        "ouvertures_s1": [
            "Énergie nucléaire : physique et technologies",
            "Énergie hydraulique",
        ],
        "approfondissement_3": [
            "Numerical Methods for Energy, Thermal and Fluid Engineering",
            "Electric Machines",
            "Exposure to Research: Energy Lab",
        ],
        "management_s2": "Économie et environnement",
        "ouverture_s2": "Life Cycle Analysis",
    },
}


def blocs_du_semestre(programme, semestre):
    """UE du semestre : (nom, coefficient, [(matière, ECTS), ...])."""
    if semestre == 1:
        return [
            (
                "Sciences et techniques — Approfondissement 1",
                10,
                [(nom, 2.5) for nom in programme["approfondissement_1"]]
                + [("Traitement du signal", 2.5)],
            ),
            (
                "Sciences et techniques — Approfondissement 2",
                10,
                [(nom, 2.5) for nom in programme["approfondissement_2"]],
            ),
            (
                "Management et sciences humaines",
                4,
                [(nom, 1.6) for nom in programme["management_s1"]]
                + [("Compétences & carrières", 0.8)],
            ),
            (
                "Sciences et techniques — Ouvertures",
                4,
                [(nom, 2) for nom in programme["ouvertures_s1"]],
            ),
            (
                "Langues vivantes",
                2,
                [("English CV", 0.7), ("English Electives 1", 1.3)],
            ),
        ]

    return [
        (
            "Sciences et techniques — Approfondissement 3",
            9,
            [(nom, 3) for nom in programme["approfondissement_3"]],
        ),
        (
            "Management et sciences humaines",
            3,
            [
                (programme["management_s2"], 2),
                ("Compétences & carrières", 1),
            ],
        ),
        (
            "Sciences et techniques — Ouvertures",
            6,
            [(programme["ouverture_s2"], 2), ("Projet E4", 4)],
        ),
        (
            "Langues vivantes",
            2,
            [("English Electives 2", 2)],
        ),
        (
            "Stage",
            10,
            [("Stage", 1)],
        ),
    ]


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
    """Formats d'évaluation plausibles (choisis pour la démonstration)."""
    nom = nom_matiere.lower()

    formats_specifiques = {
        "Python 1 : programmation avancée": [
            ("TP 1 — Fonctions", "TP", 1),
            ("TP 2 — Données", "TP", 1),
            ("Projet Python", "Projet", 3),
            ("Contrôle pratique", "Examen", 2),
        ],
        "Python 2 : manipulation de données": [
            ("TP — Pandas", "TP", 1),
            ("TP — Visualisation", "TP", 1),
            ("Projet d'analyse de données", "Projet", 3),
        ],
        "UX Design": [
            ("Maquette interactive", "Projet", 2),
            ("Tests utilisateurs", "Projet", 1),
            ("Soutenance", "Projet", 1),
        ],
        "Traitement du signal": [
            ("TP 1 — Filtrage", "TP", 1),
            ("TP 2 — Transformée de Fourier", "TP", 1),
            ("Examen final", "Examen", 3),
        ],
        "Compétences & carrières": [
            ("Bilan de compétences", "Projet", 1),
        ],
        "English CV": [
            ("CV et lettre de motivation", "Projet", 1),
        ],
        "Projet E4": [
            ("Cahier des charges", "Projet", 1),
            ("Rapport final", "Projet", 3),
            ("Soutenance finale", "Projet", 2),
        ],
        "Stage": [
            ("Rapport de stage", "Projet", 2),
            ("Soutenance de stage", "Projet", 1),
            ("Évaluation de l'entreprise", "Projet", 1),
        ],
    }

    if nom_matiere in formats_specifiques:
        return formats_specifiques[nom_matiere]

    if nom.startswith("english"):
        return [
            ("Compréhension orale", "Examen", 1),
            ("Présentation orale", "Projet", 1),
            ("Examen final", "Examen", 2),
        ]

    if "research" in nom or "recherche" in nom:
        return [
            ("Analyse d'article", "Projet", 1),
            ("Rapport de recherche", "Projet", 2),
            ("Soutenance", "Projet", 1),
        ]

    if any(mot in nom for mot in (
        "learning", "apprentissage", "data", "devops", "web",
        "rust", "robotics", "robotique", "intelligence", "ia ",
    )):
        return [
            ("TP 1", "TP", 1),
            ("TP 2", "TP", 1),
            ("Projet", "Projet", 3),
        ]

    if any(mot in nom for mot in (
        "sécurité", "security", "linux", "active directory",
        "défense", "defense", "rétro", "réseaux",
    )):
        return [
            ("TP 1", "TP", 1),
            ("TP 2", "TP", 1),
            ("Contrôle pratique", "Examen", 2),
        ]

    if any(mot in nom for mot in (
        "management", "marketing", "droit", "économie", "sociologie",
        "veille", "diriger", "rse", "politiques", "risk", "innovation",
        "life cycle",
    )):
        return [
            ("Étude de cas", "Projet", 2),
            ("Présentation orale", "Projet", 1),
        ]

    if any(mot in nom for mot in (
        "algorithm", "optimisation", "cryptographie", "architecture",
        "temps réel", "filtrage", "methods", "transferts", "thermiques",
    )):
        return [
            ("QCM", "Examen", 1),
            ("Contrôle continu", "Examen", 1),
            ("Examen final", "Examen", 3),
        ]

    return [
        ("TP d'application", "TP", 1),
        ("Contrôle continu", "Examen", 1),
        ("Examen final", "Examen", 2),
    ]


def creer_programme(connection, filiere_id, programme, semestres):
    """Crée les UE, matières et évaluations d'une filière."""
    evaluations = []

    # Matières dont la dernière évaluation n'est pas encore publiée.
    # Tous les étudiants reçoivent leurs notes en même temps : une
    # évaluation est publiée pour tout le monde, ou « à venir ».
    # Le semestre 1 est terminé : les notes à venir sont au semestre 2.
    derniere_a_venir = {
        programme["approfondissement_3"][0],
        programme["approfondissement_3"][1],
        programme["approfondissement_3"][2],
        "English Electives 2",
        "Projet E4",
    }

    for semestre in (1, 2):
        blocs = blocs_du_semestre(programme, semestre)

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

            for nom_matiere, credits in matieres:
                matiere_id = ajouter(
                    connection,
                    "matieres",
                    nom=nom_matiere,
                    ue_id=ue_id,
                    coefficient=credits,
                )

                formats = formats_evaluations(nom_matiere)

                for position, (nom, type_eval, coef) in enumerate(formats):
                    # Le stage (fin d'année) n'est pas encore publié, ni la
                    # dernière évaluation des matières choisies plus haut.
                    publiee = not (
                        nom_matiere == "Stage"
                        or (
                            nom_matiere in derniere_a_venir
                            and position == len(formats) - 1
                        )
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
                        "nom": nom,
                        "matiere": nom_matiere,
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

                    # Niveaux réalistes : moyenne de promo autour de 11,5.
                    base = (
                        rng.uniform(6.5, 9.5)
                        if profil == "fragile"
                        else rng.uniform(9.5, 14.5)
                    )

                    # Lina (compte de démonstration) : bonne étudiante,
                    # dans le haut du classement de sa filière.
                    if compteur == 1:
                        base = 14

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