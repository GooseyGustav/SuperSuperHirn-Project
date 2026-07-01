from app.game_management.game_config_management.code_constants import CodeConstants
from app.game_management.game_config_management.config import Config
from app.game_management.game_config_management.role import Role
from app.game_management.game_manager import GameManager
from app.game_management.live_game.game_engine import GameEngine
from app.game_model.game import Game
from app.game_model.game_mode import Gamemode
from app.game_model.game_state import Gamestate


class ConfigPersistencePortDouble:
    """Config persistence port double."""

    def load_config_dict(self) -> dict:
        raise AssertionError("Config must not be loaded when interrupting an existing game")

    def save_config_dict(self, config_dict: dict) -> None:
        raise AssertionError("Config must not be saved when interrupting an existing game")

    def reset_to_default(self) -> None:
        raise AssertionError("Config must not be reset when interrupting an existing game")


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
        raise AssertionError("Players must not be assembled when interrupting an existing game")


def test_interrupt_game_persists_current_game_snapshot():
    """GameManager interrupts an existing GameEngine and persists its current game snapshot.

    The test prepares a real GameEngine with a current Game object and one finished attempt.
    The game is already marked INTERRUPTED, matching the current persistence rule that only
    interrupted games are resumable. GameManager.interrupt_game() then sets the engine's
    shutdown flag and persists the snapshot.
    """

    config = Config(
        gamemode=Gamemode.CLASSIC,
        user_role=Role.CODEBREAKER,
        network_enabled=False,
        number_of_positions=CodeConstants.NUMBER_OF_PINS,
        number_of_colors=CodeConstants.NUMBER_OF_COLORS,
        countdown_millis=0,
        delay_millis=0,
    )
    engine = GameEngine(game_config=config)
    engine.game = Game(game_mode=Gamemode.CLASSIC, code_length=CodeConstants.NUMBER_OF_PINS)
    engine.game.set_secret_code([1, 2, 3, 4, 5])
    engine.game.game_state = Gamestate.RUNNING
    engine.game.set_guess([5, 4, 3, 2, 1])
    engine.game.set_feedback([1, 2])
    engine.game.game_state = Gamestate.INTERRUPTED
    game_storage = GamePersistencePortDouble()
    game_manager = GameManager(ConfigPersistencePortDouble(), PlayerAssemblerDouble(), game_storage)
    game_manager._game_engine = engine

    game_manager.interrupt_game()

    assert engine.shutdown_requested is True
    assert game_storage.saved_game_data["gamestate"] == Gamestate.INTERRUPTED.value
    assert game_storage.saved_game_data["secret_code"] == [1, 2, 3, 4, 5]
    assert game_storage.saved_game_data["attempt_list"] == [
        {
            "guess": [5, 4, 3, 2, 1],
            "feedback": {
                "black_pins": 1,
                "white_pins": 2,
                "status": "FINAL",
            },
        }
    ]
