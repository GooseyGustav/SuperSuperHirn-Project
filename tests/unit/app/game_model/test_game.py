import pytest

from app.game_model.color_code.color import Color
from app.game_model.game import Game
from app.game_model.game_mode import Gamemode
from app.game_model.game_state import Gamestate
from app.game_model.player_attempts.feedback_status import FeedbackStatus


@pytest.fixture
def new_game():
    return Game(Gamemode.CLASSIC, 5, Gamestate.NEW)


@pytest.fixture
def running_game():
    return Game(Gamemode.CLASSIC, 5, Gamestate.RUNNING)


@pytest.fixture
def blind_trial_game():
    return Game(Gamemode.BLIND_TRIAL, 5, Gamestate.RUNNING)


def test_game_constructor():
    game = Game(Gamemode.CLASSIC, 5, Gamestate.NEW)

    assert game.get_game_mode() == Gamemode.CLASSIC
    assert game.code_length == 5
    assert game.game_state == Gamestate.NEW
    assert game.secret_code is None
    assert game.current_attempt is None
    assert len(game.attempt_list) == 0


def test_set_secret_code_happy_path(new_game):
    new_game.set_secret_code([1, 2, 3, 4, 5])

    assert new_game.secret_code is not None
    assert len(new_game.secret_code.get_code()) == 5
    assert [slot.get_color() for slot in new_game.secret_code.get_code()] == [
        Color.RED,
        Color.GREEN,
        Color.YELLOW,
        Color.BLUE,
        Color.ORANGE,
    ]


def test_set_secret_code_allows_interrupted_game():
    game = Game(Gamemode.CLASSIC, 5, Gamestate.INTERRUPTED)

    game.set_secret_code([1, 2, 3, 4, 5])

    assert game.secret_code is not None


def test_set_secret_code_wrong_code_type(new_game):
    with pytest.raises(TypeError):
        new_game.set_secret_code("12345")


def test_set_secret_code_wrong_type_in_code(new_game):
    with pytest.raises(TypeError):
        new_game.set_secret_code([1, 2, "3", 4, 5])


def test_set_secret_code_wrong_code_length(new_game):
    with pytest.raises(ValueError):
        new_game.set_secret_code([1, 2, 3, 4])


def test_set_secret_code_wrong_color_coding(new_game):
    with pytest.raises(ValueError):
        new_game.set_secret_code([1, 2, 3, 4, 9])


def test_set_secret_code_wrong_game_state(running_game):
    with pytest.raises(RuntimeError):
        running_game.set_secret_code([1, 2, 3, 4, 5])


def test_set_guess_happy_path(running_game):
    running_game.set_guess([1, 2, 3, 4, 5])

    assert running_game.current_attempt is not None
    assert len(running_game.attempt_list) == 0

    guess_code = running_game.current_attempt.get_guess().get_code_guess()
    assert [slot.get_color() for slot in guess_code.get_code()] == [
        Color.RED,
        Color.GREEN,
        Color.YELLOW,
        Color.BLUE,
        Color.ORANGE,
    ]


def test_set_guess_wrong_game_state(new_game):
    with pytest.raises(RuntimeError):
        new_game.set_guess([1, 2, 3, 4, 5])


def test_set_guess_rejects_when_current_attempt_waits_for_feedback(running_game):
    running_game.set_guess([1, 2, 3, 4, 5])

    with pytest.raises(RuntimeError):
        running_game.set_guess([1, 2, 3, 4, 5])


def test_set_guess_rejects_when_no_attempts_remaining(running_game):
    running_game.attempt_list = [object() for _ in range(running_game.MAX_ATTEMPTS)]

    with pytest.raises(RuntimeError):
        running_game.set_guess([1, 2, 3, 4, 5])


def test_set_guess_wrong_guess_type(running_game):
    with pytest.raises(TypeError):
        running_game.set_guess("12345")


def test_set_guess_wrong_type_in_guess(running_game):
    with pytest.raises(TypeError):
        running_game.set_guess([1, 2, "3", 4, 5])


def test_set_guess_wrong_guess_length(running_game):
    with pytest.raises(ValueError):
        running_game.set_guess([1, 2, 3, 4])


def test_set_guess_wrong_color_coding(running_game):
    with pytest.raises(ValueError):
        running_game.set_guess([1, 2, 3, 4, 9])


def test_set_feedback_happy_path(running_game):
    running_game.set_guess([1, 2, 3, 4, 5])

    running_game.set_feedback([2, 1])

    assert running_game.current_attempt is None
    assert len(running_game.attempt_list) == 1

    feedback = running_game.attempt_list[0].get_feedback()
    assert feedback.black_pins == 2
    assert feedback.white_pins == 1
    assert feedback.status == FeedbackStatus.FINAL


def test_set_feedback_rejects_without_current_attempt(running_game):
    with pytest.raises(RuntimeError):
        running_game.set_feedback([2, 1])


def test_set_feedback_wrong_feedback_type(running_game):
    running_game.set_guess([1, 2, 3, 4, 5])

    with pytest.raises(TypeError):
        running_game.set_feedback("2,1")


def test_set_feedback_wrong_list_length(running_game):
    running_game.set_guess([1, 2, 3, 4, 5])

    with pytest.raises(ValueError):
        running_game.set_feedback([2])


def test_set_feedback_wrong_type_pins(running_game):
    running_game.set_guess([1, 2, 3, 4, 5])

    with pytest.raises(TypeError):
        running_game.set_feedback([2, "1"])


def test_set_feedback_rejects_negative_pins(running_game):
    running_game.set_guess([1, 2, 3, 4, 5])

    with pytest.raises(ValueError):
        running_game.set_feedback([-1, 2])


def test_set_feedback_rejects_pin_sum_greater_than_code_length(running_game):
    running_game.set_guess([1, 2, 3, 4, 5])

    with pytest.raises(ValueError):
        running_game.set_feedback([3, 3])


def test_set_feedback_status_is_final_in_classic_mode(running_game):
    running_game.set_guess([1, 2, 3, 4, 5])

    running_game.set_feedback([2, 1])

    assert running_game.attempt_list[0].get_feedback().status == FeedbackStatus.FINAL


def test_set_feedback_status_is_final_in_time_trial_mode():
    game = Game(Gamemode.TIME_TRIAL, 5, Gamestate.RUNNING)
    game.set_guess([1, 2, 3, 4, 5])

    game.set_feedback([2, 1])

    assert game.attempt_list[0].get_feedback().status == FeedbackStatus.FINAL


def test_set_feedback_status_is_provisional_in_blind_trial_mode(blind_trial_game):
    blind_trial_game.set_guess([1, 2, 3, 4, 5])

    blind_trial_game.set_feedback([2, 1])

    assert blind_trial_game.attempt_list[0].get_feedback().status == FeedbackStatus.PROVISIONAL


def test_set_feedback_converts_previous_blind_trial_feedback_to_final(blind_trial_game):
    blind_trial_game.set_guess([1, 2, 3, 4, 5])
    blind_trial_game.set_feedback([2, 1])

    blind_trial_game.set_guess([5, 4, 3, 2, 1])
    blind_trial_game.set_feedback([1, 2])

    assert blind_trial_game.attempt_list[0].get_feedback().status == FeedbackStatus.FINAL
    assert blind_trial_game.attempt_list[1].get_feedback().status == FeedbackStatus.PROVISIONAL


def test_convert_provision_to_final_does_nothing_without_attempts(blind_trial_game):
    blind_trial_game.convert_provision_to_final()

    assert blind_trial_game.attempt_list == []


def test_convert_provision_to_final_converts_provisional_feedback(blind_trial_game):
    blind_trial_game.set_guess([1, 2, 3, 4, 5])
    blind_trial_game.set_feedback([2, 1])

    blind_trial_game.convert_provision_to_final()

    assert blind_trial_game.attempt_list[0].get_feedback().status == FeedbackStatus.FINAL


def test_convert_provision_to_final_keeps_final_feedback_final(running_game):
    running_game.set_guess([1, 2, 3, 4, 5])
    running_game.set_feedback([2, 1])

    running_game.convert_provision_to_final()

    assert running_game.attempt_list[0].get_feedback().status == FeedbackStatus.FINAL


def test_get_game_mode_returns_current_game_mode(blind_trial_game):
    assert blind_trial_game.get_game_mode() == Gamemode.BLIND_TRIAL


def test_set_game_state_sets_valid_game_state(new_game):
    new_game.set_game_state(Gamestate.RUNNING)

    assert new_game.game_state == Gamestate.RUNNING


def test_set_game_state_rejects_invalid_game_state(new_game):
    with pytest.raises(TypeError):
        new_game.set_game_state("RUNNING")
