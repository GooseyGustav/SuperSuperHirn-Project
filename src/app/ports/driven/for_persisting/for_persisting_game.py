from abc import ABC, abstractmethod


class ForPersistingGame(ABC):
    """The port for persisting the game state (loading and saving). Implemented
    by Game-Persisting Adapters.

    Note:
        - Implemented by `GameJsonAdapter`, `FakeGameStorage` (src/adapter/driven_adapter/for_persisting_game).
        - Implemented for testing App by `FakeGameStorage` (src/adapter/driven_adapter/for_persisting_game).
        - Methods called by: `GameManager` (src/app/game_management).
        - Passed to App by `SupersuperhirnRunner` (src/startup).
    """

    @abstractmethod
    def save_game(self, game_data: dict) -> None:
        """Saves the game data provided by the app as a dictionary to an external
        location.

        Args:
            game_data: a flat dict that contains all the game data to be saved;
            describes an interrupted game for future resuming. Shape:

                {
                    "gamemode":          str,   # CLASSIC | TIME_TRIAL | BLIND_TRIAL
                    "gamestate":         str,   # NEW | RUNNING | INTERRUPTED | WON
                                             #   | LOST_TIMEOUT | LOST_ATTEMPTS
                    "code_length":       int,   # 1..9 (default 5)
                    "number_of_colors":  int,   # 1..8 (default 8); bounds the pin range
                    "max_attempts":      int,   # fixed constant (10); snapshot only
                    "secret_code":       list[int],   # len == codeLength,
                                                      #   each pin 1..numberOfColors
                    "attempt_list": [                 # 0..maxAttempts rows
                        {
                            "guess": list[int],    # len == codeLength,
                                                   #   each pin 1..numberOfColors
                            "feedback": {
                                "black_pins": int,  # 0..codeLength
                                "white_pins": int,  # 0..codeLength,
                                                   #   black + white <= codeLength
                                "status":    str,  # FINAL | PROVISIONAL
                            },
                        },
                        ...
                    ],
                    # mode / resume extras:
                    "remaining_time_millis": int,  # TIME_TRIAL only; milliseconds
                    "matchup": dict,             # opaque to the core, round-tripped only
                }

        Note:
            Trace of the upstream creation of game_data:
                (1) game started:
                   `GameManager.startGame()`
                   --> `GameEngine.run(codemaker, codebreaker): Game`
                (2) game stopped
                   --> `GameEngine.createGamePersistObject(): Object`
                   --> GameManager receives this Object from GameEngine
                   --> GameManager passes it on to the Game-Persisting Adapter as the `game_data` (dict).
        """

    @abstractmethod
    def load_game(self) -> dict:
        """Loads the game data from an external location and returns it to the App
        as a dictionary (same shape as `save_game()`).
        Core App will perform validation.
        """

    @abstractmethod
    def delete_game(self) -> None:
        """Deletes the game data from the external location."""
