from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget


class NetworkConfigView(QWidget):
    # Signals for the controller
    start_requested = pyqtSignal(str, str, str)  # Sends (address, gamer_id, role)
    cancel_requested = pyqtSignal()  # Returns to the main menu

    def __init__(self):
        super().__init__()
        self._setup()

    def _setup(self):
        layout = QVBoxLayout(self)

        # --- Title & Description ---
        lbl_title = QLabel("<b>Start Network Game</b>")
        lbl_desc = QLabel(
            "Connect to a server as a Codebreaker.\n" "The game will start automatically in Classic mode."
        )
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_desc)

        # --- Input fields ---
        self._lbl_address = QLabel("Network Address (URL or IP:Port):")
        self._edit_address = QLineEdit()
        self._edit_address.setPlaceholderText("http://127.0.0.1:8080")
        layout.addWidget(self._lbl_address)
        layout.addWidget(self._edit_address)

        self._lbl_gamer_id = QLabel("Gamer ID:")
        self._edit_gamer_id = QLineEdit()
        self._edit_gamer_id.setPlaceholderText("e.g., Team_Superhirn")
        layout.addWidget(self._lbl_gamer_id)
        layout.addWidget(self._edit_gamer_id)

        # self._lbl_role = QLabel("Select Role:")
        # self._combo_role = QComboBox()
        # self._combo_role.addItems(["CODEBREAKER", "OBSERVER"])
        # layout.addWidget(self._lbl_role)
        # layout.addWidget(self._combo_role)

        # --- Spacer for layout ---
        layout.addStretch()

        # --- Buttons ---
        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Back")
        btn_start = QPushButton("Start Game")

        btn_cancel.clicked.connect(self.cancel_requested.emit)
        btn_start.clicked.connect(self._on_start_clicked)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_start)
        layout.addLayout(btn_row)

    def _on_start_clicked(self):
        """Read the fields, check for empty inputs, and emit the signal."""
        address = self._edit_address.text().strip()
        gamer_id = self._edit_gamer_id.text().strip()
        # role = self._combo_role.currentText()
        role = "CODEBREAKER"  # Default role

        # Basic GUI validation to prevent sending empty strings to the backend
        if not address or not gamer_id:
            QMessageBox.warning(self, "Missing Data", "Please fill out all fields.")
            return

        self.start_requested.emit(address, gamer_id, role)
