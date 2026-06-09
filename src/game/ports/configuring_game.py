from abc import ABC, abstractmethod

class ForConfiguringGame(ABC):
    """Port: Schnittstelle zum Konfigurieren des Spiels von außen."""

    @abstractmethod
    def save_configuration(self, config_data: str) -> None:
        """Speichert eine neue Konfiguration (als Text)."""
        pass

    @abstractmethod
    def load_configuration(self, config_data: str) -> None:
        """Lädt eine Konfiguration"""
        pass

    @abstractmethod
    def reset_configuration(self) -> None:
        """setzt eine Konfiguration zurück"""
        pass

    @abstractmethod
    def get_language(self) -> str:
        """liefert die ausgewählte Sprache"""
        pass