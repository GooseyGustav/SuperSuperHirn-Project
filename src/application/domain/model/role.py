# src/application/domain/model/role.py
from enum import Enum


class Role(Enum):
    """Repräsentiert die Spielrollen in SuperSuperHirn."""

    CODE_MAKER = "CodeMaker"
    CODE_BREAKER = "CodeBreaker"

    def get_description(self) -> str:
        """Gibt eine kurze Beschreibung der Rolle zurück."""
        if self == Role.CODE_MAKER:
            return "Setzt den geheimen Code und gibt Feedback."
        return "Versucht den geheimen Code zu erraten."
