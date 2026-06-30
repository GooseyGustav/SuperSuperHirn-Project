from PyQt6.QtWidgets import QWidget
from gui.views.components.color import Color

COLOR_MAP = {
    Color.RED:    "red",
    Color.GREEN:  "green",
    Color.YELLOW: "yellow",
    Color.BLUE:   "blue",
    Color.ORANGE: "orange",
    Color.BROWN:  "brown",
    Color.WHITE:  "white",
    Color.BLACK:  "black",
}

class ColorSlot(QWidget):
    def __init__(self):
        super().__init__()
        print("exec")
        self.setStyleSheet("background: #123123;")
        self.setMinimumSize(20, 20)
        self.filled = False
        self._set_empty()

    def set_color(self, color: Color):
        self.setStyleSheet(
            f"background-color: {COLOR_MAP[color]}; border: 1px solid black; border-radius: 20%;"
        )
        self.filled = True

    def reset(self):
        self._set_empty()

    def _set_empty(self):
        self.setStyleSheet("background-color: lightgray; border: 1px solid black;")
        self.filled = False