const champRecherche = document.querySelector("#recherche-notes");
const retourRecherche = document.querySelector("#retour-recherche");
const blocsUE = [...document.querySelectorAll(".bloc-ue")];

// Conserve les menus ouverts avant la recherche.
let etatInitial = null;

function normaliser(texte) {
    return texte
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase()
        .trim();
}

function nomDuBloc(bloc) {
    const titre = bloc.querySelector(":scope > summary .libelle");
    return normaliser(titre?.textContent ?? "");
}

champRecherche.addEventListener("input", () => {
    const recherche = normaliser(champRecherche.value);

    if (recherche && etatInitial === null) {
        etatInitial = new Map();

        document.querySelectorAll(
            ".bloc-ue, .bloc-matiere"
        ).forEach((bloc) => {
            etatInitial.set(bloc, bloc.open);
        });
    }

    let nombreUE = 0;
    let nombreMatieres = 0;

    blocsUE.forEach((ue) => {
        const matieres = [
            ...ue.querySelectorAll(".bloc-matiere")
        ];

        if (!recherche) {
            ue.hidden = false;

            matieres.forEach((matiere) => {
                matiere.hidden = false;
            });

            return;
        }

        const ueCorrespond = nomDuBloc(ue).includes(recherche);
        let matieresVisibles = 0;

        matieres.forEach((matiere) => {
            const matiereCorrespond = nomDuBloc(matiere)
                .includes(recherche);

            const visible = ueCorrespond || matiereCorrespond;

            matiere.hidden = !visible;
            matiere.open = visible;

            if (visible) {
                matieresVisibles += 1;
                nombreMatieres += 1;
            }
        });

        const visible = ueCorrespond || matieresVisibles > 0;

        ue.hidden = !visible;
        ue.open = visible;

        if (visible) {
            nombreUE += 1;
        }
    });

    if (!recherche) {
        if (etatInitial !== null) {
            etatInitial.forEach((ouvert, bloc) => {
                bloc.open = ouvert;
            });

            etatInitial = null;
        }

        retourRecherche.textContent = "";
        return;
    }

    if (nombreUE === 0) {
        retourRecherche.textContent =
            "Aucune UE ni matière trouvée pour cette période.";
    } else {
        retourRecherche.textContent =
            `${nombreUE} UE et ${nombreMatieres} matière(s) affichée(s). ` +
            "Les moyennes restent celles de la période entière.";
    }
});