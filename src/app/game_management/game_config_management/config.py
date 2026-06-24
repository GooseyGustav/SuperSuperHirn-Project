from dataclasses import dataclass

from app.game_management.game_config_management.role import Role
from app.game_model.game_mode import Gamemode


@dataclass
class Config:
    """Selection data for one game."""

    gamemode: Gamemode
    user_role: Role
    network_enabled: bool
    number_of_positions: int
    number_of_colors: int
    countdown_millis: int
    delay_millis: int
