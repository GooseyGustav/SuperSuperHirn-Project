from abc import ABC, abstractmethod

class ForCodeBreaking(ABC):
    @abstractmethod
    def submit_guess(self, guess: list[int]) -> None:
        """Übermittelt einen Rateversuch."""
    pass

    @abstractmethod
    def get_attempts(self) -> list[list[int]]:
        """Gibt die Historie aller bisherigen Rateversuche zurück."""
        pass