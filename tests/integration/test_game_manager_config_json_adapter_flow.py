from adapter.driven_adapter.for_persisting_config.file_tool.config_json_adapter import ConfigJsonAdapter
from app.game_management.game_manager import GameManager
from app.game_model.game_state import Gamestate


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

    def get_guess(self, board: list[tuple[list[int], list[int], str]]) -> list[int]:
        return self.guess


class PlayerAssemblerDouble:
    """Player assembler port double."""

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


def test_game_manager_starts_game_with_config_loaded_from_json_adapter(tmp_path):
    """GameManager loads config through the real ConfigJsonAdapter and completes a game.

    The test writes a valid config through ConfigJsonAdapter, then starts a local game
    through GameManager using a fresh adapter instance. The loaded JSON config is validated,
    expanded for player assembly, used to run GameEngine, and the won game is persisted.
    """

    config = {
        "gamemode": "CLASSIC",
        "user_role": "CODEBREAKER",
        "network_enabled": False,
        "countdown_millis": 0,
        "delay_millis": 0,
    }
    secret_code = [1, 2, 3, 4, 5]
    config_file_path = tmp_path / "current_game_config.json"
    default_file_path = tmp_path / "default_game_config.json"
    saving_adapter = ConfigJsonAdapter(
        base_dir=tmp_path,
        config_file_path=config_file_path,
        default_file_path=default_file_path,
    )
    saving_adapter.save_config_dict(config)
    loading_adapter = ConfigJsonAdapter(
        base_dir=tmp_path,
        config_file_path=config_file_path,
        default_file_path=default_file_path,
    )
    game_storage = GamePersistencePortDouble()
    codemaker = CodemakerDouble(secret_code)
    codebreaker = CodebreakerDouble(secret_code)
    player_assembler = PlayerAssemblerDouble(codemaker, codebreaker)
    game_manager = GameManager(loading_adapter, player_assembler, game_storage)
    game_manager.executor = SynchronousExecutorDouble()

    game_manager.start_game()

    assert player_assembler.received_config["gamemode"] == "CLASSIC"
    assert player_assembler.received_config["number_of_positions"] == 5
    assert player_assembler.received_config["number_of_colors"] == 8
    assert game_manager._game_engine.get_game_obj().game_state == Gamestate.WON
    assert game_storage.saved_game_data is None
    assert config_file_path.exists()
