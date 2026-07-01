# from unittest.mock import patch

# from startup.supersuperhirn_runner import SuperSuperhirnRunner


# class TestSuperSuperhirnRunner:
#     @patch("startup.supersuperhirn_runner.MainWindow")
#     @patch("startup.supersuperhirn_runner.SupersuperhirnApp")
#     @patch("startup.supersuperhirn_runner.Matchmaker")
#     @patch("startup.supersuperhirn_runner.GameJsonAdapter")
#     @patch("startup.supersuperhirn_runner.ConfigJsonAdapter")
#     @patch("startup.supersuperhirn_runner.UiGameConfigAndAdminAdapter")
#     def test_runner_initializes_components(
#         self, mock_ui_adapter, mock_config_adapter, mock_game_adapter, mock_matchmaker, mock_app, mock_main_window
#     ):
#         # We also need to patch QApplication to prevent Qt from initializing an actual app
#         with patch("startup.supersuperhirn_runner.QApplication"):
#             runner = SuperSuperhirnRunner()

#             # Verify all components were instantiated
#             mock_config_adapter.assert_called_once()
#             mock_game_adapter.assert_called_once()
#             mock_matchmaker.assert_called_once()
#             mock_app.assert_called_once()
#             mock_ui_adapter.assert_called_once()
#             mock_main_window.assert_called_once()

#             # Verify the runner stores the instances
#             assert runner.pers_config_adapter is not None
#             assert runner.pers_game_adapter is not None
#             assert runner.matchmaker is not None
#             assert runner.app is not None
#             assert runner.ui_service_adapter is not None
#             assert runner.main_window is not None

#     @patch("startup.supersuperhirn_runner.QApplication")
#     @patch("startup.supersuperhirn_runner.MainWindow")
#     def test_connect_gui_adapter_to_ui(self, mock_main_window, mock_qapp):
#         # Temporarily mock out parts of the runner so we can test the callback in isolation
#         with patch("startup.supersuperhirn_runner.SupersuperhirnApp"):
#             runner = SuperSuperhirnRunner()

#             dummy_adapter = {"some_key": "some_value"}
#             runner._connect_gui_adapter_to_ui(dummy_adapter)

#             # The MainWindow mock should have its set_ui_adapter called
#             runner.main_window.set_ui_adapter.assert_called_once_with(dummy_adapter)
