from abc import ABC, abstractmethod


class ForGameAdministration(ABC):
    """The port that the User's Adapter uses for passing on the user's
    game administration wishes to the App.

    Note:
        - Implemented by `GameManager` (in src/app).
        - Passed to App by `SupersuperhirnRunner` (src/startup)
        - Called by `UIGameConfigAndAdminService` (in src/gui).
    """

    @abstractmethod
    def start_game(self) -> None:
        """Starts the game."""

    @abstractmethod
    def exit_application(self) -> None:
        """Exits the application (closes the entire program)."""

    @abstractmethod
    def restart_game(self) -> None:
        """Restarts the game (clears the board and starts a new game)."""

    @abstractmethod
    def abort_game(self) -> None:
        """Aborts the game (clears the board and stops the game)."""

    @abstractmethod
    def interrupt_game(self) -> None:
        """Interrupts the game (saves the game for a later time and stops it)."""

    @abstractmethod
    def resume_interrupted(self) -> None:
        """Resumes the interrupted game (loads the saved game and continues the game)."""

    @abstractmethod
    def start_game_delete_interrupted(self) -> None:
        """Starts the game and deletes the interrupted game (clears the board and
        starts a new game)."""
