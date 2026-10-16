# Portail étudiant — Projet UX Design

Prototype réalisé en groupe de quatre dans le cadre du cours d’UX Design à ESIEE Paris, en quatrième année du cycle ingénieur.

## Notre équipe

- Anella Manari
- Lilou Parrin
- Antoine Navarro
- Fregice Betsaka Tekoutche

## Présentation du projet

Notre projet consiste à concevoir un portail permettant à un étudiant de consulter ses résultats scolaires et de comprendre leur organisation.

Nous sommes partis d’un croquis pour construire une interface avec deux niveaux de lecture : une synthèse de la situation de l’étudiant, puis un accès au détail des notes.

En haut de la page, deux encadrés présentent la moyenne générale et le classement. En dessous, un tableau permet de parcourir les UE, les matières et les évaluations.

Le portail utilise des données fictives. Il n’est pas connecté au système de scolarité d’ESIEE Paris et ne constitue pas un service officiel de l’école.

## Population représentée

Le jeu de démonstration représente l’année scolaire 2026-2027 et comprend :

- 120 étudiants de niveau E4 ;
- 4 filières ;
- 30 étudiants par filière ;
- 2 groupes de 15 étudiants par filière ;
- 8 groupes au total ;
- des étudiants en formation initiale et en apprentissage.

| Filière | Code | Groupes | Effectif |
|---|---|---|---:|
| Data Science et Intelligence Artificielle | DSIA | DSIA-A et DSIA-B | 30 |
| Cybersécurité | CYBER | CYBER-A et CYBER-B | 30 |
| Systèmes embarqués | EMB | EMB-A et EMB-B | 30 |
| Énergie | ENER | ENER-A et ENER-B | 30 |

Les enseignements scientifiques dépendent de la filière et du semestre. Les programmes créés servent à la démonstration et ne prétendent pas reproduire les programmes officiels.

## Connexion au portail

La page de connexion demande une adresse e-mail et un mot de passe.

Pour tester chaque filière, utiliser les comptes suivants :

| Filière | Adresse e-mail à saisir | Mot de passe |
|---|---|---|
| Data Science et IA | etudiant0001@example.com | Demo2026! |
| Cybersécurité | etudiant0031@example.com | Demo2026! |
| Systèmes embarqués | etudiant0061@example.com | Demo2026! |
| Énergie | etudiant0091@example.com | Demo2026! |

Les comptes sont numérotés de `etudiant0001@example.com` à `etudiant0120@example.com`.

| Numéros des comptes | Filière |
|---|---|
| 0001 à 0030 | Data Science et IA |
| 0031 à 0060 | Cybersécurité |
| 0061 à 0090 | Systèmes embarqués |
| 0091 à 0120 | Énergie |

Tous utilisent le mot de passe de démonstration `Demo2026!`.

Ces comptes sont fictifs : aucune boîte mail réelle n’est nécessaire. Il ne faut pas utiliser ses identifiants personnels ESIEE.

Une fois connecté, l’étudiant retrouve les résultats liés à son inscription. Le menu portant son nom donne accès à ses informations de profil et à la déconnexion.

## Organisation des enseignements

### Deux semestres et une vue annuelle

Trois onglets permettent de choisir la période :

- **Semestre 1** ;
- **Semestre 2** ;
- **Année**, pour consulter les deux semestres ensemble.

Chaque filière possède quatre UE par semestre, soit huit sur l’année. Dans la vue annuelle, les préfixes S1 et S2 distinguent les UE des deux semestres.

### Répartition des UE

| UE | Nombre de matières par semestre | Coefficient de l’UE |
|---|---:|---:|
| Sciences et techniques — Fondamentaux | 3 | 10 |
| Sciences et techniques — Spécialité | 3 | 10 |
| Management et sciences humaines | 1 | 5 |
| Langues vivantes | 1 | 5 |

Chaque semestre comporte donc huit matières et un total de 30 coefficients d’UE.

La matière de management est « Gestion de projet » au S1 et « Management d’équipe » au S2. L’anglais est présent dans les deux semestres.

Chaque matière possède un coefficient de 1 dans son UE et comprend trois évaluations :

| Évaluation | Coefficient |
|---|---:|
| TP 1 | 1 |
| Projet | 2 |
| Examen final | 2 |

Pour chaque étudiant, cela représente 16 matières et 48 évaluations prévues sur l’année.

La base contient ainsi 5 760 entrées de résultats. Certaines correspondent à une note, d’autres à une absence ou à un résultat en attente.

## Consultation des résultats

Le tableau suit la hiérarchie suivante :

1. **UE** : regroupement de matières.
2. **Matière** : enseignement appartenant à l’UE.
3. **Évaluation** : TP, projet ou examen de la matière.

Un clic sur une UE affiche ses matières. Un clic sur une matière affiche ses évaluations.

Cette présentation permet de commencer par une vue d’ensemble puis d’ouvrir uniquement les éléments utiles.

Le tableau présente les résultats personnels, les coefficients et les moyennes de classe disponibles.

## Calcul des moyennes personnelles

Les calculs sont effectués à partir des coefficients, en conservant trois niveaux : évaluations, matières et UE.

### Moyenne d’une matière

Une évaluation entre dans le calcul uniquement si :

- elle est publiée ;
- son statut est `note` ;
- sa note est renseignée.

La formule utilisée est :

```text
Moyenne = somme des (notes × coefficients)
          / somme des coefficients retenus
```

Lorsque les trois notes sont disponibles :

```text
Moyenne de la matière = (TP + 2 × Projet + 2 × Examen) / 5
```

Si une évaluation est exclue, son coefficient est également retiré du dénominateur.

Par exemple, avec un TP à 12, un projet à 15 et un examen en attente :

```text
Moyenne provisoire = (12 × 1 + 15 × 2) / (1 + 2)
                   = 14/20
```

### Moyenne d’une UE

La moyenne d’une UE est la moyenne pondérée des moyennes disponibles de ses matières.

Dans le jeu de démonstration, les matières ont toutes un coefficient de 1 : les matières disposant d’une moyenne ont donc le même poids dans leur UE.

Une matière sans moyenne disponible est exclue du calcul et son coefficient n’est pas comptabilisé.

### Moyenne générale

La moyenne générale est calculée à partir des moyennes disponibles des UE, pondérées par leurs coefficients.

Elle correspond à la période sélectionnée : S1, S2 ou année.

La vue annuelle utilise directement les UE des deux semestres. Lorsque toutes les moyennes sont disponibles, les deux semestres ont le même poids puisque chacun totalise 30 coefficients.

## Notes manquantes, absences et résultats provisoires

Le prototype distingue les situations suivantes :

| Situation | Prise en compte dans la moyenne personnelle |
|---|---|
| Note publiée avec le statut `note` | Oui |
| Note publiée égale à 0 | Oui |
| Absence justifiée | Non |
| Absence injustifiée | Non |
| Résultat en attente | Non |
| Évaluation non publiée | Non |

L’exclusion des absences injustifiées correspond au fonctionnement actuel de notre code. Elle ne représente pas nécessairement une règle de scolarité de l’école.

Si aucune note utilisable n’existe, le calcul ne renvoie pas de moyenne : il ne remplace pas les résultats manquants par zéro.

Une matière est provisoire dès qu’au moins une évaluation ne possède pas de note utilisable. Cette indication se transmet à son UE, puis au bilan général.

## Moyennes de classe

Dans notre application, la « classe » correspond au groupe de l’étudiant connecté, soit 15 étudiants dans le jeu de démonstration.

Le calcul dépend du niveau affiché :

- **Évaluation** : moyenne simple des notes publiées et disponibles dans le groupe.
- **Matière** : moyenne simple des moyennes personnelles disponibles des étudiants du groupe.
- **UE** : moyenne simple des moyennes personnelles disponibles des étudiants du groupe pour cette UE.

Les valeurs manquantes sont exclues.

La moyenne de classe d’une matière ou d’une UE est donc calculée à partir des moyennes de chaque étudiant, et non en mélangeant directement toutes leurs notes.

Les moyennes de classe sont signalées comme provisoires lorsque les résultats nécessaires sont incomplets.

## Classement dans la filière

Le classement compare les 30 étudiants de la même filière sur la période sélectionnée.

Il utilise uniquement les évaluations :

- publiées ;
- possédant une note avec le statut `note` pour chaque étudiant de la filière.

Les étudiants sont ainsi comparés sur les mêmes évaluations, en conservant les coefficients des évaluations, des matières et des UE.

L’encadré indique le rang, l’effectif de la filière et une position exprimée sous la forme « Top … % ».

Le pourcentage est calculé ainsi :

```text
Top = 100 × rang / effectif
```

Il est arrondi à l’entier supérieur. Par exemple, un rang de 4 sur 30 donne « Top 14 % ».

Les moyennes identiques après arrondi à deux décimales partagent le même rang.

Le classement est provisoire lorsque toutes les évaluations prévues ne peuvent pas être utilisées. Si aucune évaluation commune n’est disponible, il est indiqué comme indisponible.

Le détail « Comprendre le classement » présente la base de comparaison et la moyenne utilisée.

Cette moyenne peut différer de la moyenne générale personnelle, car le classement ne retient que les évaluations communes à tous.

**Les deux comparaisons ont donc des périmètres différents :**

- moyenne de classe : groupe de 15 étudiants ;
- classement : filière de 30 étudiants.

## Recherche

La barre de recherche permet de retrouver une UE ou une matière dans la période affichée.

La recherche filtre le tableau sans modifier les moyennes générales de la période.

Effacer la recherche permet de retrouver le tableau complet.

## Choix de conception de l’interface

Nous avons organisé la page à partir de notre croquis et des informations que nous souhaitions rendre accessibles rapidement.

- **Moyenne et classement en haut** : obtenir une première lecture de sa situation.
- **Tableau détaillé en dessous** : comprendre les résultats par UE, matière et évaluation.
- **Éléments déroulants** : limiter la quantité d’informations affichées simultanément.
- **Onglets de période** : passer facilement d’un semestre à la vue annuelle.
- **Recherche** : retrouver directement un enseignement.
- **Couleurs accompagnées de notes chiffrées** : proposer des repères visuels tout en conservant la valeur exacte.
- **Mentions provisoires** : rendre visible le caractère incomplet des résultats.
- **Présentation adaptée à la largeur de l’écran** : encadrés empilés sur petit écran et défilement horizontal du tableau.

Le logo ESIEE Paris apparaît sur la page de connexion et sur la page des résultats pour conserver une présentation cohérente.

## Données de démonstration

Le script `seed_data.py` génère des identités fictives et des résultats variés.

Il prévoit cinq profils : régulier, plus à l’aise en projet, plus à l’aise en examen, en progression et en difficulté.

Les notes générées sont comprises entre 0 et 20, par pas de 0,5.

Le compte `etudiant0001@example.com` comprend volontairement plusieurs cas particuliers :

- une note de 0/20 ;
- une note de 20/20 ;
- une absence justifiée ;
- une absence injustifiée ;
- un résultat en attente.

Dans les quatre filières, l’examen final d’anglais du S2 est marqué comme non publié.

Ces situations permettent de vérifier que l’interface distingue une note de zéro d’un résultat absent ou indisponible.

Le générateur utilise une graine aléatoire fixe pour reproduire les mêmes données pédagogiques lors d’une nouvelle génération sur une base vide.

Si des filières sont déjà présentes dans la base, le script s’arrête sans modifier les données.

Lors de la création initiale, il produit également des exports CSV dans `data/exports/`. L’export des étudiants exclut les mots de passe hachés.

## Technologies utilisées

| Technologie | Rôle |
|---|---|
| Python et Flask | Application web et gestion des routes |
| SQLite | Stockage des données |
| HTML et Jinja | Structure et contenu des pages |
| CSS | Mise en forme et adaptation aux écrans |
| JavaScript | Recherche dans le tableau |
| uv | Gestion des dépendances et de l’environnement |
| Git et GitHub | Versionnement et partage du projet |

## Installation et lancement

Prérequis : Git et uv installés.

### 1. Récupérer le projet

```bash
git clone https://github.com/AnellaMnr/projet-ux-design.git
cd projet-ux-design
```

### 2. Installer les dépendances

```bash
uv sync
```

### 3. Générer les données fictives

```bash
uv run python seed_data.py
```

La base de données locale et les exports sont générés sur l’ordinateur. Ils ne sont pas inclus dans le dépôt Git.

### 4. Démarrer le serveur

```bash
uv run flask --app main run
```

Ouvrir ensuite http://127.0.0.1:5000 dans un navigateur et utiliser un compte de démonstration.

Pour arrêter le serveur, appuyer sur Ctrl + C dans le terminal.

## Organisation du dépôt

| Fichier ou dossier | Rôle |
|---|---|
| `main.py` | Routes de l’application et affichage des pages |
| `database.py` | Initialisation et connexion à la base |
| `calculs.py` | Moyennes personnelles et moyennes de groupe |
| `classement.py` | Classement dans la filière |
| `seed_data.py` | Génération des données et exports CSV |
| `templates/connexion.html` | Page de connexion |
| `templates/notes.html` | Page des résultats |
| `static/style.css` | Présentation de l’interface |
| `static/recherche.js` | Filtrage des UE et matières |
| `static/images/` | Logo utilisé dans l’interface |
| `pyproject.toml` et `uv.lock` | Configuration et dépendances du projet |

## Vérifications réalisées

Les parcours suivants ont été vérifiés manuellement :

- ouverture des UE, des matières et des évaluations ;
- recherche de Python puis retour au tableau complet ;
- passage du S1 au S2 et à la vue annuelle ;
- présence des huit UE dans la vue annuelle ;
- déconnexion puis connexion avec le compte Cybersécurité ;
- affichage des enseignements correspondant à cette filière ;
- disposition des encadrés de moyenne et de classement côte à côte sur ordinateur.

Ces vérifications fonctionnelles ne remplacent pas les tests utilisateurs. Ceux-ci permettront d’observer si les participants comprennent l’organisation et retrouvent facilement les informations demandées.

## Limites

Notre projet est un prototype pédagogique utilisant des comptes et des résultats fictifs.

Les calculs décrivent les règles implémentées dans notre application. Ils ne constituent pas une validation des règles officielles de scolarité d’ESIEE Paris.

Une utilisation réelle nécessiterait notamment une validation des règles de calcul et un travail complémentaire sur la sécurité et la gestion des comptes.