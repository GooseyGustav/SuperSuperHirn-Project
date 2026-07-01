# from unittest.mock import MagicMock, patch

# from gui.controllers.config_controller import ConfigController


# class TestConfigController:
#     def setup_method(self):
#         # Setup mocks using patch.start()
#         self.patcher_view = patch("gui.controllers.config_controller.ConfigView")
#         self.patcher_main_window = patch("gui.controllers.config_controller.MainWindow")

#         mock_config_view = self.patcher_view.start()
#         mock_main_window = self.patcher_main_window.start()

#         self.mock_view_instance = MagicMock()
#         mock_config_view.return_value = self.mock_view_instance

#         self.mock_main_window_instance = MagicMock()
#         self.mock_adapter = MagicMock()
#         self.mock_main_window_instance.get_service_adapter.return_value = self.mock_adapter
#         mock_main_window.instance.return_value = self.mock_main_window_instance

#         # Instantiate controller
#         self.controller = ConfigController()

#     def teardown_method(self):
#         self.patcher_view.stop()
#         self.patcher_main_window.stop()

#     def test_init_connects_signals(self):
#         # Verify view was registered and navigated to
#         self.mock_main_window_instance.register_view.assert_called_once_with("config", self.mock_view_instance)
#         self.mock_main_window_instance.navigate_to.assert_called_once_with("config")

#         # Verify signal connections
#         self.mock_view_instance.back_requested.connect.assert_called_once()
#         self.mock_view_instance.config_load_requested.connect.assert_called_once()
#         self.mock_view_instance.config_save_requested.connect.assert_called_once()
#         self.mock_view_instance.config_reset_requested.connect.assert_called_once()

#         # Verify load was emitted on init
#         self.mock_view_instance.config_load_requested.emit.assert_called_once()

#     def test_go_back(self):
#         self.controller._go_back()
#         self.mock_main_window_instance.navigate_to.assert_called_with("home")

#     def test_load_config_with_data(self):
#         self.mock_adapter.on_load_config.return_value = {"color_count": 6}
#         self.controller._load_config()

#         self.mock_adapter.on_load_config.assert_called_once()
#         self.mock_view_instance.populate.assert_called_once_with({"color_count": 6})

#     def test_load_config_empty_data(self):
#         self.mock_adapter.on_load_config.return_value = None
#         self.controller._load_config()

#         self.mock_view_instance.populate.assert_not_called()

#     def test_save_config(self):
#         test_payload = {"setting": "test"}
#         self.controller._save_config(test_payload)

#         self.mock_adapter.on_save_config.assert_called_once_with(test_payload)

#     def test_reset_config(self):
#         self.mock_adapter.on_load_config.return_value = {"default": True}
#         self.controller._reset_config()

#         self.mock_adapter.on_reset_config.assert_called_once()
#         # Should call load config internally after reset
#         self.mock_adapter.on_load_config.assert_called_once()
#         self.mock_view_instance.populate.assert_called_once_with({"default": True})
