from gui.views.game_view import GameView
from gui.views.main_window import MainWindow

class GameController():
    def __init__(self):
        self.game_view = GameView()

        MainWindow.instance().register_view("game", self.game_view)
        MainWindow.instance().navigate_to("game")

        self._connect_events()

    def _connect_events(self):
        self.game_view.event.connect(self._continue_game)
