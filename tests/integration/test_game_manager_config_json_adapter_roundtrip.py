from adapter.driven_adapter.for_persisting_config.file_tool.config_json_adapter import ConfigJsonAdapter
from app.game_management.game_manager import GameManager


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
    """Player assembler port double."""

    def assemble_players(self, config: dict):
        raise AssertionError("Players must not be assembled during config save/load")


def test_game_manager_config_json_adapter_roundtrip(tmp_path):
    """GameManager saves and loads a valid config through the real ConfigJsonAdapter.

    The test uses a temporary JSON storage directory and verifies that one GameManager
    can persist a valid configuration through ConfigJsonAdapter while another GameManager
    can load the same configuration back through a fresh adapter instance.
    """

    config = {
        "gamemode": "BLIND_TRIAL",
        "user_role": "OBSERVER",
        "network_enabled": False,
        "countdown_millis": 0,
        "delay_millis": 250,
    }
    config_file_path = tmp_path / "current_game_config.json"
    default_file_path = tmp_path / "default_game_config.json"
    game_storage = GamePersistencePortDouble()
    player_assembler = PlayerAssemblerDouble()
    saving_adapter = ConfigJsonAdapter(
        base_dir=tmp_path,
        config_file_path=config_file_path,
        default_file_path=default_file_path,
    )
    saving_game_manager = GameManager(saving_adapter, player_assembler, game_storage)

    saving_game_manager.save_config(config)

    loading_adapter = ConfigJsonAdapter(
        base_dir=tmp_path,
        config_file_path=config_file_path,
        default_file_path=default_file_path,
    )
    loading_game_manager = GameManager(loading_adapter, player_assembler, game_storage)

    assert loading_game_manager.load_config() == config
    assert config_file_path.exists()
