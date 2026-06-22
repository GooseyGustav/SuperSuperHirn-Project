from app.game_model.player_attempts.feedback_status import FeedbackStatus

# **Responsibility:** the black/white scoring of one guess.
# - **Attributes PEP8:**
#     black_pins: int
#     white_pins: int
#     status: FeedbackStatus


class Feedback:
    """Docstring for Feedback."""

    def __init__(self, black_pins: int, white_pins: int, status: FeedbackStatus = FeedbackStatus.FINAL) -> None:
        self.black_pins = black_pins
        self.white_pins = white_pins
        self.status = status  # default FINAL; BLIND_TRIAL passes PROVISIONAL

    def get_status(self) -> tuple[FeedbackStatus, int, int]:
        """Docstring for get_status.
        # Tuple<FeedbackStatus, white: int, black: int>
        """
