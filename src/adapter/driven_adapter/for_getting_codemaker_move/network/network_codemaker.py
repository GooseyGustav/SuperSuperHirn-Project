from app.ports.driven.for_getting_moves.for_getting_codemaker_move import ForGettingCodemakerMove
from network.network_manager import NetworkManager


class NetworkCodemaker(ForGettingCodemakerMove):
    """Drives the network communication to fetch codemaker feedback.

    This adapter acts as the bridge between the domain logic (working with integer lists)
    and the external HTTP server (working with JSON strings and maintaining a gameid).
    """

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
            ValueError: If the server response lacks a valid non-zero gameid,
                        or if the server forces an unsupported game configuration.
        """
        payload = self._build_base_payload()
        payload["value"] = ""

        response = self.network_manager.post_json(payload)

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

        Args:
            secret_code: Ignored in network mode (the remote server holds the secret).
            guess: The codebreaker's guess as a list of integers.

        Returns:
            list[int]: The server's feedback as a list of integers (e.g., [8, 8, 7]).
        """
        # Convert guess list to string (e.g., [1, 2, 4, 3] -> "1243")
        guess_string = "".join(str(pin) for pin in guess)

        payload = self._build_base_payload()
        payload["value"] = guess_string

        response = self.network_manager.post_json(payload)

        # Convert feedback string to list (e.g., "887" -> [8, 8, 7])
        feedback_string = response.get("value", "")
        feedback_list = [int(char) for char in feedback_string]

        return feedback_list

    def _build_base_payload(self) -> dict:
        """Create the boilerplate JSON structure required by the server."""
        return {
            "gameid": self.current_gameid,
            "gamerid": self.gamerid,
            "positions": self.positions,
            "colors": self.colors,
        }
