from abc import ABC, abstractmethod


class ForPersistingConfig(ABC):
    """The port for persisting the configuration of the game (loading and saving).
    Implemented by Configuration-Persisting Adapters.

    Note:
        - Implemented by: `ConfigJsonAdapter`, `FakeConfigStorage` (src/adapter/driven_adapter/for_persisting_config).
        - Implemented for testing App by `FakeConfigStorage` (src/adapter/driven_adapter/for_persisting_config).
        - Passed to App by `SupersuperhirnRunner` (src/startup).
        - Methods called by: `GameManager` (src/app/game_management).
    """

    @abstractmethod
    def load_config_dict(self) -> dict:
        """Loads the configuration data from an external location and returns it
        to the app as a dictionary.

        Returns:
            A dict containing configuration selections. Shape:

                {
                    "gamemode":             str,   # CLASSIC | TIME_TRIAL | BLIND_TRIAL
                    "user_role":            str,   # CODEMAKER | CODEBREAKER | OBSERVER
                    "network_enabled":      bool,
                    "number_of_positions":  int,   # 1..9 (default 5) -> Game.CODE_LENGTH
                    "number_of_colors":     int,   # 1..8 (default 8); bounds the pin range
                    "countdown_millis":     int,   # TIME_TRIAL countdown time, milliseconds
                    "delay_millis":         int,   # OBSERVER mode: ms between auto-moves so progress is visible
                }

            max_attempts is intentionally absent -- it is a fixed constant, not available
            for User selection. Validity check by core App.
            If no User Config is available, the default config is used.
        """

    @abstractmethod
    def save_config_dict(self, config_dict: dict) -> None:
        """Save the config data provided by the app as a dictionary to an external
        location.

        Args:
            config_dict: The dictionary containing configuration data to be saved.
            Same shape as load_config_dict() returns.
        """

    @abstractmethod
    def reset_to_default(self) -> None:
        """Reset the configuration to the default values. (The implementing Adapter
        should load the default config from the external file that has the default
        config data and write it to the user config JSON file.)
        """

    # Versions that work with Strings instead of Dictionaries:

    # @abstractmethod
    # def load_config_string(self) -> str:
    #     """Loads the configuration of the game from an external location and
    #     returns it as a string for the app to use.
    #
    #     Returns:
    #         A string containing configuration data.
    #     """
    #
    # @abstractmethod
    # def save_config_string(self, config_string: str) -> None:
    #     """Save the provided string containing configuration data to an external
    #     location.
    #
    #     Args:
    #         config_string: The string containing configuration data to be saved.
    #     """
