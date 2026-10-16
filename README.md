# Portail étudiant — Projet UX Design

Prototype réalisé en groupe de quatre dans le cadre du cours d’UX Design à ESIEE Paris, en quatrième année du cycle ingénieur.

## Notre équipe

- Anella Manari
- Lilou Parrin
- Antoine Navarro
- Fregice Betsaka Tekoutche

## Présentation du projet

Nous avons conçu un portail permettant à un étudiant de consulter ses résultats scolaires, de retrouver une évaluation et de suivre ses moyennes.

Le projet est parti d’un croquis. Nous avons ensuite construit une interface fonctionnelle, puis fait évoluer sa présentation et sa navigation.

La page présente d’abord la moyenne générale et le classement, puis les dernières évaluations notées et le tableau détaillé des résultats.

Ce prototype utilise des données fictives. Il n’est pas connecté au système de scolarité d’ESIEE Paris et ne constitue pas un portail officiel de l’école.

## Population représentée

Le jeu de démonstration représente l’année scolaire 2026-2027.

Il comprend 120 étudiants de niveau E4, répartis dans quatre filières. Chaque filière possède deux groupes de 15 étudiants.

| Filière | Code | Groupes | Effectif |
|---|---|---|---:|
| Data Science et Intelligence Artificielle | DSIA | DSIA-A et DSIA-B | 30 |
| Cybersécurité | CYBER | CYBER-A et CYBER-B | 30 |
| Systèmes embarqués | EMB | EMB-A et EMB-B | 30 |
| Énergie | ENER | ENER-A et ENER-B | 30 |

La promotion fictive compte donc huit groupes. Les étudiants sont en formation initiale ou en apprentissage.

Les programmes servent à la démonstration et ne reproduisent pas nécessairement les programmes officiels de l’école.

## Comptes de démonstration

La connexion demande une adresse e-mail et un mot de passe.

Pour découvrir chaque filière :

| Filière | Adresse e-mail | Mot de passe |
|---|---|---|
| Data Science et IA | etudiant0001@example.com | Demo2026! |
| Cybersécurité | etudiant0031@example.com | Demo2026! |
| Systèmes embarqués | etudiant0061@example.com | Demo2026! |
| Énergie | etudiant0091@example.com | Demo2026! |

Les comptes sont numérotés de `etudiant0001@example.com` à `etudiant0120@example.com`.

| Numéros | Filière |
|---|---|
| 0001 à 0030 | Data Science et IA |
| 0031 à 0060 | Cybersécurité |
| 0061 à 0090 | Systèmes embarqués |
| 0091 à 0120 | Énergie |

Tous utilisent le mot de passe `Demo2026!`.

Ces adresses sont fictives : aucune boîte mail réelle n’est nécessaire. Il ne faut pas saisir ses identifiants personnels ESIEE.

Après la connexion, les résultats affichés correspondent à l’inscription de l’étudiant. Le menu portant son nom présente ses informations et permet de se déconnecter.

## Organisation des enseignements

Trois onglets permettent de consulter :

- le semestre 1 ;
- le semestre 2 ;
- l’année complète.

Chaque filière comprend quatre UE par semestre, soit huit UE sur l’année.

| UE | Matières par semestre | Coefficient de l’UE |
|---|---:|---:|
| Sciences et techniques — Fondamentaux | 3 | 10 |
| Sciences et techniques — Spécialité | 3 | 10 |
| Management et sciences humaines | 1 | 5 |
| Langues vivantes | 1 | 5 |

Chaque semestre comporte huit matières et totalise 30 coefficients d’UE.

Chaque matière a un coefficient de 1 dans son UE. Les enseignements scientifiques varient selon la filière et le semestre.

La matière de management est « Gestion de projet » au S1 et « Management d’équipe » au S2. L’anglais est présent aux deux semestres.

Dans la vue annuelle, les mentions S1 et S2 distinguent les enseignements.

## Des évaluations adaptées aux matières

Les matières ne suivent pas toutes le même modèle d’évaluation. Leur nombre, leur nature et leurs coefficients varient.

Exemples définis dans le générateur :

| Matière | Évaluations et coefficients |
|---|---|
| Python | TP 1 : 1 ; TP 2 : 1 ; projet : 3 ; contrôle pratique : 2 |
| Algorithmique | QCM 1 : 1 ; QCM 2 : 1 ; contrôle final : 3 |
| Bases de données | TP SQL : 1 ; projet de modélisation : 2 |
| Statistiques | Contrôle continu : 1 ; examen final : 2 |
| Machine Learning | Deux TP : 1 chacun ; projet de prédiction : 3 |
| Data Engineering | TP : 1 ; projet ETL : 3 ; soutenance : 1 |
| Anglais | Compréhension orale : 1 ; présentation orale : 1 ; examen final : 2 |
| Gestion de projet | Dossier de groupe : 2 ; soutenance : 1 |

D’autres matières utilisent notamment des contrôles pratiques, des études de cas, des rapports ou des soutenances.

Ces formats sont fictifs et servent à représenter plusieurs situations pédagogiques.

Le nombre d’évaluations par étudiant dépend de sa filière. Le générateur affiche le nombre total de résultats créés à la fin de son exécution.

## Consultation des résultats

Le tableau suit trois niveaux :

1. **UE** : regroupement de matières.
2. **Matière** : enseignement appartenant à l’UE.
3. **Évaluation** : TP, QCM, projet, contrôle ou autre épreuve.

Un clic sur une UE affiche ses matières. Un clic sur une matière affiche ses évaluations.

Le tableau présente les notes personnelles, les coefficients et les moyennes du groupe.

Les boutons « Tout ouvrir » et « Tout fermer » permettent de gérer les détails affichés.

## Recherche et accès direct

Les suggestions apparaissent dès la première lettre saisie.

La recherche trouve les noms contenant la saisie, au début, au milieu ou à la fin, sans tenir compte des majuscules ni des accents.

Les suggestions précisent le semestre et le type de résultat : UE ou matière.

Sélectionner une suggestion :

- ouvre l’enseignement concerné ;
- fait défiler la page et le tableau jusqu’au résultat ;
- met la sélection en évidence ;
- conserve les autres enseignements accessibles.

La recherche sert donc à naviguer dans le tableau sans masquer les autres matières.

Les suggestions sont aussi accessibles au clavier avec les flèches, Entrée et Échap.

## Filtres du tableau

Un menu permet d’afficher :

- toutes les évaluations ;
- les notes disponibles ;
- les résultats en attente ;
- les absences ;
- les évaluations non publiées.

Les filtres modifient uniquement l’affichage. Les moyennes restent celles de la période entière.

Le bouton « Réinitialiser » efface la recherche et remet le filtre sur toutes les évaluations.

Choisir une suggestion de recherche rétablit également l’affichage de tous les statuts pour rendre la sélection accessible.

## Synthèse et dernières notes

L’encadré de moyenne présente :

- la moyenne générale et son indication `/20` sur la même ligne ;
- la période sélectionnée ;
- une mention provisoire si nécessaire ;
- le nombre d’évaluations notées sur le total prévu ;
- une barre représentant cette proportion.

Cette barre indique la part des évaluations disponibles, sans pondération par leurs coefficients.

Les trois dernières évaluations notées de la période apparaissent sous forme de cartes. Elles sont triées par date d’évaluation : aucune date de publication des notes n’est enregistrée.

Un clic sur une carte ouvre directement l’évaluation correspondante dans le tableau.

## Repères visuels

Les notes et les moyennes utilisent deux couleurs :

| Valeur avant arrondi d’affichage | Couleur |
|---|---|
| Inférieure à 10/20 | Rouge |
| Supérieure ou égale à 10/20 | Vert |

Les valeurs restent affichées sous forme numérique.

Les catégories d’UE possèdent leurs propres repères :

| Catégorie d’UE | Couleur |
|---|---|
| Fondamentaux | Bleu |
| Spécialité | Violet |
| Management et sciences humaines | Ocre |
| Langues vivantes | Vert d’eau |

Ces couleurs distinguent les catégories d’enseignement et ne représentent pas leur niveau de réussite.

Les notes du tableau sont légèrement agrandies et bénéficient d’un léger zoom au survol.

Pendant le défilement dans le tableau, l’en-tête des colonnes, le titre de l’UE ouverte et celui de la matière ouverte restent épinglés dans les limites de leur section.

## Calcul des moyennes personnelles

Une évaluation entre dans le calcul si elle est publiée, possède le statut `note` et contient une valeur.

```text
Moyenne d’une matière =
somme des (notes retenues × coefficients)
÷ somme des coefficients retenus
```

Chaque matière utilise ses propres coefficients d’évaluation.

Pour Python, lorsque toutes les notes sont disponibles :

```text
Moyenne =
(TP 1 + TP 2 + 3 × Projet + 2 × Contrôle pratique) / 7
```

Si une évaluation est exclue, son coefficient est également retiré du dénominateur.

La moyenne d’une UE est calculée à partir des moyennes disponibles de ses matières et de leurs coefficients.

La moyenne générale utilise ensuite les moyennes disponibles des UE, pondérées par leurs coefficients.

La vue annuelle réunit les UE des deux semestres. Lorsque tous les résultats sont disponibles, les deux semestres ont le même poids.

## Absences et résultats incomplets

| Situation | Prise en compte dans la moyenne personnelle |
|---|---|
| Note publiée avec le statut `note` | Oui |
| Note publiée égale à 0 | Oui |
| Absence justifiée | Non |
| Absence injustifiée | Non |
| Résultat en attente | Non |
| Évaluation non publiée | Non |

L’exclusion des absences injustifiées correspond au fonctionnement de notre prototype, sans prétendre reproduire les règles officielles de scolarité.

Si aucune note utilisable n’existe, aucune moyenne n’est calculée. Une donnée manquante n’est pas remplacée par zéro.

Une matière est provisoire lorsqu’une évaluation au moins ne dispose pas d’une note utilisable. Cette indication se transmet à l’UE et au bilan général.

## Moyennes du groupe

Les moyennes du groupe concernent les 15 étudiants du groupe de l’étudiant connecté.

- Pour une évaluation : moyenne simple des notes publiées et disponibles.
- Pour une matière : moyenne simple des moyennes personnelles disponibles.
- Pour une UE : moyenne simple des moyennes personnelles disponibles pour cette UE.

Les valeurs manquantes sont exclues.

Les moyennes du groupe sont signalées comme provisoires lorsque les résultats nécessaires sont incomplets.

## Classement

Le classement compare les 30 étudiants de la même filière sur la période sélectionnée.

Il retient uniquement les évaluations publiées possédant une note pour chacun de ces étudiants. Les coefficients des évaluations, des matières et des UE sont conservés.

L’interface affiche uniquement la position « Top … % » et, si nécessaire, une mention provisoire.

```text
Top = 100 × rang / effectif
```

Le pourcentage est arrondi à l’entier supérieur. Les moyennes identiques à deux décimales partagent le même rang.

Le classement est provisoire lorsque certaines évaluations prévues ne peuvent pas être utilisées. Si aucune évaluation commune n’existe, il est indisponible.

La moyenne utilisée pour classer peut différer de la moyenne générale personnelle, car seules les évaluations communes sont retenues.

Les deux comparaisons ont des périmètres différents :

- moyenne du groupe : 15 étudiants ;
- classement dans la filière : 30 étudiants.

## Données fictives

Le script `seed_data.py` génère les comptes, les enseignements, les évaluations et les résultats.

Il prévoit cinq profils : régulier, plus à l’aise en projet, plus à l’aise en examen, en progression et en difficulté.

Les notes sont comprises entre 0 et 20, par pas de 0,5.

Le compte `etudiant0001@example.com` contient volontairement :

- une note de 0/20 ;
- une note de 20/20 ;
- une absence justifiée ;
- une absence injustifiée ;
- un résultat en attente.

L’examen final d’anglais du S2 est non publié dans chaque filière.

Une graine aléatoire fixe permet de reproduire les mêmes données pédagogiques avec la même version du générateur sur une base vide.

Si des filières existent déjà dans la base, le script s’arrête sans modifier les données. Modifier le générateur ne met donc pas automatiquement à jour une base existante.

Lors de la création initiale, des exports CSV sont produits dans `data/exports/`. L’export des étudiants exclut les mots de passe hachés.

## Technologies utilisées

| Technologie | Rôle |
|---|---|
| Python et Flask | Application web et routes |
| SQLite | Base de données |
| HTML et Jinja | Pages et affichage des résultats |
| CSS | Présentation et adaptation aux écrans |
| JavaScript | Suggestions, navigation, filtres et commandes du tableau |
| uv | Environnement Python et dépendances |
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

### 3. Générer les données

```bash
uv run python seed_data.py
```

La base locale et les exports ne sont pas inclus dans le dépôt.

### 4. Démarrer l’application

```bash
uv run flask --app main run
```

Ouvrir http://127.0.0.1:5000 dans un navigateur, puis utiliser un compte de démonstration.

Pour arrêter le serveur, appuyer sur Ctrl + C dans le terminal.

## Organisation du dépôt

| Fichier ou dossier | Rôle |
|---|---|
| `main.py` | Routes, chargement des données et préparation des synthèses |
| `database.py` | Initialisation et connexion à la base |
| `calculs.py` | Moyennes personnelles et moyennes du groupe |
| `classement.py` | Classement dans la filière |
| `seed_data.py` | Génération des données et exports CSV |
| `templates/connexion.html` | Page de connexion |
| `templates/notes.html` | Page des résultats |
| `static/style.css` | Présentation des pages |
| `static/recherche.js` | Suggestions, navigation et filtres |
| `static/images/` | Logo |
| `pyproject.toml` et `uv.lock` | Configuration et dépendances |

Les éventuelles sauvegardes locales sont exclues du dépôt Git.

## Vérifications et tests utilisateurs

Des vérifications manuelles ont été réalisées sur l’ouverture des résultats, la navigation entre périodes, la connexion avec le compte Cybersécurité et l’affichage des enseignements correspondants.

Après les dernières modifications, les parcours à vérifier comprennent :

- sélectionner une suggestion et retrouver le résultat sans masquer le reste ;
- distinguer une matière du S1 et du S2 ;
- ouvrir une évaluation depuis une carte ;
- utiliser chaque filtre et réinitialiser l’affichage ;
- ouvrir et fermer tous les détails ;
- vérifier les notes rouges sous 10 et vertes dès 10 ;
- vérifier les titres épinglés pendant le défilement ;
- vérifier la présentation de la connexion et des résultats sur petit écran.

Ces vérifications fonctionnelles ne remplacent pas les tests utilisateurs. Ceux-ci permettront d’observer si les participants comprennent la page et retrouvent les informations demandées.

## Limites

Ce projet est un prototype pédagogique utilisant des données fictives.

Les programmes, formats d’évaluation et règles de calcul décrivent notre démonstration. Ils ne constituent pas une validation des règles officielles d’ESIEE Paris.

Une utilisation réelle demanderait notamment une validation des calculs, une gestion adaptée des comptes et un travail complémentaire sur la sécurité.