import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "data" / "portail.db"


def get_connection():
    """Ouvre une connexion à la base de données."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def init_database():
    """Crée les tables si elles n'existent pas encore."""
    connection = get_connection()

    try:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS filieres (
                id INTEGER PRIMARY KEY,
                code TEXT NOT NULL UNIQUE,
                nom TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS groupes (
                id INTEGER PRIMARY KEY,
                nom TEXT NOT NULL,
                filiere_id INTEGER NOT NULL,
                niveau TEXT NOT NULL,
                annee_scolaire TEXT NOT NULL,

                UNIQUE(nom, annee_scolaire),

                FOREIGN KEY (filiere_id)
                    REFERENCES filieres(id)
            );

            CREATE TABLE IF NOT EXISTS etudiants (
                id INTEGER PRIMARY KEY,
                numero TEXT NOT NULL UNIQUE,
                prenom TEXT NOT NULL,
                nom TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                mot_de_passe_hash TEXT NOT NULL,
                statut TEXT NOT NULL CHECK (
                    statut IN ('initial', 'apprentissage')
                )
            );

            CREATE TABLE IF NOT EXISTS inscriptions (
                id INTEGER PRIMARY KEY,
                etudiant_id INTEGER NOT NULL,
                groupe_id INTEGER NOT NULL,

                UNIQUE(etudiant_id, groupe_id),

                FOREIGN KEY (etudiant_id)
                    REFERENCES etudiants(id),

                FOREIGN KEY (groupe_id)
                    REFERENCES groupes(id)
            );

            CREATE TABLE IF NOT EXISTS semestres (
                id INTEGER PRIMARY KEY,
                numero INTEGER NOT NULL CHECK (
                    numero IN (1, 2)
                ),
                annee_scolaire TEXT NOT NULL,

                UNIQUE(numero, annee_scolaire)
            );

            CREATE TABLE IF NOT EXISTS ues (
                id INTEGER PRIMARY KEY,
                nom TEXT NOT NULL,
                filiere_id INTEGER NOT NULL,
                semestre_id INTEGER NOT NULL,
                coefficient REAL NOT NULL CHECK (
                    coefficient > 0
                ),

                FOREIGN KEY (filiere_id)
                    REFERENCES filieres(id),

                FOREIGN KEY (semestre_id)
                    REFERENCES semestres(id)
            );

            CREATE TABLE IF NOT EXISTS matieres (
                id INTEGER PRIMARY KEY,
                nom TEXT NOT NULL,
                ue_id INTEGER NOT NULL,
                coefficient REAL NOT NULL CHECK (
                    coefficient > 0
                ),

                FOREIGN KEY (ue_id)
                    REFERENCES ues(id)
            );

            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY,
                nom TEXT NOT NULL,
                type_evaluation TEXT NOT NULL,
                matiere_id INTEGER NOT NULL,
                date_evaluation TEXT NOT NULL,
                coefficient REAL NOT NULL CHECK (
                    coefficient > 0
                ),
                publiee INTEGER NOT NULL DEFAULT 0 CHECK (
                    publiee IN (0, 1)
                ),

                FOREIGN KEY (matiere_id)
                    REFERENCES matieres(id)
            );

            CREATE TABLE IF NOT EXISTS resultats (
                id INTEGER PRIMARY KEY,
                inscription_id INTEGER NOT NULL,
                evaluation_id INTEGER NOT NULL,
                note REAL,
                statut TEXT NOT NULL CHECK (
                    statut IN (
                        'note',
                        'absence_justifiee',
                        'absence_injustifiee',
                        'en_attente'
                    )
                ),

                UNIQUE(inscription_id, evaluation_id),

                CHECK (
                    (
                        statut = 'note'
                        AND note IS NOT NULL
                        AND note BETWEEN 0 AND 20
                    )
                    OR
                    (
                        statut != 'note'
                        AND note IS NULL
                    )
                ),

                FOREIGN KEY (inscription_id)
                    REFERENCES inscriptions(id),

                FOREIGN KEY (evaluation_id)
                    REFERENCES evaluations(id)
            );
        """)

        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    init_database()
    print("Base de données créée avec succès.")