from unittest.mock import MagicMock, patch

import pytest
import requests

from adapter.driven_adapter.for_getting_codemaker_move.network.network_codemaker import NetworkCodemaker

GAME_ID_NOT_ZER0 = 42
POSITIONS_VALID_5 = 5
COLORS_VALID_8 = 8
GAMER_ID_VALID = "Team_Superhirn"


@pytest.fixture
def network_manager_mock():
    """Provides a mocked NetworkManager."""
    return MagicMock()


@pytest.fixture
def network_codemaker(network_manager_mock):
    """Provides a configured NetworkCodemaker instance enforcing 5 positions and 8 colors."""
    return NetworkCodemaker(network_manager=network_manager_mock, gamerid="Team_Superhirn", positions=5, colors=8)


# ---------- Initialization Tests ----------


def test_initialization(network_codemaker):
    """Ensure the adapter initializes with the correct state (gameid = 0)."""
    assert network_codemaker.gamerid == "Team_Superhirn"
    assert network_codemaker.positions == 5
    assert network_codemaker.colors == 8
    assert network_codemaker.current_gameid == 0


# ---------- Handshake Tests (UC-19) ----------


def test_start_network_session_success(network_codemaker, network_manager_mock):
    """Starting a session should send gameid=0 and store the returned ID."""
    # Arrange
    network_manager_mock.post_json.return_value = {
        "gameid": GAME_ID_NOT_ZER0,
        "gamerid": "Team_Superhirn",
        "positions": 5,
        "colors": 8,
        "value": "",
    }

    expected_payload = {"gameid": 0, "gamerid": "Team_Superhirn", "positions": 5, "colors": 8, "value": ""}

    # Act
    network_codemaker.start_network_session()

    # Assert
    network_manager_mock.post_json.assert_called_once_with(expected_payload)
    assert network_codemaker.current_gameid == GAME_ID_NOT_ZER0


def test_start_network_session_missing_gameid(network_codemaker, network_manager_mock):
    """If the server returns an invalid gameid, a ValueError should be raised."""
    # Arrange
    network_manager_mock.post_json.return_value = {
        "gameid": 0,  # Invalid returned ID
        "gamerid": "Team_Superhirn",
        "positions": 5,
        "colors": 8,
        "value": "",
    }

    # Act & Assert
    with pytest.raises(ValueError, match="Server did not return a valid gameid"):
        network_codemaker.start_network_session()


def test_handshake_raises_connection_error(network_codemaker, network_manager_mock):
    network_manager_mock.post_json.side_effect = requests.ConnectionError("refused")
    with pytest.raises(ConnectionError, match="Could not connect"):
        network_codemaker.start_network_session()


# ---------- Domain Protection Tests ----------


def test_start_network_session_mismatch_positions(network_codemaker, network_manager_mock):
    """If the server forces a different number of positions, raise a ValueError."""
    # Arrange: Valid JSON schema, but wrong domain configuration (4 instead of 5)
    network_manager_mock.post_json.return_value = {
        "gameid": GAME_ID_NOT_ZER0,
        "gamerid": "Team_Superhirn",
        "positions": 4,
        "colors": 8,
        "value": "",
    }

    # Act & Assert
    with pytest.raises(ValueError, match="Server mismatch: We requested 5 positions"):
        network_codemaker.start_network_session()


def test_start_network_session_mismatch_colors(network_codemaker, network_manager_mock):
    """If the server forces a different number of colors, raise a ValueError."""
    # Arrange: Valid JSON schema, but wrong domain configuration (6 instead of 8)
    network_manager_mock.post_json.return_value = {
        "gameid": GAME_ID_NOT_ZER0,
        "gamerid": "Team_Superhirn",
        "positions": 5,
        "colors": 6,
        "value": "",
    }

    # Act & Assert
    with pytest.raises(ValueError, match="Server mismatch: We requested 8 colors"):
        network_codemaker.start_network_session()


# ---------- Feedback Tests (UC-20) ----------


def test_get_feedback_success(network_codemaker, network_manager_mock):
    """A guess list should be sent as a string, and the string response parsed into a list."""
    # Arrange
    network_codemaker.current_gameid = GAME_ID_NOT_ZER0  # Simulate an active session

    network_manager_mock.post_json.return_value = {
        "gameid": GAME_ID_NOT_ZER0,
        "gamerid": "Team_Superhirn",
        "positions": 5,
        "colors": 8,
        "value": "887",  # The feedback string from the server
    }

    # 5 positions long, using colors up to 8
    guess_list = [1, 2, 8, 4, 5]
    secret_code = []  # Ignored by network adapter

    expected_payload = {
        "gameid": GAME_ID_NOT_ZER0,
        "gamerid": "Team_Superhirn",
        "positions": 5,
        "colors": 8,
        "value": "12845",  # The adapter must convert the 5-item list to this string!
    }

    # Act
    feedback_list = network_codemaker.get_feedback(secret_code, guess_list)

    # Assert
    network_manager_mock.post_json.assert_called_once_with(expected_payload)
    assert feedback_list == [8, 8, 7]


@patch("adapter.driven_adapter.for_getting_codemaker_move.network.network_codemaker.time.sleep")
def test_get_feedback_request_exception_passed_on_as_connection_error(
    sleep,
    network_codemaker,
    network_manager_mock,
):
    network_codemaker.current_gameid = GAME_ID_NOT_ZER0
    network_manager_mock.post_json.side_effect = requests.RequestException("down")
    with pytest.raises(ConnectionError, match="No connection after"):  # no request Exc through core
        network_codemaker.get_feedback([], [1, 2, 3, 4, 5])
    assert network_manager_mock.post_json.call_count == network_codemaker.MAX_RESEND_ATTEMPTS


@patch("adapter.driven_adapter.for_getting_codemaker_move.network.network_codemaker.time.sleep")
def test_feedback_invalid_bad_data_passed_as_value_error(
    sleep,
    network_codemaker,
    network_manager_mock,
):
    network_codemaker.current_gameid = GAME_ID_NOT_ZER0

    network_manager_mock.post_json.return_value = {  # invalid feedback data
        "gameid": GAME_ID_NOT_ZER0,
        "gamerid": GAMER_ID_VALID,
        "positions": POSITIONS_VALID_5,
        "colors": COLORS_VALID_8,
        "value": "1",
    }

    with pytest.raises(ValueError, match="No valid feedback after"):
        network_codemaker.get_feedback([], [1, 2, 3, 4, 5])


@patch("adapter.driven_adapter.for_getting_codemaker_move.network.network_codemaker.time.sleep")
def test_get_feedback_one_connection_fail_retry_successs(
    sleep,
    network_codemaker,
    network_manager_mock,
):
    network_codemaker.current_gameid = GAME_ID_NOT_ZER0

    feedback_valid = network_manager_mock.post_json.return_value = {  # invalid feedback data
        "gameid": GAME_ID_NOT_ZER0,
        "gamerid": GAMER_ID_VALID,
        "positions": POSITIONS_VALID_5,
        "colors": COLORS_VALID_8,
        "value": "778",
    }

    network_manager_mock.post_json.side_effect = [requests.RequestException("down"), feedback_valid]
    assert network_codemaker.get_feedback([], [1, 2, 3, 4, 5]) == [7, 7, 8]
    assert network_manager_mock.post_json.call_count == 2
