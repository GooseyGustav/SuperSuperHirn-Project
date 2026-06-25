from app.game_model.player_attempts.feedback import Feedback
from app.game_model.player_attempts.feedback_status import FeedbackStatus


class TestFeedbackInit:
    def test_stores_black_pins(self):
        fb = Feedback(3, 1)
        assert fb.black_pins == 3

    def test_stores_white_pins(self):
        fb = Feedback(3, 1)
        assert fb.white_pins == 1

    def test_default_status_is_final(self):
        fb = Feedback(3, 1)
        assert fb.status == FeedbackStatus.FINAL

    def test_explicit_provisional_status_is_stored(self):
        fb = Feedback(3, 1, FeedbackStatus.PROVISIONAL)
        assert fb.status == FeedbackStatus.PROVISIONAL


class TestFeedbackGetStatus:
    def test_returns_final_when_constructed_with_final(self):
        fb = Feedback(5, 0, FeedbackStatus.FINAL)
        assert fb.get_status() == FeedbackStatus.FINAL

    def test_returns_provisional_when_constructed_with_provisional(self):
        fb = Feedback(0, 0, FeedbackStatus.PROVISIONAL)
        assert fb.get_status() == FeedbackStatus.PROVISIONAL
