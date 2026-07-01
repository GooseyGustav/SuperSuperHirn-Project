import logging
import sys

from PyQt6.QtWidgets import QApplication, QMessageBox

from adapter.driven_adapter.for_persisting_config.file_tool.config_json_adapter import ConfigJsonAdapter
from adapter.driven_adapter.for_persisting_game.file_tool.game_json_adapter import GameJsonAdapter
from adapter.driving_adapter.for_game_config_and_admin.gui.ui_game_config_and_admin_service import (
    UiGameConfigAndAdminAdapter,
)
from app.supersuperhirn_app import SupersuperhirnApp
from gui.views.main_window import MainWindow

from .matchmaker import Matchmaker


def main():
    app = QApplication(sys.argv)

    def crash_net(exc_type, exc, tb):
        logging.error("Unhandled exception", exc_info=(exc_type, exc, tb))
        QMessageBox.critical(None, "Unexpected error", f"Something went wrong:\n\n{exc}")

    sys.excepthook = crash_net  # install BEFORE building UI

    SuperSuperhirnRunner()
    sys.exit(app.exec())


class SuperSuperhirnRunner:

    def __init__(self):
        self.pers_config_adapter = ConfigJsonAdapter()
        self.pers_game_adapter = GameJsonAdapter()
        self.matchmaker = Matchmaker(gui_callback=self._connect_gui_adapter_to_ui)

        self.app = SupersuperhirnApp(
            for_persisting_game=self.pers_game_adapter,
            for_persisting_config=self.pers_config_adapter,
            for_assembling_players=self.matchmaker,
        )

        self.ui_service_adapter = UiGameConfigAndAdminAdapter(
            self.app.for_game_configuration(), self.app.for_game_administration()
        )
        self.main_window = MainWindow(self.ui_service_adapter)

    def _connect_gui_adapter_to_ui(self, player_adapter: dict):
        self.main_window.set_ui_adapter(player_adapter)
