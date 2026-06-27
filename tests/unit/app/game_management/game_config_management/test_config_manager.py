import pytest

from app.game_management.game_config_management.code_constants import CodeConstants
from app.game_management.game_config_management.config import Config
from app.game_management.game_config_management.config_manager import ConfigManager
from app.game_management.game_config_management.role import Role
from app.game_model.game_mode import Gamemode


def test_config_manager_stores_config_data():
    config_data = {
        "gamemode": "CLASSIC",
        "user_role": "CODEBREAKER",
        "network_enabled": False,
        "countdown_millis": 10000,
        "delay_millis": 1000,
    }

    config_manager = ConfigManager(config_data)

    assert config_manager.get_config_data() == config_data


def test_create_config_obj_happy_path():
    config_data = {
        "gamemode": "CLASSIC",
        "user_role": "CODEBREAKER",
        "network_enabled": False,
        "countdown_millis": 10000,
        "delay_millis": 1000,
    }

    config = ConfigManager(config_data).create_config_obj()

    assert isinstance(config, Config)
    assert config.gamemode == Gamemode.CLASSIC
    assert config.user_role == Role.CODEBREAKER
    assert config.network_enabled is False
    assert config.number_of_positions == CodeConstants.NUMBER_OF_PINS.value
    assert config.number_of_colors == CodeConstants.NUMBER_OF_COLORS.value
    assert config.countdown_millis == 10000
    assert config.delay_millis == 1000


def test_create_config_obj_accepts_other_valid_values():
    config_data = {
        "gamemode": "BLIND_TRIAL",
        "user_role": "OBSERVER",
        "network_enabled": True,
        "countdown_millis": 30000,
        "delay_millis": 2500,
    }

    config = ConfigManager(config_data).create_config_obj()

    assert config.gamemode == Gamemode.BLIND_TRIAL
    assert config.user_role == Role.OBSERVER
    assert config.network_enabled is True
    assert config.countdown_millis == 30000
    assert config.delay_millis == 2500


def test_create_config_obj_rejects_invalid_gamemode():
    config_data = {
        "gamemode": "INVALID",
        "user_role": "CODEBREAKER",
        "network_enabled": False,
        "countdown_millis": 10000,
        "delay_millis": 1000,
    }

    with pytest.raises(ValueError):
        ConfigManager(config_data).create_config_obj()


def test_create_config_obj_rejects_invalid_role():
    config_data = {
        "gamemode": "CLASSIC",
        "user_role": "INVALID",
        "network_enabled": False,
        "countdown_millis": 10000,
        "delay_millis": 1000,
    }

    with pytest.raises(ValueError):
        ConfigManager(config_data).create_config_obj()
