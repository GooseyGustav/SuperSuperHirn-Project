from unittest.mock import MagicMock

import pytest

from app.game_management.game_config_management.code_constants import CodeConstants
from app.game_management.game_config_management.config import Config
from app.game_management.game_config_management.role import Role
from app.game_management.live_game.game_engine import GameEngine
from app.game_model.game import Game
from app.game_model.game_mode import Gamemode
from app.game_model.game_state import Gamestate
from app.game_model.player_attempts.feedback_status import FeedbackStatus


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


@pytest.mark.parametrize("invalid_color", [0, CodeConstants.NUMBER_OF_COLORS.value + 1])
def test_game_engine_assert_code_legal_invalid_color_values(engine, invalid_color):
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


def test_game_engine_assert_feedback_legal_empty_list(engine):
    """An empty feedback list raises no exception."""
    try:
        engine._assert_feedback_legal([])
    except Exception as e:
        pytest.fail(f"Unexpected exception for empty feedback: {e}")


@pytest.mark.parametrize("invalid_peg", [6, 9])
def test_game_engine_assert_feedback_legal_invalid_color_values(engine, invalid_peg):
    invalid_feedback_list = [8, invalid_peg, 7]
    with pytest.raises(ValueError, match="7 \\(white peg\\) or 8 \\(black peg\\)"):
        engine._assert_feedback_legal(invalid_feedback_list)


# ---------- GameEngine: run Tests ----------


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
    codemaker_mock = MagicMock()
    codebreaker_mock = MagicMock()

    codemaker_mock.get_secret_code.return_value = [1, 2, 3, 4]

    with pytest.raises(ValueError, match="length"):
        engine.run(codemaker=codemaker_mock, codebreaker=codebreaker_mock)

    codebreaker_mock.get_guess.assert_not_called()


def test_game_engine_run_player_invalid_guess(engine):
    codemaker_mock = MagicMock()
    codebreaker_mock = MagicMock()

    codemaker_mock.get_secret_code.return_value = [1, 2, 3, 4, 5]
    codebreaker_mock.get_guess.return_value = [1, 2, 3, 4]

    with pytest.raises(ValueError, match="length"):
        engine.run(codemaker=codemaker_mock, codebreaker=codebreaker_mock)

    codemaker_mock.get_feedback.assert_not_called()


def test_game_engine_run_player_invalid_feedback(engine):
    codemaker_mock = MagicMock()
    codebreaker_mock = MagicMock()

    codemaker_mock.get_secret_code.return_value = [1, 2, 3, 4, 5]
    codebreaker_mock.get_guess.return_value = [5, 4, 3, 2, 1]
    codemaker_mock.get_feedback.return_value = [8, 1, 7]

    with pytest.raises(ValueError, match="7 \\(white peg\\) or 8 \\(black peg\\)"):
        engine.run(codemaker=codemaker_mock, codebreaker=codebreaker_mock)


def test_run_after_resume_uses_existing_secret_and_previous_board(engine):
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


# ---------- GameEngine: interrupt_game Tests ----------


def test_interrupt_game_sets_shutdown_requested(engine):
    engine.interrupt_game()

    assert engine.shutdown_requested is True


# ---------- GameEngine: get_game_obj Tests ----------


def test_get_game_obj_happy_path(engine):
    codemaker_mock = MagicMock()
    codebreaker_mock = MagicMock()

    codemaker_mock.get_secret_code.return_value = [1, 2, 3, 4, 5]
    codebreaker_mock.get_guess.return_value = [1, 2, 3, 4, 5]
    codemaker_mock.get_feedback.return_value = [8, 8, 8, 8, 8]

    game = engine.run(codemaker=codemaker_mock, codebreaker=codebreaker_mock)

    assert engine.get_game_obj() is game


def test_get_game_obj_before_start_return_none(engine):
    assert engine.get_game_obj() is None


# ---------- GameEngine: board_for_codebreaker Tests ----------


def test_board_for_codebreaker_happy_path(engine):
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
    engine.game = Game(game_mode=Gamemode.CLASSIC, code_length=CodeConstants.NUMBER_OF_PINS)

    assert engine._board_for_codebreaker() == []


# ---------- GameEngine: create_game_persist_object Tests ----------


def test_create_game_persist_object_happy_path(engine, default_config):
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
    with pytest.raises(AttributeError):
        engine.create_game_persist_object()


# ---------- GameEngine: resume Tests ----------


def test_resume_happy_path(engine):
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
    game_data = {
        "secret_code": [1, 2, 3, 4],
        "attempt_list": [],
    }

    with pytest.raises(ValueError, match="length"):
        engine.resume(game_data)


def test_resume_invalid_guess_in_attempt_list(engine):
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
