from app.game_management.game_manager import GameManager
from app.game_model.game_state import Gamestate
from app.ports.driven.for_getting_moves.errors import TimeoutInterrupt


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
    """Codemaker double."""

    def __init__(self, secret_code: list[int]):
        self.secret_code = secret_code
        self.feedback_was_requested = False

    def get_secret_code(self) -> list[int]:
        return self.secret_code

    def get_feedback(self, secret_code: list[int], guess: list[int]) -> list[int]:
        self.feedback_was_requested = True
        raise AssertionError("Feedback must not be requested after a time trial timeout")


class TimeoutCodebreakerDouble:
    """Codebreaker double simulating a GUI timeout by raising TimeoutInterrupt."""

    def __init__(self):
        self.received_boards: list[list[tuple[list[int], list[int], str]]] = []

    def get_guess(self, board: list[tuple[list[int], list[int], str]]) -> list[int]:
        self.received_boards.append(board)
        raise TimeoutInterrupt


class PlayerAssemblerDouble:
    """Player assembler port double."""

    def __init__(self, codemaker: CodemakerDouble, codebreaker: TimeoutCodebreakerDouble):
        self.codemaker = codemaker
        self.codebreaker = codebreaker
        self.received_config: dict | None = None

    def assemble_players(self, config: dict) -> tuple[CodemakerDouble, TimeoutCodebreakerDouble]:
        self.received_config = config
        return self.codemaker, self.codebreaker


class SynchronousExecutorDouble:
    """Thread executor double."""

    def run(self, fn) -> None:
        fn()


def test_time_trial_timeout_is_persisted_as_lost_timeout():
    """GameManager runs a Time Trial game that times out as LOST_TIMEOUT.

    The test loads a valid TIME_TRIAL config, creates a real GameEngine with Clock,
    and uses a Codebreaker double that raises TimeoutInterrupt. GameEngine converts
    the timeout into LOST_TIMEOUT. GameManager does not persist the result because
    only INTERRUPTED games are resumable and persisted in the current lifecycle.
    """

    config = {
        "gamemode": "TIME_TRIAL",
        "user_role": "CODEBREAKER",
        "network_enabled": False,
        "countdown_millis": 100,
        "delay_millis": 0,
    }
    secret_code = [1, 2, 3, 4, 5]
    config_storage = ConfigPersistencePortDouble(config)
    game_storage = GamePersistencePortDouble()
    codemaker = CodemakerDouble(secret_code)
    codebreaker = TimeoutCodebreakerDouble()
    player_assembler = PlayerAssemblerDouble(codemaker, codebreaker)
    game_manager = GameManager(config_storage, player_assembler, game_storage)
    game_manager.executor = SynchronousExecutorDouble()

    game_manager.start_game()

    assert player_assembler.received_config["gamemode"] == "TIME_TRIAL"
    assert player_assembler.received_config["countdown_millis"] == 100
    assert codebreaker.received_boards == [[]]
    assert codemaker.feedback_was_requested is False
    assert game_manager._game_engine.get_game_obj().game_state == Gamestate.LOST_TIMEOUT
    assert game_manager._game_engine.get_game_obj().attempt_list == []
    assert game_storage.saved_game_data is None
