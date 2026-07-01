from gui.views.game_view import GameView
from gui.views.main_window import MainWindow
from gui.views.components.color import Color


class GameController():

    def __init__(self):
        self.game_view = GameView()
        self.guess_list = []
        self.codebreaker = MainWindow.instance().player_adapter.get("codebreaker")
        
        MainWindow.instance().register_view("game", self.game_view)
        MainWindow.instance().navigate_to("game")

        self._connect_events()

    def _connect_events(self):
        self.game_view.color_selected.connect(self._handle_color)
        self.game_view.submit_pressed.connect(self._on_submit)
        self.game_view.key_delete_pressed.connect(self._on_delete)
        self.game_view.key_enter_pressed.connect(self._on_enter)
        self.codebreaker._qt_emitter.guess_requested.connect(self._on_guess_requested)
    
    def _on_guess_requested(self, attempt_list):
        """Core is waiting for a guess — update the board and arm the submit button."""
        self._update_board(attempt_list)
        self.guess_list = []                        # clear previous guess
        self.game_view.set_submit_enabled(True)     # optionally lock until ready
        
    def _handle_color(self, color: Color):
        self.add_color_guess_list(color)
        self.game_view.display_color(color)
        print(self.guess_list)
    
    def add_color_guess_list(self, color: Color):
        if len(self.guess_list) < 5:
            self.guess_list.append(color)


    def _on_submit(self):
        if len(self.guess_list) == 5:
            print(self.guess_list)
            self.codebreaker.submit_guess(self.guess_list)  # wakes the Core thread
            self.game_view.set_submit_enabled(False)   # lock until next guess_requested
            self.guess_list = []

    def _update_board(self, attempt_list):
        for i, (guess, feedback, _) in enumerate(attempt_list):
            colors = [Color(v) for v in guess]
            black  = feedback.count(8)
            white  = feedback.count(7)
            print(i, colors, black, white)
            # self.game_view.attempts_board.set_attempt(i, colors, black, white)


    def _on_delete(self):
        if len(self.guess_list) > 0:
            removed = self.guess_list.pop()
            print(self.guess_list)
            # self.game_view.undo_last_color(removed)

    def _on_enter(self):
        self._on_submit()
