import logging
import time

import requests

from app.ports.driven.for_getting_moves.for_getting_codemaker_move import ForGettingCodemakerMove
from network.network_manager import NetworkManager


class NetworkCodemaker(ForGettingCodemakerMove):
    """Drives the network communication to fetch codemaker feedback.

    This adapter acts as the bridge between the domain logic (working with integer lists)
    and the external HTTP server (working with JSON strings and maintaining a gameid).
    """

    MAX_RESEND_ATTEMPTS = 10
    RETRY_PAUSE_SECONDS = 0.5

    def __init__(self, network_manager: NetworkManager, gamerid: str, positions: int, colors: int) -> None:
        """Initialize the network adapter.

        Args:
            network_manager: The infrastructure class handling HTTP POSTs.
            gamerid: The unique identifier for the player/team.
            positions: The number of pins in the game.
            colors: The total number of available colors.
        """
        self.network_manager = network_manager
        self.gamerid = gamerid
        self.positions = positions
        self.colors = colors
        self.current_gameid = 0

    def start_network_session(self) -> None:
        """Initiate the network handshake to receive a valid gameid.

        Raises:
            ValueError: If the server response lacks a valid non-zero gameid or
                        if the server forces an unsupported game configuration.
            ConnectionError: If there is a connection/HTTP failure.
        """
        payload = self._build_base_payload()
        payload["value"] = ""

        try:
            response = self.network_manager.post_json(payload)
        except requests.RequestException as e:
            # propagates to GameManager._configure_and_run()
            raise ConnectionError(f"Could not connect to remote player: {e}") from e

        # check game id validity
        returned_gameid = response.get("gameid", 0)
        if not returned_gameid or returned_gameid == 0:
            raise ValueError("Server did not return a valid gameid.")

        # check if server's positions and colors match our requested configuration
        if response.get("positions") != self.positions:
            raise ValueError(
                f"Server mismatch: We requested {self.positions} positions, "
                f"but server configured {response.get('positions')}."
            )

        if response.get("colors") != self.colors:
            raise ValueError(
                f"Server mismatch: We requested {self.colors} colors, "
                f"but server configured {response.get('colors')}."
            )

        self.current_gameid = returned_gameid

    def get_secret_code(self) -> list[int]:
        """Provide a dummy secret code for network games.

        Since the real secret code is kept hidden on the remote server, we
        cannot retrieve it. We return a valid dummy code (e.g., all 1s) to
        satisfy the port contract and pass the GameEngine's initial validation.

        Returns:
            list[int]: A valid dummy code matching the configured length.
        """
        # Returns a list of 1s matching the required length, e.g., [1, 1, 1, 1]
        return [1] * self.positions

    def get_feedback(self, secret_code: list[int], guess: list[int]) -> list[int]:
        """Send a guess to the remote server and return the parsed feedback.
        Resends same guess on bad/failed reply (aborts after a maximum number of resends).

        Args:
            secret_code: Ignored in network mode (the remote server holds the secret).
            guess: The codebreaker's guess as a list of integers.

        Returns:
            list[int]: The server's feedback as a list of integers (e.g., [8, 8, 7]).

        Raises:
            ConnectionError: If there is a persistent connection/HTTP failure after
            MAX_RESEND_ATTEMPTS.
            ValueError: If the server persistently sends a malformed or invalid feedback string.
        """
        # Convert guess list to string (e.g., [1, 2, 4, 3] -> "1243")
        guess_string = "".join(str(pin) for pin in guess)

        payload = self._build_base_payload()
        payload["value"] = guess_string

        # System to resend message with guess if we get bad feedback messages
        last_error = None
        for attempt in range(self.MAX_RESEND_ATTEMPTS):
            try:
                response = self.network_manager.post_json(payload)  # raises ValueError or requests exception
                return self._parse_feedback(response)  # raises ValueError if bad feedback
            except (ValueError, requests.RequestException) as e:
                last_error = e
                logging.warning("Bad feedback message: %s", e)
                time.sleep(self.RETRY_PAUSE_SECONDS)
        if isinstance(last_error, requests.RequestException):
            raise ConnectionError(
                f"No connection after {self.MAX_RESEND_ATTEMPTS} attempts: {last_error}"
            ) from last_error
        raise ValueError(f"No valid feedback after {self.MAX_RESEND_ATTEMPTS} attempts ({last_error}).")

    def _build_base_payload(self) -> dict:
        """Create the boilerplate JSON structure required by the server."""
        return {
            "gameid": self.current_gameid,
            "gamerid": self.gamerid,
            "positions": self.positions,
            "colors": self.colors,
        }

    # helper method to raise Errors on bad feedback messages
    def _parse_feedback(self, response: dict) -> list[int]:
        if not isinstance(response, dict):
            raise ValueError(f"response is not a dict: {response!r}")
        value = response.get("value")
        if not isinstance(value, str):
            raise ValueError(f"'value' missing or is not a string: {value!r}")
        if value == "":
            return []
        if not all(char in ("7", "8") for char in value):
            raise ValueError(f"chars are not feedback pegs: {value!r}")
        if len(value) > self.positions:
            raise ValueError(f"feedback too long: {value!r}")
        return [int(char) for char in value]
