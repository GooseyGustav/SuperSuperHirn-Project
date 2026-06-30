from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout

from PyQt6.QtCore import pyqtSignal


class ConfigView(QWidget):
    config_load_requested = pyqtSignal()
    config_save_requested = pyqtSignal(dict)
    config_reset_requested = pyqtSignal()

    def __init__(self):
        super().__init__()

        self._setup()

    def _setup(self):
        layout = QVBoxLayout(self)

        btn_save_config = QPushButton("Save Config")
        btn_reset_config = QPushButton("Reset Config")

        btn_save_config.clicked.connect(lambda: self.config_save_requested.emit({"SomeDummyKey1": "SomeDummyValue1"}))
        btn_reset_config.clicked.connect(self.config_reset_requested.emit)

        layout.addWidget(btn_save_config)
        layout.addWidget(btn_reset_config)
