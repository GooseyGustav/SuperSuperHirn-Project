from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QLabel, QPushButton, QVBoxLayout, QWidget


class HomeView(QWidget):
    game_continue_requested = pyqtSignal()
    game_new_requested = pyqtSignal()
    network_game_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    credits_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._title_label = None
        self._setup()

    def _setup(self):
        self.setObjectName("HomeRoot")
        self.setStyleSheet(
            """
            QWidget#HomeRoot {
                background-color: #1e1e2f;
            }
            QFrame#TitleBar {
                background-color: #16162a;
                border-bottom: 1px solid #2d2d44;
            }
            QLabel#TitleLabel {
                color: #1e1e2f;
            }
            QFrame#Card {
                background-color: #262638;
                border-radius: 14px;
                border: 1px solid #34344a;
            }
            QLabel#CardTitle {
                color: #1e1e2f;
                font-size: 12px;
                font-weight: 600;
                padding-left: 4px;
            }
            QPushButton {
                background-color: #2d2d44;
                color: #f0f0f5;
                border: none;
                border-radius: 10px;
                padding: 14px;
                padding-left: 18px;
                font-size: 15px;
                font-weight: 500;
                text-align: left;
            }
            QPushButton:hover { background-color: #3d3d5c; }
            QPushButton:pressed { background-color: #52527a; }
            QPushButton#PrimaryButton { background-color: Indigo; }
            QPushButton#PrimaryButton:hover { background-color: #6c6ce8; }
            QPushButton#PrimaryButton:pressed { background-color: #4a4ac0; }
        """
        )

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ---- Title bar: full-width strip, independent of button width ----
        title_bar = QFrame()
        title_bar.setObjectName("TitleBar")
        title_layout = QVBoxLayout(title_bar)
        title_layout.setContentsMargins(20, 28, 20, 24)

        title = QLabel("GRAND MASTERMIND")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_font.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 115)
        title.setFont(title_font)
        title_layout.addWidget(title)
        self._title_label = title

        root_layout.addWidget(title_bar)

        # ---- Content area ----
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(40, 32, 40, 40)
        content_layout.setSpacing(20)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # "Play" card
        play_card = QFrame()
        play_card.setObjectName("Card")
        play_layout = QVBoxLayout(play_card)
        play_layout.setContentsMargins(18, 16, 18, 18)
        play_layout.setSpacing(10)

        play_title = QLabel("▶  PLAY")
        play_title.setObjectName("CardTitle")
        play_layout.addWidget(play_title)

        btn_game_new = QPushButton("New Game")
        btn_game_new.setObjectName("PrimaryButton")
        btn_game_continue = QPushButton("Resume Game")
        btn_network_game = QPushButton("Network Game")

        for btn in (btn_game_new, btn_game_continue, btn_network_game):
            self._style_button(btn)
            play_layout.addWidget(btn)

        content_layout.addWidget(play_card)

        # "More" card
        options_card = QFrame()
        options_card.setObjectName("Card")
        options_layout = QVBoxLayout(options_card)
        options_layout.setContentsMargins(18, 16, 18, 18)
        options_layout.setSpacing(10)

        options_title = QLabel("⚙  MORE")
        options_title.setObjectName("CardTitle")
        options_layout.addWidget(options_title)

        btn_settings = QPushButton("Settings")
        btn_credits = QPushButton("Credits")

        for btn in (btn_settings, btn_credits):
            self._style_button(btn)
            options_layout.addWidget(btn)

        content_layout.addWidget(options_card)
        content_layout.addStretch()

        root_layout.addWidget(content)

        # signal wiring (unchanged)
        btn_game_continue.clicked.connect(self.game_continue_requested.emit)
        btn_game_new.clicked.connect(self.game_new_requested.emit)
        btn_network_game.clicked.connect(self.network_game_requested.emit)
        btn_settings.clicked.connect(self.settings_requested.emit)
        btn_credits.clicked.connect(self.credits_requested.emit)

    def _style_button(self, btn: QPushButton):
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setMinimumHeight(46)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 120))
        btn.setGraphicsEffect(shadow)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._title_label is not None:
            width = self.width()
            size = max(14, min(24, width // 20))
            font = self._title_label.font()
            font.setPointSize(size)
            self._title_label.setFont(font)
