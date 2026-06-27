from unittest.mock import MagicMock

import pytest

from app.game_management.game_config_management.code_constants import CodeConstants
from app.game_management.game_config_management.config import Config
from app.game_management.live_game.game_engine import GameEngine
from app.game_model.game_state import Gamestate


@pytest.fixture
def default_config():
    """Creates a valid Config instance using Mocks for enums."""
    return Config(
        gamemode=MagicMock(),
        user_role=MagicMock(),
        network_enabled=False,
        number_of_positions=CodeConstants.NUMBER_OF_PINS,
        number_of_colors=CodeConstants.NUMBER_OF_COLORS,
        countdown_millis=0,
        delay_millis=0,
    )


@pytest.fixture
def engine(default_config):
    """Instantiates the GameEngine."""
    return GameEngine(game_config=default_config)


# TODO: extra tests


# ---------- GameEngine: Code Validation Tests ----------


def test_game_engine_assert_code_legal_valid_code(engine):
    """A valid list of color integers raises no exception."""
    valid_code_list = [1, 2, 3, 4, 5]
    try:
        engine._assert_code_legal(valid_code_list)
    except Exception as e:
        pytest.fail(f"Unexpected exception for valid code: {e}")


def test_game_engine_assert_code_legal_wrong_length(engine):
    """A list with an incorrect length raises a ValueError."""
    short_code_list = [1, 2, 3, 4]
    with pytest.raises(ValueError, match="length"):
        engine._assert_code_legal(short_code_list)


def test_game_engine_assert_code_legal_invalid_color(engine):
    """A list with an invalid integer raises a ValueError."""
    invalid_code_list = [1, 2, 99, 4, 5]  # 99 is not a valid color
    with pytest.raises(ValueError, match="invalid color"):
        engine._assert_code_legal(invalid_code_list)


def test_game_engine_assert_code_legal_rejects_non_list(engine):
    """A non-list code raises a ValueError thanks to the isinstance(list) guard."""
    with pytest.raises(ValueError, match="list"):
        engine._assert_code_legal("12345")  # str len is 5, but not a list


# ---------- GameEngine: Feedback Validation Tests ----------


def test_game_engine_assert_feedback_legal_valid_feedback(engine):
    """A valid list of feedback integers raises no exception."""
    valid_feedback_list = [8, 8, 7]  # 2 black, 1 white
    try:
        engine._assert_feedback_legal(valid_feedback_list)
    except Exception as e:
        pytest.fail(f"Unexpected exception for valid feedback: {e}")


def test_game_engine_assert_feedback_legal_count_exceeds_code_length(engine):
    """A feedback list exceeding the pin count raises a ValueError."""
    too_many_pegs = [8, 8, 8, 8, 8, 8]  # 6 pegs > 5
    with pytest.raises(ValueError, match="length"):
        engine._assert_feedback_legal(too_many_pegs)


def test_game_engine_assert_feedback_legal_invalid_peg(engine):
    """A feedback list containing numbers other than 7 or 8 raises a ValueError."""
    bad_peg = [8, 1, 7]  # 1 is not a valid peg
    with pytest.raises(ValueError, match="7 \\(white peg\\) or 8 \\(black peg\\)"):
        engine._assert_feedback_legal(bad_peg)


def test_game_engine_assert_feedback_legal_rejects_non_list(engine):
    """A non-list feedback raises a ValueError thanks to the isinstance(list) guard
    (no crashing later at .count()).
    """
    with pytest.raises(ValueError, match="list"):
        engine._assert_feedback_legal({8: 1})


# ---------- GameEngine: Core Loop Tests ----------


def test_game_engine_run_player_wins_first_round(engine):
    """Test the core game loop for a first-round win."""
    # Arrange
    codemaker_mock = MagicMock()
    codebreaker_mock = MagicMock()

    secret_code_list = [1, 2, 3, 4, 5]
    guess_list = [1, 2, 3, 4, 5]
    winning_feedback_pegs = [8, 8, 8, 8, 8]

    codemaker_mock.get_secret_code.return_value = secret_code_list
    codebreaker_mock.get_guess.return_value = guess_list
    codemaker_mock.get_feedback.return_value = winning_feedback_pegs

    # Act
    game = engine.run(codemaker=codemaker_mock, codebreaker=codebreaker_mock)

    # Assert
    codemaker_mock.get_secret_code.assert_called_once()
    codebreaker_mock.get_guess.assert_called_once()
    codemaker_mock.get_feedback.assert_called_once()

    assert game is not None
    assert game.game_state == Gamestate.WON


def test_game_engine_raises_on_illegal_secret_code(engine):
    """A illegal secret code from the Codemaker propagates and stops run()."""
    codemaker_mock, codebreaker_mock = MagicMock(), MagicMock()
    codemaker_mock.get_secret_code.return_value = [1, 2, 3]  # too short
    with pytest.raises(ValueError):
        engine.run(codemaker=codemaker_mock, codebreaker=codebreaker_mock)


def test_game_engine_raises_on_illegal_guess(engine):
    """A illegal guess from the Codebreaker propagates and stops run()."""
    codemaker_mock, codebreaker_mock = MagicMock(), MagicMock()
    codemaker_mock.get_secret_code.return_value = [1, 2, 3, 4, 5]
    codebreaker_mock.get_guess.return_value = [1, 2, 3]  # too short
    with pytest.raises(ValueError):
        engine.run(codemaker=codemaker_mock, codebreaker=codebreaker_mock)
