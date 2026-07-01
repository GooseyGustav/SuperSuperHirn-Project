from app.game_management.game_manager import GameManager
from app.game_model.game_state import Gamestate


class ConfigPersistencePortDouble:
    """Config persistence port double."""

    def __init__(self, config: dict):
        self.config = config

    def load_config_dict(self) -> dict:
        return self.config

    def save_config_dict(self, config_dict: dict) -> None:
        self.config = config_dict

    def reset_to_default(self) -> None:
        raise NotImplementedError


class GamePersistencePortDouble:
    """Game persistence port double."""

    def __init__(self):
        self.saved_game_data: dict | None = None

    def save_game(self, game_data: dict) -> None:
        self.saved_game_data = game_data

    def load_game(self) -> dict:
        return self.saved_game_data

    def delete_game(self) -> None:
        self.saved_game_data = None


class CodemakerDouble:
    """Codemaker double."""

    def __init__(self, secret_code: list[int]):
        self.secret_code = secret_code

    def get_secret_code(self) -> list[int]:
        return self.secret_code

    def get_feedback(self, secret_code: list[int], guess: list[int]) -> list[int]:
        return [8 for secret_pin, guess_pin in zip(secret_code, guess) if secret_pin == guess_pin]


class CodebreakerDouble:
    """Codebreaker double."""

    def __init__(self, guess: list[int]):
        self.guess = guess
        self.received_boards: list[list[tuple[list[int], list[int], str]]] = []

    def get_guess(self, board: list[tuple[list[int], list[int], str]]) -> list[int]:
        self.received_boards.append(board)
        return self.guess


class PlayerAssemblerDouble:
    """Player assembler port double returning predefined codemaker and codebreaker."""

    def __init__(self, codemaker: CodemakerDouble, codebreaker: CodebreakerDouble):
        self.codemaker = codemaker
        self.codebreaker = codebreaker
        self.received_config: dict | None = None

    def assemble_players(self, config: dict) -> tuple[CodemakerDouble, CodebreakerDouble]:
        self.received_config = config
        return self.codemaker, self.codebreaker


class SynchronousExecutorDouble:
    """Thread executor double."""

    def run(self, fn) -> None:
        fn()


def test_start_game_happy_path_finishes_without_persisting_won_game():
    """GameManager starts a local game, runs it through GameEngine, and leaves won games unpersisted.

    The test loads and validates the configuration through the ConfigPersistPortDouble, creates a ConfigManager and a
    Config object, initializes the GameEngine, asks the PlayerAssembler for the Codemaker and Codebreaker, and executes
    GameEngine.run(). During the GameEngine run, the game is won. Since only INTERRUPTED games are resumable, no game
    persistence data is written.
    """

    config = {
        "gamemode": "CLASSIC",
        "user_role": "CODEBREAKER",
        "network_enabled": False,
        "countdown_millis": 0,
        "delay_millis": 0,
    }
    secret_code = [1, 2, 3, 4, 5]
    config_storage = ConfigPersistencePortDouble(config)
    game_storage = GamePersistencePortDouble()
    codemaker = CodemakerDouble(secret_code)
    codebreaker = CodebreakerDouble(secret_code)
    player_assembler = PlayerAssemblerDouble(codemaker, codebreaker)
    game_manager = GameManager(config_storage, player_assembler, game_storage)
    game_manager.executor = SynchronousExecutorDouble()

    game_manager.start_game()

    assert player_assembler.received_config["gamemode"] == "CLASSIC"
    assert player_assembler.received_config["number_of_positions"] == 5
    assert player_assembler.received_config["number_of_colors"] == 8

    game = game_manager._game_engine.get_game_obj()
    assert game.game_state == Gamestate.WON
    assert game_storage.saved_game_data is None

    persist_object = game_manager._game_engine.create_game_persist_object()
    assert persist_object["secret_code"] == secret_code
    assert persist_object["attempt_list"] == [
        {
            "guess": secret_code,
            "feedback": {
                "black_pins": 5,
                "white_pins": 0,
                "status": "FINAL",
            },
        }
    ]
