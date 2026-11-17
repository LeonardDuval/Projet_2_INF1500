import json
import os

import joblib
import numpy as np
import pandas as pd

from src.donnees import COLONNES_ENTREE
from src.exceptions import DonneeInvalideError
from src.variables import Variable, creer_variable


class Modele:
    """Modèle sauvegardé + variables construites depuis les métadonnées."""

    def __init__(self, dossier: str):
        chemin_modele = os.path.join(dossier, "modele.joblib")
        chemin_meta = os.path.join(dossier, "metadonnees.json")
        for chemin in (chemin_modele, chemin_meta):
            if not os.path.exists(chemin):
                raise DonneeInvalideError(f"Fichier introuvable : {chemin}")
        with open(chemin_meta, encoding="utf-8") as f:
            self._meta = json.load(f)
        self._pipeline = joblib.load(chemin_modele)
        self._variables = [creer_variable(v) for v in self._meta["variables"]]

    @property
    def variables(self) -> list[Variable]:
        return self._variables

    @property
    def metrique(self) -> dict:
        return self._meta["metrique"]

    def predire(self, saisies: dict) -> dict[str, float]:
        """Valide les saisies, prédit, reconvertit de log1p en millions.
        Lève DonneeInvalideError si une saisie est invalide."""
        valeurs = {v.nom: v.valider(saisies.get(v.nom))
                   for v in self._variables}
        X = pd.DataFrame([valeurs], columns=COLONNES_ENTREE)
        pred = np.clip(np.expm1(self._pipeline.predict(X))[0], 0, None)
        return dict(zip(self._meta["cibles"], pred.tolist()))

    def __str__(self) -> str:
        return f"Modele({len(self._variables)} variables)"