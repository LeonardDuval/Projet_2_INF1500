import os
import pandas as pd
import matplotlib.pyplot as plt

DOSSIER = os.path.dirname(__file__)
CHEMIN = os.path.join(DOSSIER, "donnees", "vgsales.csv")

# 1. Chargement
df = pd.read_csv(CHEMIN)
print("Avant nettoyage :", df.shape)
print(df.info())
print(df.isna().sum())
print(df["Year"].describe())

# 2. Nettoyage
df = df.dropna(subset=["Year"])
df = df[df["Year"] <= 2016]
df["Year"] = df["Year"].astype(int)
df["Publisher"] = df["Publisher"].fillna("Inconnu")
top = df["Publisher"].value_counts().head(20).index
df["Publisher"] = df["Publisher"].where(df["Publisher"].isin(top), "Autre")
print("Après nettoyage :", df.shape)

# 3. Graphique d'exploration
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].hist(df["Global_Sales"], bins=50)
axes[0].set_title("Ventes globales (échelle brute)")
axes[0].set_xlabel("Millions d'exemplaires")
axes[0].set_ylabel("Nombre de jeux")
axes[1].hist(df["Global_Sales"].clip(upper=2), bins=50)
axes[1].set_title("Ventes globales (tronquées à 2 M)")
axes[1].set_xlabel("Millions d'exemplaires")
fig.tight_layout()
fig.savefig(os.path.join(DOSSIER, "exploration_ventes.png"), dpi=150)