from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QWidget


class CreditsView(QWidget):
    """Credits screen — displays team, project info, and repository link.

    Emits back_requested when the user wants to return to the home screen.
    Styled with a monospace font for a subtle retro feel, matching the
    default background of the rest of the app.
    """

    back_requested = pyqtSignal()

    # shared retro font used across all labels
    _FONT_MONO = QFont("Courier New", 10)
    _FONT_TITLE = QFont("Courier New", 16, QFont.Weight.Bold)
    _FONT_NAME = QFont("Courier New", 11, QFont.Weight.Bold)
    _FONT_SMALL = QFont("Courier New", 9)

    def __init__(self):
        super().__init__()
        self._setup()

    def _setup(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(40, 30, 40, 20)

        # --- Title ---
        layout.addWidget(self._label("* SUPERSUPERHIRN *", self._FONT_TITLE))
        layout.addWidget(self._label("SoSe 2026  |  HTW Berlin  |  Gruppe 13", self._FONT_SMALL))

        layout.addWidget(self._rule())

        # --- About ---
        layout.addWidget(self._label("A student project — developed as a full project team", self._FONT_MONO))
        layout.addWidget(self._label("in the Software Engineering 2 course at HTW Berlin.", self._FONT_MONO))
        layout.addWidget(self._label("A digital reimagining of the classic Mastermind board game.", self._FONT_MONO))
        layout.addWidget(self._label("5 pins  |  8 colors  |  3 game modes", self._FONT_SMALL))

        layout.addWidget(self._rule())

        # --- Team ---
        layout.addWidget(self._label("[ THE TEAM ]", self._FONT_MONO))
        layout.addSpacing(6)

        team = [
            ("Ky Anh", "Head of Requirements Engineering"),
            ("Elo", "Head of Project Coordination"),
            ("Marlon", "Lead Developer"),
            ("Felix", "Software Architect"),
            ("Matti", "Head of Quality Assurance"),
        ]
        for name, role in team:
            layout.addWidget(self._label(name, self._FONT_NAME))
            layout.addWidget(self._label(role, self._FONT_SMALL))
            layout.addSpacing(4)

        layout.addWidget(self._rule())

        # --- Built with ---
        layout.addWidget(self._label("[ BUILT WITH ]", self._FONT_MONO))
        layout.addWidget(self._label("Python 3  |  PyQt6  |  Hexagonal Architecture", self._FONT_SMALL))

        layout.addWidget(self._rule())

        # --- GitLab link ---
        link = QLabel(
            '<a href="https://gitlab.rz.htw-berlin.de/Elodie.Viennot/sose26_superhirn_13">GitLab Repository</a>'
        )
        link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        link.setFont(self._FONT_MONO)
        link.setOpenExternalLinks(True)  # opens in system browser on click
        layout.addWidget(link)

        layout.addWidget(self._rule())

        # --- Footer ---
        layout.addWidget(self._label("(c) 2026  Gruppe 13  |  HTW Berlin", self._FONT_SMALL))

        layout.addStretch()

        # --- Back button ---
        btn_back = QPushButton("< Back")
        btn_back.setFont(self._FONT_MONO)
        btn_back.clicked.connect(self.back_requested.emit)
        layout.addWidget(btn_back)

    def _label(self, text: str, font: QFont) -> QLabel:
        """Centered label with the given retro font."""
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(font)
        return label

    def _rule(self) -> QFrame:
        """Thin horizontal line used as a section separator."""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        return line
