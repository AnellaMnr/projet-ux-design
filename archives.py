"""Archives des années précédentes (E1, E2, E3).

Les matières viennent des programmes officiels d'ESIEE Paris :
- « Enseignements de 1re et 2e année (E1 - E2) », mise à jour juin 2026 ;
- « Tableau des programmes E3 » (E3E, E3S, E3T).

Les notes sont fictives et générées de façon reproductible : un même
étudiant voit toujours les mêmes archives. Le programme E3 ne donne
pas d'ECTS : la répartition en UE et les crédits de l'E3 sont choisis
pour la démonstration.

Parcours selon l'étudiant :
- apprentissage : entrée en E3 après DUT, BTS ou licence (E3T) ;
- formation initiale : soit E1 → E2 → E3 à ESIEE Paris (E3E),
  soit entrée en E3 après une classe préparatoire (E3S).
"""

import random

# Cours au choix d'E2 et d'E3, cohérents avec la filière suivie en E4.
ELECTIVE_E2 = {
    "DSIA": "Programmation en Python",
    "CYBER": "Introduction aux réseaux et à la cybersécurité",
    "EMB": "Électronique sur carte (PCB) et FPGA",
    "ENER": "Cartographie énergétique",
}

ELECTIVE_E3 = {
    "DSIA": "IA et Deep Learning",
    "CYBER": "Cybersécurité avancée",
    "EMB": "Robotique",
    "ENER": "Distribution énergie électrique",
}

OPTIONS_ARTISTIQUES = [
    "Design et créativité", "Théâtre", "Court métrage fiction",
    "Improvisations", "Écriture littéraire", "Exploring Music",
]

OPTIONS_SOCIETE = [
    "L'actualité économique en questions", "Tech for Good",
    "Scientific journalism", "Sciences, techniques et sociétés",
    "Art et sciences",
]

LANGUES = ["Espagnol", "Allemand", "Chinois", "Japonais"]

PROGRAMMATION_E3 = [
    "Programmation Java et C (par problèmes)",
    "Programmation Python et C",
]


def programme_e1(rng, filiere):
    return {
        1: [
            ("Sciences fondamentales", 10, [
                "Maths générales", "Analyse",
                "Mécanique du point", "Énergie mécanique",
            ]),
            ("Sciences de l'ingénieur", 4, [
                "Fonctions numériques",
                "Initiation à la programmation et aux algorithmes",
            ]),
            ("Ateliers", 4, [
                "Rédiger un document scientifique",
                "Régression linéaire",
                "Calculatrice pour les complexes",
            ]),
            ("Management, sciences humaines et langues", 4, [
                "L'ingénieur explorateur", "English One",
            ]),
        ],
        2: [
            ("Sciences fondamentales", 14.5, [
                "Maths générales (suite)", "Analyse (suite)",
                "Algèbre linéaire", "Systèmes oscillants",
                "Introduction à la magnétostatique", "Électrostatique",
            ]),
            ("Sciences de l'ingénieur", 11.5, [
                "Électronique : régime continu",
                "Électronique : régime alternatif",
                "Initiation à la programmation objet",
                "Initiation à la programmation des microprocesseurs",
            ]),
            ("Ateliers", 6, [
                "Chiffrement asymétrique RSA", "Carte PCB",
                "Feux tricolores",
            ]),
            ("Management, sciences humaines et langues", 6, [
                "Controverses", "English Two",
            ]),
        ],
    }


def programme_e2(rng, filiere):
    return {
        1: [
            ("Sciences fondamentales", 10, [
                "Algèbre linéaire", "Séries", "Thermodynamique",
                "Mécanique du solide", "Magnétostatique",
            ]),
            ("Sciences de l'ingénieur", 7.5, [
                "Électronique : conception", "Algorithmique",
            ]),
            ("Ateliers et électives", 5, [
                "Algèbre linéaire et vision 3D",
                ELECTIVE_E2.get(filiere, "Programmation en Python"),
            ]),
            ("Management, sciences humaines et langues", 7.5, [
                "English Three",
                rng.choice(OPTIONS_ARTISTIQUES),
                rng.choice(LANGUES),
            ]),
        ],
        2: [
            ("Sciences fondamentales", 11, [
                "Maths discrètes", "Fonctions de plusieurs variables",
                "Probabilités", "Ondes",
                "Optique ondulatoire et corpusculaire",
            ]),
            ("Sciences fondamentales physique", 9, [
                "Signaux et systèmes", "Traitements numériques matériels",
                "La ligne de commande",
                "Programmation en C et efficacité énergétique",
            ]),
            ("Ateliers", 4, [
                "Applications en maths", "Phénomènes de diffusion",
                "Introduction to International Competence",
            ]),
            ("Management, sciences humaines et langues", 6, [
                "English Four",
                rng.choice(OPTIONS_SOCIETE),
                rng.choice(LANGUES),
            ]),
        ],
    }


def programme_e3(rng, filiere, parcours):
    if parcours == "E3E":
        sciences_s1 = [
            ("Sciences et techniques", 16, [
                "Systèmes électroniques analogiques", "Probabilités",
                "Systèmes d'exploitation", "Réseaux",
            ]),
            ("Stage technicien", 6, ["Stage technicien (2 mois)"]),
        ]
        langues_s1 = ["Presentation Skills", rng.choice(LANGUES)]
    else:
        if parcours == "E3S":
            choix = [
                "Traitement de l'information analogique",
                "Introduction à l'électronique numérique",
                "Programmation et systèmes à base de microprocesseurs",
            ]
        else:  # E3T
            choix = [
                rng.choice([
                    "Lois fondamentales de l'électrostatique "
                    "à l'électromagnétisme",
                    "Traitement de l'information analogique",
                ]),
                rng.choice([
                    "Électronique numérique « débutant »",
                    "Thermodynamique",
                ]),
                "Analyse", "Algèbre linéaire",
            ]

        sciences_s1 = [
            ("Sciences et techniques", 22, choix + [
                rng.choice(PROGRAMMATION_E3),
                "Probabilités", "Outils pour le traitement du signal",
                "Algorithmique", "Réseaux",
            ]),
        ]
        langues_s1 = ["Integrated Language Skills", "Anglais renforcé"]

    return {
        1: sciences_s1 + [
            ("Management et sciences humaines", 8, [
                "Initiation au management",
                "Projet personnel et professionnel",
            ] + langues_s1),
        ],
        2: [
            ("Sciences et techniques", 15, [
                "Optimisation et introduction à l'IA",
                "Bases de données relationnelles",
                "Contrôle des systèmes dynamiques",
                "Systèmes électroniques à base de microcontrôleurs",
                "Cybersécurité",
                "Éthique et impact sociétal des technologies",
            ]),
            ("Électives", 5, [
                ELECTIVE_E3.get(filiere, "Data Sciences"),
            ]),
            ("Management et sciences humaines", 5, [
                "Suite de l'introduction au management",
                "Management de projet : théories et pratique",
                "Anglais renforcé",
            ]),
            ("Projet", 5, ["Projet E3"]),
        ],
    }


PARCOURS = {
    "E3E": "Entrée en E1 à ESIEE Paris",
    "E3S": "Entrée en E3 après une classe préparatoire",
    "E3T": "Entrée en E3 après un DUT, un BTS ou une licence",
}


def _annee_precedente(annee_scolaire, ecart):
    """« 2026-2027 », 1 -> « 2025-2026 »."""
    debut = int(annee_scolaire.split("-")[0]) - ecart
    return f"{debut}-{debut + 1}"


def _moyenne_ponderee(elements, cle="coefficient"):
    total = sum(e[cle] for e in elements)
    return sum(e["moyenne"] * e[cle] for e in elements) / total


def _noter(rng, niveau_eleve, programme):
    """Ajoute des notes fictives à un programme d'une année."""
    semestres = []

    for numero in (1, 2):
        ues = []

        for nom_ue, credits, matieres in programme[numero]:
            notes = []

            for nom_matiere in matieres:
                note = rng.gauss(niveau_eleve, 2)
                note = round(min(19.5, max(6.0, note)) * 2) / 2
                notes.append({"nom": nom_matiere, "moyenne": note})

            ues.append({
                "nom": nom_ue,
                "coefficient": credits,
                "matieres": notes,
                "moyenne": sum(n["moyenne"] for n in notes) / len(notes),
            })

        semestres.append({
            "numero": numero,
            "ues": ues,
            "moyenne": _moyenne_ponderee(ues),
            "credits": sum(ue["coefficient"] for ue in ues),
        })

    toutes_les_ues = [ue for s in semestres for ue in s["ues"]]
    return semestres, _moyenne_ponderee(toutes_les_ues)


def parcours_etudiant(numero, statut):
    if statut == "apprentissage":
        return "E3T"

    rng = random.Random(f"parcours-{numero}")
    return "E3E" if rng.random() < 0.65 else "E3S"


def generer_archives(numero, statut, annee_scolaire, filiere):
    """Retourne (libellé du parcours, années de la plus récente à la plus ancienne)."""
    rng = random.Random(f"archives-{numero}")
    niveau_eleve = rng.uniform(10.5, 15.5)
    parcours = parcours_etudiant(numero, statut)

    niveaux = [("E3", programme_e3(rng, filiere, parcours))]

    if parcours == "E3E":
        niveaux += [
            ("E2", programme_e2(rng, filiere)),
            ("E1", programme_e1(rng, filiere)),
        ]

    annees = []

    for ecart, (niveau, programme) in enumerate(niveaux, start=1):
        semestres, moyenne = _noter(rng, niveau_eleve, programme)
        credits = sum(s["credits"] for s in semestres)

        annees.append({
            "niveau": niveau,
            "annee_scolaire": _annee_precedente(annee_scolaire, ecart),
            "semestres": semestres,
            "moyenne": moyenne,
            "validee": moyenne >= 10,
            "credits": round(credits) if moyenne >= 10 else 0,
        })

    return PARCOURS[parcours], annees
