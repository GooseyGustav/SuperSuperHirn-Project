from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy
from PyQt6.QtCore import Qt
from gui.views.components.color import Color
from gui.views.components.color_slots import ColorSlot

NUM_ROWS  = 10
NUM_SLOTS = 5


class FeedbackPeg(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(14, 14)
        self.reset()

    def set_black(self):
        self.setStyleSheet("background: #111; border-radius: 7px;")

    def set_white(self):
        self.setStyleSheet("background: white; border: 1px solid #aaa; border-radius: 7px;")

    def reset(self):
        self.setStyleSheet("background: #ccc; border-radius: 7px;")


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
            slot.reset()


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

    def set_guess(self, colors: list[Color]):
        self.guess.set_guess(colors)

    def set_feedback(self, black_count: int, white_count: int):
        self.feedback.set_feedback(black_count, white_count)

    def reset(self):
        self.guess.reset()
        self.feedback.reset()


class AttemptsBoard(QWidget):
    def __init__(self):
        super().__init__()
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
