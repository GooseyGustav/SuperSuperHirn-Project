from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal

from gui.views.components.color import Color
from gui.views.components.game_attempt_board import AttemptsBoard, FeedbackWidget, GuessWidget
from gui.views.components.color_slots import ColorSlot

class GameView(QWidget):

    # ----- Admin Events -----
    exit_game_no_save_pressed = pyqtSignal()
    exit_game_save_pressed = pyqtSignal()
    restart_game_pressed = pyqtSignal()

    # ----- Color Picker -----
    color_selected = pyqtSignal(object)
    submit_pressed = pyqtSignal()
    feedback_color_selected = pyqtSignal(object)

    # ----- Key Events -----
    key_delete_pressed = pyqtSignal()
    key_enter_pressed = pyqtSignal()
    key_move_slot = pyqtSignal(int)

    def __init__(self, mode: str, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        self.submit_enabled = False
        self.player_mode: str = mode
        self._setup_layout()
        self._setup_ui_admin_stuff()
        self._setup_secret_code(self.player_mode)
        self._setup_attempts_board()
        self._setup_color_picker(self.player_mode)
    
    def _setup_layout(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        self.margin_widget = QWidget()
        self.margin_layout = QVBoxLayout(self.margin_widget)
        self.margin_layout.setSpacing(8)

        self.ui_admin_stuff = QWidget()
        if self.player_mode in ("secret", "guess"):
            self.secret_code = QWidget()
        self.attempts_board = QWidget()
        self.color_picker = QWidget()

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
        self.ui_admin_stuff.setStyleSheet("background-color: #4A90D9;")
        layout = QHBoxLayout(self.ui_admin_stuff)

        # Left side
        left_layout = QHBoxLayout()

        left_layout.setContentsMargins(10, 10, 10, 10) 
        left_layout.setSpacing(8)

        btn_no_save_exit = QPushButton("NoSaveExit")
        btn_no_save_exit.clicked.connect(self.exit_game_no_save_pressed.emit)

        btn_save_exit = QPushButton("SaveExit")
        btn_save_exit.clicked.connect(self.exit_game_save_pressed.emit)

        btn_restart = QPushButton("Restart")
        btn_restart.clicked.connect(self.restart_game_pressed.emit)

        left_layout.addWidget(btn_no_save_exit)
        left_layout.addWidget(btn_save_exit)
        left_layout.addWidget(btn_restart)

        # Empty space to the right of the buttons
        left_layout.addStretch()

        # Right side
        right_layout = QVBoxLayout()

        right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        right_layout.addWidget(QLabel("Top"))
        right_layout.addWidget(QLabel("Bottom"))

        # Add layouts with stretch factors
        layout.addLayout(left_layout, 3)   # 60%
        layout.addLayout(right_layout, 2)  # 40%

    def _setup_secret_code(self, mode):
        if mode in ("guess"):
            return
        
        self.secret_code.setStyleSheet("background: #E67E22;")

        layout = QHBoxLayout(self.secret_code)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(0)

        # Guess slots
        self.secret_code_widget = GuessWidget()
        layout.addWidget(self.secret_code_widget, stretch=3)

        # Same spacer as AttemptRow
        spacer = QWidget()
        spacer.setFixedWidth(20)
        layout.addWidget(spacer)

        # Placeholder with same width as FeedbackWidget
        placeholder = QWidget()
        placeholder.setFixedWidth(60)   # same as FeedbackWidget
        layout.addWidget(placeholder, stretch=1)

    def _setup_attempts_board(self):
        self.attempts_board.setStyleSheet("""
            background-color: BurlyWood;
            border: 3px solid red;
        """)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.game_attempt_board = AttemptsBoard()

        layout.addWidget(self.game_attempt_board)

        self.attempts_board.setLayout(layout)

    def _setup_color_picker(self, mode):
        self.color_picker.setStyleSheet("background: #8E44AD;")

        # clear previous widgets
        layout = self.color_picker.layout()
        if layout is None:
            layout = QHBoxLayout(self.color_picker)
            layout.setContentsMargins(10, 10, 10, 10)
        else:
            self._clear_layout(layout)

        if mode in ("secret", "guess"):
            for color in Color:
                button = QPushButton(color.name.capitalize())

                button.clicked.connect(
                    lambda checked=False, c=color:
                        self.color_selected.emit(c)
                )
                layout.addWidget(button)

        elif mode == "feedback":
            button_white = QPushButton("White")
            button_white.clicked.connect(
                lambda: self.color_selected.emit(Color.WHITE)
            )

            button_black = QPushButton("Black")
            button_black.clicked.connect(
                lambda: self.color_selected.emit(Color.BLACK)
            )

            layout.addWidget(button_white)
            layout.addWidget(button_black)
        
        submit_btn = QPushButton("Submit") 
        submit_btn.clicked.connect(self.submit_pressed.emit) 
        layout.addWidget(submit_btn)
    
    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
    
    def set_submit_enabled(self, value: bool):
        self.submit_enabled = value

    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key.Key_Backspace:
            self.key_delete_pressed.emit()

        elif key == Qt.Key.Key_Return:
            self.key_enter_pressed.emit()

        # elif key == Qt.Key.Key_Left:
        #     self.key_move_slot.emit(-1)

        # elif key == Qt.Key.Key_Right:
        #     self.key_move_slot.emit(1)

        else:
            super().keyPressEvent(event)
