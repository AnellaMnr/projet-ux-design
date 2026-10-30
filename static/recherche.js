const champRecherche = document.querySelector("#recherche-notes");
const retourRecherche = document.querySelector("#retour-recherche");
const listeSuggestions = document.querySelector("#suggestions-recherche");
const filtreStatut = document.querySelector("#filtre-statut");
const tableau = document.querySelector("#liste-resultats");
const entete = tableau.querySelector(".entete-notes");
const blocsUE = [...document.querySelectorAll(".bloc-ue")];
const blocsMatieres = [...document.querySelectorAll(".bloc-matiere")];
const blocs = [...blocsUE, ...blocsMatieres];
const totalEvaluations = document.querySelectorAll(".ligne-evaluation").length;
const zoneRecherche = document.querySelector(".recherche");
const bandeau = document.querySelector(".bandeau");
const menuProfil = document.querySelector(".menu-profil");
const boutonEffacer = document.querySelector("#reinitialiser-filtres");

let etatAvantFiltre = null;
let cibleCourante = null;

function normaliser(texte) {
    return texte.normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase()
        .trim();
}

let fermetureEnCours = false;

function fermerSuggestions() {
    // Évite une double fermeture quand le bouton cliqué perd le focus.
    if (fermetureEnCours) return;
    fermetureEnCours = true;
    listeSuggestions.hidden = true;
    listeSuggestions.replaceChildren();
    fermetureEnCours = false;
}

function effacerSurbrillance() {
    cibleCourante?.classList.remove("cible-recherche");
    cibleCourante = null;
}

function mesurerTitres() {
    document.documentElement.style.setProperty(
        "--hauteur-bandeau",
        `${bandeau.getBoundingClientRect().height}px`
    );

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

    // Les anciens noms d'UE (Fondamentaux, Spécialité) restent reconnus.
    ue.dataset.categorie = nom.includes("approfondissement")
        || nom.includes("fondamentaux")
        ? "fondamentaux"
        : nom.includes("ouverture") || nom.includes("specialite")
        ? "specialite"
        : nom.includes("management")
        ? "management"
        : nom.includes("stage")
        ? "stage"
        : "langues";
});

function majBoutonEffacer() {
    boutonEffacer.hidden = filtreStatut.value === "tout"
        && !champRecherche.value.trim();
}

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

    const libelle = filtreStatut.selectedOptions[0].textContent.trim();

    // État vide : on dit pourquoi et comment en sortir.
    retourRecherche.textContent = statut === "tout"
        ? ""
        : nombre === 0
        ? `Aucune évaluation « ${libelle} » sur cette période. `
            + "Clique sur « Effacer » pour tout revoir."
        : `${nombre} évaluation${nombre > 1 ? "s" : ""} `
            + `affichée${nombre > 1 ? "s" : ""} sur ${totalEvaluations} · `
            + "Les moyennes restent calculées sur toutes tes notes.";

    // Avec un filtre actif, le message est mis en avant : on ne doit pas
    // croire que les moyennes portent sur les seules lignes affichées.
    retourRecherche.classList.toggle("retour-filtre", statut !== "tout");

    majBoutonEffacer();
    requestAnimationFrame(mesurerTitres);
}

function allerAuResultat(cible) {
    if (!cible) return;

    // Une matière seule dans son UE n'a pas de ligne propre : on vise l'UE.
    if (cible.matches(".matiere-unique")) cible = cible.closest(".bloc-ue");

    filtreStatut.value = "tout";
    appliquerFiltre();
    fermerSuggestions();
    effacerSurbrillance();

    // Seul le chemin vers le résultat reste ouvert, pour qu'il soit visible.
    blocs.forEach((bloc) => {
        if (!bloc.contains(cible) && bloc !== cible) bloc.open = false;
    });

    let parent = cible.parentElement;

    while (parent && parent !== tableau) {
        if (parent.matches("details")) parent.open = true;
        parent = parent.parentElement;
    }

    if (cible.matches("details")) cible.open = true;

    cibleCourante = cible;
    void cible.offsetWidth; // relance l'animation de surlignage
    cible.classList.add("cible-recherche");
    champRecherche.blur();
    majBoutonEffacer();

    requestAnimationFrame(() => {
        mesurerTitres();

        const titre = cible.matches("details")
            ? cible.querySelector(":scope > summary")
            : cible;

        // Place le résultat juste sous les titres épinglés.
        let espace = bandeau.getBoundingClientRect().height
            + entete.getBoundingClientRect().height;

        const ue = cible.closest(".bloc-ue");
        const matiere = cible.closest(".bloc-matiere");

        if (ue && cible !== ue) {
            espace += ue.querySelector(":scope > summary")
                .getBoundingClientRect().height;
        }

        if (matiere && cible !== matiere) {
            espace += matiere.querySelector(":scope > summary")
                .getBoundingClientRect().height;
        }

        window.scrollTo({
            top: Math.max(
                0,
                titre.getBoundingClientRect().top + window.scrollY - espace
            ),
            behavior: window.matchMedia(
                "(prefers-reduced-motion: reduce)"
            ).matches ? "auto" : "smooth"
        });

        if (!titre.matches("summary")) {
            titre.setAttribute("tabindex", "-1");
        }

        titre.focus({ preventScroll: true });
        retourRecherche.textContent = "";
    });
}

function trouverCorrespondances(saisie) {
    return blocs.filter((bloc) =>
        normaliser(bloc.dataset.nom || "").includes(saisie)
    ).sort((a, b) =>
        // Les matières d'abord : ce sont elles qui contiennent les notes.
        Number(a.matches(".bloc-ue")) - Number(b.matches(".bloc-ue"))
        || Number(!normaliser(a.dataset.nom).startsWith(saisie))
            - Number(!normaliser(b.dataset.nom).startsWith(saisie))
        || a.dataset.nom.localeCompare(b.dataset.nom, "fr")
    );
}

function afficherSuggestions() {
    const saisie = normaliser(champRecherche.value);
    fermerSuggestions();

    if (!saisie) {
        retourRecherche.textContent = "";
        return;
    }

    const correspondances = trouverCorrespondances(saisie);

    correspondances.forEach((bloc) => {
        const ligne = document.createElement("li");
        const bouton = document.createElement("button");

        bouton.type = "button";
        const nom = document.createElement("span");
        const detail = document.createElement("span");
        nom.className = "suggestion-nom";
        detail.className = "suggestion-detail";
        nom.textContent = bloc.dataset.nom;
        detail.textContent = (bloc.matches(".bloc-ue") ? "UE" : "Matière")
            + ` · S${bloc.dataset.semestre}`;
        bouton.append(nom, detail);

        bouton.addEventListener("click", () => {
            champRecherche.value = bloc.dataset.nom;
            allerAuResultat(bloc);
        });

        ligne.append(bouton);
        listeSuggestions.append(ligne);
    });

    listeSuggestions.hidden = correspondances.length === 0;

    retourRecherche.classList.remove("retour-filtre");
    retourRecherche.textContent = correspondances.length
        ? ""
        : "Aucune matière trouvée pour cette période";
}

champRecherche.addEventListener("input", () => {
    effacerSurbrillance();
    afficherSuggestions();
    majBoutonEffacer();
});

champRecherche.addEventListener("focus", afficherSuggestions);

champRecherche.addEventListener("keydown", (event) => {
    if (event.key === "ArrowDown" && !listeSuggestions.hidden) {
        event.preventDefault();
        listeSuggestions.querySelector("button")?.focus();
    }

    // Entrée ouvre directement le meilleur résultat.
    if (event.key === "Enter") {
        event.preventDefault();
        const saisie = normaliser(champRecherche.value);
        const meilleur = saisie ? trouverCorrespondances(saisie)[0] : null;

        if (meilleur) {
            champRecherche.value = meilleur.dataset.nom;
            allerAuResultat(meilleur);
        }
    }
});

// Sans cela, Safari ferme la liste avant que le clic ne soit pris en compte.
listeSuggestions.addEventListener("mousedown", (event) => {
    event.preventDefault();
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

    // Le menu du profil se ferme dès qu'on clique ailleurs.
    if (menuProfil?.open && !menuProfil.contains(event.target)) {
        menuProfil.open = false;
    }
});

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && menuProfil?.open) {
        menuProfil.open = false;
        menuProfil.querySelector("summary").focus();
    }
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
        retourRecherche.textContent = "";
    }
);

document.querySelectorAll(".carte-note[data-cible]").forEach((lien) => {
    lien.addEventListener("click", (event) => {
        const cible = document.getElementById(lien.dataset.cible);
        if (!cible) return;
        event.preventDefault();
        allerAuResultat(cible);

        // L'utilisateur vient de cliquer sur cette note : on la fait
        // ressortir quelques secondes parmi les autres de la matière.
        cible.classList.remove("note-retrouvee");
        void cible.offsetWidth; // relance l'animation si on reclique
        cible.classList.add("note-retrouvee");
        clearTimeout(cible.minuteurSurlignage);
        cible.minuteurSurlignage = setTimeout(
            () => cible.classList.remove("note-retrouvee"),
            3200
        );
    });
});

blocs.forEach((bloc) => {
    bloc.addEventListener("toggle", () => {
        // Une matière seule dans son UE reste toujours dépliée.
        if (bloc.matches(".matiere-unique") && !bloc.open) bloc.open = true;

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

majBoutonEffacer();
mesurerTitres();
