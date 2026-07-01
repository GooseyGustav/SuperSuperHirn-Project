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
from app.game_management.live_game.clock import Clock
from app.game_model.color_code.code import Code
from app.game_model.color_code.color import Color
from app.game_model.color_code.slot import Slot
from app.game_model.game import Game
from app.game_model.game_mode import Gamemode
from app.game_model.game_state import Gamestate
from app.game_model.player_attempts.attempt import Attempt
from app.game_model.player_attempts.feedback import Feedback
from app.game_model.player_attempts.feedback_status import FeedbackStatus
from app.game_model.player_attempts.guess import Guess
from app.ports.driven.for_getting_moves.errors import TimeoutInterrupt


class GameEngine:
    """The GameEngine runs one round's loop. It pulls moves from the player ports; owns the live `Game`, `Clock`"""

    # deleted file mentioned in docstring GameSessionManager per modification of
    # Class Reference and Diagram, following discussion with Marlon that it was
    # unnecessary because GameManagement and GameEngine seem to cover everything.
    # If necessary TODO: reinstate GameSessionManager for threading in TIME_TRIAL (?)

    def __init__(self, game_config: Config) -> None:
        self.game_config = game_config
        self.shutdown_requested = False
        self.game: Game | None = None
        # Clock is only created for TIME_TRIAL; None in all other modes.
        self.clock: Clock | None = (
            Clock(game_config.countdown_millis) if game_config.gamemode == Gamemode.TIME_TRIAL else None
        )

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

        # create game if not already created through resume() (as called by GameManager)
        if self.game is None:
            self.game = Game(game_mode=self.game_config.gamemode, code_length=CodeConstants.NUMBER_OF_PINS)

        # differentiate between a new game and a resumed game
        if self.game.secret_code is None:
            secret_code_as_list = codemaker.get_secret_code()
            self._assert_code_legal(secret_code_as_list)
            if not self.game_config.network_enabled:
                # TODO: check if bad side effects if not set in Game during a network game
                self.game.set_secret_code(secret_code_as_list)
        else:  # if code exists in Game object, use it
            secret_code_as_list = [slot.get_color().value for slot in self.game.secret_code.get_code()]
            self._assert_code_legal(secret_code_as_list)

        self.game.game_state = Gamestate.RUNNING
        is_time_trial = self.game_config.gamemode == Gamemode.TIME_TRIAL

        while not self.shutdown_requested:
            # Per-move clock: reset + start immediately before get_guess.
            # get_feedback is intentionally outside the timed window.
            if is_time_trial:
                self.clock.start()

            try:
                guess_as_list = codebreaker.get_guess(self._board_for_codebreaker())
            except TimeoutInterrupt:
                # Interactive cutoff: raised by the GUI adapter when the player runs out of time.
                self.game.game_state = Gamestate.LOST_TIMEOUT
                break

            # Post-hoc cutoff: for CPU codebreakers that finish after the deadline.
            if is_time_trial and self.clock.is_expired():
                self.game.game_state = Gamestate.LOST_TIMEOUT
                break

            self._assert_code_legal(guess_as_list)
            self.game.set_guess(guess_as_list)

            feedback_pegs = codemaker.get_feedback(secret_code_as_list, guess_as_list)  # int list
            self._assert_feedback_legal(feedback_pegs)
            nr_of_black_pins = feedback_pegs.count(8)
            nr_of_white_pins = feedback_pegs.count(7)
            self.game.set_feedback([nr_of_black_pins, nr_of_white_pins])

            # Win condition: All guessed pegs are completely correct
            # VERSION FOR INT LIST
            if nr_of_black_pins == CodeConstants.NUMBER_OF_PINS:
                self.game.game_state = Gamestate.WON
                if self.game.game_mode == Gamemode.BLIND_TRIAL:
                    self.game.convert_provision_to_final()
                break

            # Loss condition: Maximum number of attempts reached
            if len(self.game.attempt_list) >= Game.MAX_ATTEMPTS:
                self.game.game_state = Gamestate.LOST_ATTEMPTS
                if self.game.game_mode == Gamemode.BLIND_TRIAL:
                    self.game.convert_provision_to_final()
                break

        # Defensive catch: Mark game as interrupted if loop exited via flag
        if self.shutdown_requested:
            self.game.game_state = Gamestate.INTERRUPTED

        return self.game

    def _board_for_codebreaker(self) -> list[tuple[list[int], list[int], str]]:
        """Convert the live attempt history into the (guess, feedback, status) rows that
        the ForGettingCodebreakerMove port declares.
            guess: list[int]  # pegs with colors guessed
            feedback: list[int]  # pegs with feedback colors (7 = white, 8 = black); order not relevant
            status:  str  # status of the attempt ("FINAL", "PROVISIONAL", set by model)

        """
        board = []
        for attempt in self.game.attempt_list:
            guess_pegs = [pin.get_color().value for pin in attempt.get_guess().get_code_guess().get_code()]
            fb = attempt.get_feedback()
            if fb.get_status() == FeedbackStatus.PROVISIONAL:
                feedback_pegs = [7] * (fb.black_pins + fb.white_pins)
            else:
                feedback_pegs = [8] * fb.black_pins + [7] * fb.white_pins
            board.append((guess_pegs, feedback_pegs, fb.get_status().value))
        return board

    def create_game_persist_object(self) -> dict:
        """Save a snapshot of the live game into the Persist dict.
        Outputs the shape defined by ForPersistingGame.save_game().

        The `matchup` sub-dict carries the config selection in effect at
        GameManager.interrupt_game() (role, network bool, gamemode, timing).
        On GameManager.resume_interrupted() the GameManager merges that config
        back over the live config so that the Matchmaker can rewire the same
        adapters, even if the user changed the config between interrupt and resume.
        The ForPersistingGame round-trips the `matchup` sub-dict as is.
        """
        game = self.game
        secret = [pin.get_color().value for pin in game.secret_code.get_code()] if game.secret_code is not None else []

        attempt_rows = []
        for attempt in game.attempt_list:
            guess_as_int_list = [pin.get_color().value for pin in attempt.get_guess().get_code_guess().get_code()]
            fb = attempt.get_feedback()
            attempt_rows.append(
                {
                    "guess": guess_as_int_list,
                    "feedback": {
                        "black_pins": fb.black_pins,
                        "white_pins": fb.white_pins,
                        "status": fb.get_status().value,
                    },
                }
            )
        return {
            "gamemode": game.game_mode.value,
            "gamestate": game.game_state.value,
            "number_of_positions": self.game_config.number_of_positions,
            "number_of_colors": self.game_config.number_of_colors,
            "max_attempts": Game.MAX_ATTEMPTS,
            "secret_code": secret,
            "attempt_list": attempt_rows,
            "remaining_time_millis": (
                self.game_config.countdown_millis if self.game_config.gamemode == Gamemode.TIME_TRIAL else 0
            ),
            "matchup": {
                "gamemode": self.game_config.gamemode.value,
                "user_role": self.game_config.user_role.value,
                "network_enabled": self.game_config.network_enabled,
                "countdown_millis": self.game_config.countdown_millis,
                "delay_millis": self.game_config.delay_millis,
            },
        }

    # TODO: naming conflict with GameEngine.interrupt_game() with different effect
    #  (GamEngine does not save, GameManager saves). --> rename here (not in GameManager!)
    def interrupt_game(self) -> None:
        """Signal the run loop to stop; run() will mark the game as INTERRUPTED."""
        self.shutdown_requested = True

    def resume(self, game_data: dict) -> None:
        """Rebuild the Game from a saved snapshot so run() can continue it.
        Built in gamestate INTERRUPTED; run() will flip the switch to RUNNING.

        Args:
            game_data: The persisted dict containing the saved game data
            collected by the GameManager from the ForPersistingGame port.
            (Shape defined by ForPersistingGame.save_game()/load_game()).
        """

        # TODO : handle corrupt persisted data:
        #  the game_data[...] / attempt_row[...] / fb[...] accesses can raise KeyError (missing keys),
        #  and Color()/FeedbackStatus()/ _assert_code_legal can raise ValueError on a corrupt/malformed save.
        #  These currently propagate UNHANDLED — corrupt-persist handling is a separate deferred decision.

        code_length = CodeConstants.NUMBER_OF_PINS

        self.game = Game(game_mode=self.game_config.gamemode, code_length=code_length, game_state=Gamestate.INTERRUPTED)

        # Secret code restored for local games.
        # If ever wished for network games: the remote codemaker owns it.
        if not self.game_config.network_enabled:
            secret_code_list = game_data["secret_code"]
            self._assert_code_legal(secret_code_list)
            self.game.set_secret_code(secret_code_list)

        for attempt_row in game_data["attempt_list"]:
            guess_as_list = attempt_row["guess"]
            self._assert_code_legal(guess_as_list)
            guess_object = Guess(Code((code_length, [Slot(Color(c)) for c in guess_as_list])))
            fb = attempt_row["feedback"]
            feedback_object = Feedback(fb["black_pins"], fb["white_pins"], FeedbackStatus(fb["status"]))
            self.game.attempt_list.append(Attempt(guess_object, feedback_object))

    def get_game_obj(self) -> Game | None:
        """Returns the current game object."""
        return self.game

    # On raise Error during run(): GameManager catches (ValueError, TypeError)
    # and aborts the round without saving.
    @staticmethod
    def _assert_code_legal(code: list[int]) -> None:
        """Validate the raw code list from a port that represents a secret code or guess."""
        if not isinstance(code, list):
            raise ValueError("Code must be a list of integers.")

        if not all(isinstance(c, int) and not isinstance(c, bool) for c in code):
            raise ValueError("Code must contain only integers.")

        if len(code) != CodeConstants.NUMBER_OF_PINS:
            raise ValueError(f"Invalid code length: expected {CodeConstants.NUMBER_OF_PINS} pins.")

        if not all(1 <= c <= CodeConstants.NUMBER_OF_COLORS for c in code):
            raise ValueError("Code contains invalid color integers.")

    # On raise Error during run(): GameManager catches (ValueError, TypeError)
    # and aborts the round without saving.
    @staticmethod
    def _assert_feedback_legal(feedback: list[int]) -> None:
        """Validate the feedback as peg list from the codemaker port
        (7 = white, 8 = black)."""
        if not isinstance(feedback, list):
            raise ValueError("Feedback must be a list of integers.")

        if not all(isinstance(f, int) and not isinstance(f, bool) for f in feedback):
            raise ValueError("Feedback must contain only integers.")

        if len(feedback) > CodeConstants.NUMBER_OF_PINS:
            raise ValueError(f"Feedback length cannot exceed {CodeConstants.NUMBER_OF_PINS} pins.")

        # 7 = white peg, 8 = black peg
        if not all(peg in (7, 8) for peg in feedback):
            raise ValueError("Feedback must only contain 7 (white peg) or 8 (black peg).")
