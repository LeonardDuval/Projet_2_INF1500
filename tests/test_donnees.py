import pandas as pd
import pytest
import numpy as np

from src.donnees import nettoyer, regrouper_editeur, charger_donnees
from src.exceptions import DonneeInvalideError
from sklearn.metrics import r2_score
from src.modele import r2_numpy


def test_nettoyer_retire_annee_manquante_et_future():
    df = pd.DataFrame({"Year": [2005.0, None, 2020.0]})
    assert list(nettoyer(df)["Year"]) == [2005]


def test_regrouper_editeur():
    assert regrouper_editeur("Sega", ["Sega"]) == "Sega"
    assert regrouper_editeur("Petit Studio", ["Sega"]) == "Autre"
    assert regrouper_editeur(None, ["Sega"]) == "Autre"


def test_charger_fichier_absent():
    with pytest.raises(DonneeInvalideError):
        charger_donnees("inexistant.csv")


def test_r2_numpy_egal_sklearn():
    rng = np.random.default_rng(0)
    y = rng.random((50, 4))
    p = y + rng.normal(0, 0.1, (50, 4))
    assert r2_numpy(y, p) == pytest.approx(r2_score(y, p))