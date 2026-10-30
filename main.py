
import os
import secrets
import time
from datetime import date

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash

from archives import generer_archives
from calculs import ajouter_objectifs, calculer_resultats
from classement import calculer_classement
from database import get_connection, init_database


app = Flask(__name__)

app.config["SECRET_KEY"] = (
    os.environ.get("SECRET_KEY") or secrets.token_hex(32)
)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Durée d'inactivité avant expiration de la session (en minutes).
# Pour la démo : SESSION_MINUTES=1 uv run flask --app main run
DUREE_SESSION = int(os.environ.get("SESSION_MINUTES", "30"))

# Crée les tables manquantes (par exemple « signalements ») sans
# toucher aux données existantes.
init_database()

PAGES_PROTEGEES = {"accueil", "archives", "signaler"}


def etudiants_presents():
    connection = get_connection()

    try:
        return connection.execute(
            "SELECT COUNT(*) FROM etudiants"
        ).fetchone()[0] > 0
    finally:
        connection.close()


def adresse_sure(adresse):
    """N'accepte que les adresses internes au portail."""
    return bool(adresse) and adresse.startswith("/") and not adresse.startswith("//")


@app.before_request
def verifier_session():
    """Expire la session après une période d'inactivité."""
    if request.endpoint not in PAGES_PROTEGEES:
        return None

    if "etudiant_id" not in session:
        if request.endpoint == "signaler":
            return jsonify(erreur="session_expiree"), 401

        return redirect(url_for("connexion"))

    maintenant = time.time()
    derniere = session.get("derniere_activite", maintenant)

    if maintenant - derniere > DUREE_SESSION * 60:
        session.clear()

        if request.endpoint == "signaler":
            return jsonify(erreur="session_expiree"), 401

        return redirect(url_for(
            "connexion",
            expiree=1,
            suivant=request.full_path.rstrip("?"),
        ))

    session["derniere_activite"] = maintenant
    return None


@app.route("/connexion", methods=["GET", "POST"])
def connexion():
    erreur = None
    information = None
    email = ""
    suivant = request.values.get("suivant", "")

    if request.args.get("expiree"):
        information = (
            f"Ta session a expiré après {DUREE_SESSION} min "
            "d'inactivité, pour protéger tes notes. "
            "Reconnecte-toi pour reprendre où tu en étais."
        )
    elif request.args.get("deconnecte"):
        information = "Tu es déconnecté. À bientôt !"

    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)

    if request.method == "POST":
        token = request.form.get("csrf_token", "")
        email = request.form.get("email", "").strip().lower()
        mot_de_passe = request.form.get("mot_de_passe", "")

        if not secrets.compare_digest(
            token,
            session["csrf_token"],
        ):
            # La page était restée ouverte trop longtemps.
            session["csrf_token"] = secrets.token_hex(32)

            return render_template(
                "connexion.html",
                erreur=(
                    "La page était restée ouverte trop longtemps. "
                    "Saisis à nouveau ton mot de passe."
                ),
                email=email,
                suivant=suivant,
            )

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
            session["derniere_activite"] = time.time()

            if adresse_sure(suivant):
                return redirect(suivant)

            return redirect(url_for("accueil"))

        if not etudiants_presents():
            erreur = (
                "Aucun compte n'existe encore. Dans le terminal, lance "
                "« uv run python seed_data.py », puis réessaie."
            )
        else:
            erreur = (
                "E-mail ou mot de passe incorrect. Vérifie l'adresse "
                "et les majuscules du mot de passe."
            )

    return render_template(
        "connexion.html",
        erreur=erreur,
        information=information,
        email=email,
        suivant=suivant,
    )


@app.route("/")
def accueil():
    semestre = request.args.get(
        "semestre",
        default=1,
        type=int,
    )

    # 0 correspond à la vue annuelle.
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

                lignes_evaluations = connection.execute(
                    """
                    SELECT
                        ev.id,
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

                matiere["evaluations"] = [
                    dict(evaluation)
                    for evaluation in lignes_evaluations
                ]

                ue["matieres"].append(matiere)

            ues.append(ue)

    finally:
        connection.close()

    # Calcule les moyennes personnelles et celles du groupe.
    bilan = calculer_resultats(
        ues,
        etudiant["inscription_id"],
    )

    # Note nécessaire pour avoir la moyenne dans chaque matière.
    ajouter_objectifs(ues)

    signalements = signalements_envoyes(etudiant["inscription_id"])

    # Calcule le classement dans la filière.
    classement = calculer_classement(
        etudiant,
        semestre,
    )

    # Compte les différents états des évaluations.
    suivi = {
        "total": 0,
        "notees": 0,
        "absences": 0,
        "non_publiees": 0,
    }

    dernieres_evaluations = []

    for ue in ues:
        moyenne_ue = ue["moyenne"]
        moyenne_groupe_ue = ue["moyenne_classe"]

        ue["ecart_groupe"] = (
            moyenne_ue - moyenne_groupe_ue
            if moyenne_ue is not None
            and moyenne_groupe_ue is not None
            else None
        )

        for matiere in ue["matieres"]:
            moyenne_matiere = matiere["moyenne"]
            moyenne_groupe_matiere = matiere["moyenne_classe"]

            matiere["ecart_groupe"] = (
                moyenne_matiere - moyenne_groupe_matiere
                if moyenne_matiere is not None
                and moyenne_groupe_matiere is not None
                else None
            )

            for evaluation in matiere["evaluations"]:
                suivi["total"] += 1

                if not evaluation["publiee"]:
                    suivi["non_publiees"] += 1

                elif (
                    evaluation["statut"] == "note"
                    and evaluation["note"] is not None
                ):
                    suivi["notees"] += 1

                    dernieres_evaluations.append({
                        "id": evaluation["id"],
                        "matiere": matiere["nom"],
                        "matiere_id": matiere["id"],
                        "ue_id": ue["id"],
                        "semestre": ue["semestre"],
                        "evaluation": evaluation["nom"],
                        "note": evaluation["note"],
                        "date": evaluation["date_evaluation"],
                    })

                elif evaluation["statut"] in (
                    "absence_justifiee",
                    "absence_injustifiee",
                ):
                    suivi["absences"] += 1

                else:
                    # Résultat manquant : traité comme une note à venir.
                    suivi["non_publiees"] += 1

    # Résultats définitifs : notes et absences (pas les notes à venir).
    suivi["termines"] = suivi["notees"] + suivi["absences"]

    # La date disponible est celle de l'évaluation,
    # pas celle de la publication de sa note.
    dernieres_evaluations.sort(
        key=lambda evaluation: (
            evaluation["date"] or "",
            evaluation["id"],
        ),
        reverse=True,
    )

    dernieres_evaluations = dernieres_evaluations[:3]

    return render_template(
        "notes.html",
        etudiant=etudiant,
        ues=ues,
        semestre=semestre,
        bilan=bilan,
        classement=classement,
        suivi=suivi,
        dernieres_evaluations=dernieres_evaluations,
        signalements=signalements,
    )


@app.route("/archives")
def archives():
    connection = get_connection()

    try:
        etudiant = connection.execute(
            """
            SELECT
                e.numero,
                e.prenom,
                e.nom,
                e.statut,
                g.nom AS groupe,
                g.annee_scolaire,
                f.code AS code_filiere,
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
    finally:
        connection.close()

    if etudiant is None:
        session.clear()
        return redirect(url_for("connexion"))

    parcours, annees = generer_archives(
        etudiant["numero"],
        etudiant["statut"],
        etudiant["annee_scolaire"],
        etudiant["code_filiere"],
    )

    return render_template(
        "archives.html",
        etudiant=etudiant,
        parcours=parcours,
        annees=annees,
    )


def signalements_envoyes(inscription_id):
    """Évaluations déjà signalées : {evaluation_id: date affichable}."""
    connection = get_connection()

    try:
        lignes = connection.execute(
            """
            SELECT evaluation_id, cree_le
            FROM signalements
            WHERE inscription_id = ?
            """,
            (inscription_id,),
        ).fetchall()
    finally:
        connection.close()

    return {
        ligne["evaluation_id"]: date.fromisoformat(
            ligne["cree_le"]
        ).strftime("%d/%m")
        for ligne in lignes
    }


@app.route("/signalements", methods=["POST"])
def signaler():
    """Enregistre une erreur de note signalée par l'étudiant."""
    if not secrets.compare_digest(
        request.headers.get("X-CSRF-Token", ""),
        session.get("csrf_token", ""),
    ):
        return jsonify(erreur="formulaire_expire"), 403

    donnees = request.get_json(silent=True) or {}
    message = str(donnees.get("message", "")).strip()[:500]
    note_attendue = donnees.get("note_attendue")

    if note_attendue in ("", None):
        note_attendue = None
    else:
        try:
            note_attendue = float(str(note_attendue).replace(",", "."))
        except ValueError:
            return jsonify(erreur="note_invalide"), 400

        if not 0 <= note_attendue <= 20:
            return jsonify(erreur="note_invalide"), 400

    if note_attendue is None and not message:
        return jsonify(erreur="vide"), 400

    connection = get_connection()

    try:
        # L'évaluation doit appartenir au parcours de l'étudiant
        # et être publiée.
        ligne = connection.execute(
            """
            SELECT i.id AS inscription_id
            FROM evaluations AS ev
            JOIN matieres AS m ON m.id = ev.matiere_id
            JOIN ues AS u ON u.id = m.ue_id
            JOIN groupes AS g ON g.filiere_id = u.filiere_id
            JOIN inscriptions AS i ON i.groupe_id = g.id
            WHERE ev.id = ?
                AND ev.publiee = 1
                AND i.etudiant_id = ?
            ORDER BY i.id DESC
            LIMIT 1
            """,
            (donnees.get("evaluation_id"), session["etudiant_id"]),
        ).fetchone()

        if ligne is None:
            return jsonify(erreur="evaluation_inconnue"), 404

        aujourd_hui = date.today().isoformat()

        with connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO signalements (
                    inscription_id, evaluation_id,
                    note_attendue, message, cree_le
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    ligne["inscription_id"],
                    donnees.get("evaluation_id"),
                    note_attendue,
                    message,
                    aujourd_hui,
                ),
            )
    finally:
        connection.close()

    return jsonify(
        ok=True,
        date=date.fromisoformat(aujourd_hui).strftime("%d/%m"),
    )


@app.errorhandler(404)
def page_introuvable(erreur):
    return render_template(
        "erreur.html",
        titre="Page introuvable",
        texte="Cette adresse ne mène à aucune page du portail.",
    ), 404


@app.errorhandler(500)
def erreur_serveur(erreur):
    return render_template(
        "erreur.html",
        titre="Un problème est survenu",
        texte=(
            "Le portail n'a pas pu afficher cette page. "
            "Réessaie dans un instant."
        ),
    ), 500


@app.route("/deconnexion", methods=["POST"])
def deconnexion():
    # Une déconnexion ne présente pas de risque : on l'accepte toujours,
    # même si la page était restée ouverte longtemps.
    session.clear()

    return redirect(url_for("connexion", deconnecte=1))


if __name__ == "__main__":
    app.run(debug=True)