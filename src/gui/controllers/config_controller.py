from gui.views.main_window import MainWindow
from gui.views.config_view import ConfigView


class ConfigController():
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
        """Load config from the adapter and populate the view's widgets."""
        config_data: dict = self.adapter.on_load_config()
        if config_data:  # guard against None or empty dict from adapter
            self.config_view.populate(config_data)

    def _save_config(self, payload: dict) -> None:
        """Forward the dict built by the view directly to the adapter."""
        self.adapter.on_save_config(payload)
        MainWindow.instance().navigate_to("home")

    def _reset_config(self) -> None:
        """Reset config via adapter, then reload so widgets reflect the new defaults."""
        self.adapter.on_reset_config()
        self._load_config()
