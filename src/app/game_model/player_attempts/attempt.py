from app.game_model.player_attempts.feedback import Feedback
from app.game_model.player_attempts.guess import Guess


class Attempt:
    """One board row: a guess paired with the feedback it received.

    An Attempt is created with both a Guess and its Feedback. The engine
    may later overwrite the feedback (e.g. when revealing a blind-trial
    result) via set_feedback().
    """

    def __init__(self, guess: Guess, feedback: Feedback | None = None) -> None:
        self.guess = guess
        self.feedback = feedback

    def get_guess(self) -> Guess:
        """Return the Guess that was made in this attempt.

        Returns:
            Guess: The guess of the attempt.
        """

        return self.guess

    def get_feedback(self) -> Feedback:
        """Return the Feedback currently associated with this attempt.

        Returns:
            Feedback: The Feedback of the attempt.
        """

        return self.feedback

    def set_feedback(self, feedback: Feedback) -> None:
        """Replace the feedback, e.g. when a provisional result is finalized.

        Args:
            feedback (Feedback): New feedback that replaces the current feedback.
        """
        self.feedback = feedback
