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
    """Game persistence port double initialized with an interrupted game."""

    def __init__(self, game_data: dict):
        self.saved_game_data = game_data

    def save_game(self, game_data: dict) -> None:
        self.saved_game_data = game_data

    def load_game(self) -> dict:
        return self.saved_game_data

    def delete_game(self) -> None:
        self.saved_game_data = None


class CodemakerDouble:
    """Codemaker double used after resume."""

    def get_secret_code(self) -> list[int]:
        raise AssertionError("Resumed local games must use the persisted secret code")

    def get_feedback(self, secret_code: list[int], guess: list[int]) -> list[int]:
        return [8 for secret_pin, guess_pin in zip(secret_code, guess) if secret_pin == guess_pin]


class CodebreakerDouble:
    """Codebreaker double."""

    def __init__(self, guess: list[int]):
        self.guess = guess
        self.received_boards: list[list[tuple[list[int], list[int], str]]] = []

    def get_guess(self, board: list[tuple[list[int], list[int], str]]) -> list[int]:
        self.received_boards.append(board)
        return self.guess


class PlayerAssemblerDouble:
    """Player assembler port double."""

    def __init__(self, codemaker: CodemakerDouble, codebreaker: CodebreakerDouble):
        self.codemaker = codemaker
        self.codebreaker = codebreaker
        self.received_config: dict | None = None

    def assemble_players(self, config: dict) -> tuple[CodemakerDouble, CodebreakerDouble]:
        self.received_config = config
        return self.codemaker, self.codebreaker


def test_resume_interrupted_continues_without_overwriting_save_when_won():
    """GameManager resumes an interrupted game, continues it through GameEngine, and keeps the old save when won.

    The test loads an interrupted game through the GamePersistPortDouble. GameManager merges the
    saved matchup config with the loaded config, GameEngine.resume() rebuilds the previous attempt,
    and GameEngine.run() continues with the persisted secret code until the game is won. Since won games
    are not resumable, the interrupted save is not overwritten.
    """

    config = {
        "gamemode": "CLASSIC",
        "user_role": "CODEBREAKER",
        "network_enabled": False,
        "countdown_millis": 0,
        "delay_millis": 0,
    }
    secret_code = [1, 2, 3, 4, 5]
    previous_guess = [5, 4, 3, 2, 1]
    game_data = {
        "gamemode": "CLASSIC",
        "gamestate": "INTERRUPTED",
        "number_of_positions": 5,
        "number_of_colors": 8,
        "max_attempts": 10,
        "secret_code": secret_code,
        "attempt_list": [
            {
                "guess": previous_guess,
                "feedback": {
                    "black_pins": 1,
                    "white_pins": 2,
                    "status": "FINAL",
                },
            }
        ],
        "remaining_time_millis": 0,
        "matchup": config,
    }
    config_storage = ConfigPersistencePortDouble(config)
    game_storage = GamePersistencePortDouble(game_data)
    codemaker = CodemakerDouble()
    codebreaker = CodebreakerDouble(secret_code)
    player_assembler = PlayerAssemblerDouble(codemaker, codebreaker)
    game_manager = GameManager(config_storage, player_assembler, game_storage)

    game_manager.resume_interrupted()

    assert player_assembler.received_config["gamemode"] == "CLASSIC"
    assert codebreaker.received_boards == [
        [
            (previous_guess, [8, 7, 7], "FINAL"),
        ]
    ]
    assert game_manager._game_engine.get_game_obj().game_state == Gamestate.WON
    assert game_storage.saved_game_data == game_data

    persist_object = game_manager._game_engine.create_game_persist_object()
    assert persist_object["secret_code"] == secret_code
    assert persist_object["attempt_list"] == [
        {
            "guess": previous_guess,
            "feedback": {
                "black_pins": 1,
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
