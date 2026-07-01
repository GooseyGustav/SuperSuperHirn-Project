from adapter.driving_adapter.for_game_config_and_admin.gui.ui_game_config_and_admin_service import (
    UiGameConfigAndAdminAdapter,
)

from ..views.home_view import HomeView
from ..views.main_window import MainWindow


class HomeController:
    def __init__(self):
        self.home_view = HomeView()

        MainWindow.instance().register_view("home", self.home_view)
        MainWindow.instance().navigate_to("home")

        self.ui_service_adapter: UiGameConfigAndAdminAdapter = MainWindow.instance().ui_service_adapter

        self._connect_events()

    def _connect_events(self):
        self.home_view.game_continue_requested.connect(self._continue_game)
        self.home_view.game_new_requested.connect(self._new_game)
        self.home_view.network_game_requested.connect(self._go_to_network_setup)
        self.home_view.settings_requested.connect(self._go_to_settings)
        self.home_view.credits_requested.connect(self._go_to_credits)

    def _new_game(self):
        from gui.controllers.codemaker_controller import GameCodemakerController
        from gui.controllers.game_ui_controller import GameController
        from gui.controllers.observer_controller import GameObserverController

        self.ui_service_adapter.on_start_game()

        config = self.ui_service_adapter.on_load_config()

        role = config.get("user_role")

        match role:
            case "OBSERVER":
                self.observer_ctrl = GameObserverController()

            case "CODEBREAKER":
                self.codebreaker_ctrl = GameController()

            case "CODEMAKER":
                self.codemaker_ctrl = GameCodemakerController()

            case _:
                raise ValueError(f"Unknown user_role: {role}")

    def _continue_game(self):
        from gui.controllers.game_ui_controller import GameController

        self.ui_service_adapter.on_resume_interrupted()
        self.game_ctrl = GameController()

    def _go_to_settings(self):
        from gui.controllers.config_controller import ConfigController

        self.config_ctrl = ConfigController()

    def _go_to_credits(self):
        from gui.controllers.credits_controller import CreditsController

        self.credits_ctrl = CreditsController()

    def _go_to_network_setup(self) -> None:
        """Open the network configuration view."""
        from ..views.network_config_view import NetworkConfigView

        self.network_view = NetworkConfigView()
        MainWindow.instance().register_view("network_setup", self.network_view)
        MainWindow.instance().navigate_to("network_setup")

        # connect the view's signals
        self.network_view.cancel_requested.connect(lambda: MainWindow.instance().navigate_to("home"))
        self.network_view.start_requested.connect(self._start_network_game)

    def _start_network_game(self, address: str, gamer_id: str) -> None:
        """Start the network game and handle potential connection errors."""
        from PyQt6.QtWidgets import QMessageBox

        from gui.controllers.game_ui_controller import GameController

        try:
            # pass the data to the adapter (and thus to the GameManager)
            self.ui_service_adapter.on_start_network_game(address, gamer_id)

            # if no errors occur, initialize the GameController to start the game view
            self.game_ctrl = GameController()

        except (ConnectionError, ValueError) as e:
            # catch exceptions from the GameManager or NetworkCodemaker
            QMessageBox.critical(
                self.network_view,
                "Connection Error",
                f"The network game could not be started:\n\n{e}",
            )
