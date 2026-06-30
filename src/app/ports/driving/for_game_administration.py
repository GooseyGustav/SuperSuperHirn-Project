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
        """Starts the game.

        Raises:
            ValueError: If the game configuration or the choice of players is invalid.
        """

    @abstractmethod
    def exit_application(self) -> None:
        """Exits the application (closes the entire program)."""

    @abstractmethod
    def restart_game(self) -> None:
        """Restarts the game (clears the board and starts a new game).

        Raises:
             ValueError: If the game configuration or the choice of players is invalid.
        """

    @abstractmethod
    def abort_game(self) -> None:
        """Aborts the game (clears the board and stops the game)."""

    @abstractmethod
    def interrupt_game(self) -> None:
        """Interrupts the game (saves the game for a later time and stops it)."""

    @abstractmethod
    def resume_interrupted(self) -> None:
        """Resumes the interrupted game (loads the saved game and continues the game).

        Raises:
            ValueError: If the game configuration or saved game data is invalid (corrupt save).
        """

    @abstractmethod
    def start_game_delete_interrupted(self) -> None:
        """Starts the game and deletes the interrupted game (clears the board and
        starts a new game).

        Raises:
            ValueError: If the game configuration or the choice of players is invalid.
        """

    @abstractmethod
    def start_network_game(self, network_address: str, gamer_id: str) -> None:
        """Starts the game with a remote player. The App connects to the remote player's
        network address and provides the User's Gamer ID. The implementer is responsible for
        validating the network address and gamer ID.

        Args:
            network_address: IP:port or URL ("http://" or "https://" optional.)
            gamer_id: the user's gamer ID

        Raises:
            ValueError: data or protocol failure :
                - invalid network address: empty, no host, bad/missing port (IP always needs port)
                - invalid gameid or mismatch with remote player's game configuration (nr of positions, colors)
            ConnectionError: network connection failure (HTTP failure):
                - can't reach remote player
                - connection lost during game (--> aborts game round)

        Note:
            Raised Errors -> driving adapter can fix and retry (GUI: ask input again)
            Illegal move from remote player during game -> logged, game round aborted silently (no error raise).
        """
