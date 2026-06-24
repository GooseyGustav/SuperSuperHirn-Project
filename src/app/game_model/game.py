# - **Responsibility:** the board state of a round — the secret plus the stack of attempts.
# - **Attributes PEP8:**
#     MAX_ATTEMPTS: int # fixed at 10 (not configurable)
#     CODE_LENGTH: int # = `GameEngine.gameConfig.numberOfPositions` (cotr injection
#                      # (maybe unnecessary since not checking for legality (GameEngine's job))
#     secret_code: Code # created after construction
#     attempt_list: list[Attempt]
#     game_state: Gamestate
#     game_mode: Gamemode

# - **Instantiated by:** `GameEngine`.
# If `Game` must get `CODE_LENGTH` for this round from
# `GameEngine`(`GameEngine.gameConfig.numberOfPositions`): get via Constructor injection.
# Otherwise, remove from Params and not pass into constructor.

from app.game_model.color_code.code import Code
from app.game_model.color_code.color import Color
from app.game_model.color_code.slot import Slot
from app.game_model.game_mode import Gamemode
from app.game_model.game_state import Gamestate
from app.game_model.player_attempts.attempt import Attempt


class Game:
    """Represents the board state of one game round.

    The game stores the secret code, the list of attempts, the current game state and the active game mode. The game
    does not know anything about the GUI, HTTP Communication, file persisting or solver logic.

    The GameEngie is responsible for creating and managing a game.

    The class protects the game from the following wrong inputs:
    - not more than MAX_ATTEMPS may be submitted
    - a secret code must exist before ..... -> was mit Netzwerk??? da gibt keinen secret code
    - feedback can only be added to the latest attempts
    - ... TODO : sollte das überhaupt alles in die Klassenbeschreibung
    """

    MAX_ATTEMPTS = 10  # not user-changeable (if it were: GameEngine would need to inject int in cotr)

    def __init__(
        self,
        game_mode: Gamemode,
        code_length: int,
        game_state: Gamestate = Gamestate.NEW,  # can be overridden by GameEngine
    ) -> None:
        self.game_mode = game_mode  # constructor injection
        self.CODE_LENGTH = code_length  # constructor injection
        self.game_state = game_state  # constructor injection for override, otherwise default: NEW
        self.secret_code: Code | None = None  # created after construction
        self.current_attempt: Attempt | None = None
        self.attempt_list: list[Attempt] = []  # populated by `set_guess` after construction

    def set_secret_code(self, code: list[int]) -> None:
        """Set the secret code for the game round.

        The secret code can be created by a human codemaker or cpu-codemaker.
        In a network game with a remote codemaker, this method should not be used, because the secret code is known
        only by the remote server.

        Args:
            code (list[int]): List of integers. Each integer represents one color from the color enumeration.

        Raises:
            TypeError: If `code` is not a list or contains non-integer values.
            ValueError: If `code` does not have exactly `CODE_LENGTH` entries.
            ValueError: If at least one integer value in `code` is not part of the color enumeration.
            RuntimeError: If the current `game_state` does not allow setting a secret code.
        """

        if self.game_state not in (Gamestate.NEW, Gamestate.INTERRUPTED):
            raise RuntimeError(
                "Secret code can only be set when the game state is NEW or an INTERRUPTED games is resumed."
            )

        if not isinstance(code, list):
            raise TypeError("Secret code must be provided as a list of integers.")

        if not all(isinstance(color, int) for color in code):
            raise TypeError("Secret code must contain only integer values.")

        if len(code) != self.CODE_LENGTH:
            raise ValueError(f"Secret code must contain exactly {self.CODE_LENGTH} colors.")

        valid_color_values = [color.value for color in Color]
        if not all(color in valid_color_values for color in code):
            raise ValueError("Secret code contains values outside the color enumeration.")

        slots = [Slot(color) for color in code]
        self.secret_code = Code((self.CODE_LENGTH, slots))

    def set_guess(self, guess: list[int]) -> None:
        """Add a new guess as the next attempt.

        The guess is stored as `current_attempt` until feedback is added with `set_feedback()`. After feedback is set,
        the completed attempt is moved to `attempt_list`.

        Args:
            guess (list[int]): List of integers. Each integer represents one color from the color enumeration.

        Raises:
            TypeError: If `code` is not a list or contains non-integer values.
            ValueError: If `code` does not have exactly `CODE_LENGTH` entries.
            ValueError: If at least one integer value in `code` is not part of the color enumeration.
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

        if not isinstance(guess, list):
            raise TypeError("Guess must be provided as a list of integers.")

        if not all(isinstance(color, int) for color in guess):
            raise TypeError("Guess must contain only integer values.")

        if len(guess) != self.CODE_LENGTH:
            raise ValueError(f"Guess must contain exactly {self.CODE_LENGTH} colors.")

        valid_color_values = [color.value for color in Color]
        if not all(color in valid_color_values for color in guess):
            raise ValueError("Guess contains values outside the color enumeration.")

        slots = [Slot(color) for color in guess]
        guess_code = Code((self.CODE_LENGTH, slots))

        self.current_attempt = Attempt(guess_code)

    def set_feedback(self, feedback: list[int]) -> None:
        """Add feedback for the current attempts.

        A current attempt exists after the Codebreaker has submitted a guess, but
        before feedback has been added. After feedback is set, the attempt is moved
        to `attempt_list` and `current_attempt` is reset to None.
        """

        if self.current_attempt is None:
            raise RuntimeError("Cannot set feedback without a current attempt.")

        self.current_attempt.set_feedback(feedback)
        self.attempt_list.append(self.current_attempt)
        self.current_attempt = None

    def convert_provision_to_final(self) -> None: ...

    def get_game_mode(self) -> Gamemode:
        """returns the current game_mode of the round.

        Returns:
            Gamemode: current game mode
        """

    # TODO: eine set_game_state-Methode
    # TODO: Hilfsfunktion, die einen Code überprüft (is list?, alles Integer?, correkte Farbwerte?, richtige Länge?, )
