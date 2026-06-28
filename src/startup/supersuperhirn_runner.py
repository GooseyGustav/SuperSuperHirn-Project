from adapter.driving_adapter.for_game_config_and_admin.gui.ui_game_config_and_admin_service import (
    UiGameConfigAndAdminAdapter
)
from gui.views.main_window import MainWindow
from .matchmaker import Matchmaker
from app.supersuperhirn_app import SupersuperhirnApp
from adapter.driven_adapter.for_persisting_config.file_tool.config_json_adapter import ConfigJsonAdapter
from adapter.driven_adapter.for_persisting_game.file_tool.game_json_adapter import GameJsonAdapter

import sys
from PyQt6.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)

    SuperSuperhirnRunner()

    sys.exit(app.exec())


class SuperSuperhirnRunner():

    def __init__(self):
        self.pers_config_adapter = ConfigJsonAdapter()
        self.pers_game_adapter = GameJsonAdapter()
        self.matchmaker = Matchmaker(gui_callback=self._connect_gui_adapter_to_ui)

        self.app = SupersuperhirnApp(
            for_persisting_game=self.pers_game_adapter,
            for_persisting_config=self.pers_config_adapter,
            for_assembling_players=self.matchmaker
        )

        self.ui_service_adapter = UiGameConfigAndAdminAdapter(
            self.app.for_game_configuration(),
            self.app.for_game_administration()
        )
        self.network_manager = None
        self.main_window = MainWindow(self.ui_service_adapter)

    def _connect_gui_adapter_to_ui(self, player_adapter: dict):
        self.main_window.set_ui_adapter(player_adapter)
