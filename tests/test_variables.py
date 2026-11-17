import pytest

from src.exceptions import DonneeInvalideError
from src.variables import VariableCategorielle, VariableNumerique


def test_numerique_valide():
    assert VariableNumerique("Year", 1980, 2016).valider("2005") == pytest.approx(2005.0)


@pytest.mark.parametrize("saisie", ["", "   ", "abc", "1900", "2100"])
def test_numerique_invalide(saisie):
    with pytest.raises(DonneeInvalideError):
        VariableNumerique("Year", 1980, 2016).valider(saisie)


def test_categorielle():
    v = VariableCategorielle("Genre", ["Action", "Sports"])
    assert v.valider("Sports") == "Sports"
    with pytest.raises(DonneeInvalideError):
        v.valider("Inconnu")


def test_str():
    assert str(VariableNumerique("Year", 1980, 2016)) == "VariableNumerique(Year)"