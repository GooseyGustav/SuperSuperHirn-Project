from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QWidget


class HomeView(QWidget):
    game_continue_requested = pyqtSignal()
    game_new_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    credits_requested = pyqtSignal()

    def __init__(self):
        super().__init__()

        self._setup()

    def _setup(self):
        layout = QVBoxLayout(self)

        btn_game_continue = QPushButton("Spiel fortsetzen")
        btn_game_new = QPushButton("Spiel Starten")
        btn_settings = QPushButton("Einstellungen")
        btn_credits = QPushButton("Credits")

        btn_game_continue.clicked.connect(self.game_continue_requested.emit)
        btn_game_new.clicked.connect(self.game_new_requested.emit)
        btn_settings.clicked.connect(self.settings_requested.emit)
        btn_credits.clicked.connect(self.credits_requested.emit)

        layout.addWidget(btn_game_continue)
        layout.addWidget(btn_game_new)
        layout.addWidget(btn_settings)
        layout.addWidget(btn_credits)
