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


from app.game_management.game_config_management.config import Config
from app.game_model.game import Game


class GameEngine:
    """Docstring for GameEngine. # TODO"""

    # deleted file mentioned in docstring GameSessionManager per modification of
    # Class Reference and Diagram, following discussion with Marlon that it was
    # unnecessary because GameManagement and GameEngine seem to cover everything.
    # If necessary TODO: reinstate GameSessionManager for threading in TIME_TRIAL

    def __init__(self, game_config: Config) -> None:
        self.game_config = game_config

    def run(self, codemaker, codebreaker) -> Game: ...

    def create_game_persist_object(self) -> object: ...

    def interrupt_game(self) -> None: ...

    def resume(self, game_data: dict) -> None: ...

    def start_clock(self, time_millis: int) -> bool: ...

    def get_game_obj(self) -> Game: ...

    def _assert_code_legal(self, code: list[int]) -> None:
        """Docstring for _assert_code_legal."""
        # check
        # len(code) == self.game_config.number_of_positions
        # and
        # all(1 <= c <= self.game_config.number_of_colors for c in code)\

    def _assert_feedback_legal(self, feedback: list[int]) -> None:
        """Docstring for _assert_feedback_legal."""
        # check :
        # len(feedback) <= self.game_config.number_of_positions
        # and
        # all(c in (7, 8) for c in feedback)
