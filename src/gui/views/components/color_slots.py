from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtCore import Qt
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
        self.setFixedSize(30, 30)
        self.color = None
        self.selected = False

    def set_selected(self, selected: bool):
        self.selected = selected
        self.update()

    def set_color(self, color):
        self.color = color
        self.update()

    def reset_color(self):
        self.color = None
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        fill = QColor("lightgray") if self.color is None else QColor(COLOR_MAP[self.color])

        # Fill circle
        painter.setBrush(fill)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(self.rect())

        # Border circle
        if self.selected:
            painter.setPen(QColor("yellow"))
        else:
            painter.setPen(QColor("black"))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(self.rect().adjusted(1, 1, -1, -1))
