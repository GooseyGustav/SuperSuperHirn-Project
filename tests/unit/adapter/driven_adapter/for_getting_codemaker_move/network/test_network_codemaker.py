from unittest.mock import MagicMock

import pytest

from adapter.driven_adapter.for_getting_codemaker_move.network.network_codemaker import NetworkCodemaker


@pytest.fixture
def mock_network_manager():
    """Provides a mocked NetworkManager."""
    return MagicMock()


@pytest.fixture
def network_codemaker(mock_network_manager):
    """Provides a configured NetworkCodemaker instance enforcing 5 positions and 8 colors."""
    return NetworkCodemaker(network_manager=mock_network_manager, gamerid="Team_Superhirn", positions=5, colors=8)


# ---------- Initialization Tests ----------


def test_initialization(network_codemaker):
    """Ensure the adapter initializes with the correct state (gameid = 0)."""
    assert network_codemaker.gamerid == "Team_Superhirn"
    assert network_codemaker.positions == 5
    assert network_codemaker.colors == 8
    assert network_codemaker.current_gameid == 0


# ---------- Handshake Tests (UC-19) ----------


def test_start_network_session_success(network_codemaker, mock_network_manager):
    """Starting a session should send gameid=0 and store the returned ID."""
    # Arrange
    mock_network_manager.post_json.return_value = {
        "gameid": 42,
        "gamerid": "Team_Superhirn",
        "positions": 5,
        "colors": 8,
        "value": "",
    }

    expected_payload = {"gameid": 0, "gamerid": "Team_Superhirn", "positions": 5, "colors": 8, "value": ""}

    # Act
    network_codemaker.start_network_session()

    # Assert
    mock_network_manager.post_json.assert_called_once_with(expected_payload)
    assert network_codemaker.current_gameid == 42


def test_start_network_session_missing_gameid(network_codemaker, mock_network_manager):
    """If the server returns an invalid gameid, a ValueError should be raised."""
    # Arrange
    mock_network_manager.post_json.return_value = {
        "gameid": 0,  # Invalid returned ID
        "gamerid": "Team_Superhirn",
        "positions": 5,
        "colors": 8,
        "value": "",
    }

    # Act & Assert
    with pytest.raises(ValueError, match="Server did not return a valid gameid"):
        network_codemaker.start_network_session()


# ---------- Domain Protection Tests ----------


def test_start_network_session_mismatch_positions(network_codemaker, mock_network_manager):
    """If the server forces a different number of positions, raise a ValueError."""
    # Arrange: Valid JSON schema, but wrong domain configuration (4 instead of 5)
    mock_network_manager.post_json.return_value = {
        "gameid": 42,
        "gamerid": "Team_Superhirn",
        "positions": 4,
        "colors": 8,
        "value": "",
    }

    # Act & Assert
    with pytest.raises(ValueError, match="Server mismatch: We requested 5 positions"):
        network_codemaker.start_network_session()


def test_start_network_session_mismatch_colors(network_codemaker, mock_network_manager):
    """If the server forces a different number of colors, raise a ValueError."""
    # Arrange: Valid JSON schema, but wrong domain configuration (6 instead of 8)
    mock_network_manager.post_json.return_value = {
        "gameid": 42,
        "gamerid": "Team_Superhirn",
        "positions": 5,
        "colors": 6,
        "value": "",
    }

    # Act & Assert
    with pytest.raises(ValueError, match="Server mismatch: We requested 8 colors"):
        network_codemaker.start_network_session()


# ---------- Feedback Tests (UC-20) ----------


def test_get_feedback_success(network_codemaker, mock_network_manager):
    """A guess list should be sent as a string, and the string response parsed into a list."""
    # Arrange
    network_codemaker.current_gameid = 42  # Simulate an active session

    mock_network_manager.post_json.return_value = {
        "gameid": 42,
        "gamerid": "Team_Superhirn",
        "positions": 5,
        "colors": 8,
        "value": "887",  # The feedback string from the server
    }

    # 5 positions long, using colors up to 8
    guess_list = [1, 2, 8, 4, 5]
    secret_code = []  # Ignored by network adapter

    expected_payload = {
        "gameid": 42,
        "gamerid": "Team_Superhirn",
        "positions": 5,
        "colors": 8,
        "value": "12845",  # The adapter must convert the 5-item list to this string!
    }

    # Act
    feedback_list = network_codemaker.get_feedback(secret_code, guess_list)

    # Assert
    mock_network_manager.post_json.assert_called_once_with(expected_payload)
    assert feedback_list == [8, 8, 7]
