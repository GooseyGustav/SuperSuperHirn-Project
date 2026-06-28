from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QWidget


class MainWindow(QMainWindow):
    _instance = None

    def __init__(self, ui_service_adapter):
        super().__init__()
        MainWindow._instance = self
        self.ui_service_adapter = ui_service_adapter
        self.player_adapter: dict = None
        self.translator = None

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        from ..controllers.home_controller import HomeController
        self.home_controller = HomeController()

        self.show()

    @staticmethod
    def instance():
        return MainWindow._instance

    def navigate_to(self, name: str):
        widget = self._stack.findChild(QWidget, name)
        if widget:
            self._stack.setCurrentWidget(widget)

    def register_view(self, name: str, view: QWidget):
        view.setObjectName(name)
        self._stack.addWidget(view)

    def set_ui_adapter(self, player_adapter: dict):
        self.home_controller.set_gui_adapter(player_adapter)

    def get_service_adapter(self):
        return self.ui_service_adapter
