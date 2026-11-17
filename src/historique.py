import csv
import os

CHAMPS = ["nom", "Platform", "Year", "Genre", "Publisher",
          "NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]


def ajouter(chemin: str, nom: str, saisies: dict, resultat: dict) -> None:
    """Ajoute une prédiction à la fin du fichier CSV."""
    nouveau = not os.path.exists(chemin)
    ligne = {"nom": nom, **saisies,
             **{k: round(v, 3) for k, v in resultat.items()}}
    with open(chemin, "a", newline="", encoding="utf-8") as f:
        ecrivain = csv.DictWriter(f, fieldnames=CHAMPS)
        if nouveau:
            ecrivain.writeheader()
        ecrivain.writerow(ligne)


def lire(chemin: str) -> list[dict]:
    """Renvoie toutes les prédictions (liste vide si aucun fichier)."""
    if not os.path.exists(chemin):
        return []
    with open(chemin, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))