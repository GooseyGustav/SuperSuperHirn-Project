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
from app.game_model.game_mode import Gamemode
from app.game_model.game_state import Gamestate
from app.game_model.player_attempts.attempt import Attempt


class Game:
    """Docstring for Game."""

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
        self.attempt_list: list[Attempt] = []  # populated by `set_guess` after construction

    def set_secret_code(self, code: list[int]) -> None: ...

    # if check `secretCode.len` and `colorID`:
    # only static code len <=9, each colorID <= 8
    # -- whether config is legal: checked by `GameEngine`
    # (or simply skip check since not responsibility)

    def set_guess(self, guess: list[int]) -> None:
        """Docstring for set_guess.
        # starts new Attempt
        """
        # if check `guess.len` and `colorID`:
        # -- whether config is legal: checked by `GameEngine`
        # (or simply skip check since not responsibility)

    def set_feedback(self, feedback: list[int]) -> None:
        """Docstring for set_feedback.
        # adds feedback to last Attempt
        """

    def convert_provision_to_final(self) -> None: ...

    def get_game_mode(self) -> Gamemode: ...
