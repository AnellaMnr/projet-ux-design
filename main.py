import os
import secrets
from classement import calculer_classement

from flask import (
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash

from calculs import calculer_resultats
from database import get_connection


app = Flask(__name__)

app.config["SECRET_KEY"] = (
    os.environ.get("SECRET_KEY") or secrets.token_hex(32)
)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


@app.route("/connexion", methods=["GET", "POST"])
def connexion():
    erreur = None

    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)

    if request.method == "POST":
        token = request.form.get("csrf_token", "")

        if not secrets.compare_digest(
            token, session["csrf_token"]
        ):
            return "Formulaire expiré. Recharge la page.", 400

        email = request.form.get("email", "").strip().lower()
        mot_de_passe = request.form.get("mot_de_passe", "")

        connection = get_connection()

        try:
            etudiant = connection.execute(
                """
                SELECT *
                FROM etudiants
                WHERE email = ?
                """,
                (email,),
            ).fetchone()
        finally:
            connection.close()

        if etudiant and check_password_hash(
            etudiant["mot_de_passe_hash"],
            mot_de_passe,
        ):
            session.clear()
            session["etudiant_id"] = etudiant["id"]
            session["csrf_token"] = secrets.token_hex(32)

            return redirect(url_for("accueil"))

        erreur = "Adresse e-mail ou mot de passe incorrect."

    return render_template(
        "connexion.html",
        erreur=erreur,
    )


@app.route("/")
def accueil():
    if "etudiant_id" not in session:
        return redirect(url_for("connexion"))

    semestre = request.args.get(
        "semestre",
        default=1,
        type=int,
    )

    # 0 représente la vue annuelle.
    if semestre not in (0, 1, 2):
        semestre = 1

    connection = get_connection()

    try:
        etudiant = connection.execute(
            """
            SELECT
                e.numero,
                e.prenom,
                e.nom,
                e.email,
                e.statut,
                i.id AS inscription_id,
                g.nom AS groupe,
                g.niveau,
                g.annee_scolaire,
                g.filiere_id,
                f.nom AS filiere
            FROM etudiants AS e
            JOIN inscriptions AS i
                ON i.etudiant_id = e.id
            JOIN groupes AS g
                ON g.id = i.groupe_id
            JOIN filieres AS f
                ON f.id = g.filiere_id
            WHERE e.id = ?
            ORDER BY
                g.annee_scolaire DESC,
                i.id DESC
            LIMIT 1
            """,
            (session["etudiant_id"],),
        ).fetchone()

        if etudiant is None:
            session.clear()
            return redirect(url_for("connexion"))

        lignes_ues = connection.execute(
            """
            SELECT
                u.id,
                u.nom,
                u.coefficient,
                s.numero AS semestre
            FROM ues AS u
            JOIN semestres AS s
                ON s.id = u.semestre_id
            WHERE u.filiere_id = ?
              AND (? = 0 OR s.numero = ?)
              AND s.annee_scolaire = ?
            ORDER BY s.numero, u.id
            """,
            (
                etudiant["filiere_id"],
                semestre,
                semestre,
                etudiant["annee_scolaire"],
            ),
        ).fetchall()

        ues = []

        for ligne_ue in lignes_ues:
            ue = dict(ligne_ue)
            ue["matieres"] = []

            lignes_matieres = connection.execute(
                """
                SELECT
                    id,
                    nom,
                    coefficient
                FROM matieres
                WHERE ue_id = ?
                ORDER BY id
                """,
                (ue["id"],),
            ).fetchall()

            for ligne_matiere in lignes_matieres:
                matiere = dict(ligne_matiere)

                matiere["evaluations"] = connection.execute(
                    """
                    SELECT
                        ev.nom,
                        ev.coefficient,
                        ev.date_evaluation,
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
                    ORDER BY
                        ev.date_evaluation,
                        ev.id
                    """,
                    (
                        etudiant["inscription_id"],
                        matiere["id"],
                    ),
                ).fetchall()

                ue["matieres"].append(matiere)

            ues.append(ue)

    finally:
        connection.close()

    bilan = calculer_resultats(
        ues,
        etudiant["inscription_id"],
    )

    classement = calculer_classement(etudiant, semestre)

    return render_template(
        "notes.html",
        etudiant=etudiant,
        ues=ues,
        semestre=semestre,
        bilan=bilan,
        classement=classement,
    )


@app.route("/deconnexion", methods=["POST"])
def deconnexion():
    token = request.form.get("csrf_token", "")
    token_attendu = session.get("csrf_token", "")

    if not token_attendu or not secrets.compare_digest(
        token, token_attendu
    ):
        return "Formulaire expiré. Recharge la page.", 400

    session.clear()

    return redirect(url_for("connexion"))


if __name__ == "__main__":
    app.run(debug=True)