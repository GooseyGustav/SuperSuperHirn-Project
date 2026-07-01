from PyQt6.QtWidgets import (QWidget, QPushButton, QVBoxLayout,
QHBoxLayout, QLabel, QComboBox, QSpinBox)

from PyQt6.QtCore import pyqtSignal


class ConfigView(QWidget):
    back_requested = pyqtSignal()           # controller navigates back
    config_load_requested = pyqtSignal()    # controller should load + populate
    config_save_requested = pyqtSignal(dict)  # filled dict will be saved
    config_reset_requested = pyqtSignal()   # adapter will reset to defaults

    def __init__(self):
        super().__init__()
        self._setup()

    def _setup(self):
        layout = QVBoxLayout(self)

        # --- Gamemode ---
        layout.addWidget(QLabel("Gamemode:"))
        self._combo_gamemode = QComboBox()
        self._combo_gamemode.addItems(["CLASSIC", "TIME_TRIAL", "BLIND_TRIAL"])
        layout.addWidget(self._combo_gamemode)

        # --- User Role ---
        layout.addWidget(QLabel("User Role:"))
        self._combo_role = QComboBox()
        self._combo_role.addItems(["CODEMAKER", "CODEBREAKER", "OBSERVER"])
        layout.addWidget(self._combo_role)

        # --- Countdown - only meaningful in TIME_TRIAL, disabled otherwise ---
        layout.addWidget(QLabel("Countdown (ms) - TIME_TRIAL only:"))
        self._spin_countdown = QSpinBox()
        self._spin_countdown.setRange(1000, 60000)
        self._spin_countdown.setSingleStep(500)
        self._spin_countdown.setValue(10000)
        self._spin_countdown.setEnabled(False)  # disabled until TIME_TRIAL selected
        layout.addWidget(self._spin_countdown)

        # --- Delay - only meaningful in OBSERVER role, disabled otherwise ---
        layout.addWidget(QLabel("Delay (ms) - OBSERVER only:"))
        self._spin_delay = QSpinBox()
        self._spin_delay.setRange(100, 5000)
        self._spin_delay.setSingleStep(100)
        self._spin_delay.setValue(300)
        self._spin_delay.setEnabled(False)  # disabled until OBSERVER selected
        layout.addWidget(self._spin_delay)

        # wire combo changes to enable/disable dependent spinboxes
        self._combo_gamemode.currentTextChanged.connect(self._on_gamemode_changed)
        self._combo_role.currentTextChanged.connect(self._on_role_changed)

        # --- Buttons row ---
        btn_row = QHBoxLayout()
        btn_back  = QPushButton("Back")
        btn_save  = QPushButton("Save Config")
        btn_reset = QPushButton("Reset Config")

        btn_back.clicked.connect(self.back_requested.emit)
        btn_save.clicked.connect(self._emit_save)
        btn_reset.clicked.connect(self.config_reset_requested.emit)

        btn_row.addWidget(btn_back)
        btn_row.addWidget(btn_save)
        btn_row.addWidget(btn_reset)
        layout.addLayout(btn_row)

    def _on_gamemode_changed(self, value: str):
        """Enable countdown spinbox only when TIME_TRIAL is selected."""
        self._spin_countdown.setEnabled(value == "TIME_TRIAL")

    def _on_role_changed(self, value: str):
        """Enable delay spinbox only when OBSERVER role is selected."""
        self._spin_delay.setEnabled(value == "OBSERVER")

    def _emit_save(self):
        """Collect widget values into the config dict and emit the signal.
        network_enabled is always False here — network is started from the home screen,
        not configured here, and GameManager overwrites this field at game-start anyway.
        """
        self.config_save_requested.emit({
            "gamemode":         self._combo_gamemode.currentText(),
            "user_role":        self._combo_role.currentText(),
            "network_enabled":  False,
            "countdown_millis": self._spin_countdown.value(),
            "delay_millis":     self._spin_delay.value(),
        })

    def populate(self, config_dict: dict):
        """Fill all widgets from a loaded config dict (called by controller on load/reset)."""
        if "gamemode" in config_dict:
            idx = self._combo_gamemode.findText(config_dict["gamemode"])
            if idx >= 0:
                self._combo_gamemode.setCurrentIndex(idx)

        if "user_role" in config_dict:
            idx = self._combo_role.findText(config_dict["user_role"])
            if idx >= 0:
                self._combo_role.setCurrentIndex(idx)

        if "countdown_millis" in config_dict:
            self._spin_countdown.setValue(config_dict["countdown_millis"])

        if "delay_millis" in config_dict:
            self._spin_delay.setValue(config_dict["delay_millis"])
