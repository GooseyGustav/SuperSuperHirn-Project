from abc import ABC, abstractmethod


class ForConfiguringGame(ABC):
    """The port that the User's Adapter uses for configuring the game.

    Note:
        - Implemented by `GameManager` (in src/app).
        - Passed to App by `SupersuperhirnRunner` (src/startup)
        - Methods called by: `UIGameConfigAndAdminService` (in src/gui)
    """

    @abstractmethod
    def save_config(self, config_dict: dict) -> None:
        """Passes the game configuration provided by the Adapter as a dictionary
        to the App.

        Args:
            config_dict: the game configuration as a dictionary. Shape:

            {
                "gamemode":             str,   # CLASSIC | TIME_TRIAL | BLIND_TRIAL
                "user_role":            str,   # CODEMAKER | CODEBREAKER | OBSERVER
                "network_enabled":      bool,
                "number_of_positions":  int,   # 1..9 (default 5) -> Game.CODE_LENGTH
                "number_of_colors":     int,   # 1..8 (default 8); bounds the pin range
                "countdown_millis":     int,   # TIME_TRIAL countdown time, milliseconds
                "delay_millis":         int,   # OBSERVER mode: ms between auto-moves so progress is visible
            }

            Core App validates the config before saving it.
        """

    @abstractmethod
    def load_config(self) -> dict:
        """Loads a game configuration and returns it as a dictionary.
        (same shape as `save_config()` accepts).
        """

    @abstractmethod
    def reset_config(self) -> None:
        """Resets the game configuration to the default values."""
