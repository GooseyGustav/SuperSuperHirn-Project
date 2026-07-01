from gui.views.game_view import GameView
from gui.views.main_window import MainWindow
from gui.views.components.color import Color

from adapter.driving_adapter.for_game_config_and_admin.gui.ui_game_config_and_admin_service import UiGameConfigAndAdminAdapter
from adapter.driven_adapter.for_getting_codemaker_move.gui.gui_codemaker import GuiCodemaker


class GameCodemakerController():

    def __init__(self):
        self.codemaker_mode = "secret"
        self.round_index = 0
        self.slot_index = 0
        self.secret_list = []
        self.feedback_list = []
        self.game_view = GameView(self.codemaker_mode)
        self.codemaker: GuiCodemaker = MainWindow.instance().player_adapter.get("codemaker")
        self.ui_service_adapter: UiGameConfigAndAdminAdapter = MainWindow.instance().ui_service_adapter
        
        MainWindow.instance().register_view("game", self.game_view)
        MainWindow.instance().navigate_to("game")

        self._connect_events()

    def _connect_events(self):
        self.game_view.exit_game_no_save_pressed.connect(self._on_game_aborted)
        self.game_view.exit_game_save_pressed.connect(self._on_exit_game_save)
        self.game_view.restart_game_pressed.connect(self._on_restart_game)

        self.game_view.color_selected.connect(self._handle_color_input)
        self.game_view.feedback_color_selected.connect(self._handle_feedback_input)
        self.game_view.submit_pressed.connect(self._on_submit)
        self.game_view.key_delete_pressed.connect(self._on_delete)
        self.game_view.key_enter_pressed.connect(self._on_submit)
        self.codemaker._qt_emitter.secret_code_requested.connect(self._on_secret_code_requested)
        self.codemaker._qt_emitter.feedback_requested.connect(self._on_feedback_requested)
    

    def _on_secret_code_requested(self):
        pass
        

    def _on_feedback_requested(self, secret: list[int], guess: list[int]):
        self.update_board_current_guess(guess)

    def _on_guess_requested(self, attempt_list):
        """Core is waiting for a guess — update the board and arm the submit button."""
        print(attempt_list)
        print("exec1")
        self._update_board(attempt_list)
        self.game_view.game_attempt_board.set_active_slot(self.round_index, self.slot_index)
        self.guess_list = []                        # clear previous guess
        self.game_view.set_submit_enabled(True)     # optionally lock until ready
        
    def _update_board(self, attempt_list):
        for i, (_, feedback, _) in enumerate(attempt_list):

            if not feedback:
                black = 0
                white = 0
            else:
                black = feedback.count(8)
                white = feedback.count(7)
            
            print(white, "white", black, "black")

            self.game_view.game_attempt_board.set_feedback_slots(i, white, black)
    
    def update_board_current_guess(self, guess: list[int]):
        row = self.round_index

        # update only the current row
        for col, value in enumerate(guess):
            self.game_view.game_attempt_board.set_guess_slot(
                row,
                col,
                value
            )
    def _handle_color_input(self, color: Color):
        if self.codemaker_mode in ("secret", "guess"):
            self._handle_secret_input(color)
        elif self.codemaker_mode == "feedback":
            self._handle_feedback_input(color)

    def _handle_secret_input(self, color: Color):
        if len(self.secret_list) >= 5:
            return

        self.add_color_secret_list(color)
        self.game_view.secret_code_widget.set_guess(self.secret_list)

        self._change_slot_index(1)
    
    def _handle_feedback_input(self, color: Color):
        if len(self.feedback_list) >= 5:
            return

        self.add_color_feedback_list(color)

        white = self.feedback_list.count(Color.WHITE)
        black = self.feedback_list.count(Color.BLACK)

        self.game_view.game_attempt_board.set_feedback_slots(
            self.round_index,
            white,
            black,
        )
    
    def _change_slot_index(self, value: int):
        """
        Adds or removes the value from slot_index.
        Keeps slot_index in range [0, 5].
        """
        self.slot_index = max(0, min(5, self.slot_index + value))
        print(self.slot_index)        
    
    def add_color_secret_list(self, color: Color):
        if len(self.secret_list) < 5:
            self.secret_list.append(color)
    
    def add_color_feedback_list(self, color: Color):
        if len(self.feedback_list) < 5:
            self.feedback_list.append(color)
            print(self.feedback_list)

    def _on_delete(self):
        if not self.secret_list:
            return

        self.secret_list.pop()
        self._change_slot_index(-1)

        # sync cursor to truth
        self.slot_index = len(self.secret_list)

        self.game_view.game_attempt_board.set_guess_slot(
            self.round_index,
            self.slot_index,
            None
        )

    def _on_submit(self):
        if self.codemaker_mode == "secret":
            if len(self.secret_list) == 5:
                print(self.secret_list)
                self.codemaker.submit_secret_code(self.secret_list)
                self.codemaker_mode = "feedback"
                self.game_view._setup_color_picker(self.codemaker_mode)

        elif self.codemaker_mode == "feedback":
            all_black = False

            if len(self.feedback_list) == 5:
                all_black = all(color == Color.BLACK for color in self.feedback_list)

            print(f"submitting list {self.feedback_list}")
            self.codemaker.submit_feedback(self.feedback_list)

            if all_black:
                MainWindow.instance().navigate_to("home")

            self.feedback_list = []
            self.round_index += 1
            self.slot_index = 0

            if self.round_index == 10:
                MainWindow.instance().navigate_to("home")

    def _on_move_slot(self, delta: int):
        self._change_slot_index(delta)


    # ---------- Game Administration Methods ----------

    def _on_abort_game(self):
        self.ui_service_adapter.on_abort_game()
    
    def _on_game_aborted(self):
        MainWindow.instance().navigate_to("home")

    def _on_exit_game_save(self):
        self.ui_service_adapter.on_interrupt_game()

    def _on_game_interrupted(self):
        MainWindow.instance().navigate_to("home")

    def _on_restart_game(self):
        print("exec button 3")