// Signalement d'une erreur de note.
// États : formulaire → envoi en cours → succès, ou erreur avec une sortie.

const dialogue = document.querySelector("#dialogue-signalement");
const formulaire = document.querySelector("#form-signalement");
const champNote = document.querySelector("#note-attendue");
const champMessage = document.querySelector("#message-signalement");
const zoneErreur = document.querySelector("#erreur-signalement");
const boutonEnvoyer = document.querySelector("#envoyer-signalement");
const vueSucces = document.querySelector("#succes-signalement");
const texteSucces = document.querySelector("#texte-succes");
const jeton = document.querySelector('meta[name="csrf-token"]').content;

let boutonSource = null;

function cleBrouillon(id) {
    return `brouillon-signalement-${id}`;
}

// Le brouillon est gardé si l'envoi échoue ou si la session expire.
function lireBrouillon(id) {
    try {
        return JSON.parse(sessionStorage.getItem(cleBrouillon(id))) || {};
    } catch {
        return {};
    }
}

function ecrireBrouillon() {
    if (!boutonSource) return;

    try {
        sessionStorage.setItem(
            cleBrouillon(boutonSource.dataset.evaluation),
            JSON.stringify({
                note: champNote.value,
                message: champMessage.value,
            })
        );
    } catch {
        // Stockage indisponible : le formulaire reste rempli à l'écran.
    }
}

function effacerBrouillon(id) {
    try {
        sessionStorage.removeItem(cleBrouillon(id));
    } catch {
        // Rien à faire.
    }
}

function afficherErreur(html) {
    zoneErreur.innerHTML = html;
    zoneErreur.hidden = false;
}

function etatEnvoi(enCours) {
    boutonEnvoyer.disabled = enCours;
    boutonEnvoyer.classList.toggle("chargement", enCours);
    boutonEnvoyer.textContent = enCours
        ? "Envoi en cours…"
        : "Envoyer le signalement";
}

function ouvrir(bouton) {
    boutonSource = bouton;
    const brouillon = lireBrouillon(bouton.dataset.evaluation);

    document.querySelector("#signalement-matiere").textContent =
        bouton.dataset.matiere;
    document.querySelector("#signalement-evaluation").textContent =
        bouton.dataset.nom;
    document.querySelector("#signalement-note").textContent =
        bouton.dataset.note;

    champNote.value = brouillon.note || "";
    champMessage.value = brouillon.message || "";
    champNote.removeAttribute("aria-invalid");
    zoneErreur.hidden = true;
    formulaire.hidden = false;
    vueSucces.hidden = true;
    etatEnvoi(false);

    dialogue.showModal();
    champNote.focus();
}

function fermer() {
    dialogue.close();
}

function noteValide(texte) {
    if (!texte.trim()) return true;
    const valeur = Number(texte.replace(",", "."));
    return Number.isFinite(valeur) && valeur >= 0 && valeur <= 20;
}

async function envoyer(event) {
    event.preventDefault();
    zoneErreur.hidden = true;

    // Validation au moment de l'envoi, pas pendant la saisie.
    if (!noteValide(champNote.value)) {
        champNote.setAttribute("aria-invalid", "true");
        afficherErreur(
            "La note attendue doit être un nombre entre 0 et 20, "
            + "par exemple 14,5."
        );
        champNote.focus();
        return;
    }

    if (!champNote.value.trim() && !champMessage.value.trim()) {
        afficherErreur(
            "Indique la note que tu attendais ou décris le problème."
        );
        champMessage.focus();
        return;
    }

    champNote.removeAttribute("aria-invalid");
    ecrireBrouillon();
    etatEnvoi(true);

    let reponse;

    try {
        reponse = await fetch("/signalements", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRF-Token": jeton,
            },
            body: JSON.stringify({
                evaluation_id: Number(boutonSource.dataset.evaluation),
                note_attendue: champNote.value.trim(),
                message: champMessage.value.trim(),
            }),
        });
    } catch {
        etatEnvoi(false);
        boutonEnvoyer.textContent = "Réessayer";
        afficherErreur(
            "Le signalement n'a pas pu être envoyé : le portail ne répond "
            + "pas. Vérifie ta connexion internet puis réessaie. "
            + "Ton message est conservé."
        );
        return;
    }

    if (reponse.status === 401 || reponse.status === 403) {
        etatEnvoi(false);
        const retour = encodeURIComponent(
            window.location.pathname + window.location.search
        );
        afficherErreur(
            "Ta session a expiré. Ton message est conservé : "
            + `<a href="/connexion?expiree=1&amp;suivant=${retour}">`
            + "reconnecte-toi</a>, puis rouvre ce signalement."
        );
        return;
    }

    if (!reponse.ok) {
        etatEnvoi(false);
        boutonEnvoyer.textContent = "Réessayer";
        afficherErreur(
            "Le portail n'a pas pu enregistrer ton signalement. "
            + "Réessaie dans un instant. Ton message est conservé."
        );
        return;
    }

    const donnees = await reponse.json();
    effacerBrouillon(boutonSource.dataset.evaluation);

    // Nouvel état : la ligne indique que l'erreur a été signalée.
    const pastille = document.createElement("span");
    pastille.className = "pastille-signale";
    pastille.textContent = `Signalé le ${donnees.date}`;
    boutonSource.replaceWith(pastille);

    texteSucces.textContent =
        `La scolarité et l'enseignant de ${boutonSource.dataset.matiere} `
        + "ont reçu ta demande. Tu recevras une réponse par e-mail.";
    formulaire.hidden = true;
    vueSucces.hidden = false;
    document.querySelector("#fermer-signalement").focus();
}

document.querySelectorAll(".bouton-signaler").forEach((bouton) => {
    bouton.addEventListener("click", (event) => {
        // Le bouton est dans une ligne : on n'ouvre pas la matière.
        event.stopPropagation();
        ouvrir(bouton);
    });
});

champNote.addEventListener("input", ecrireBrouillon);
champMessage.addEventListener("input", ecrireBrouillon);
formulaire.addEventListener("submit", envoyer);
document.querySelector("#annuler-signalement").addEventListener("click", fermer);
document.querySelector("#fermer-signalement").addEventListener("click", fermer);

// Clic sur le fond assombri : on ferme sans perdre le brouillon.
dialogue.addEventListener("click", (event) => {
    if (event.target === dialogue) fermer();
});

dialogue.addEventListener("close", () => {
    boutonSource?.isConnected && boutonSource.focus();
});
