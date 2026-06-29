from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal

from gui.views.components.color import Color
from gui.views.components.game_attempt_board import AttemptsBoard

class GameView(QWidget):

    color_selected = pyqtSignal(object)
    submit_pressed = pyqtSignal()
    key_delete_pressed = pyqtSignal()
    key_enter_pressed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        self.submit_enabled = False
        self._setup_layout()
        self._setup_ui_admin_stuff()
        self._setup_secret_code()
        self._setup_attempts_board()
        self._setup_color_picker()
    
    def _setup_layout(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        self.margin_widget = QWidget()
        self.margin_layout = QVBoxLayout(self.margin_widget)
        self.margin_layout.setSpacing(8)

        self.ui_admin_stuff  = QWidget()
        self.secret_code     = QWidget()
        self.attempts_board  = QWidget()
        self.color_picker    = QWidget()

        self.margin_layout.addWidget(self.ui_admin_stuff,  10)
        self.margin_layout.addWidget(self.secret_code,     10)
        self.margin_layout.addWidget(self.attempts_board,  70)
        self.margin_layout.addWidget(self.color_picker,    10)

        outer_layout.addWidget(self.margin_widget)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        h_margin = int(self.width()  * 0.03)
        v_margin = int(self.height() * 0.03)
        self.margin_layout.setContentsMargins(h_margin, v_margin, h_margin, v_margin)
    
    # ── Boxes ─────────────────────────────────────────────────────────────────

    def _setup_ui_admin_stuff(self):
        self.ui_admin_stuff.setStyleSheet("background: #4A90D9;")
        layout = QHBoxLayout(self.ui_admin_stuff)
        layout.setContentsMargins(0, 0, 0, 0)

        submit_btn = QPushButton("Submit")
        submit_btn.clicked.connect(self.submit_pressed.emit)
        layout.addWidget(submit_btn)
        # add child widgets here

    def _setup_secret_code(self):
        self.secret_code.setStyleSheet("background: #E67E22;")
        layout = QHBoxLayout(self.secret_code)
        layout.setContentsMargins(0, 0, 0, 0)
        # add child widgets here

    def _setup_attempts_board(self):
        self.attempts_board.setStyleSheet("background: #27AE60;")
        layout = QVBoxLayout(self.attempts_board)
        layout.setContentsMargins(0, 0, 0, 0)

        self.game_attempt_board = AttemptsBoard()

        layout.addWidget(self.game_attempt_board)
        # add child widgets here
    
    def display_color(self, color):
        print(color)

    def _setup_color_picker(self):
        self.color_picker.setStyleSheet("background: #8E44AD;")
        layout = QHBoxLayout(self.color_picker)
        layout.setContentsMargins(0, 0, 0, 0)

        for color in Color:
            button = QPushButton(color.name.capitalize())
            button.clicked.connect(
                lambda checked=False, c=color: self.color_selected.emit(c)
            )
            layout.addWidget(button)
    
    def set_submit_enabled(self, value: bool):
        self.submit_enabled = value

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Backspace:
            print("backspace pressed")
            self.key_delete_pressed.emit()
        elif event.key() == Qt.Key.Key_Return:
            print("enter pressed")
            self.key_enter_pressed.emit()
        else:
            super().keyPressEvent(event)

"""
#  ------------------ Version: CC1.0 ------------------

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal

# from gui.color import Color
from gui.views.components.color_slot import ColorSlot
from gui.views.components.attempts_board import AttemptsBoard

NUM_SLOTS = 5


class GameView(QWidget):
    color_selected = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_layout()
        self._setup_ui_admin_stuff()
        self._setup_secret_code()
        self._setup_attempts_board()  # replaces placeholder after layout is built
        self._setup_color_picker()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _setup_layout(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        from PyQt6.QtWidgets import QSizePolicy

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        self.margin_widget = QWidget()
        self.margin_layout = QVBoxLayout(self.margin_widget)
        self.margin_layout.setSpacing(8)

        self.ui_admin_stuff = QWidget()
        self.secret_code    = QWidget()
        self.attempts_board = QWidget()
        self.color_picker   = QWidget()

        self.margin_layout.addWidget(self.ui_admin_stuff,  10)
        self.margin_layout.addWidget(self.secret_code,     10)
        self.margin_layout.addWidget(self.attempts_board,  70)
        self.margin_layout.addWidget(self.color_picker,    10)

        outer_layout.addWidget(self.margin_widget, 1)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        h_margin = int(self.width()  * 0.03)
        v_margin = int(self.height() * 0.03)
        self.margin_layout.setContentsMargins(h_margin, v_margin, h_margin, v_margin)

    # ── Boxes ─────────────────────────────────────────────────────────────────

    def _setup_ui_admin_stuff(self):
        self.ui_admin_stuff.setStyleSheet("background: #4A90D9;")
        layout = QHBoxLayout(self.ui_admin_stuff)
        layout.setContentsMargins(0, 0, 0, 0)

    def _setup_secret_code(self):
        self.secret_code.setStyleSheet("background: #E67E22;")
        self.guess_slots = [ColorSlot() for _ in range(NUM_SLOTS)]
        layout = QHBoxLayout(self.secret_code)
        layout.setContentsMargins(0, 0, 0, 0)
        for slot in self.guess_slots:
            layout.addWidget(slot)

    def _setup_attempts_board(self):
        # Remove the placeholder and insert the real widget at the same position
        placeholder = self.attempts_board
        index = self.margin_layout.indexOf(placeholder)
        self.margin_layout.removeWidget(placeholder)
        placeholder.deleteLater()

        self.attempts_board = AttemptsBoard()
        self.margin_layout.insertWidget(index, self.attempts_board)

    def _setup_color_picker(self):
        self.color_picker.setStyleSheet("background: #8E44AD;")
        layout = QHBoxLayout(self.color_picker)
        layout.setContentsMargins(0, 0, 0, 0)
        for color in Color:
            btn = QPushButton(color.name.capitalize())
            btn.clicked.connect(lambda checked=False, c=color: self.color_selected.emit(c))
            layout.addWidget(btn)

    # ── Public API ────────────────────────────────────────────────────────────

    def display_color(self, color: Color):
        slot = self._next_empty_slot()
        if slot:
            slot.set_color(color)

    def _next_empty_slot(self):
        for slot in self.guess_slots:
            if not slot.filled:
                return slot
        return None

"""