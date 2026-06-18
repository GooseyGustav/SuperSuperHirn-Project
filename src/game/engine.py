from .domain.board import Board
from .domain.config import Config
from .ports.persisting_config import ForPersistingConfig
from .ports.persisting_game import ForPersistingGame
from .ports.game_administration import ForGameAdministration
from .ports.configuring_game import ForConfiguringGame
from .ports.for_code_making import ForCodeMaking
from .ports.for_code_breaking import ForCodeBreaking

class GameEngine(ForGameAdministration, ForConfiguringGame, ForCodeMaking, ForCodeBreaking):
    """
    Der Kern des Spiels (Hexagon).
    Hier laufen alle Fäden zusammen.
    """
    
    def __init__(
        self, 
        board: Board, 
        config: Config, 
        persisting_config_port: ForPersistingConfig, 
        persisting_game_port: ForPersistingGame
    ):
        self.board = board
        self.config = config
        self.persisting_config_port = persisting_config_port
        self.persisting_game_port = persisting_game_port

    # --- ForGameAdministration Implementierungen ---

    def start_game(self):
        print("-> Die GameEngine startet jetzt das Spiel!")
        self.initialize_board()

    def start_game_delete_interrupted(self):
        print("-> Lösche abgebrochenen Spielstand und starte neu!")
        self.initialize_board()

    def resume_interrupted(self):
        print("-> Setze unterbrochenes Spiel fort...")
        # Hier würden wir theoretisch load_game() vom Persistenz-Port aufrufen

    def abort_game(self):
        print("-> Spiel abgebrochen. Speichere Zustand...")
        self.save_current_state()

    def restart_game(self):
        print("-> Spiel wird neu gestartet.")
        self.abort_game()
        self.start_game()

    def exit_application(self):
        print("-> Anwendung wird beendet. Tschüss!")
        self.save_current_state()


    # --- ForConfiguringGame Implementierung ---

    def save_configuration(self, config_data: str):
        print(f"-> Verarbeite neue Konfiguration: {config_data}")
        # Beispiel: Aktualisiere das Config-Objekt und speichere es
        self.config.difficulty = config_data
        self.persisting_config_port.save_config(self.config)

    def load_configuration(self):
        print(f"-> Lade Konfiguration über den Persistenz-Port.")

        geladene_config = self.persisting_config_port.load_config() # Ruft den Port auf und speichert das Ergebnis
        self.config = geladene_config

    def reset_configuration(self):
        print("-> setze Config zurück auf Standard...")
        self.config.difficulty = "normal" #Standardwert
        self.persisting_config_port.save_config(self.config) #Speichere über Standard Port.

    def get_language(self) -> str:
        """Implementierung aus ForConfiguringGame."""
        print("-> Lese Sprache aus...")
        return "de"


    # --- ForCodeMaking Implementierung

    def set_secret_code(self, code: tuple[int, ...]) -> None:
        print(f"-> Setze Geheimen Code: {code}")

    def give_feedback(self, code: tuple[int, ...]) -> None:
        print(f"-> Gib Antwort auf Spielrunde {code}")


    # --- ForCodeBreaking Implementierung
    def submit_guess(self, guess: list[int]) -> None:
        print(f"-> Spieler hat folgenden Versuch abgegeben: {guess}")
        #Überprüfe ob der Guess mit Secret Code übereinstimmt

    def get_attempts(self) -> list[list[int]]:
        print("-> Lese Versuchshistorie aus...")
        # fiktive Daten hier
        return [[1,2,3,4,], [5,6,7,8]]

    # --- Interne Hilfsmethoden ---

    def initialize_board(self):
        print("-> Board wird initialisiert...")

    def save_current_state(self):
        print("-> Speichere Spielstand über den Port...")
        self.persisting_game_port.save_game(self.board)
        self.persisting_config_port.save_config(self.config)

    def __repr__(self):
        return f"GameEngine(board={self.board}, config={self.config})"
