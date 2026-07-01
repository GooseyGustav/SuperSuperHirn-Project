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
        self.home_view.game_new_requested.connect(self._new_game_updated)
        self.home_view.settings_requested.connect(self._go_to_settings)
        self.home_view.credits_requested.connect(self._go_to_credits)

    def _new_game(self):
        from gui.controllers.game_ui_controller import GameController

        self.ui_service_adapter.on_start_game()
        self.game_ctrl = GameController()

    def _new_game_updated(self):
        from gui.controllers.codemaker_controller import GameCodemakerController
        from gui.controllers.game_ui_controller import GameController
        from gui.controllers.observer_controller import GameObserverController

        self.ui_service_adapter.on_start_game()

        config = self.ui_service_adapter.on_load_config()
        print(config)

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

        self.ui_service_adapter.on_start_network_game("123.123.123.123", "1")
        self.game_ctrl = GameController()

    def _go_to_settings(self):
        from gui.controllers.config_controller import ConfigController

        self.config_ctrl = ConfigController()

    def _go_to_credits(self):
        from gui.controllers.credits_controller import CreditsController

        self.credits_ctrl = CreditsController()
