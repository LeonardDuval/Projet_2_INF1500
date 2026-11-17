# Fiche de décisions

Format:
| Choix | Options envisagées | Choix retenu et justification |


| Domaine | Immobilier, sport, jeux vidéo | **Jeux vidéo** : prédire les ventes d'un jeu selon sa plateforme, son genre, son année et son éditeur. Domaine qui nous intéresse, aucune donnée personnelle. |

| Jeu de données | vgsales.csv (Kaggle) ; version enrichie avec scores critiques et ESRB | **vgsales.csv** (16 598 lignes, source vgchartz via Kaggle). Version enrichie écartée : beaucoup de valeurs manquantes, moins de lignes exploitables. Licence à vérifier sur la page Kaggle. |

| Colonnes d'entrée | 5 colonnes (exigé) ; 4 colonnes | **4 colonnes** : Platform, Year, Genre, Publisher. `Rank` exclue (calculée à partir des ventes : fuite d'information), `Name` exclue (identifiant quasi unique). Écart avec l'énoncé à faire accepter. |

| Variables cibles | Une cible (`Global_Sales`) ; quatre cibles régionales | **Quatre cibles** : NA, EU, JP, Other. L'interface affiche déjà quatre régions. Un seul modèle multi-sorties. | 

| Transformation de la cible | Ventes brutes ; `log1p` | **`log1p`** : ventes très asymétriques (médiane NA 0,08 M, maximum 41,49 M). L'interface reconvertit avec `expm1`. |

| Métrique | RMSE, MAE, R^2 | **R^2 sur l'échelle log**, moyenné sur les 4 régions. La RMSE serait dominée par quelques gros succès. R² recalculé avec NumPy et comparé à scikit-learn dans un test. |

| Modèle | Régression linéaire, KNN, forêt aléatoire | **RandomForestRegressor** (100 arbres, `min_samples_leaf=5`) : gère la multi-sortie et les interactions plateforme/genre/éditeur. Régression linéaire trop simple pour des catégories nombreuses ; KNN peu adapté aux variables catégorielles. | 

| Référence | Moyenne ; aucune | **`DummyRegressor(strategy="mean")`** : R^2 de 0, point de comparaison. |

| Séparation | 80/20 ; 70/30 | **80/20, `random_state=42`** : résultats reproductibles. |

| Années manquantes (271 lignes) | Imputer ; supprimer | **Supprimer** : 1,6 % du jeu, une année imputée serait inventée. |

| Années > 2016 (4 lignes) | Garder ; supprimer | **Supprimer** : une erreur évidente (DS en 2020) et trois sorties de 2017 aux ventes probablement incomplètes. Plage de `Year` : 1980 à 2016. |

| Éditeurs | Garder tous (centaines) ; 20 plus fréquents + « Autre » | **20 plus fréquents + « Autre »** : liste déroulante utilisable, encodage plus léger. Les éditeurs manquants tombent dans « Autre ». Limite : la liste est calculée sur tout le jeu. |

| Prétraitement | Encoder à part ; `Pipeline` | **`Pipeline` (OneHotEncoder + forêt)** sauvegardé d'un bloc : l'interface envoie des valeurs brutes. `handle_unknown="ignore"` évite un plantage sur une catégorie inconnue. |

| Format des métadonnées | Plusieurs possibles | **JSON** : cibles, transformation, `top_editeurs`, variables (type, min/max ou valeurs), métrique. Format convenu avec le coéquipier. | Convenu en équipe |

| Technologie d'interface | Tkinter, Streamlit, Gradio | **Streamlit** (choix du coéquipier), fonctionne en local. |

| Saisie de l'année | `number_input` ; champ texte validé par nos classes | **Champ texte** validé par `VariableNumerique` : message clair pour une saisie vide, non numérique ou hors intervalle. |

| Structure du code | Un seul fichier ; modules séparés | **Modules** : donnees, modele, exceptions, variables, predicteur, historique, interface, entrainement. L'interface ne contient aucune logique de calcul. |

| Emplacement de `main.py` | Dans `src/` ; à la racine | **À la racine** : `streamlit run main.py` trouve ainsi le package `src`. |

| Outil du chapitre 7 | Décorateur, générateur, lambda | **Décorateur `chronometrer`** (durée de l'entraînement). Une lambda sert aussi à regrouper les éditeurs. |

| Historique | CSV ; JSON | **CSV** (`historique.csv`), non versionné (dans `.gitignore`). |

