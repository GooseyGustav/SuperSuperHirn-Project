from gui.views.main_window import MainWindow
from gui.views.config_view import ConfigView


class ConfigController():
    def __init__(self):
        self.config_view = ConfigView()

        MainWindow.instance().register_view("config", self.config_view)
        MainWindow.instance().navigate_to("config")

        self._connect_events()

    def _connect_events(self):
        self.config_view.config_load_requested.connect(self._load_config)
        self.config_view.config_save_requested.connect(self._save_config)
        self.config_view.config_reset_requested.connect(self._reset_config)

    @property
    def adapter(self):
        return MainWindow.instance().get_service_adapter()

    def _load_config(self) -> dict:
        config_data: dict = self.adapter.on_load_config()
        return config_data

    def _save_config(self, payload: dict) -> None:
        some_dummy_data = {
                    "gamemode":             "CLASSIC",   # CLASSIC | TIME_TRIAL | BLIND_TRIAL
                    "user_role":            "CODEMAKER",   # CODEMAKER | CODEBREAKER | OBSERVER
                    "network_enabled":      False,
                    "countdown_millis":     1000,   # TIME_TRIAL countdown time, milliseconds
                    "delay_millis":         300,   # OBSERVER mode: ms between auto-moves so progress is visible
                }
        save_data = some_dummy_data  # Temporary data mock, remove later when driven config adapter is ready
        self.adapter.on_save_config(save_data)

    def _reset_config(self) -> None:
        self.adapter.on_reset_config()
