const champRecherche = document.querySelector("#recherche-notes");
const retourRecherche = document.querySelector("#retour-recherche");
const listeSuggestions = document.querySelector("#suggestions-recherche");
const filtreStatut = document.querySelector("#filtre-statut");
const tableau = document.querySelector("#liste-resultats");
const entete = tableau.querySelector(".entete-notes");
const blocsUE = [...document.querySelectorAll(".bloc-ue")];
const blocsMatieres = [...document.querySelectorAll(".bloc-matiere")];
const blocs = [...blocsUE, ...blocsMatieres];
const zoneRecherche = document.querySelector(".recherche");

let etatAvantFiltre = null;
let cibleCourante = null;

function normaliser(texte) {
    return texte.normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase()
        .trim();
}

function fermerSuggestions() {
    listeSuggestions.hidden = true;
    listeSuggestions.replaceChildren();
}

function effacerSurbrillance() {
    cibleCourante?.classList.remove("cible-recherche");
    cibleCourante = null;
}

function mesurerTitres() {
    tableau.style.setProperty(
        "--hauteur-entete",
        `${entete.getBoundingClientRect().height}px`
    );

    blocsUE.forEach((ue) => {
        const titre = ue.querySelector(":scope > summary");
        ue.style.setProperty(
            "--hauteur-ue",
            `${titre.getBoundingClientRect().height}px`
        );
    });
}

// Associe les couleurs aux catégories réelles des UE.
blocsUE.forEach((ue) => {
    const nom = normaliser(ue.dataset.nom || "");

    ue.dataset.categorie = nom.includes("fondamentaux")
        ? "fondamentaux"
        : nom.includes("specialite")
        ? "specialite"
        : nom.includes("management")
        ? "management"
        : "langues";
});

function appliquerFiltre() {
    const statut = filtreStatut.value;

    if (statut !== "tout" && etatAvantFiltre === null) {
        etatAvantFiltre = new Map(
            blocs.map((bloc) => [bloc, bloc.open])
        );
    }

    let nombre = 0;

    blocsUE.forEach((ue) => {
        let matieresVisibles = 0;

        ue.querySelectorAll(".bloc-matiere").forEach((matiere) => {
            let evaluationsVisibles = 0;

            matiere.querySelectorAll(".ligne-evaluation").forEach(
                (evaluation) => {
                    const visible = statut === "tout"
                        || evaluation.dataset.statut === statut;

                    evaluation.hidden = !visible;

                    if (visible) {
                        evaluationsVisibles += 1;
                        nombre += 1;
                    }
                }
            );

            matiere.hidden = (
                statut !== "tout" && evaluationsVisibles === 0
            );

            if (!matiere.hidden) {
                matieresVisibles += 1;

                if (statut !== "tout") {
                    matiere.open = true;
                }
            }
        });

        ue.hidden = statut !== "tout" && matieresVisibles === 0;

        if (!ue.hidden && statut !== "tout") {
            ue.open = true;
        }
    });

    if (statut === "tout" && etatAvantFiltre !== null) {
        etatAvantFiltre.forEach((ouvert, bloc) => {
            bloc.open = ouvert;
        });
        etatAvantFiltre = null;
    }

    retourRecherche.textContent = statut === "tout"
        ? ""
        : `${nombre} évaluation(s) affichée(s). Les moyennes restent inchangées.`;

    requestAnimationFrame(mesurerTitres);
}

function allerAuResultat(cible) {
    if (!cible) return;

    // Une recherche donne accès au résultat sans masquer les autres.
    filtreStatut.value = "tout";
    appliquerFiltre();
    fermerSuggestions();
    effacerSurbrillance();

    let parent = cible.parentElement;

    while (parent && parent !== tableau) {
        if (parent.matches("details")) parent.open = true;
        parent = parent.parentElement;
    }

    if (cible.matches("details")) cible.open = true;

    cibleCourante = cible;
    cible.classList.add("cible-recherche");

    requestAnimationFrame(() => {
        mesurerTitres();

        const titre = cible.matches("details")
            ? cible.querySelector(":scope > summary")
            : cible;

        if (!titre.matches("summary")) {
            titre.setAttribute("tabindex", "-1");
        }

        titre.focus({ preventScroll: true });

        const ue = cible.matches(".bloc-ue")
            ? cible
            : cible.closest(".bloc-ue");

        const matiere = cible.closest(".bloc-matiere");

        let espace = entete.getBoundingClientRect().height;

        if (cible !== ue && ue) {
            espace += ue.querySelector(":scope > summary")
                .getBoundingClientRect().height;
        }

        if (cible.matches(".ligne-evaluation") && matiere) {
            espace += matiere.querySelector(":scope > summary")
                .getBoundingClientRect().height;
        }

        // Déplace d'abord le tableau, puis la page.
        const position = titre.getBoundingClientRect().top
            - tableau.getBoundingClientRect().top
            + tableau.scrollTop
            - tableau.clientTop
            - espace
            - 8;

        tableau.scrollTo({
            top: Math.max(0, position),
            behavior: "auto"
        });

        tableau.scrollIntoView({
            block: "start",
            behavior: window.matchMedia(
                "(prefers-reduced-motion: reduce)"
            ).matches ? "auto" : "smooth"
        });

        retourRecherche.textContent =
            `${cible.dataset.nom || "Évaluation"} sélectionné(e). `
            + "Les autres enseignements restent accessibles.";
    });
}

function afficherSuggestions() {
    const saisie = normaliser(champRecherche.value);
    fermerSuggestions();

    if (!saisie) {
        retourRecherche.textContent = "";
        return;
    }

    const correspondances = blocs.filter((bloc) =>
        normaliser(bloc.dataset.nom || "").includes(saisie)
    ).sort((a, b) =>
        a.dataset.nom.localeCompare(b.dataset.nom, "fr")
        || Number(a.dataset.semestre) - Number(b.dataset.semestre)
    );

    correspondances.forEach((bloc) => {
        const ligne = document.createElement("li");
        const bouton = document.createElement("button");

        bouton.type = "button";
        bouton.textContent = `${bloc.dataset.nom} · S${bloc.dataset.semestre}`
            + (bloc.matches(".bloc-ue") ? " · UE" : " · Matière");

        bouton.addEventListener("click", () => {
            champRecherche.value = bloc.dataset.nom;
            allerAuResultat(bloc);
        });

        ligne.append(bouton);
        listeSuggestions.append(ligne);
    });

    listeSuggestions.hidden = correspondances.length === 0;

    retourRecherche.textContent = correspondances.length
        ? `${correspondances.length} suggestion(s). Choisis un résultat pour y accéder.`
        : "Aucune UE ni matière trouvée pour cette période.";
}

champRecherche.addEventListener("input", () => {
    effacerSurbrillance();
    afficherSuggestions();
});

champRecherche.addEventListener("focus", afficherSuggestions);

champRecherche.addEventListener("keydown", (event) => {
    if (event.key === "ArrowDown" && !listeSuggestions.hidden) {
        event.preventDefault();
        listeSuggestions.querySelector("button")?.focus();
    }

    if (event.key === "Enter" && !listeSuggestions.hidden) {
        event.preventDefault();
        listeSuggestions.querySelector("button")?.click();
    }
});

listeSuggestions.addEventListener("keydown", (event) => {
    const boutons = [...listeSuggestions.querySelectorAll("button")];
    const index = boutons.indexOf(document.activeElement);

    if (!boutons.length) return;

    if (event.key === "ArrowDown") {
        event.preventDefault();
        boutons[(index + 1) % boutons.length].focus();
    }

    if (event.key === "ArrowUp") {
        event.preventDefault();
        if (index <= 0) champRecherche.focus();
        else boutons[index - 1].focus();
    }
});

zoneRecherche.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        event.preventDefault();
        champRecherche.focus();
        fermerSuggestions();
    }
});

zoneRecherche.addEventListener("focusout", (event) => {
    if (!zoneRecherche.contains(event.relatedTarget)) {
        fermerSuggestions();
    }
});

document.addEventListener("click", (event) => {
    if (!zoneRecherche.contains(event.target)) fermerSuggestions();
});

filtreStatut.addEventListener("change", () => {
    fermerSuggestions();
    effacerSurbrillance();
    appliquerFiltre();
});

document.querySelector("#tout-ouvrir").addEventListener("click", () => {
    blocs.forEach((bloc) => {
        if (!bloc.hidden) bloc.open = true;
    });
    requestAnimationFrame(mesurerTitres);
});

document.querySelector("#tout-fermer").addEventListener("click", () => {
    blocs.forEach((bloc) => { bloc.open = false; });
});

document.querySelector("#reinitialiser-filtres").addEventListener(
    "click",
    () => {
        champRecherche.value = "";
        filtreStatut.value = "tout";
        effacerSurbrillance();
        fermerSuggestions();
        appliquerFiltre();
        champRecherche.focus();
    }
);

document.querySelectorAll(".carte-note[data-cible]").forEach((lien) => {
    lien.addEventListener("click", (event) => {
        const cible = document.getElementById(lien.dataset.cible);
        if (!cible) return;
        event.preventDefault();
        allerAuResultat(cible);
    });
});

blocs.forEach((bloc) => {
    bloc.addEventListener("toggle", () => {
        requestAnimationFrame(mesurerTitres);
    });
});

window.addEventListener("resize", mesurerTitres);

if ("ResizeObserver" in window) {
    const observateur = new ResizeObserver(mesurerTitres);
    observateur.observe(entete);
    blocsUE.forEach((ue) => {
        observateur.observe(ue.querySelector(":scope > summary"));
    });
}

mesurerTitres();
