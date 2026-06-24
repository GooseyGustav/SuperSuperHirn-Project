from app.game_management.game_config_management.code_constants import CodeConstants
from app.game_management.game_config_management.config import Config
from app.game_management.game_config_management.role import Role
from app.game_model.game_mode import Gamemode


class ConfigManager:
    """Maps the persisted dict to a `Config` object."""

    def __init__(self, config: dict) -> None:
        self.config_data = config

    def create_config_obj(self) -> Config:
        """Creates a Config object from the persisted dict."""

        # Gamemode and Role objects created from the loaded strings
        gamemode_object = Gamemode(self.config_data["gamemode"])
        role_object = Role(self.config_data["user_role"])

        return Config(
            gamemode=gamemode_object,
            user_role=role_object,
            network_enabled=self.config_data["network_enabled"],
            number_of_positions=CodeConstants.NUMBER_OF_PINS.value,
            number_of_colors=CodeConstants.NUMBER_OF_COLORS.value,
            countdown_millis=self.config_data["countdown_millis"],
            delay_millis=self.config_data["delay_millis"],
        )

    def get_config_data(self) -> dict:
        return self.config_data
