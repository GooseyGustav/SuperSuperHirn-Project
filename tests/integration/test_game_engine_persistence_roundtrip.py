from pathlib import Path

import pytest

from adapter.driven_adapter.for_persisting_game.file_tool.game_json_adapter import GameJsonAdapter
from app.game_management.game_config_management.code_constants import CodeConstants
from app.game_management.game_config_management.config import Config
from app.game_management.game_config_management.role import Role
from app.game_management.live_game.game_engine import GameEngine
from app.game_model.game import Game
from app.game_model.game_mode import Gamemode
from app.game_model.game_state import Gamestate


@pytest.fixture
def default_config() -> Config:
    """Provides a valid baseline configuration for the GameEngine."""
    return Config(
        gamemode=Gamemode.CLASSIC,
        user_role=Role.CODEBREAKER,
        network_enabled=False,
        number_of_positions=CodeConstants.NUMBER_OF_PINS,
        number_of_colors=CodeConstants.NUMBER_OF_COLORS,
        countdown_millis=0,
        delay_millis=0,
    )


# ---------- Integration Tests: Persistence Roundtrip ----------


def test_engine_saves_and_resumes_active_game_state(tmp_path: Path, default_config: Config) -> None:
    """Proves that a mid-game state can be serialized, saved, loaded, and perfectly resumed."""

    # 1. Arrange: Create a mid-game state
    original_engine = GameEngine(game_config=default_config)
    original_engine.game = Game(game_mode=default_config.gamemode, code_length=CodeConstants.NUMBER_OF_PINS)

    # Set secret code while state is NEW
    original_engine.game.set_secret_code([1, 2, 3, 4, 5])

    # Transition to RUNNING and make a move
    original_engine.game.game_state = Gamestate.RUNNING
    original_engine.game.set_guess([1, 2, 8, 8, 8])
    original_engine.game.set_feedback([2, 0])

    # Interrupt the game for saving
    original_engine.game.game_state = Gamestate.INTERRUPTED

    # 2. Act: Save, Load, and Resume
    save_dict = original_engine.create_game_persist_object()

    adapter = GameJsonAdapter(base_dir=tmp_path, file_name="roundtrip_save.json")
    adapter.save_game(save_dict)

    loaded_dict = adapter.load_game()

    new_engine = GameEngine(game_config=default_config)
    new_engine.resume(loaded_dict)

    # 3. Assert: Verify the resumed game object is perfectly identical
    resumed_game = new_engine.get_game_obj()

    assert resumed_game is not None
    assert resumed_game.game_state == Gamestate.INTERRUPTED

    # Verify secret code
    original_secret = [pin.get_color().value for pin in original_engine.game.secret_code.get_code()]
    resumed_secret = [pin.get_color().value for pin in resumed_game.secret_code.get_code()]
    assert resumed_secret == original_secret

    # Verify attempt history
    assert len(resumed_game.attempt_list) == 1

    resumed_guess = [
        pin.get_color().value for pin in resumed_game.attempt_list[0].get_guess().get_code_guess().get_code()
    ]
    assert resumed_guess == [1, 2, 8, 8, 8]

    resumed_feedback = resumed_game.attempt_list[0].get_feedback()
    assert resumed_feedback.black_pins == 2
    assert resumed_feedback.white_pins == 0
