from abc import ABC, abstractmethod
from ..domain.board import Board

class ForPersistingGame(ABC):
    """Port für das Speichern und Laden des Spielzustands."""
    
    @abstractmethod
    def save_game(self, board: Board) -> None:
        """Speichert den aktuellen Spielzustand."""
        pass

    @abstractmethod
    def load_game(self) -> Board:
        """Lädt einen gespeicherten Spielzustand."""
        pass
