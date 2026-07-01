from PyQt6.QtCore import Qt

from adapter.driven_adapter.for_getting_codebreaker_move.cpu.cpu_codebreaker import CpuCodebreaker
from adapter.driven_adapter.for_getting_codemaker_move.cpu.cpu_codemaker import CpuCodemaker
from adapter.driving_adapter.for_game_config_and_admin.gui.ui_game_config_and_admin_service import (
    UiGameConfigAndAdminAdapter,
)
from gui.views.game_view import GameView
from gui.views.main_window import MainWindow


class GameObserverController:
    def __init__(self):
        self.round_index = 0
        self.secret_list = []
        self.guess_list = []
        self.feedback_list = []
        self._pending_interrupt = False
        self.game_view = GameView("observer")
        self.codemaker: CpuCodemaker = MainWindow.instance().player_adapter.get("codemaker")
        self.codebreaker: CpuCodebreaker = MainWindow.instance().player_adapter.get("codebreaker")
        self.ui_service_adapter: UiGameConfigAndAdminAdapter = MainWindow.instance().ui_service_adapter

        MainWindow.instance().register_view("game", self.game_view)
        MainWindow.instance().navigate_to("game")

        self._connect_events()

    def _connect_events(self):
        self.game_view.exit_game_no_save_pressed.connect(self._on_abort_game)

        self.codebreaker.emitter.guess_submitted.connect(self._handle_guess_input, Qt.ConnectionType.QueuedConnection)
        self.codemaker.emitter.secret_submitted.connect(self._handle_secret_input, Qt.ConnectionType.QueuedConnection)
        self.codemaker.emitter.feedback_submitted.connect(
            self._handle_feedback_input, Qt.ConnectionType.QueuedConnection
        )

    def _update_board(self, attempt_list):
        for i, (_, feedback, _) in enumerate(attempt_list):

            if not feedback:
                black = 0
                white = 0
            else:
                black = feedback.count(8)
                white = feedback.count(7)

            self.game_view.game_attempt_board.set_feedback_slots(i, white, black)

    def _handle_guess_input(self, guess: list[int]):
        row = self.round_index

        self.game_view.game_attempt_board.set_guess(row, guess)

        # update only the current row
        for col, value in enumerate(guess):
            self.game_view.game_attempt_board.set_guess_slot(row, col, value)

    def _handle_secret_input(self, secret_list: list[int]):
        self.secret_list = secret_list
        self.game_view.secret_code_widget.set_guess(self.secret_list)

    def _handle_feedback_input(self, feedback: list[int]):
        black = feedback.count(self.codemaker.BLACK_PEG)
        white = feedback.count(self.codemaker.WHITE_PEG)

        self.game_view.game_attempt_board.set_feedback_slots(
            self.round_index,
            white,
            black,
        )

        self.round_index += 1

    # ---------- Game Administration Methods ----------

    def _on_abort_game(self):
        self.ui_service_adapter.on_abort_game()
        MainWindow.instance().navigate_to("home")
