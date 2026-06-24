from unittest.mock import MagicMock

import pytest

from app.game_management.game_manager import GameManager
from app.ports.driven.for_assembling_players import ForAssemblingPlayers
from app.ports.driven.for_persisting.for_persisting_config import ForPersistingConfig
from app.ports.driven.for_persisting.for_persisting_game import ForPersistingGame


@pytest.fixture
def persist_config():
    return MagicMock(spec=ForPersistingConfig)


@pytest.fixture
def assembling_players():
    return MagicMock(spec=ForAssemblingPlayers)


@pytest.fixture
def persist_game():
    return MagicMock(spec=ForPersistingGame)


@pytest.fixture
def game_manager(persist_config, assembling_players, persist_game):
    return GameManager(persist_config, assembling_players, persist_game)


@pytest.fixture
def valid_config_dict():
    return {
        "gamemode": "CLASSIC",
        "user_role": "CODEMAKER",
        "network_enabled": False,
        "countdown_millis": 0,
        "delay_millis": 0,
    }
