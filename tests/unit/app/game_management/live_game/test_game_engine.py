from unittest.mock import MagicMock

import pytest

from app.game_management.game_config_management.code_constants import CodeConstants
from app.game_management.game_config_management.config import Config
from app.game_management.game_config_management.role import Role
from app.game_management.live_game.clock import Clock
from app.game_management.live_game.game_engine import GameEngine
from app.game_model.game import Game
from app.game_model.game_mode import Gamemode
from app.game_model.game_state import Gamestate
from app.game_model.player_attempts.feedback_status import FeedbackStatus
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
    """Creates a valid Config instance."""
    return Config(
        gamemode=Gamemode.CLASSIC,
        user_role=Role.CODEBREAKER,
        network_enabled=False,
        number_of_positions=CodeConstants.NUMBER_OF_PINS.value,
        number_of_colors=CodeConstants.NUMBER_OF_COLORS.value,
        countdown_millis=0,
        delay_millis=0,
    )


@pytest.fixture
def engine(default_config):
    """Instantiates the GameEngine."""
    return GameEngine(game_config=default_config)


# ---------- GameEngine: Constructor Tests ----------


def test_game_engine_constructor_initializes_state():
    """The constructor stores the config and starts without shutdown flag or game."""
    config = Config(
        gamemode=Gamemode.CLASSIC,
        user_role=Role.CODEBREAKER,
        network_enabled=False,
        number_of_positions=CodeConstants.NUMBER_OF_PINS.value,
        number_of_colors=CodeConstants.NUMBER_OF_COLORS.value,
        countdown_millis=0,
        delay_millis=0,
    )

    engine = GameEngine(game_config=config)

    assert engine.game_config is config
    assert engine.shutdown_requested is False
    assert engine.game is None


# ---------- GameEngine: Code Validation Tests ----------


def test_game_engine_assert_code_legal_valid_code(engine):
    """A valid list of color integers raises no exception."""
    valid_code_list = [1, 2, 3, 4, 5]
    try:
        engine._assert_code_legal(valid_code_list)
    except Exception as e:
        pytest.fail(f"Unexpected exception for valid code: {e}")


def test_game_engine_assert_code_legal_invalid_length(engine):
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


def test_game_engine_assert_code_rejects_non_int_element_double(engine):
    """A non-int element raises a ValueError thanks to the isinstance(int) guard."""
    with pytest.raises(ValueError, match="integers"):
        engine._assert_code_legal([1, 2, 3, 4, 5.5])


def test_game_engine_assert_code_rejects_non_int_element_char(engine):
    """A non-int element raises a ValueError thanks to the isinstance(int) guard."""
    with pytest.raises(ValueError, match="integers"):
        engine._assert_code_legal(["1, 2, 3, 4, 5"])


def test_game_engine_assert_code_rejects_non_int_element_bool(engine):
    """A non-int element (bool, which could be recognized as int 1) raises a
    ValueError thanks to the isinstance(int) guard."""
    with pytest.raises(ValueError, match="integers"):
        engine._assert_code_legal([True, True, True, True, True])


@pytest.mark.parametrize("invalid_color", [0, CodeConstants.NUMBER_OF_COLORS.value + 1])
def test_game_engine_assert_code_legal_invalid_color_values(engine, invalid_color):
    """Color values just outside the valid range raise a ValueError."""
    invalid_code_list = [1, 2, invalid_color, 4, 5]
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


def test_game_engine_assert_feedback_legal_rejects_non_list(engine):
    """A non-list feedback raises a ValueError thanks to the isinstance(list) guard
    (no crashing later at .count()).
    """
    with pytest.raises(ValueError, match="list"):
        engine._assert_feedback_legal({8: 1})


def test_game_engine_assert_feedback_rejects_non_int_element_double(engine):
    """A non-int element (double) raises a ValueError thanks to the isinstance(int) guard."""
    with pytest.raises(ValueError, match="integers"):
        engine._assert_feedback_legal([7.5])


def test_game_engine_assert_feedback_rejects_non_int_element_str(engine):
    """A non-int element (str) raises a ValueError thanks to the isinstance(int) guard."""
    with pytest.raises(ValueError, match="integers"):
        engine._assert_feedback_legal(["white"])


def test_game_engine_assert_feedback_rejects_non_int_element_bool(engine):
    """A non-int element (bool, which could be recognized as int 1) raises a
    ValueError thanks to the isinstance(int) guard."""
    with pytest.raises(ValueError, match="integers"):
        engine._assert_feedback_legal([True, True, True, True, True])


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
    assert game.secret_code is not None
    assert game.current_attempt is None
    assert len(game.attempt_list) == 1
    assert game.attempt_list[0].get_feedback().black_pins == 5
    assert game.attempt_list[0].get_feedback().white_pins == 0


def test_game_engine_run_player_loses_from_attempts(engine):
    """The game is lost when the maximum number of attempts is reached."""
    codemaker_mock = MagicMock()
    codebreaker_mock = MagicMock()

    codemaker_mock.get_secret_code.return_value = [1, 2, 3, 4, 5]
    codebreaker_mock.get_guess.return_value = [5, 4, 3, 2, 1]
    codemaker_mock.get_feedback.return_value = []

    game = engine.run(codemaker=codemaker_mock, codebreaker=codebreaker_mock)

    assert game.game_state == Gamestate.LOST_ATTEMPTS
    assert len(game.attempt_list) == Game.MAX_ATTEMPTS
    assert codebreaker_mock.get_guess.call_count == Game.MAX_ATTEMPTS
    assert codemaker_mock.get_feedback.call_count == Game.MAX_ATTEMPTS


def test_game_engine_run_player_invalid_secret_code(engine):
    """An invalid secret code aborts the run before asking for a guess."""
    codemaker_mock = MagicMock()
    codebreaker_mock = MagicMock()

    codemaker_mock.get_secret_code.return_value = [1, 2, 3, 4]

    with pytest.raises(ValueError, match="length"):
        engine.run(codemaker=codemaker_mock, codebreaker=codebreaker_mock)

    codebreaker_mock.get_guess.assert_not_called()


def test_game_engine_run_player_invalid_guess(engine):
    """An invalid guess aborts the run before feedback is requested."""
    codemaker_mock = MagicMock()
    codebreaker_mock = MagicMock()

    codemaker_mock.get_secret_code.return_value = [1, 2, 3, 4, 5]
    codebreaker_mock.get_guess.return_value = [1, 2, 3, 4]

    with pytest.raises(ValueError, match="length"):
        engine.run(codemaker=codemaker_mock, codebreaker=codebreaker_mock)

    codemaker_mock.get_feedback.assert_not_called()


def test_game_engine_run_player_invalid_feedback(engine):
    """Invalid feedback from the codemaker aborts the run with a ValueError."""
    codemaker_mock = MagicMock()
    codebreaker_mock = MagicMock()

    codemaker_mock.get_secret_code.return_value = [1, 2, 3, 4, 5]
    codebreaker_mock.get_guess.return_value = [5, 4, 3, 2, 1]
    codemaker_mock.get_feedback.return_value = [8, 1, 7]

    with pytest.raises(ValueError, match="7 \\(white peg\\) or 8 \\(black peg\\)"):
        engine.run(codemaker=codemaker_mock, codebreaker=codebreaker_mock)


def test_run_after_resume_uses_existing_secret_and_previous_board(engine):
    """A resumed game reuses its secret and passes previous attempts as board."""
    game_data = {
        "secret_code": [1, 2, 3, 4, 5],
        "attempt_list": [
            {
                "guess": [5, 4, 3, 2, 1],
                "feedback": {
                    "black_pins": 1,
                    "white_pins": 2,
                    "status": FeedbackStatus.FINAL.value,
                },
            }
        ],
    }
    codemaker_mock = MagicMock()
    codebreaker_mock = MagicMock()

    engine.resume(game_data)
    codebreaker_mock.get_guess.return_value = [1, 2, 3, 4, 5]
    codemaker_mock.get_feedback.return_value = [8, 8, 8, 8, 8]

    game = engine.run(codemaker=codemaker_mock, codebreaker=codebreaker_mock)

    codemaker_mock.get_secret_code.assert_not_called()
    codebreaker_mock.get_guess.assert_called_once_with([([5, 4, 3, 2, 1], [8, 7, 7], FeedbackStatus.FINAL.value)])
    codemaker_mock.get_feedback.assert_called_once_with([1, 2, 3, 4, 5], [1, 2, 3, 4, 5])
    assert game.game_state == Gamestate.WON
    assert len(game.attempt_list) == 2


def test_run_sets_game_state_interrupted_when_interrupt_requested(engine):
    """An interrupt requested during the loop marks the game as interrupted."""
    codemaker_mock = MagicMock()
    codebreaker_mock = MagicMock()

    codemaker_mock.get_secret_code.return_value = [1, 2, 3, 4, 5]
    codebreaker_mock.get_guess.return_value = [5, 4, 3, 2, 1]

    def feedback_and_interrupt(*_args):
        engine.interrupt_game()
        return [8, 7]

    codemaker_mock.get_feedback.side_effect = feedback_and_interrupt

    game = engine.run(codemaker=codemaker_mock, codebreaker=codebreaker_mock)

    assert game.game_state == Gamestate.INTERRUPTED
    assert len(game.attempt_list) == 1


def test_run_network_game_does_not_store_secret_code(default_config):
    """Network games validate but do not store the secret code locally."""
    default_config.network_enabled = True
    engine = GameEngine(game_config=default_config)
    codemaker_mock = MagicMock()
    codebreaker_mock = MagicMock()

    codemaker_mock.get_secret_code.return_value = [1, 2, 3, 4, 5]
    codebreaker_mock.get_guess.return_value = [1, 2, 3, 4, 5]
    codemaker_mock.get_feedback.return_value = [8, 8, 8, 8, 8]

    game = engine.run(codemaker=codemaker_mock, codebreaker=codebreaker_mock)

    assert game.game_state == Gamestate.WON
    assert game.secret_code is None


def test_run_win_converts_provisional_feedback_to_final_feedback(default_config):
    """A Blind Trial win converts all provisional feedback to final feedback."""
    default_config.gamemode = Gamemode.BLIND_TRIAL
    engine = GameEngine(game_config=default_config)
    codemaker_mock = MagicMock()
    codebreaker_mock = MagicMock()

    codemaker_mock.get_secret_code.return_value = [1, 2, 3, 4, 5]
    codebreaker_mock.get_guess.side_effect = [[5, 4, 3, 2, 1], [1, 2, 3, 4, 5]]
    codemaker_mock.get_feedback.side_effect = [[8, 7], [8, 8, 8, 8, 8]]

    game = engine.run(codemaker=codemaker_mock, codebreaker=codebreaker_mock)

    assert game.game_state == Gamestate.WON
    assert [attempt.get_feedback().get_status() for attempt in game.attempt_list] == [
        FeedbackStatus.FINAL,
        FeedbackStatus.FINAL,
    ]


def test_run_lost_to_attempts_converts_provisional_feedback_to_final_feedback(default_config):
    """A Blind Trial attempt loss converts all provisional feedback to final feedback."""
    default_config.gamemode = Gamemode.BLIND_TRIAL
    engine = GameEngine(game_config=default_config)
    codemaker_mock = MagicMock()
    codebreaker_mock = MagicMock()

    codemaker_mock.get_secret_code.return_value = [1, 2, 3, 4, 5]
    codebreaker_mock.get_guess.return_value = [5, 4, 3, 2, 1]
    codemaker_mock.get_feedback.return_value = []

    game = engine.run(codemaker=codemaker_mock, codebreaker=codebreaker_mock)

    assert game.game_state == Gamestate.LOST_ATTEMPTS
    assert len(game.attempt_list) == Game.MAX_ATTEMPTS
    assert all(attempt.get_feedback().get_status() == FeedbackStatus.FINAL for attempt in game.attempt_list)


def test_run_empty_feedback_from_port_does_not_abort_game(engine):
    """The core accepts an empty feedback list as meaning [0, 0], a legal feedback
    with 0 black pins and 0 white pins, so the game continues (doesn't abort).
    Feedback [8,8,8,8,8] added in second call to close the run() loop."""
    codemaker_mock, codebreaker_mock = MagicMock(), MagicMock()
    codemaker_mock.get_secret_code.return_value = [1, 2, 3, 4, 5]
    codebreaker_mock.get_guess.return_value = [1, 2, 3, 4, 5]
    codemaker_mock.get_feedback.side_effect = [[], [8, 8, 8, 8, 8]]  # empty feedback (no pins), then win to end loop

    game = engine.run(codemaker=codemaker_mock, codebreaker=codebreaker_mock)

    assert codemaker_mock.get_feedback.call_count == 2
    assert len(game.attempt_list) == 2
    assert game.game_state == Gamestate.WON


def test_run_records_empty_feedback_from_port_as_zero_pins(engine):
    """The core records an empty feedback list and translates it as [0, 0],
    a legal feedback with 0 black pins and 0 white pins.
    (That translation happens in GameEngine.run() with .count() of black and
    white pins before passing those counts to the Game.)
    Feedback [8,8,8,8,8] added in second call to close the run() loop."""
    codemaker_mock, codebreaker_mock = MagicMock(), MagicMock()
    codemaker_mock.get_secret_code.return_value = [1, 2, 3, 4, 5]
    codebreaker_mock.get_guess.return_value = [1, 2, 3, 4, 5]
    codemaker_mock.get_feedback.side_effect = [[], [8, 8, 8, 8, 8]]  # empty feedback (no pins), then win to end loop

    game = engine.run(codemaker=codemaker_mock, codebreaker=codebreaker_mock)

    first_feedback = game.attempt_list[0].get_feedback()
    assert first_feedback.black_pins == 0
    assert first_feedback.white_pins == 0


# ---------- GameEngine: interrupt_game Tests ----------


def test_interrupt_game_sets_shutdown_requested(engine):
    """interrupt_game sets the shutdown flag used by the run loop."""
    engine.interrupt_game()

    assert engine.shutdown_requested is True


# ---------- GameEngine: get_game_obj Tests ----------


def test_get_game_obj_happy_path(engine):
    """get_game_obj returns the game object created by run."""
    codemaker_mock = MagicMock()
    codebreaker_mock = MagicMock()

    codemaker_mock.get_secret_code.return_value = [1, 2, 3, 4, 5]
    codebreaker_mock.get_guess.return_value = [1, 2, 3, 4, 5]
    codemaker_mock.get_feedback.return_value = [8, 8, 8, 8, 8]

    game = engine.run(codemaker=codemaker_mock, codebreaker=codebreaker_mock)

    assert engine.get_game_obj() is game


def test_get_game_obj_before_start_return_none(engine):
    """get_game_obj returns None before a game has been started or resumed."""
    assert engine.get_game_obj() is None


# ---------- GameEngine: board_for_codebreaker Tests ----------


def test_board_for_codebreaker_happy_path(engine):
    """The board for the codebreaker contains previous final guesses and feedback."""
    codemaker_mock = MagicMock()
    codebreaker_mock = MagicMock()

    codemaker_mock.get_secret_code.return_value = [1, 2, 3, 4, 5]
    codebreaker_mock.get_guess.return_value = [5, 4, 3, 2, 1]
    codemaker_mock.get_feedback.side_effect = [[8, 8, 7], [8, 8, 8, 8, 8]]

    engine.run(codemaker=codemaker_mock, codebreaker=codebreaker_mock)

    assert codebreaker_mock.get_guess.call_args_list[1].args[0] == [
        ([5, 4, 3, 2, 1], [8, 8, 7], FeedbackStatus.FINAL.value)
    ]


def test_board_for_codebreaker_provisional_as_white_pins(default_config):
    """Provisional feedback is hidden from the codebreaker as white pins only."""
    default_config.gamemode = Gamemode.BLIND_TRIAL
    engine = GameEngine(game_config=default_config)
    codemaker_mock = MagicMock()
    codebreaker_mock = MagicMock()

    codemaker_mock.get_secret_code.return_value = [1, 2, 3, 4, 5]
    codebreaker_mock.get_guess.return_value = [5, 4, 3, 2, 1]
    codemaker_mock.get_feedback.side_effect = [[8, 8, 7], [8, 8, 8, 8, 8]]

    engine.run(codemaker=codemaker_mock, codebreaker=codebreaker_mock)

    assert codebreaker_mock.get_guess.call_args_list[1].args[0] == [
        ([5, 4, 3, 2, 1], [7, 7, 7], FeedbackStatus.PROVISIONAL.value)
    ]


def test_board_for_codebreaker_empty_list(engine):
    """An empty attempt history is exposed as an empty board."""
    engine.game = Game(game_mode=Gamemode.CLASSIC, code_length=CodeConstants.NUMBER_OF_PINS)

    assert engine._board_for_codebreaker() == []


# ---------- GameEngine: create_game_persist_object Tests ----------


def test_create_game_persist_object_happy_path(engine, default_config):
    """A completed game is converted into the expected persistence shape."""
    codemaker_mock = MagicMock()
    codebreaker_mock = MagicMock()

    codemaker_mock.get_secret_code.return_value = [1, 2, 3, 4, 5]
    codebreaker_mock.get_guess.return_value = [1, 2, 3, 4, 5]
    codemaker_mock.get_feedback.return_value = [8, 8, 8, 8, 8]

    engine.run(codemaker=codemaker_mock, codebreaker=codebreaker_mock)

    persist_object = engine.create_game_persist_object()

    assert persist_object["gamemode"] == Gamemode.CLASSIC.value
    assert persist_object["gamestate"] == Gamestate.WON.value
    assert persist_object["number_of_positions"] == CodeConstants.NUMBER_OF_PINS.value
    assert persist_object["number_of_colors"] == CodeConstants.NUMBER_OF_COLORS.value
    assert persist_object["max_attempts"] == Game.MAX_ATTEMPTS
    assert persist_object["secret_code"] == [1, 2, 3, 4, 5]
    assert persist_object["attempt_list"] == [
        {
            "guess": [1, 2, 3, 4, 5],
            "feedback": {
                "black_pins": 5,
                "white_pins": 0,
                "status": FeedbackStatus.FINAL.value,
            },
        }
    ]
    assert persist_object["remaining_time_millis"] == 0
    assert persist_object["matchup"] == {
        "gamemode": default_config.gamemode.value,
        "user_role": default_config.user_role.value,
        "network_enabled": default_config.network_enabled,
        "countdown_millis": default_config.countdown_millis,
        "delay_millis": default_config.delay_millis,
    }


def test_create_game_persist_object_happy_path_multiple_attempts(engine):
    """The persistence object includes all attempts in order."""
    codemaker_mock = MagicMock()
    codebreaker_mock = MagicMock()

    codemaker_mock.get_secret_code.return_value = [1, 2, 3, 4, 5]
    codebreaker_mock.get_guess.side_effect = [[5, 4, 3, 2, 1], [1, 2, 3, 4, 5]]
    codemaker_mock.get_feedback.side_effect = [[8, 7], [8, 8, 8, 8, 8]]

    engine.run(codemaker=codemaker_mock, codebreaker=codebreaker_mock)

    persist_object = engine.create_game_persist_object()

    assert persist_object["attempt_list"] == [
        {
            "guess": [5, 4, 3, 2, 1],
            "feedback": {
                "black_pins": 1,
                "white_pins": 1,
                "status": FeedbackStatus.FINAL.value,
            },
        },
        {
            "guess": [1, 2, 3, 4, 5],
            "feedback": {
                "black_pins": 5,
                "white_pins": 0,
                "status": FeedbackStatus.FINAL.value,
            },
        },
    ]


def test_create_game_persist_object_save_provisional_feedback(default_config):
    """The persistence object preserves provisional Blind Trial feedback."""
    default_config.gamemode = Gamemode.BLIND_TRIAL
    engine = GameEngine(game_config=default_config)
    codemaker_mock = MagicMock()
    codebreaker_mock = MagicMock()

    codemaker_mock.get_secret_code.return_value = [1, 2, 3, 4, 5]
    codebreaker_mock.get_guess.return_value = [5, 4, 3, 2, 1]

    def feedback_and_interrupt(*_args):
        engine.interrupt_game()
        return [8, 7]

    codemaker_mock.get_feedback.side_effect = feedback_and_interrupt
    engine.run(codemaker=codemaker_mock, codebreaker=codebreaker_mock)

    persist_object = engine.create_game_persist_object()

    assert persist_object["gamemode"] == Gamemode.BLIND_TRIAL.value
    assert persist_object["attempt_list"] == [
        {
            "guess": [5, 4, 3, 2, 1],
            "feedback": {
                "black_pins": 1,
                "white_pins": 1,
                "status": FeedbackStatus.PROVISIONAL.value,
            },
        }
    ]


def test_create_game_persist_object_before_run_raises_error(engine):
    """Creating a persistence object before a game exists raises an AttributeError."""
    with pytest.raises(AttributeError):
        engine.create_game_persist_object()


# ---------- GameEngine: resume Tests ----------


def test_resume_happy_path(engine):
    """resume rebuilds an interrupted game with secret code and attempts."""
    game_data = {
        "secret_code": [1, 2, 3, 4, 5],
        "attempt_list": [
            {
                "guess": [5, 4, 3, 2, 1],
                "feedback": {
                    "black_pins": 1,
                    "white_pins": 2,
                    "status": FeedbackStatus.FINAL.value,
                },
            }
        ],
    }

    engine.resume(game_data)

    game = engine.get_game_obj()
    assert game is not None
    assert game.game_state == Gamestate.INTERRUPTED
    assert [slot.get_color().value for slot in game.secret_code.get_code()] == [1, 2, 3, 4, 5]
    assert len(game.attempt_list) == 1

    attempt = game.attempt_list[0]
    assert [slot.get_color().value for slot in attempt.get_guess().get_code_guess().get_code()] == [5, 4, 3, 2, 1]
    assert attempt.get_feedback().black_pins == 1
    assert attempt.get_feedback().white_pins == 2
    assert attempt.get_feedback().get_status() == FeedbackStatus.FINAL


def test_resume_invalid_secret_code(engine):
    """resume rejects persisted data with an invalid secret code."""
    game_data = {
        "secret_code": [1, 2, 3, 4],
        "attempt_list": [],
    }

    with pytest.raises(ValueError, match="length"):
        engine.resume(game_data)


def test_resume_invalid_guess_in_attempt_list(engine):
    """resume rejects persisted attempts with an invalid guess."""
    game_data = {
        "secret_code": [1, 2, 3, 4, 5],
        "attempt_list": [
            {
                "guess": [1, 2, 3, 4],
                "feedback": {
                    "black_pins": 0,
                    "white_pins": 0,
                    "status": FeedbackStatus.FINAL.value,
                },
            }
        ],
    }

    with pytest.raises(ValueError, match="length"):
        engine.resume(game_data)


def test_resume_network_game_dont_set_secret_code(default_config):
    """resume restores network games without storing the secret code locally."""
    default_config.network_enabled = True
    engine = GameEngine(game_config=default_config)
    game_data = {
        "secret_code": [1, 2, 3, 4, 5],
        "attempt_list": [
            {
                "guess": [5, 4, 3, 2, 1],
                "feedback": {
                    "black_pins": 1,
                    "white_pins": 2,
                    "status": FeedbackStatus.FINAL.value,
                },
            }
        ],
    }

    engine.resume(game_data)

    game = engine.get_game_obj()
    assert game is not None
    assert game.secret_code is None
    assert len(game.attempt_list) == 1


def test_resume_load_provisional_feedback(engine):
    """resume restores provisional feedback status from persisted data."""
    game_data = {
        "secret_code": [1, 2, 3, 4, 5],
        "attempt_list": [
            {
                "guess": [5, 4, 3, 2, 1],
                "feedback": {
                    "black_pins": 1,
                    "white_pins": 1,
                    "status": FeedbackStatus.PROVISIONAL.value,
                },
            }
        ],
    }

    engine.resume(game_data)

    feedback = engine.get_game_obj().attempt_list[0].get_feedback()
    assert feedback.black_pins == 1
    assert feedback.white_pins == 1
    assert feedback.get_status() == FeedbackStatus.PROVISIONAL


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
