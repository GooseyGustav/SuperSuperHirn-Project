from adapter.driving_adapter.for_game_config_and_admin.gui.ui_game_config_and_admin_service import (
    UiGameConfigAndAdminAdapter,
)
from gui.views.components.color import Color
from gui.views.game_view import GameView
from gui.views.main_window import MainWindow


class GameController:

    def __init__(self):
        self.game_view = GameView("guess")
        self.round_index = 0
        self.slot_index = 0
        self.guess_list = []
        self.codebreaker = MainWindow.instance().player_adapter.get("codebreaker")
        self.ui_service_adapter: UiGameConfigAndAdminAdapter = MainWindow.instance().ui_service_adapter

        MainWindow.instance().register_view("game", self.game_view)
        MainWindow.instance().navigate_to("game")

        self._connect_events()

    def _connect_events(self):
        self.game_view.exit_game_no_save_pressed.connect(self._on_game_aborted)
        self.game_view.exit_game_save_pressed.connect(self._on_exit_game_save)
        self.game_view.restart_game_pressed.connect(self._on_restart_game)

        self.game_view.color_selected.connect(self._handle_color)
        self.game_view.submit_pressed.connect(self._on_submit)
        self.game_view.key_delete_pressed.connect(self._on_delete)
        self.game_view.key_enter_pressed.connect(self._on_enter)
        self.codebreaker._qt_emitter.guess_requested.connect(self._on_guess_requested)
        self.game_view.key_move_slot.connect(self._on_move_slot)

    def _on_guess_requested(self, attempt_list):
        """Core is waiting for a guess — update the board and arm the submit button."""
        print(attempt_list)
        print("exec1")
        self._update_board(attempt_list)
        self.game_view.game_attempt_board.set_active_slot(self.round_index, self.slot_index)
        self.guess_list = []  # clear previous guess
        self.game_view.set_submit_enabled(True)  # optionally lock until ready

    def _update_board(self, attempt_list):
        print("exec2")
        for i, (_, feedback, _) in enumerate(attempt_list):

            if not feedback:
                black = 0
                white = 0
            else:
                black = feedback.count(8)
                white = feedback.count(7)

            print(white, "white", black, "black")

            self.game_view.game_attempt_board.set_feedback_slots(i, white, black)

    def _handle_color(self, color: Color):
        if len(self.guess_list) >= 5:
            return

        self.add_color_guess_list(color)
        self.game_view.game_attempt_board.set_guess_slot(self.round_index, self.slot_index, color)

        self._change_slot_index(1)

    def _change_slot_index(self, value: int):
        """
        Adds or removes the value from slot_index.
        Keeps slot_index in range [0, 5].
        """
        self.slot_index = max(0, min(5, self.slot_index + value))
        print(self.slot_index)

    def add_color_guess_list(self, color: Color):
        if len(self.guess_list) < 5:
            self.guess_list.append(color)

    def _on_submit(self):
        if len(self.guess_list) == 5:
            print(self.guess_list)
            self.codebreaker.submit_guess(self.guess_list)  # wakes the Core thread
            self.game_view.set_submit_enabled(False)  # lock until next guess_requested
            self.guess_list = []
            self.round_index += 1
            self.slot_index = 0

    def _on_delete(self):
        if not self.guess_list:
            return

        self.guess_list.pop()
        self._change_slot_index(-1)

        # sync cursor to truth
        self.slot_index = len(self.guess_list)

        self.game_view.game_attempt_board.set_guess_slot(self.round_index, self.slot_index, None)

    def _on_enter(self):
        self._on_submit()

    def _on_move_slot(self, delta: int):
        self._change_slot_index(delta)

    # ---------- Game Administration Methods ----------

    def _on_abort_game(self):
        self.ui_service_adapter.on_abort_game()

    def _on_game_aborted(self):
        MainWindow.instance().navigate_to("home")

    def _on_exit_game_save(self):
        self.ui_service_adapter.on_interrupt_game()
        MainWindow.instance().navigate_to("home")

    def _on_game_interrupted(self):
        MainWindow.instance().navigate_to("home")

    def _on_restart_game(self):
        print("exec button 3")
