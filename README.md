# Prédiction des ventes de jeux vidéo

Projet 2 INF1007 (A2026). Équipe : Léonard Duval et Mouhamed Ndiaye

## Description

Application qui estime les ventes d'un jeu vidéo (en millions) pour quatre régions : Amérique du Nord, Europe, Asie et autres marchés. L'utilisateur choisit une plateforme, un genre, un éditeur et une année de sortie. L'application affiche l'estimation, une carte, un graphique et garde un historique des prédictions.

## Jeu de données

- Source : « Video Game Sales » (vgsales.csv), Kaggle, données issues de vgchartz.com. Lien : https://www.kaggle.com/code/mohaiminul101/video-game-sales/input
- 16 598 lignes avant nettoyage, 16 323 après.
- Entrées : Platform, Year, Genre, Publisher. Cibles : NA_Sales, EU_Sales, JP_Sales, Other_Sales.

## Installation et lancement

```
pip install -r requirements.txt
python -m src.entrainement      
python -m streamlit run main.py 
python -m pytest                
python exploration.py           
```

## Résultat du modèle

- Cible : ventes régionales, transformées avec `log1p` (ventes très asymétriques).
- Modèle : forêt aléatoire (`RandomForestRegressor`) dans un `Pipeline` avec encodage `OneHotEncoder`.
- Métrique : R² sur l'échelle log, moyenné sur les 4 régions, jeu de test (20 %, `random_state=42`).

| Modèle | R^2 |
|---|---|
| Référence (moyenne) | 0,00 |
| Forêt aléatoire | 0,22 |

Le modèle bat la référence mais reste modeste : il sous-estime fortement les très gros succès, car la plateforme, le genre, l'année et l'éditeur ne distinguent pas un jeu moyen d'un jeu exceptionnel (franchise, marketing et qualité sont absents du fichier). Voir `predit_vs_reel.png`.

## Structure du code

```
main.py                 point d'entrée de l'application
exploration.py          exploration des données et graphique
src/
  donnees.py            chargement, nettoyage, regroupement des éditeurs
  modele.py             pipeline, baseline, évaluation, métriques, sauvegarde
  entrainement.py       script qui entraîne et sauvegarde le modèle
  variables.py          classes Variable, VariableNumerique, VariableCategorielle
  predicteur.py         classe Modele : charge le modèle et prédit
  historique.py         lecture et écriture de l'historique (CSV)
  interface.py          interface Streamlit
  exceptions.py         exception personnalisée DonneeInvalideError
tests/                  tests pytest
modeles/                modele.joblib et metadonnees.json
donnees/                vgsales.csv
DECISIONS.md            fiche de décisions
JOURNAL_IA.md           journal d'utilisation de l'IA
```

## Outil du chapitre 7

Le décorateur `chronometrer` (dans `src/modele.py`) enveloppe la fonction d'entraînement pour afficher sa durée sans modifier son code.

## Tests et couverture

Nombre de tests : 9. Couverture mesurée avec `coverage` : 77%.

## Documentation consultée

- pandas, « 10 minutes to pandas » : https://pandas.pydata.org/docs/user_guide/10min.html
- scikit-learn, RandomForestRegressor : https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html
- Streamlit : https://docs.streamlit.io

## Documents du projet

Choix et justifications : `DECISIONS.md`. Usage de l'IA : `JOURNAL_IA.md`.