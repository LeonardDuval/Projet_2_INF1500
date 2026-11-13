import os

import matplotlib.pyplot as plt

from src.donnees import (CIBLES, charger_donnees, nettoyer,
                         trouver_top_editeurs)
from src.modele import (construire_metadonnees, construire_pipeline,
                        entrainer, entrainer_baseline, evaluer, preparer_xy,
                        sauvegarder, separer)

RACINE = os.path.dirname(os.path.dirname(__file__))


def main() -> None:
    df = nettoyer(charger_donnees(
        os.path.join(RACINE, "donnees", "vgsales.csv")))
    top = trouver_top_editeurs(df)
    X, y = preparer_xy(df, top)
    X_train, X_test, y_train, y_test = separer(X, y)

    base = entrainer_baseline(X_train, y_train)
    modele = entrainer(construire_pipeline(), X_train, y_train)

    r2_base = evaluer(base, X_test, y_test)
    r2_modele = evaluer(modele, X_test, y_test)
    print(f"R2 baseline : {r2_base:.3f}")
    print(f"R2 modele   : {r2_modele:.3f}")

    # Graphique prédit vs réel (une région par panneau)
    pred = modele.predict(X_test)
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    for i, ax in enumerate(axes):
        ax.scatter(y_test[:, i], pred[:, i], s=5, alpha=0.4)
        ax.plot([0, y_test[:, i].max()], [0, y_test[:, i].max()], "r--",
                label="prédiction parfaite")
        ax.set_title(CIBLES[i])
        ax.set_xlabel("Réel (log1p, M)")
        ax.set_ylabel("Prédit (log1p, M)")
        ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(RACINE, "predit_vs_reel.png"), dpi=150)

    meta = construire_metadonnees(X, top, r2_modele, r2_base)
    sauvegarder(modele, meta, os.path.join(RACINE, "modeles"))


if __name__ == "__main__":
    main()