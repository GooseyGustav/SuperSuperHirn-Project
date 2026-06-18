from __future__ import annotations
from .color import COLOR


class Slot:
    def __init__(self):
        self._color: COLOR | None = None

    def isEmpty(self) -> bool:
        return self._color is None

    def setColor(self, color: COLOR) -> None:
        self._color = color

    def getColor(self) -> COLOR:
        return self._color

    def __repr__(self):
        return f"Slot(color={self._color})"
