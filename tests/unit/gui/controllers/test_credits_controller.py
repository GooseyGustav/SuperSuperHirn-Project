from unittest.mock import MagicMock, patch

from gui.controllers.credits_controller import CreditsController


class TestCreditsController:
    def setup_method(self):
        self.patcher_view = patch("gui.controllers.credits_controller.CreditsView")
        self.patcher_main_window = patch("gui.controllers.credits_controller.MainWindow")

        mock_credits_view = self.patcher_view.start()
        mock_main_window = self.patcher_main_window.start()

        # Setup mocks
        self.mock_view_instance = MagicMock()
        mock_credits_view.return_value = self.mock_view_instance

        self.mock_main_window_instance = MagicMock()
        mock_main_window.instance.return_value = self.mock_main_window_instance

        # Instantiate controller
        self.controller = CreditsController()

    def teardown_method(self):
        self.patcher_view.stop()
        self.patcher_main_window.stop()

    def test_init_connects_signals(self):
        self.mock_main_window_instance.register_view.assert_called_once_with("credits", self.mock_view_instance)
        self.mock_main_window_instance.navigate_to.assert_called_once_with("credits")

        self.mock_view_instance.back_requested.connect.assert_called_once_with(self.controller._go_back)

    def test_go_back(self):
        self.controller._go_back()
        self.mock_main_window_instance.navigate_to.assert_called_with("home")
