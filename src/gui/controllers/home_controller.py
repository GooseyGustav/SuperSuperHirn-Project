from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMessageBox

from adapter.driving_adapter.for_game_config_and_admin.gui.ui_game_config_and_admin_service import (
    UiGameConfigAndAdminAdapter,
)
from app.ports.driven.for_persisting.save_errors import CorruptedSaveError

from ..views.home_view import HomeView
from ..views.main_window import MainWindow


class HomeController:
    def __init__(self):
        self.home_view = HomeView()

        MainWindow.instance().register_view("home", self.home_view)
        MainWindow.instance().navigate_to("home")

        self.ui_service_adapter: UiGameConfigAndAdminAdapter = MainWindow.instance().ui_service_adapter

        self._connect_events()

        self.home_view.btn_game_continue.setEnabled(False)

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

        self.home_view.btn_game_continue.setEnabled(True)

    def _continue_game(self):

        try:
            MainWindow.instance().player_adapter = None  # make sure adapters are reset
            resumed_game = self.ui_service_adapter.on_resume_interrupted()
        except CorruptedSaveError:
            answer = QMessageBox.question(
                self.home_view,
                "Saved game file corrupted",
                "The saved game can't be loaded. Delete it and start new game?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if answer == QMessageBox.StandardButton.Yes:
                self.ui_service_adapter.on_start_game_delete_interrupted()
            return
        except (ValueError, OSError) as e:
            QMessageBox.critical(self.home_view, "Couldn't continue", str(e))
            return

        if not resumed_game:
            QMessageBox.information(self.home_view, "No saved game found", "There is no available game to continue.")
            return

        # assemble players on the resume worker thread; wait for the
        # assemly to finish, then build view
        self._players_ready_timer = QTimer()
        self._players_ready_timer.timeout.connect(self._check_if_players_ready_for_resume)
        self._players_ready_timer.start(100)

    def _check_if_players_ready_for_resume(self):
        from gui.controllers.game_ui_controller import GameController

        # first assemble right players (from resumed game), then start controller
        if MainWindow.instance().player_adapter is not None:
            self._players_ready_timer.stop()
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

    # ---------- Config & Timer Methods ----------

    def _start_network_game(self, address: str, gamer_id: str, role: str) -> None:
        """
        Starts the network game and waits for the background thread to be ready.

        Args:
            address (str): The network address to connect to.
            gamer_id (str): The identifier for the local player.
        """
        from PyQt6.QtCore import QTimer
        from PyQt6.QtWidgets import QMessageBox

        self._network_role = role

        try:
            self.ui_service_adapter.on_start_network_game(address, gamer_id, role)

            # start a QTimer to check every 100 milliseconds if the core is ready
            self.ready_timer = QTimer()
            self.ready_timer.timeout.connect(self._check_if_core_is_ready)
            self.ready_timer.start(100)

        except Exception as e:
            QMessageBox.critical(
                self.network_view,
                "Connection Error",
                f"The network game could not be started:\n\n{e}",
            )

    def _check_if_core_is_ready(self) -> None:
        """Called every 100ms until the core has initialized the player_adapter."""
        from gui.controllers.game_ui_controller import GameController

        # once the player_adapter is no longer None, the core has finished its setup
        if MainWindow.instance().player_adapter is not None:
            # stop the timer immediately so it does not trigger again <-- right at the beginning
            self.ready_timer.stop()
            role = self._network_role
            if role == "OBSERVER":
                from gui.controllers.observer_controller import GameObserverController

                self.observer_ctrl = GameObserverController()
                print("Observer role detected. Starting observer game in background.")
            else:
                self.game_ctrl = GameController(is_network=True)
