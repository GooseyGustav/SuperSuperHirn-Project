from app.game_model.player_attempts.feedback_status import FeedbackStatus


class Feedback:
    """The black/white peg scoring for one guess.

    black_pins: pegs in the correct position with the correct color.
    white_pins: pegs with the correct color but wrong position.
    status: FINAL when the full result is known; PROVISIONAL when the
            engine is hiding position information (blind-trial mode).
    """

    def __init__(self, black_pins: int, white_pins: int, status: FeedbackStatus = FeedbackStatus.FINAL) -> None:
        self.black_pins = black_pins
        self.white_pins = white_pins
        self.status = status

    def get_status(self) -> FeedbackStatus:
        """Return whether this feedback is final or provisional."""
        return self.status
