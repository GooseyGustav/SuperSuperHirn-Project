from app.game_model.color_code.code import Code
from app.game_model.color_code.color import Color
from app.game_model.color_code.slot import Slot
from app.game_model.game_mode import Gamemode
from app.game_model.game_state import Gamestate
from app.game_model.player_attempts.attempt import Attempt
from app.game_model.player_attempts.feedback import Feedback
from app.game_model.player_attempts.feedback_status import FeedbackStatus


class Game:
    """Represents the board state of one game round.

    The game stores the secret code, the list of attempts, the current game state and the active game mode. The game
    does not know anything about the GUI, HTTP Communication, file persisting or solver logic.

    The GameEngine is responsible for creating and managing a game.
    """

    MAX_ATTEMPTS = 10
    VALID_COLOR_VALUES = frozenset(color.value for color in Color)

    def __init__(
        self,
        game_mode: Gamemode,
        code_length: int,
        game_state: Gamestate = Gamestate.NEW,
    ) -> None:
        self.game_mode = game_mode
        self.code_length = code_length
        self.game_state = game_state
        self.secret_code: Code | None = None
        self.current_attempt: Attempt | None = None
        self.attempt_list: list[Attempt] = []

    def set_secret_code(self, code: list[int]) -> None:
        """Set the secret code for the game round.

        The secret code can be created by a human codemaker or cpu-codemaker.
        In a network game with a remote codemaker, this method should not be used, because the secret code is known
        only by the remote server.

        Args:
            code (list[int]): List of integers. Each integer represents one color from the color enumeration.

        Raises:
            TypeError: If `code` is not a list or contains non-integer values.
            ValueError: If `code` does not have exactly `code_length` entries.
            ValueError: If at least one integer value in `code` is not part of the color enumeration.
            RuntimeError: If the current `game_state` does not allow setting a secret code.
        """

        if self.game_state not in (Gamestate.NEW, Gamestate.INTERRUPTED):
            raise RuntimeError(
                "Secret code can only be set when the game state is NEW or an INTERRUPTED game is resumed."
            )

        self._validate_code(code, "Secret code")

        slots = [Slot(color) for color in code]
        self.secret_code = Code((self.code_length, slots))

    def set_guess(self, guess: list[int]) -> None:
        """Add a new guess as the next attempt.

        The guess is stored as `current_attempt` until feedback is added with `set_feedback()`. After feedback is set,
        the completed attempt is moved to `attempt_list`.

        Args:
            guess (list[int]): List of integers. Each integer represents one color from the color enumeration.

        Raises:
            TypeError: If `guess` is not a list or contains non-integer values.
            ValueError: If `guess` does not have exactly `code_length` entries.
            ValueError: If at least one integer value in `guess` is not part of the color enumeration.
            RuntimeError: If the current `game_state` is not RUNNING.
            RuntimeError: If no attempts remain.
            RuntimeError: If another attempt is already waiting for feedback.
        """
        if self.game_state != Gamestate.RUNNING:
            raise RuntimeError("A guess can only be set while the game is running.")

        if len(self.attempt_list) >= self.MAX_ATTEMPTS:
            raise RuntimeError("No attempts remaining.")

        if self.current_attempt is not None:
            raise RuntimeError("The current attempt is still waiting for feedback.")

        self._validate_code(guess, "Guess")

        slots = [Slot(color) for color in guess]
        guess_code = Code((self.code_length, slots))

        self.current_attempt = Attempt(guess_code)

    def set_feedback(self, feedback: list[int]) -> None:
        """Add feedback for the current attempts.

        A current attempt exists after the Codebreaker has submitted a guess, but
        before feedback has been added. After feedback is set, the attempt is moved
        to `attempt_list` and `current_attempt` is reset to None.

        Args:
            feedback (list[int]): feedback as a list of integers
        """

        if self.current_attempt is None:
            raise RuntimeError("Cannot set feedback without a current attempt.")

        self._validate_feedback(feedback)

        status = FeedbackStatus.PROVISIONAL if self.game_mode == Gamemode.BLIND_TRIAL else FeedbackStatus.FINAL

        feedback_obj = Feedback(feedback[0], feedback[1], status)
        self.current_attempt.set_feedback(feedback_obj)
        self.attempt_list.append(self.current_attempt)
        self.current_attempt = None

    def convert_provision_to_final(self) -> None:
        """Convert provisional feedback to final feedback.

        This is relevant for Blind Trial mode.
        """
        # TODO

    def get_game_mode(self) -> Gamemode:
        """returns the current game_mode of the round.

        Returns:
            Gamemode: current game mode
        """
        return self.game_mode

    def set_game_state(self, game_state: Gamestate) -> None:
        """Set the current game state of the round.

        Gets used by the GameManager to set the game state (For example, to interrupt a game).

        Args:
            game_state (Gamestate): the gamestate of the round.

        Raises:
            TypeError: If `game_state` is not a gamestate.
        """
        if not isinstance(game_state, Gamestate):
            raise TypeError("Game state must be a Gamestate.")

        self.game_state = game_state

    def _validate_code(self, code: list[int], code_name: str) -> None:
        """Helper function to validate codes as lists of integers."""
        if not isinstance(code, list):
            raise TypeError(f"{code_name} must be provided as a list of integers.")

        for color in code:
            if not isinstance(color, int):
                raise TypeError(f"{code_name} must contain only integer values.")

        if len(code) != self.code_length:
            raise ValueError(f"{code_name} must contain exactly {self.code_length} colors.")

        valid_color_values = self.VALID_COLOR_VALUES
        for color in code:
            if color not in valid_color_values:
                raise ValueError(f"{code_name} contains values outside the color enumeration.")

    def _validate_feedback(self, feedback: list[int]) -> None:
        """Helper function to validate a feedback as list of integers"""
        if not isinstance(feedback, list):
            raise TypeError("Feedback must be provided as a list of integers.")

        if len(feedback) != 2:
            raise ValueError("Feedback must contain black and white pins.")

        black_pins, white_pins = feedback

        if not isinstance(black_pins, int) or not isinstance(white_pins, int):
            raise TypeError("Feedback must contain only integer values.")

        if black_pins < 0 or white_pins < 0:
            raise ValueError("Feedback pins cannot be negative.")

        if black_pins + white_pins > self.code_length:
            raise ValueError("Feedback pins cannot exceed the code length.")
