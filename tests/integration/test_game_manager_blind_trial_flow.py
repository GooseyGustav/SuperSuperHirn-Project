from app.game_management.game_manager import GameManager
from app.game_model.game_state import Gamestate


class ConfigPersistencePortDouble:
    """Config persistence port double."""

    def __init__(self, config: dict):
        self.config = config

    def load_config_dict(self) -> dict:
        return self.config

    def save_config_dict(self, config_dict: dict) -> None:
        self.config = config_dict

    def reset_to_default(self) -> None:
        raise NotImplementedError


class GamePersistencePortDouble:
    """Game persistence port double."""

    def __init__(self):
        self.saved_game_data: dict | None = None

    def save_game(self, game_data: dict) -> None:
        self.saved_game_data = game_data

    def load_game(self) -> dict:
        return self.saved_game_data

    def delete_game(self) -> None:
        self.saved_game_data = None


class CodemakerDouble:
    """Codemaker double returning."""

    def __init__(self, secret_code: list[int], feedback_rows: list[list[int]]):
        self.secret_code = secret_code
        self.feedback_rows = feedback_rows
        self.feedback_call_count = 0

    def get_secret_code(self) -> list[int]:
        return self.secret_code

    def get_feedback(self, secret_code: list[int], guess: list[int]) -> list[int]:
        feedback = self.feedback_rows[self.feedback_call_count]
        self.feedback_call_count += 1
        return feedback


class CodebreakerDouble:
    """Codebreaker double."""

    def __init__(self, guesses: list[list[int]]):
        self.guesses = guesses
        self.guess_call_count = 0
        self.received_boards: list[list[tuple[list[int], list[int], str]]] = []

    def get_guess(self, board: list[tuple[list[int], list[int], str]]) -> list[int]:
        self.received_boards.append(board)
        guess = self.guesses[self.guess_call_count]
        self.guess_call_count += 1
        return guess


class PlayerAssemblerDouble:
    """Player assembler port double."""

    def __init__(self, codemaker: CodemakerDouble, codebreaker: CodebreakerDouble):
        self.codemaker = codemaker
        self.codebreaker = codebreaker

    def assemble_players(self, config: dict) -> tuple[CodemakerDouble, CodebreakerDouble]:
        return self.codemaker, self.codebreaker


class SynchronousExecutorDouble:
    """Thread executor double."""

    def run(self, fn) -> None:
        fn()


def test_blind_trial_hides_provisional_feedback_and_persists_final_feedback():
    """GameManager runs a Blind Trial game with hidden provisional feedback and final live feedback.

    The first attempt receives mixed black/white feedback, which is stored as PROVISIONAL in the live game.
    On the next guess, the Codebreaker receives that row as white-only feedback. After the second guess wins,
    GameEngine finalizes all Blind Trial feedback. Finished games are not persisted by the current lifecycle.
    """

    config = {
        "gamemode": "BLIND_TRIAL",
        "user_role": "CODEBREAKER",
        "network_enabled": False,
        "countdown_millis": 0,
        "delay_millis": 0,
    }
    secret_code = [1, 2, 3, 4, 5]
    first_guess = [1, 2, 3, 5, 4]
    config_storage = ConfigPersistencePortDouble(config)
    game_storage = GamePersistencePortDouble()
    codemaker = CodemakerDouble(secret_code, [[8, 8, 8, 7, 7], [8, 8, 8, 8, 8]])
    codebreaker = CodebreakerDouble([first_guess, secret_code])
    player_assembler = PlayerAssemblerDouble(codemaker, codebreaker)
    game_manager = GameManager(config_storage, player_assembler, game_storage)
    game_manager.executor = SynchronousExecutorDouble()

    game_manager.start_game()

    assert codebreaker.received_boards == [
        [],
        [(first_guess, [7, 7, 7, 7, 7], "PROVISIONAL")],
    ]

    assert game_manager._game_engine.get_game_obj().game_state == Gamestate.WON
    assert game_storage.saved_game_data is None

    persist_object = game_manager._game_engine.create_game_persist_object()
    assert persist_object["attempt_list"] == [
        {
            "guess": first_guess,
            "feedback": {
                "black_pins": 3,
                "white_pins": 2,
                "status": "FINAL",
            },
        },
        {
            "guess": secret_code,
            "feedback": {
                "black_pins": 5,
                "white_pins": 0,
                "status": "FINAL",
            },
        },
    ]
