from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, QSizePolicy, QVBoxLayout, QWidget

from gui.views.components.color import Color
from gui.views.components.color_slots import ColorSlot

NUM_ROWS = 10
NUM_SLOTS = 5


class FeedbackPeg(QWidget):
    BLACK = 1
    WHITE = 2
    EMPTY = 0

    def __init__(self):
        super().__init__()
        self.setFixedSize(14, 14)
        self.state = self.EMPTY

    def set_black(self):
        self.state = self.BLACK
        self.update()

    def set_white(self):
        self.state = self.WHITE
        self.update()

    def reset(self):
        self.state = self.EMPTY
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()

        if self.state == self.BLACK:
            fill = QColor("#111")
            border = None
        elif self.state == self.WHITE:
            fill = QColor("white")
            border = QColor("#aaa")
        else:
            fill = QColor("#ccc")
            border = None

        # Fill circle
        painter.setBrush(fill)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(rect)

        # Optional border (only for white pegs)
        if border:
            painter.setPen(border)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(rect.adjusted(1, 1, -1, -1))


class FeedbackWidget(QWidget):
    """5 pegs: 3 on top row, 2 on bottom row."""

    def __init__(self):
        super().__init__()
        self.setFixedWidth(60)
        grid = QGridLayout(self)
        grid.setContentsMargins(6, 4, 6, 4)
        grid.setSpacing(3)

        self.pegs = [FeedbackPeg() for _ in range(NUM_SLOTS)]
        for col, peg in enumerate(self.pegs[:3]):
            grid.addWidget(peg, 0, col, alignment=Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(self.pegs[3], 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(self.pegs[4], 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)

    def set_feedback(self, black_count: int, white_count: int):
        for i, peg in enumerate(self.pegs):
            if i < black_count:
                peg.set_black()
            elif i < black_count + white_count:
                peg.set_white()
            else:
                peg.reset()

    def reset(self):
        for peg in self.pegs:
            peg.reset()


class GuessWidget(QWidget):
    """5 color slots arranged horizontally."""

    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(4)

        self.slots: list[ColorSlot] = []
        for _ in range(NUM_SLOTS):
            slot = ColorSlot()
            self.slots.append(slot)
            layout.addWidget(slot)

    def set_guess(self, colors: list[Color]):
        for slot, color in zip(self.slots, colors):
            slot.set_color(color)

    def reset(self):
        for slot in self.slots:
            slot.reset_color()

    def set_slot(self, index: int, color: Color):
        self.slots[index].set_color(color)

    def set_active_slot(self, index: int):
        for i, slot in enumerate(self.slots):
            slot.set_selected(i == index)


class AttemptRow(QWidget):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(0)

        # Left: guess slots
        self.guess = GuessWidget()
        layout.addWidget(self.guess, stretch=3)

        # Middle: spacer (like flex gap in CSS)
        spacer = QWidget()
        spacer.setFixedWidth(20)
        layout.addWidget(spacer)

        # Right: feedback pegs
        self.feedback = FeedbackWidget()
        layout.addWidget(self.feedback, stretch=1)

    def set_slot_selected(self, index: int):
        self.guess.set_active_slot(index)

    def set_guess(self, colors: list[Color]):
        self.guess.set_guess(colors)

    def set_feedback(self, black_count: int, white_count: int):
        self.feedback.set_feedback(black_count, white_count)

    def reset(self):
        self.guess.reset()
        self.feedback.reset()

    def set_slot(self, index: int, color: Color):
        self.guess.set_slot(index, color)


class AttemptsBoard(QWidget):
    def __init__(self):
        super().__init__()
        self.current_row = 0
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.rows: list[AttemptRow] = []
        for _ in range(NUM_ROWS):
            row = AttemptRow()
            self.rows.append(row)
            layout.addWidget(row)

    def set_attempt(self, row_index: int, colors: list[Color], black: int, white: int):
        self.rows[row_index].set_guess(colors)
        self.rows[row_index].set_feedback(black, white)

    def reset(self):
        for row in self.rows:
            row.reset()

    def set_guess_slot(self, row_index: int, col, color):
        self.rows[row_index].set_slot(col, color)

    def set_feedback_slots(self, row_index: int, white, black):
        self.rows[row_index].set_feedback(black, white)

    def set_active_slot(self, row_index: int, slot_index):
        self.rows[row_index].set_slot_selected(slot_index)
