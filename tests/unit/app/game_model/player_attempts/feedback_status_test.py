from app.game_model.player_attempts.feedback_status import FeedbackStatus


class TestFeedbackStatus:
    def test_final_value_exists(self):
        assert FeedbackStatus.FINAL is not None

    def test_provisional_value_exists(self):
        assert FeedbackStatus.PROVISIONAL is not None

    def test_final_and_provisional_are_distinct(self):
        assert FeedbackStatus.FINAL != FeedbackStatus.PROVISIONAL
