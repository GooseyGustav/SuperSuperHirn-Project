from unittest.mock import MagicMock, patch

import pytest
import requests

from network.network_manager import NetworkManager


@pytest.fixture
def valid_payload() -> dict:
    """Provides a valid JSON payload according to UC-21."""
    return {"gameid": 0, "gamerid": "TestTeam", "positions": 4, "colors": 6, "value": ""}


@pytest.fixture
def valid_response() -> dict:
    """Provides a valid JSON response from the server."""
    return {"gameid": 42, "gamerid": "TestTeam", "positions": 4, "colors": 6, "value": "887"}


@pytest.fixture
def network_manager() -> NetworkManager:
    """Provides a configured NetworkManager instance."""
    return NetworkManager(server_url="http://dummy.url/api", timeout=1)


# ---------- Tests for Schema Validation (UC-21) ----------


def test_validate_schema_with_valid_payload(network_manager, valid_payload):
    """A perfectly formatted payload should pass silently."""
    try:
        network_manager._validate_schema(valid_payload)
    except ValueError as e:
        pytest.fail(f"Validation failed unexpectedly: {e}")


def test_validate_schema_missing_key(network_manager, valid_payload):
    """A payload missing a required key should raise a ValueError."""
    del valid_payload["gameid"]
    with pytest.raises(ValueError, match="Missing required key"):
        network_manager._validate_schema(valid_payload)


def test_validate_schema_wrong_type(network_manager, valid_payload):
    """A payload with an incorrect data type should raise a ValueError."""
    valid_payload["positions"] = "4"  # Should be int, not str
    with pytest.raises(ValueError, match="Invalid type"):
        network_manager._validate_schema(valid_payload)


def test_validate_schema_out_of_bounds(network_manager, valid_payload):
    """A payload with values outside the allowed range should raise a ValueError."""
    valid_payload["colors"] = 9  # Allowed is 1-8
    with pytest.raises(ValueError, match="Value out of bounds"):
        network_manager._validate_schema(valid_payload)


# ---------- Tests for HTTP POST (UC-19 & UC-20) ----------


@patch("src.network.network_manager.requests.post")
def test_post_json_success(mock_post, network_manager, valid_payload, valid_response):
    """A successful POST request should return the validated response dictionary."""
    # Arrange: Mock the HTTP response
    mock_response = MagicMock()
    mock_response.json.return_value = valid_response
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    # Act
    result = network_manager.post_json(valid_payload)

    # Assert
    mock_post.assert_called_once_with("http://dummy.url/api", json=valid_payload, timeout=1)
    assert result == valid_response


@patch("src.network.network_manager.requests.post")
def test_post_json_http_error(mock_post, network_manager, valid_payload):
    """An HTTP error (e.g., 404, 500) should raise a RequestException."""
    # Arrange: Simulate a 404 Not Found error
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
    mock_post.return_value = mock_response

    # Act & Assert
    with pytest.raises(requests.exceptions.HTTPError):
        network_manager.post_json(valid_payload)


@patch("src.network.network_manager.requests.post")
def test_post_json_invalid_incoming_response(mock_post, network_manager, valid_payload):
    """If the server returns invalid JSON formatting, it should be caught and raise a ValueError."""
    # Arrange: Server returns a payload missing the 'value' key
    invalid_response = {
        "gameid": 42,
        "gamerid": "TestTeam",
        "positions": 4,
        "colors": 6,
        # 'value' is missing
    }

    mock_response = MagicMock()
    mock_response.json.return_value = invalid_response
    mock_post.return_value = mock_response

    # Act & Assert
    with pytest.raises(ValueError, match="Missing required key"):
        network_manager.post_json(valid_payload)
