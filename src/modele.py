import time
from functools import wraps

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.donnees import CIBLES, COLONNES_ENTREE, regrouper_editeur

GRAINE = 42


def chronometrer(fonction):
    """Décorateur : affiche la durée d'exécution de la fonction."""
    @wraps(fonction)
    def enveloppe(*args, **kwargs):
        debut = time.perf_counter()
        resultat = fonction(*args, **kwargs)
        print(f"{fonction.__name__} : {time.perf_counter() - debut:.2f} s")
        return resultat
    return enveloppe


def preparer_xy(df: pd.DataFrame, top: list[str]) -> tuple[pd.DataFrame, np.ndarray]:
    """Renvoie X (4 colonnes, éditeurs regroupés) et y (log1p des 4 ventes)."""
    X = df[COLONNES_ENTREE].copy()
    X["Publisher"] = X["Publisher"].map(lambda e: regrouper_editeur(e, top))
    y = np.log1p(df[CIBLES].to_numpy())
    return X, y


def separer(X: pd.DataFrame, y: np.ndarray):
    """Sépare en entraînement (80 %) et test (20 %), graine fixée."""
    return train_test_split(X, y, test_size=0.2, random_state=GRAINE)


def construire_pipeline() -> Pipeline:
    """Pipeline : encodage des catégories + forêt aléatoire."""
    encodage = ColumnTransformer(
        [("cat", OneHotEncoder(handle_unknown="ignore"),
          ["Platform", "Genre", "Publisher"])],
        remainder="passthrough",  # Year reste numérique
    )
    return Pipeline([
        ("encodage", encodage),
        ("modele", RandomForestRegressor(
            n_estimators=100, min_samples_leaf=5, random_state=GRAINE)),
    ])


@chronometrer
def entrainer(pipeline: Pipeline, X_train, y_train) -> Pipeline:
    """Entraîne le pipeline et le renvoie."""
    return pipeline.fit(X_train, y_train)


def entrainer_baseline(X_train, y_train) -> DummyRegressor:
    """Modèle de référence : prédit toujours la moyenne."""
    return DummyRegressor(strategy="mean").fit(X_train, y_train)


def r2_numpy(y_vrai: np.ndarray, y_pred: np.ndarray) -> float:
    """R² moyen sur les sorties, calculé avec NumPy sans boucle."""
    ss_res = ((y_vrai - y_pred) ** 2).sum(axis=0)
    ss_tot = ((y_vrai - y_vrai.mean(axis=0)) ** 2).sum(axis=0)
    return float((1 - ss_res / ss_tot).mean())

def evaluer(modele, X_test, y_test) -> float:
    """Renvoie le R² (échelle log) du modèle sur le jeu de test."""
    return r2_numpy(y_test, modele.predict(X_test))


def construire_metadonnees(X: pd.DataFrame, top: list[str],
                           r2_modele: float, r2_base: float) -> dict:
    """Construit le dictionnaire de métadonnées pour l'interface."""
    variables = []
    for nom in COLONNES_ENTREE:
        if nom == "Year":
            variables.append({"nom": nom, "type": "numerique",
                              "min": int(X[nom].min()), "max": int(X[nom].max())})
        else:
            valeurs = sorted(X[nom].unique().tolist())
            variables.append({"nom": nom, "type": "categorielle",
                              "valeurs": valeurs})
    return {
        "cibles": CIBLES,
        "type_probleme": "regression",
        "transformation": "log1p",
        "top_editeurs": top,
        "variables": variables,
        "metrique": {"nom": "R2 (log)", "valeur": r2_modele,
                     "reference": r2_base},
    }


def sauvegarder(pipeline: Pipeline, meta: dict, dossier: str) -> None:
    """Écrit modele.joblib et metadonnees.json dans dossier."""
    os.makedirs(dossier, exist_ok=True)
    joblib.dump(pipeline, os.path.join(dossier, "modele.joblib"))
    with open(os.path.join(dossier, "metadonnees.json"), "w",
              encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)