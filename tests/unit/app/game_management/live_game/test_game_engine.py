from unittest.mock import MagicMock

import pytest

from app.game_management.game_config_management.code_constants import CodeConstants
from app.game_management.game_config_management.config import Config
from app.game_management.live_game.clock import Clock
from app.game_management.live_game.game_engine import GameEngine
from app.game_model.game_mode import Gamemode
from app.game_model.game_state import Gamestate
from app.ports.driven.for_getting_moves.errors import TimeoutInterrupt


class FakeNow:
    """Controllable time source for testing. Advances time without real sleeps."""

    def __init__(self, t: float = 0.0):
        self.t = t

    def __call__(self) -> float:
        return self.t

    def advance(self, millis: float) -> None:
        self.t += millis / 1000


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


# ---------- GameEngine: Time-Trial Tests ----------


@pytest.fixture
def fake_now():
    return FakeNow()


@pytest.fixture
def time_trial_config():
    """Config with TIME_TRIAL gamemode and a 5-second budget."""
    return Config(
        gamemode=Gamemode.TIME_TRIAL,
        user_role=MagicMock(),
        network_enabled=False,
        number_of_positions=CodeConstants.NUMBER_OF_PINS,
        number_of_colors=CodeConstants.NUMBER_OF_COLORS,
        countdown_millis=5000,
        delay_millis=0,
    )


@pytest.fixture
def time_trial_engine(time_trial_config, fake_now):
    """GameEngine in TIME_TRIAL mode with an injectable fake clock."""
    engine = GameEngine(game_config=time_trial_config)
    engine.clock = Clock(time_trial_config.countdown_millis, now=fake_now)
    return engine


def test_game_engine_timeout_interrupt_sets_lost_timeout(time_trial_engine):
    """TimeoutInterrupt raised by the codebreaker adapter leads to LOST_TIMEOUT."""
    # Arrange
    codemaker_mock = MagicMock()
    codebreaker_mock = MagicMock()
    codemaker_mock.get_secret_code.return_value = [1, 2, 3, 4, 5]
    codebreaker_mock.get_guess.side_effect = TimeoutInterrupt

    # Act
    game = time_trial_engine.run(codemaker=codemaker_mock, codebreaker=codebreaker_mock)

    # Assert
    assert game.game_state == Gamestate.LOST_TIMEOUT


def test_game_engine_posthoc_expiry_sets_lost_timeout(time_trial_engine, fake_now):
    """Clock expiry detected after get_guess returns leads to LOST_TIMEOUT (CPU path)."""
    # Arrange
    codemaker_mock = MagicMock()
    codebreaker_mock = MagicMock()
    codemaker_mock.get_secret_code.return_value = [1, 2, 3, 4, 5]

    def slow_guess(_):
        fake_now.advance(9999)  # advance past deadline during computation
        return [1, 2, 3, 4, 5]

    codebreaker_mock.get_guess.side_effect = slow_guess

    # Act
    game = time_trial_engine.run(codemaker=codemaker_mock, codebreaker=codebreaker_mock)

    # Assert
    assert game.game_state == Gamestate.LOST_TIMEOUT


def test_game_engine_in_time_guess_wins_normally(time_trial_engine):
    """A guess within the time limit results in a normal WON state."""
    # Arrange
    codemaker_mock = MagicMock()
    codebreaker_mock = MagicMock()
    secret = [1, 2, 3, 4, 5]
    codemaker_mock.get_secret_code.return_value = secret
    codebreaker_mock.get_guess.return_value = secret
    codemaker_mock.get_feedback.return_value = [8, 8, 8, 8, 8]

    # Act
    game = time_trial_engine.run(codemaker=codemaker_mock, codebreaker=codebreaker_mock)

    # Assert
    assert game.game_state == Gamestate.WON


def test_game_engine_clock_resets_between_moves(time_trial_engine, fake_now):
    """Clock resets each move; time from move N does not carry over into move N+1."""
    # Arrange
    codemaker_mock = MagicMock()
    codebreaker_mock = MagicMock()
    secret = [1, 2, 3, 4, 5]
    wrong_guess = [1, 2, 3, 4, 1]
    codemaker_mock.get_secret_code.return_value = secret

    call_count = 0

    def guess_side_effect(_):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            fake_now.advance(4999)  # almost expired — but reset should clear this
            return wrong_guess
        return secret

    codebreaker_mock.get_guess.side_effect = guess_side_effect
    codemaker_mock.get_feedback.side_effect = [
        [8, 8, 8, 8, 7],  # move 1: one peg wrong
        [8, 8, 8, 8, 8],  # move 2: win
    ]

    # Act
    game = time_trial_engine.run(codemaker=codemaker_mock, codebreaker=codebreaker_mock)

    # Assert: game was won, meaning move 2 was not rejected as timed out
    assert game.game_state == Gamestate.WON


def test_game_engine_resume_arms_fresh_clock(time_trial_config):
    """resume() creates a fresh Clock; saved remaining_time_millis is ignored."""
    # Arrange
    engine = GameEngine(game_config=time_trial_config)
    game_data = {
        "secret_code": [1, 2, 3, 4, 5],
        "attempt_list": [],
    }

    # Act
    engine.resume(game_data)

    # Assert
    assert engine.clock is not None
    assert not engine.clock.is_expired()
    assert engine.clock.remaining_millis() == time_trial_config.countdown_millis
