from abc import ABC, abstractmethod

class ForCodeMaking(ABC):
    """Port: Schnittstelle fuur den Code-Macher"""
    @abstractmethod
    def set_secret_code(self, code: tuple[int, ...]) -> None:
        """Setz den gemeinen Code. Erwartet ein Tupel von Zahlen, z.B. (1, 2, 3, 4)."""
    pass

    @abstractmethod
    def give_feedback(self, code: tuple[int, ...]) -> None:
        """Gibt eine Antwort, ob die Eingabe richtig war"""
        pass