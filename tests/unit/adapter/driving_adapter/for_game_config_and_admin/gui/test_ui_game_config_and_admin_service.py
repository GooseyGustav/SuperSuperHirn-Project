from unittest.mock import MagicMock

from adapter.driving_adapter.for_game_config_and_admin.gui.ui_game_config_and_admin_service import (
    UiGameConfigAndAdminAdapter,
)
from app.ports.driving.for_configuring_game import ForConfiguringGame
from app.ports.driving.for_game_administration import ForGameAdministration


class TestUiGameConfigAndAdminAdapter:
    def setup_method(self):
        self.mock_config_port = MagicMock(spec=ForConfiguringGame)
        self.mock_admin_port = MagicMock(spec=ForGameAdministration)
        self.adapter = UiGameConfigAndAdminAdapter(
            for_configuring_game=self.mock_config_port,
            for_game_administration=self.mock_admin_port,
        )

    def test_on_load_config_delegates(self):
        self.mock_config_port.load_config.return_value = {"key": "value"}
        result = self.adapter.on_load_config()
        self.mock_config_port.load_config.assert_called_once()
        assert result == {"key": "value"}

    def test_on_save_config_delegates(self):
        test_data = {"setting": "test"}
        self.adapter.on_save_config(test_data)
        self.mock_config_port.save_config.assert_called_once_with(test_data)

    def test_on_reset_config_delegates(self):
        self.adapter.on_reset_config()
        self.mock_config_port.reset_config.assert_called_once()

    def test_on_start_game_delegates(self):
        self.adapter.on_start_game()
        self.mock_admin_port.start_game.assert_called_once()

    def test_on_start_game_delete_interrupted_delegates(self):
        self.adapter.on_start_game_delete_interrupted()
        self.mock_admin_port.start_game_delete_interrupted.assert_called_once()

    def test_on_interrupt_game_delegates(self):
        self.adapter.on_interrupt_game()
        self.mock_admin_port.interrupt_game.assert_called_once()

    def test_on_abort_game_delegates(self):
        self.adapter.on_abort_game()
        self.mock_admin_port.abort_game.assert_called_once()

    def test_on_start_network_game_delegates(self):
        test_ip = "127.0.0.1"
        test_id = 123
        self.adapter.on_start_network_game(test_ip, test_id)
        self.mock_admin_port.start_network_game.assert_called_once_with(test_ip, test_id)

    def test_on_resume_interrupted(self):
        # The method currently has `pass`, but we can verify it executes without error.
        self.adapter.on_resume_interrupted()

    def test_on_exit_application(self):
        # The method currently has `pass`, but we can verify it executes without error.
        self.adapter.on_exit_application()
