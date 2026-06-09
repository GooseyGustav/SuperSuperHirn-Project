from abc import ABC, abstractmethod
from ..domain.config import Config

class ForPersistingConfig(ABC):
    """Port für das Speichern und Laden der Konfiguration."""
    
    @abstractmethod
    def save_config(self, config: Config) -> None:
        """Speichert die Konfiguration."""
        pass

    @abstractmethod
    def load_config(self) -> Config:
        """Lädt die Konfiguration."""
        pass
