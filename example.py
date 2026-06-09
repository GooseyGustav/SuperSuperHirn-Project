from src.game.domain.board import Board
from src.game.domain.config import Config
from src.game.ports.persisting_config import ForPersistingConfig
from src.game.ports.persisting_game import ForPersistingGame
from src.game.engine import GameEngine

class InMemoryPersistence(ForPersistingConfig, ForPersistingGame):
    def save_config(self, config: Config):
        print(f"Fake-Save: Config gespeichert ({config.difficulty})")

    def load_config(self) -> Config:
        return Config()

    def save_game(self, board: Board):
        print("Fake-Save: Board gespeichert")

    def load_game(self) -> Board:
        return Board()

# 1. Objekte erstellen
my_board = Board()
my_config = Config(difficulty="hard")
persistence = InMemoryPersistence()

# 2. Engine starten (Dependency Injection)
engine = GameEngine(
    board=my_board, 
    config=my_config, 
    persisting_config_port=persistence, 
    persisting_game_port=persistence
)

print("\n--- Testlauf: Game Administration ---")
engine.start_game()
engine.abort_game()

print("\n--- Testlauf: Configuration ---")
engine.save_configuration("extreme")
