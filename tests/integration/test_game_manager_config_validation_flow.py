import pytest

from app.game_management.game_manager import GameManager


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


class PlayerAssemblerDouble:
    """Player assembler port double that records whether player assembly was requested."""

    def __init__(self):
        self.received_config: dict | None = None
        self.was_called = False

    def assemble_players(self, config: dict):
        self.was_called = True
        self.received_config = config
        raise AssertionError("Players must not be assembled for invalid config")


class SynchronousExecutorDouble:
    """Thread executor double."""

    def run(self, fn) -> None:
        fn()


def test_start_game_invalid_config_stops_before_player_assembly_and_persistence():
    """GameManager rejects an invalid loaded config before assembling players or saving a game.

    The test loads a invalid configuration through the ConfigPersistPortDouble. GameManager.load_config() validates the
    dict and raises an error before ConfigManager, GameEngine, or the PlayerAssembler can be used. Therefore no game
    persistence data is written.
    """

    invalid_config = {
        "gamemode": "NOT_A_MODE",
        "user_role": "CODEBREAKER",
        "network_enabled": False,
        "countdown_millis": 0,
        "delay_millis": 0,
    }
    config_storage = ConfigPersistencePortDouble(invalid_config)
    game_storage = GamePersistencePortDouble()
    player_assembler = PlayerAssemblerDouble()
    game_manager = GameManager(config_storage, player_assembler, game_storage)
    game_manager.executor = SynchronousExecutorDouble()

    with pytest.raises(ValueError):
        game_manager.start_game()

    assert player_assembler.was_called is False
    assert player_assembler.received_config is None
    assert game_storage.saved_game_data is None
