from app.game_model.color_code.code import Code
from app.game_model.color_code.color import Color
from app.game_model.color_code.slot import Slot
from app.game_model.player_attempts.attempt import Attempt
from app.game_model.player_attempts.feedback import Feedback
from app.game_model.player_attempts.feedback_status import FeedbackStatus
from app.game_model.player_attempts.guess import Guess


def make_guess(*color_ids: int) -> Guess:
    slots = [Slot(Color(c)) for c in color_ids]
    return Guess(Code((len(slots), slots)))


def make_feedback(black: int, white: int, status: FeedbackStatus = FeedbackStatus.FINAL) -> Feedback:
    return Feedback(black, white, status)


class TestAttemptGetGuess:
    def test_returns_the_guess_passed_at_construction(self):
        guess = make_guess(1, 2, 3, 4, 5)
        attempt = Attempt(guess, make_feedback(3, 1))
        assert attempt.get_guess() is guess


class TestAttemptGetFeedback:
    def test_returns_the_feedback_passed_at_construction(self):
        fb = make_feedback(3, 1)
        attempt = Attempt(make_guess(1, 2, 3, 4, 5), fb)
        assert attempt.get_feedback() is fb


class TestAttemptSetFeedback:
    def test_set_feedback_replaces_existing_feedback(self):
        attempt = Attempt(make_guess(1, 2, 3, 4, 5), make_feedback(2, 1))
        new_fb = make_feedback(5, 0)
        attempt.set_feedback(new_fb)
        assert attempt.get_feedback() is new_fb

    def test_set_feedback_provisional_to_final(self):
        provisional = make_feedback(2, 2, FeedbackStatus.PROVISIONAL)
        attempt = Attempt(make_guess(1, 2, 3, 4, 5), provisional)

        final = make_feedback(2, 2, FeedbackStatus.FINAL)
        attempt.set_feedback(final)

        assert attempt.get_feedback().get_status() == FeedbackStatus.FINAL
