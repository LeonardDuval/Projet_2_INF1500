from abc import ABC, abstractmethod

from src.exceptions import DonneeInvalideError


class Variable(ABC):
    """Variable d'entrée du modèle (classe parente abstraite)."""

    def __init__(self, nom: str):
        self._nom = nom

    @property
    def nom(self) -> str:
        return self._nom

    @abstractmethod
    def valider(self, saisie):
        """Renvoie la valeur validée ou lève DonneeInvalideError."""

    def __str__(self) -> str:
        return f"{type(self).__name__}({self._nom})"


class VariableNumerique(Variable):
    def __init__(self, nom: str, minimum: float, maximum: float):
        super().__init__(nom)
        self._min = minimum
        self._max = maximum

    @property
    def minimum(self) -> float:
        return self._min

    @property
    def maximum(self) -> float:
        return self._max

    def valider(self, saisie) -> float:
        if saisie is None or str(saisie).strip() == "":
            raise DonneeInvalideError(f"{self._nom} : le champ est vide.")
        try:
            valeur = float(str(saisie).replace(",", "."))
        except ValueError:
            raise DonneeInvalideError(
                f"{self._nom} : « {saisie} » n'est pas un nombre.") from None
        if not self._min <= valeur <= self._max:
            raise DonneeInvalideError(
                f"{self._nom} : entrez une valeur entre "
                f"{self._min:g} et {self._max:g}.")
        return valeur


class VariableCategorielle(Variable):
    def __init__(self, nom: str, valeurs: list[str]):
        super().__init__(nom)
        self._valeurs = list(valeurs)

    @property
    def valeurs(self) -> list[str]:
        return self._valeurs

    def valider(self, saisie) -> str:
        if saisie not in self._valeurs:
            raise DonneeInvalideError(
                f"{self._nom} : « {saisie} » n'est pas une valeur permise.")
        return saisie


def creer_variable(description: dict) -> Variable:
    """Construit la bonne variable à partir d'une entrée du JSON."""
    if description["type"] == "numerique":
        return VariableNumerique(description["nom"], description["min"],
                                 description["max"])
    if description["type"] == "categorielle":
        return VariableCategorielle(description["nom"],
                                    description["valeurs"])
    raise DonneeInvalideError(f"Type inconnu : {description['type']}")