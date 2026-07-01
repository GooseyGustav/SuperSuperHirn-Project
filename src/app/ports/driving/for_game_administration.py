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

        Note:
            Runs on a worker thread because main thread must stay free for GUI.
            Consequence: Config/assembly errors do NOT raise synchronously to the caller.
            They are logged (and, if wired, emitted via the executor's error signal).
            A synchronous try/except here catches nothing. # TODO fix threading issue
        """

    @abstractmethod
    def exit_application(self) -> None:
        """Exits the application (closes the entire program).

        Note:
            No automatic game saving --> does not raise Error.
        """

    @abstractmethod
    def restart_game(self) -> None:
        """Restarts the game (clears the board and starts a new game).

        Raises:
             ValueError: If the game configuration or the choice of players is invalid.

        Note:
            Runs on a worker thread because main thread must stay free for GUI.
            Consequence: Config/assembly errors do NOT raise synchronously to the caller.
            They are logged (and, if wired, emitted via the executor's error signal).
            A synchronous try/except here catches nothing. # TODO fix threading issue
        """

    @abstractmethod
    def abort_game(self) -> None:
        """Aborts the game (clears the board and stops the game).

        Note:
            No game saving --> does not raise Error."""

    @abstractmethod
    def interrupt_game(self) -> None:
        """Interrupts the game (saves the game for a later time and stops it).

        Raises:
            OSError: could not write the save file.
        """

    @abstractmethod
    def resume_interrupted(self) -> None:
        """Resumes the interrupted game (loads the saved game and continues the game).

        Raises:
            CorruptedSaveError (a custom Exception): saved game exists but is malformed
            (offer to delete, start new).
            ValueError: game configuration or matchup is invalid.
            OSError: failure reading saved game file (permission or disk error).

        Note:
            Missing saved game file -> start new game (no Error raise).
        """

    @abstractmethod
    def start_game_delete_interrupted(self) -> None:
        """Starts the game and deletes the interrupted game (clears the board and
        starts a new game).

        Raises:
            ValueError: If the game configuration or the choice of players is invalid.

        Note:
            Runs on a worker thread because main thread must stay free for GUI.
            Consequence: Config/assembly errors do NOT raise synchronously to the caller.
            They are logged (and, if wired, emitted via the executor's error signal).
            A synchronous try/except here catches nothing. # TODO fix threading issue
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
