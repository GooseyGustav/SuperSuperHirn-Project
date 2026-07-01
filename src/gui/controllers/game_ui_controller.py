from adapter.driving_adapter.for_game_config_and_admin.gui.ui_game_config_and_admin_service import (
    UiGameConfigAndAdminAdapter,
)
from gui.views.components.color import Color
from gui.views.game_view import GameView
from gui.views.main_window import MainWindow


class GameController:

    def __init__(self, is_network: bool = False):
        self.is_network = is_network
        self.game_view = GameView("guess")
        self.round_index = 0
        self.slot_index = 0
        self.guess_list = []
        self.codebreaker = MainWindow.instance().player_adapter.get("codebreaker")
        self.ui_service_adapter: UiGameConfigAndAdminAdapter = MainWindow.instance().ui_service_adapter

        MainWindow.instance().register_view("game", self.game_view)
        MainWindow.instance().navigate_to("game")

        self._connect_events()

        # Setup timer and network UI states
        self._apply_game_config()

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

        # Connect the timer signal
        self.game_view.time_expired.connect(self._on_time_expired)

    def _on_guess_requested(self, attempt_list):
        """Core is waiting for a guess — update the board and arm the submit button."""
        print(f"Guess requested with history: {attempt_list}")
        self._update_board(attempt_list)
        self.game_view.game_attempt_board.set_active_slot(self.round_index, self.slot_index)
        self.guess_list = []  # clear previous guess
        self.game_view.set_submit_enabled(True)  # optionally lock until ready

        # Start timer for this turn if we are in TIME_TRIAL mode
        if getattr(self, "is_time_trial", False):
            self.game_view.start_timer(self.countdown_millis)

    def _update_board(self, attempt_list):
        for i, (_, feedback, _) in enumerate(attempt_list):
            if not feedback:
                black = 0
                white = 0
            else:
                black = feedback.count(8)
                white = feedback.count(7)

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

    def add_color_guess_list(self, color: Color):
        if len(self.guess_list) < 5:
            self.guess_list.append(color)

    def _on_submit(self) -> None:
        """Handles the submission of a completed guess to the core."""
        if len(self.guess_list) == 5:
            print(f"Submitted guess: {self.guess_list}")

            if getattr(self, "is_time_trial", False):
                self.game_view.stop_timer()

            current_guess = self.guess_list
            self.guess_list = []
            self.round_index += 1
            self.slot_index = 0
            self.game_view.set_submit_enabled(False)

            self.codebreaker.submit_guess(current_guess)

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

    # ---------- Config & Timer Methods ----------

    def _apply_game_config(self) -> None:
        """Reads the configuration and prepares the UI setup (Network Mode & Timer)."""
        self.is_time_trial = False
        self.countdown_millis = 10000

        try:
            # 1. Network Gatekeeper: Adjust UI for network play
            if hasattr(self.game_view, "set_network_mode"):
                self.game_view.set_network_mode(self.is_network)

            # 2. Timer Setup: ONLY activate if we are NOT in a network game
            if not self.is_network:
                config = self.ui_service_adapter.on_load_config()
                mode = str(config.get("gamemode", "")).upper()

                if "TIME" in mode and "TRIAL" in mode:
                    self.is_time_trial = True
                    self.countdown_millis = int(config.get("countdown_millis", 10000))
                    self.game_view.start_timer(self.countdown_millis)

        except Exception as e:
            print(f"Warning: Could not apply config for UI: {e}")

    def _on_time_expired(self) -> None:
        """Called when the TIME_TRIAL countdown reaches 00:00."""
        from PyQt6.QtWidgets import QMessageBox

        QMessageBox.information(self.game_view, "Time's Up!", "You ran out of time! The game is over.")
        self._on_abort_game()
        self._on_game_aborted()

    # ---------- Game Administration Methods ----------

    def _stop_timer_safely(self) -> None:
        """Safely stops the timer before leaving the game view."""
        if getattr(self, "is_time_trial", False):
            try:
                self.game_view.stop_timer()
            except Exception:
                pass

    def _on_abort_game(self):
        self._stop_timer_safely()
        self.ui_service_adapter.on_abort_game()

    def _on_game_aborted(self):
        self._stop_timer_safely()
        MainWindow.instance().navigate_to("home")

    def _on_exit_game_save(self):
        self._stop_timer_safely()
        self.ui_service_adapter.on_interrupt_game()
        MainWindow.instance().navigate_to("home")

    def _on_game_interrupted(self):
        self._stop_timer_safely()
        MainWindow.instance().navigate_to("home")

    def _on_restart_game(self):
        self._stop_timer_safely()
        print("Restart game requested")
