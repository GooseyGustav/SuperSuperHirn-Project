from gui.views.credits_view import CreditsView
from gui.views.main_window import MainWindow


class CreditsController:
    """Controller for the credits screen.

    Registers CreditsView with MainWindow and wires the back button
    to navigate back to the home screen.
    """

    def __init__(self):
        self.credits_view = CreditsView()

        MainWindow.instance().register_view("credits", self.credits_view)
        MainWindow.instance().navigate_to("credits")

        self.credits_view.back_requested.connect(self._go_back)

    def _go_back(self):
        """Navigate back to the home screen."""
        MainWindow.instance().navigate_to("home")
