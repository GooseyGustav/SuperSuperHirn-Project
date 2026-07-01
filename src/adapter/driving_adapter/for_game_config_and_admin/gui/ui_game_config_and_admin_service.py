from app.ports.driving.for_configuring_game import ForConfiguringGame
from app.ports.driving.for_game_administration import ForGameAdministration


class UiGameConfigAndAdminAdapter:
    def __init__(self, for_configuring_game: ForConfiguringGame, for_game_administration: ForGameAdministration):
        self.for_configuring_game = for_configuring_game
        self.for_game_administration = for_game_administration

    def on_load_config(self) -> dict:
        return self.for_configuring_game.load_config()

    def on_save_config(self, save_data: dict) -> None:
        self.for_configuring_game.save_config(save_data)

    def on_reset_config(self) -> None:
        self.for_configuring_game.reset_config()

    def on_start_game(self) -> None:
        self.for_game_administration.start_game()

    def on_start_game_delete_interrupted(self) -> None:
        self.for_game_administration.start_game_delete_interrupted()

    def on_interrupt_game(self) -> None:
        self.for_game_administration.interrupt_game()

    def on_abort_game(self) -> None:
        self.for_game_administration.abort_game()

    def on_start_network_game(self, ip_adress: str, gamer_id: int, role: str) -> None:
        self.for_game_administration.start_network_game(ip_adress, gamer_id, role)

    def on_resume_interrupted(self) -> None:
        self.for_game_administration.resume_interrupted()

    def on_exit_application(self) -> None:
        self.for_game_administration.exit_application()
