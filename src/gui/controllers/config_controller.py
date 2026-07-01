from gui.views.config_view import ConfigView
from gui.views.main_window import MainWindow


class ConfigController:
    """Controller for the game configuration screen.

    Connects ConfigView signals to the service adapter (ForConfiguringGame port).
    Owns the ConfigView instance and registers it with MainWindow.
    """

    def __init__(self):
        self.config_view = ConfigView()

        MainWindow.instance().register_view("config", self.config_view)
        MainWindow.instance().navigate_to("config")

        self._connect_events()

        # Trigger a load immediately so the form is pre-filled when the screen opens
        self.config_view.config_load_requested.emit()

    def _connect_events(self):
        self.config_view.back_requested.connect(self._go_back)
        self.config_view.config_load_requested.connect(self._load_config)
        self.config_view.config_save_requested.connect(self._save_config)
        self.config_view.config_reset_requested.connect(self._reset_config)

    @property
    def adapter(self):
        return MainWindow.instance().get_service_adapter()

    def _go_back(self):
        """Navigate back to the home screen."""
        MainWindow.instance().navigate_to("home")

    def _load_config(self):
        from PyQt6.QtWidgets import QMessageBox

        try:
            config_data: dict = self.adapter.on_load_config()
        except (ValueError, OSError) as e:
            QMessageBox.critical(self.config_view, "Couldn't load config", str(e))
            return
        if config_data:
            self.config_view.populate(config_data)

    def _save_config(self, payload: dict) -> None:
        from PyQt6.QtWidgets import QMessageBox

        try:
            self.adapter.on_save_config(payload)
        except ValueError as e:
            QMessageBox.warning(self.config_view, "Invalid settings", str(e))
            return  # stay on form for re-input
        except OSError as e:
            QMessageBox.critical(self.config_view, "Couldn't save config", str(e))
            return
        MainWindow.instance().navigate_to("home")

    def _reset_config(self) -> None:
        from PyQt6.QtWidgets import QMessageBox

        try:
            self.adapter.on_reset_config()
        except OSError as e:
            QMessageBox.critical(self.config_view, "Couldn't reset config", str(e))
            return
        self._load_config()
