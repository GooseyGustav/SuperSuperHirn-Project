import requests


class NetworkManager:
    """Handles HTTP POST communication and strict JSON schema validation.

    This class ensures that all outgoing and incoming HTTP traffic conforms
    strictly to the predefined Superhirn JSON schema before any data reaches
    the domain logic.
    """

    def __init__(self, server_url: str, timeout: int = 5) -> None:
        """Initialize the network manager with a target URL and timeout.

        Args:
            server_url: The full URL to the remote server endpoint.
            timeout: Maximum time in seconds to wait for a response.
        """
        self.server_url = server_url
        self.timeout = timeout

    def post_json(self, payload: dict) -> dict:
        """Send a validated JSON payload and return the validated response.

        Args:
            payload: The dictionary to send as JSON.

        Returns:
            dict: The parsed and validated JSON response from the server.

        Raises:
            ValueError: If the payload or response violates the schema.
            requests.exceptions.RequestException: On network or HTTP errors.
        """
        # 1. Validate outgoing data (UC-21)
        self._validate_schema(payload)

        # 2. Perform HTTP POST request (UC-19, UC-20)
        response = requests.post(self.server_url, json=payload, timeout=self.timeout)

        # Will raise an HTTPError for status codes 4xx and 5xx
        response.raise_for_status()

        # 3. Decode JSON response
        try:
            response_data = response.json()
        except ValueError as e:
            raise ValueError(f"Server returned invalid JSON format: {e}")

        # 4. Validate incoming data (UC-21)
        self._validate_schema(response_data)

        return response_data

    def _validate_schema(self, payload: dict) -> None:
        """Validate a dictionary against the strict Superhirn schema.

        Args:
            payload: The dictionary to validate.

        Raises:
            ValueError: If any key is missing, types are wrong, or values
                        are out of allowed bounds.
        """
        expected_types = {"gameid": int, "gamerid": str, "positions": int, "colors": int, "value": str}

        # Check for missing keys and incorrect data types
        for key, expected_type in expected_types.items():
            if key not in payload:
                raise ValueError(f"Missing required key: '{key}'")

            # Note: In Python, bool is a subclass of int. We must explicitly reject bools.
            value = payload[key]
            if type(value) is not expected_type:
                raise ValueError(
                    f"Invalid type for '{key}': expected {expected_type.__name__}, " f"got {type(value).__name__}"
                )

        # Check domain-specific boundaries
        positions = payload["positions"]
        if not (1 <= positions <= 9):
            raise ValueError(f"Value out of bounds for 'positions': {positions} (must be 1-9).")

        colors = payload["colors"]
        if not (1 <= colors <= 8):
            raise ValueError(f"Value out of bounds for 'colors': {colors} (must be 1-8).")
