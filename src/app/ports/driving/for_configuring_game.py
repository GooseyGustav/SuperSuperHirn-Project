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
                "gamemode":          str,   # CLASSIC | TIME_TRIAL | BLIND_TRIAL
                "userRole":          str,   # CODEMAKER | CODEBREAKER | OBSERVER
                "networkEnabled":    bool,
                "numberOfPositions": int,   # 1..9 (default 5)
                "numberOfColors":    int,   # 1..8 (default 8)
                "countdownMillis":   int,   # milliseconds
                "delayMillis":       int,   # milliseconds
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
