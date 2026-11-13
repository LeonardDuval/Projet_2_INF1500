import os
import pandas as pd

from src.exceptions import DonneeInvalideError

COLONNES_ENTREE = ["Platform", "Year", "Genre", "Publisher"]
CIBLES = ["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]
ANNEE_MAX = 2016


def charger_donnees(chemin: str) -> pd.DataFrame:
    """Lit le CSV. Échoue avec DonneeInvalideError si le fichier est absent
    ou s'il manque des colonnes."""
    if not os.path.exists(chemin):
        raise DonneeInvalideError(f"Fichier introuvable : {chemin}")
    with open(chemin, encoding="utf-8") as f:
        df = pd.read_csv(f)
    manquantes = set(COLONNES_ENTREE + CIBLES) - set(df.columns)
    if manquantes:
        raise DonneeInvalideError(f"Colonnes manquantes : {sorted(manquantes)}")
    return df


def nettoyer(df: pd.DataFrame) -> pd.DataFrame:
    """Retire les lignes sans année ou après ANNEE_MAX, convertit Year en int.
    Renvoie une copie."""
    df = df.dropna(subset=["Year"])
    df = df[df["Year"] <= ANNEE_MAX].copy()
    df["Year"] = df["Year"].astype(int)
    return df


def trouver_top_editeurs(df: pd.DataFrame, n: int = 20) -> list[str]:
    """Renvoie les n éditeurs les plus fréquents."""
    return df["Publisher"].value_counts().head(n).index.tolist()


def regrouper_editeur(editeur: str | None, top: list[str]) -> str:
    """Renvoie l'éditeur s'il est dans top, sinon 'Autre'
    (couvre aussi les valeurs manquantes)."""
    return editeur if editeur in top else "Autre"