# enum: CODEMAKER, CODEBREAKER, OBSERVER
# Held by `Config`; read by `Matchmaker`.

from enum import Enum


class Role(Enum):
    """Die Rolle, die der menschliche Nutzer in dieser Runde hat."""

    CODEMAKER = "CODEMAKER"
    CODEBREAKER = "CODEBREAKER"
    OBSERVER = "OBSERVER"
