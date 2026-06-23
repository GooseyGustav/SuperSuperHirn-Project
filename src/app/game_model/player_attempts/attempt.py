# - ** Responsibility: ** one board row — a guess paired with its feedback.
# - ** Attributes PEP8: **
# guess: Guess
# feedback: Feedback

from app.game_model.player_attempts.feedback import Feedback
from app.game_model.player_attempts.guess import Guess


class Attempt:
    """Docstring for Attempt."""

    def __init__(self, guess: Guess, feedback: Feedback) -> None:
        self.guess = guess
        self.feedback = feedback

    def get_guess(self) -> Guess: ...
    def get_feedback(self) -> Feedback: ...
    def set_feedback(self, feedback: Feedback) -> None: ...
