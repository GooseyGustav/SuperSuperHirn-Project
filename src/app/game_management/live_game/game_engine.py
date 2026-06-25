# NOTE: GameSessionManager removed (explained below DocStrings).
# Still mentioned in big description from Class Reference just in case should be created again.
#
# From Class Reference:
#
# - **Responsibility:** runs one round's loop; pulls moves from the player ports; owns the live `Game`, `Clock`,
# `GameSessionManager`;
# **checks legality of each move (length of secret code, of guess and of feedback, colors used)
# - **Attributes:** `game: Game`, `game_session_manager: GameSessionManager`, `clock: Clock`, `game_config: Config`,
# `shutdown_requested: bool`.
# - **Methods:** `run(codemaker, codebreaker): Game`, `create_game_persist_object(): object`, `interrupt_game()`,
# **`resume(game_data: dict)`**,
# `start_clock(time_millis: int): bool` , `get_game_obj(): Game`, `assert_code_legal(code: list[int])`,
# `assert_feedback_legal(fb: list[int])`
#     - **Notes:**
#         - `run(codemaker, codebreaker): Game` // ruft die ports für moves auf ; config aus Params entfernt
#         (ist schon Attr. self.game_config);
#         check each move's legality with helpers assert_code_legal , assert_feedback_legal
#         - `create_game_persist_object(): object` // beinhaltet auch numberOfColors, remainingTimeMillis ;
#         Params entfernt da schon Attribute (self.game, self.clock. self.game_config)
#         - `interrupt_game()`
#         - `resume(game_data: dict)` // (`game_data` passed from GameManager); checks imported game data for
#         legality before starting (in case
#         corrupt file) with `assert_code_legal`
#             - `start_clock(time_millis: int): bool` // gibt true flag ("future object") zurueck wenn countdown 0 ist ;
#             (changed: no unit parameter as millis in the internals of the app)
#             + `get_game_obj(): Game -` assert_code_legal(code: list) `// priv. helper, checks secret/guess legal
#             (length, colors) -` assert_feedback_legal(fb: list)` // priv. helper,
#             checks feedback legal (length, colors)
#
# # Legality validating helpers:
#
# _assert_code_legal(code): # for secret and guess
# len(code) == self.game_config.number_of_positions
# all(1 <= c <= self.game_config.number_of_colors for c in code)
#
# _assert_feedback_legal(fb):
# len(fb) <= self.game_config.number_of_positions
# all(c in (7, 8) for c in fb)
#
# - **Constructor (injection):** `(game_config: Config)`; player ports arrive via `run(...)`.
# (Holds no persistence port — it returns the `Game`; `GameManager` persists.)
# - **Creates:** `Game`, `Clock`, `GameSessionManager`.
# - **Instantiated by:** `GameManager` (per game).


from app.game_management.game_config_management.code_constants import CodeConstants
from app.game_management.game_config_management.config import Config
from app.game_model.game import Game
from app.game_model.game_state import Gamestate


class GameEngine:
    """Docstring for GameEngine. # TODO"""

    # deleted file mentioned in docstring GameSessionManager per modification of
    # Class Reference and Diagram, following discussion with Marlon that it was
    # unnecessary because GameManagement and GameEngine seem to cover everything.
    # If necessary TODO: reinstate GameSessionManager for threading in TIME_TRIAL

    def __init__(self, game_config: Config) -> None:
        self.game_config = game_config
        self.shutdown_requested = False

    def run(self, codemaker, codebreaker) -> Game:
        """Execute the core gameplay loop.

        Queries the secret code from the codemaker, then repeatedly asks
        the codebreaker for guesses and the codemaker for feedback until
        the game is won, lost, or interrupted.

        Args:
            codemaker: The port/adapter acting as the codemaker.
            codebreaker: The port/adapter acting as the codebreaker.

        Returns:
            Game: The final game state containing the attempt history.
        """
        self.game = Game(game_mode=self.game_config.gamemode, code_length=CodeConstants.NUMBER_OF_PINS)

        secret_code_list = codemaker.get_secret_code()

        # Validate the secret code before proceeding
        self._assert_code_legal(secret_code_list)

        if not self.game_config.network_enabled:
            # Set the secret code in the game state only if network is not enabled
            self.game.set_secret_code(secret_code_list)

        self.game.game_state = Gamestate.RUNNING

        while not self.shutdown_requested:
            guess_list = codebreaker.get_guess()
            self._assert_code_legal(guess_list)
            self.game.set_guess(guess_list)

            feedback_list = codemaker.get_feedback(secret_code_list, guess_list)
            self._assert_feedback_legal(feedback_list)
            self.game.set_feedback(feedback_list)

            # Win condition: All guessed pins are completely correct (black pegs)
            if feedback_list.count(8) == CodeConstants.NUMBER_OF_PINS:
                self.game.game_state = Gamestate.WON
                break

            # Loss condition: Maximum number of attempts reached
            if len(self.game.attempt_list) >= Game.MAX_ATTEMPTS:
                self.game.game_state = Gamestate.LOST
                break

        # Defensive catch: Mark game as interrupted if loop exited via flag
        if self.shutdown_requested:
            self.game.game_state = Gamestate.INTERRUPTED

        return self.game

    # + createGamePersistObject(): Object // beinhaltet auch  numberOfColors, remainingTimeMillis ;
    # Params entfernt da schon Attribute (self.game, self.clock. self.gameConfig)
    def create_game_persist_object(self) -> dict: ...

    # braucht anderen name: namenkonflikt mit gamemanager (bedeutet dort mit speichern, hier nicht)
    def interrupt_game(self) -> None: ...

    def resume(self, game_data: dict) -> None: ...

    def start_clock(self, time_millis: int) -> bool: ...

    def get_game_obj(self) -> Game: ...

    # TODO: Was nach Error raised passiert wurde muss noch geklärt werden.
    # TODO: Brauchen evtl noch KeyError
    def _assert_code_legal(self, code: list[int]) -> None:
        """Validate the raw code list from a port that represents a secret code or guess."""
        if len(code) != CodeConstants.NUMBER_OF_PINS:
            raise ValueError(f"Invalid code length: expected {CodeConstants.NUMBER_OF_PINS} pins.")

        if not all(1 <= c <= CodeConstants.NUMBER_OF_COLORS for c in code):
            raise ValueError("Code contains invalid color integers.")

    # TODO: Was nach Error raised passiert wurde muss noch geklärt werden.
    # TODO: Brauchen evtl noch KeyError
    def _assert_feedback_legal(self, feedback: list[int]) -> None:
        """Validate the raw feedback list from a port."""
        if len(feedback) > CodeConstants.NUMBER_OF_PINS:
            raise ValueError(f"Feedback length cannot exceed {CodeConstants.NUMBER_OF_PINS} pins.")

        # 7 = white peg, 8 = black peg
        if not all(c in (7, 8) for c in feedback):
            raise ValueError("Feedback must only contain 7 (white) or 8 (black).")
