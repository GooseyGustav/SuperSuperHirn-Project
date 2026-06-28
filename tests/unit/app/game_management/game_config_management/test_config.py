from app.game_management.game_config_management.config import Config
from app.game_management.game_config_management.role import Role
from app.game_model.game_mode import Gamemode


def test_config_stores_values():
    config = Config(
        gamemode=Gamemode.CLASSIC,
        user_role=Role.CODEBREAKER,
        network_enabled=False,
        number_of_positions=5,
        number_of_colors=8,
        countdown_millis=10000,
        delay_millis=1000,
    )

    assert config.gamemode == Gamemode.CLASSIC
    assert config.user_role == Role.CODEBREAKER
    assert config.network_enabled is False
    assert config.number_of_positions == 5
    assert config.number_of_colors == 8
    assert config.countdown_millis == 10000
    assert config.delay_millis == 1000
