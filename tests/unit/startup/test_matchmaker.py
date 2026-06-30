from unittest.mock import patch

import pytest

from startup.matchmaker import Matchmaker

NUMBER_OF_POSITIONS = 5
NUMBER_OF_COLORS = 8
TEST_ADDRESS = "http://1.2.3.4:8080"


@pytest.fixture
def matchmaker():
    return Matchmaker()


@pytest.fixture
def config_for_network_codemaker_valid():
    return {
        "user_role": "CODEBREAKER",
        "network_enabled": True,
        "number_of_positions": NUMBER_OF_POSITIONS,
        "number_of_colors": NUMBER_OF_COLORS,
        "network_address": TEST_ADDRESS,
        "gamer_id": "team13",
    }


@pytest.fixture
def network_participants_patched():
    """Patches the 3 Network Participants.
    Yields network_manager, network_codemaker, gui_codebreaker.
    """
    with (
        patch("startup.matchmaker.NetworkManager") as network_manager,
        patch("startup.matchmaker.NetworkCodemaker") as network_codemaker,
        patch("startup.matchmaker.GuiCodebreaker") as gui_codebreaker,
    ):
        yield network_manager, network_codemaker, gui_codebreaker


# ----- Matchmaker correctly assembles GUI Codebreaker and Network Codemaker -----


def test_network_codemaker_gets_game_manager_address_unchanged(
    matchmaker, config_for_network_codemaker_valid, network_participants_patched
):
    network_manager, network_codemaker, _ = network_participants_patched
    matchmaker.assemble_players(config_for_network_codemaker_valid)

    network_manager.assert_called_once_with(TEST_ADDRESS)  # unchanged
    network_codemaker.return_value.start_network_session.assert_called_once()


def test_no_build_url_in_matchmaker_class():
    assert not hasattr(Matchmaker, "_build_url")  # regression test: no more _build_url


def test_network_game_only_if_user_role_is_codebreaker(matchmaker, config_for_network_codemaker_valid):
    config_user_role_codemaker_invalid = {
        **config_for_network_codemaker_valid,
        "user_role": "CODEMAKER",
    }  # overwrite user_role
    with pytest.raises(ValueError, match="codebreaker"):
        matchmaker.assemble_players(config_user_role_codemaker_invalid)
