from unittest.mock import MagicMock, patch

from gui.controllers.home_controller import HomeController


class TestHomeController:
    def setup_method(self):
        self.patcher_view = patch("gui.controllers.home_controller.HomeView")
        self.patcher_main_window = patch("gui.controllers.home_controller.MainWindow")

        mock_home_view = self.patcher_view.start()
        mock_main_window = self.patcher_main_window.start()

        # Setup mocks
        self.mock_view_instance = MagicMock()
        mock_home_view.return_value = self.mock_view_instance

        self.mock_main_window_instance = MagicMock()
        self.mock_adapter = MagicMock()
        self.mock_main_window_instance.ui_service_adapter = self.mock_adapter
        mock_main_window.instance.return_value = self.mock_main_window_instance

        # Instantiate controller
        self.controller = HomeController()

    def teardown_method(self):
        self.patcher_view.stop()
        self.patcher_main_window.stop()

    def test_init_connects_signals(self):
        self.mock_main_window_instance.register_view.assert_called_once_with("home", self.mock_view_instance)
        self.mock_main_window_instance.navigate_to.assert_called_once_with("home")

        self.mock_view_instance.game_continue_requested.connect.assert_called_once()
        self.mock_view_instance.game_new_requested.connect.assert_called_once()
        self.mock_view_instance.settings_requested.connect.assert_called_once()
        self.mock_view_instance.credits_requested.connect.assert_called_once()

    @patch("gui.controllers.home_controller.MainWindow")
    def test_new_game(self, mock_main_window_again):
        self.mock_adapter.on_load_config.return_value = {"user_role": "CODEBREAKER"}

        with patch("gui.controllers.game_ui_controller.GameController") as mock_game_controller:
            self.controller._new_game()

            self.mock_adapter.on_start_game.assert_called_once()
            self.mock_adapter.on_load_config.assert_called_once()
            mock_game_controller.assert_called_once()

    @patch("gui.controllers.home_controller.MainWindow")
    def test_continue_game(self, mock_main_window_again):
        with patch("gui.controllers.game_ui_controller.GameController") as mock_game_controller:
            self.controller._continue_game()

            self.mock_adapter.on_resume_interrupted.assert_called_once_with()
            mock_game_controller.assert_called_once()

    @patch("gui.controllers.home_controller.MainWindow")
    def test_go_to_settings(self, mock_main_window_again):
        with patch("gui.controllers.config_controller.ConfigController") as mock_config_controller:
            self.controller._go_to_settings()
            mock_config_controller.assert_called_once()

    @patch("gui.controllers.home_controller.MainWindow")
    def test_go_to_credits(self, mock_main_window_again):
        with patch("gui.controllers.credits_controller.CreditsController") as mock_credits_controller:
            self.controller._go_to_credits()
            mock_credits_controller.assert_called_once()
