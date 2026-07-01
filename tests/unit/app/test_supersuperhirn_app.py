import pytest
from unittest.mock import MagicMock
from app.supersuperhirn_app import SupersuperhirnApp
from app.ports.driven.for_assembling_players import ForAssemblingPlayers
from app.ports.driven.for_persisting.for_persisting_config import ForPersistingConfig
from app.ports.driven.for_persisting.for_persisting_game import ForPersistingGame
from app.ports.driving.for_configuring_game import ForConfiguringGame
from app.ports.driving.for_game_administration import ForGameAdministration

class TestSupersuperhirnApp:
    def setup_method(self):
        self.mock_persisting_game = MagicMock(spec=ForPersistingGame)
        self.mock_persisting_config = MagicMock(spec=ForPersistingConfig)
        self.mock_assembling_players = MagicMock(spec=ForAssemblingPlayers)
        
        self.app = SupersuperhirnApp(
            for_persisting_game=self.mock_persisting_game,
            for_persisting_config=self.mock_persisting_config,
            for_assembling_players=self.mock_assembling_players
        )

    def test_app_initializes_game_manager_with_ports(self):
        assert self.app._for_persisting_game == self.mock_persisting_game
        assert self.app._for_persisting_config == self.mock_persisting_config
        assert self.app._for_assembling_players == self.mock_assembling_players
        assert self.app._game_manager is not None

    def test_for_game_administration_returns_game_manager(self):
        admin_port = self.app.for_game_administration()
        assert isinstance(admin_port, ForGameAdministration)
        assert admin_port == self.app._game_manager

    def test_for_game_configuration_returns_game_manager(self):
        config_port = self.app.for_game_configuration()
        assert isinstance(config_port, ForConfiguringGame)
        assert config_port == self.app._game_manager
