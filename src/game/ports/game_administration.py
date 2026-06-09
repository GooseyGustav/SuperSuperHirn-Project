from abc import ABC, abstractmethod

class ForGameAdministration(ABC):
    """Port: Schnittstelle zur Steuerung des Spielablaufs von außen."""

    @abstractmethod
    def start_game(self) -> None:
        pass

    @abstractmethod
    def start_game_delete_interrupted(self) -> None:
        pass

    @abstractmethod
    def resume_interrupted(self) -> None:
        """Setzt ein unterbrochenes Spiel fort."""
        pass

    @abstractmethod
    def abort_game(self) -> None:
        """Bricht das aktuelle Spiel ab."""
        pass

    @abstractmethod
    def restart_game(self) -> None:
        """Startet das laufende Spiel neu."""
        pass

    @abstractmethod
    def exit_application(self) -> None:
        """Beendet die gesamte Anwendung."""
        pass
