from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal


class GameView(QWidget):

    event = pyqtSignal()

    def __init__(self):
        super().__init__()

        self._setup()

    def _setup(self):
        self.setWindowTitle("Running Game")
        self.setMinimumSize(550, 450)