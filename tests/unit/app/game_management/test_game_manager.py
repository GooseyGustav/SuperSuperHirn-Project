from unittest.mock import MagicMock, patch

import pytest

from app.game_management.game_manager import GameManager
from app.ports.driven.for_assembling_players import ForAssemblingPlayers
from app.ports.driven.for_persisting.for_persisting_config import ForPersistingConfig
from app.ports.driven.for_persisting.for_persisting_game import ForPersistingGame

#   As noted in the DocString of the ForPersistingConfig Port:
#   A dict containing configuration selections. Shape:
#                 {
#                     "gamemode":             str,   # CLASSIC | TIME_TRIAL | BLIND_TRIAL
#                     "user_role":            str,   # CODEMAKER | CODEBREAKER | OBSERVER
#                     "network_enabled":      bool,
#                     "countdown_millis":     int,   # TIME_TRIAL countdown time, milliseconds
#                     "delay_millis":         int,   # OBSERVER mode: ms between auto-moves so progress is visible
#                 }
#
# As noted in the DocString of the ForPersistingGame Port:
# game_data: a flat dict that contains all the game data to be saved;
#             describes an interrupted game for future resuming. Shape:
#
#                 {
#                     "gamemode":            str,   # CLASSIC | TIME_TRIAL | BLIND_TRIAL
#                     "gamestate":           str,   # NEW | RUNNING | INTERRUPTED | WON
#                                                   #   | LOST_TIMEOUT | LOST_ATTEMPTS
#                     "number_of_positions": int,   # fixed constant (5), app-injected; snapshot only
#                     "number_of_colors":    int,   # fixed constant (8), app-injected; snapshot only
#                     "max_attempts":        int,   # fixed constant (10), app-injected; snapshot only
#                     "secret_code":         list[int],  # len == codeLength,
#                                                       #   each pin 1..numberOfColors
#                     "attempt_list": [                 # 0..MAX_ATTEMPTS rows
#                         {
#                             "guess": list[int],    # len == number_of_positions (fixed constant)
#                             "feedback": {
#                                 "black_pins": int,  # 0..codeLength
#                                 "white_pins": int,  # 0..codeLength,
#                                                    #   black + white <= codeLength
#                                 "status":    str,  # FINAL | PROVISIONAL
#                             },
#                         },
#                         ...
#                     ],
#                     # mode / resume extras:
#                     "remaining_time_millis": int,  # TIME_TRIAL only; milliseconds
#                     "matchup": dict,             # opaque to the core, round-tripped only
#                 }


@pytest.fixture
def persist_config_port_mock():
    return MagicMock(spec=ForPersistingConfig)


@pytest.fixture
def assembling_players_port_mock():
    return MagicMock(spec=ForAssemblingPlayers)


@pytest.fixture
def persist_game_port_mock():
    return MagicMock(spec=ForPersistingGame)


@pytest.fixture
def game_manager(persist_config_port_mock, assembling_players_port_mock, persist_game_port_mock):
    return GameManager(persist_config_port_mock, assembling_players_port_mock, persist_game_port_mock)


@pytest.fixture
def valid_config_dict():
    return {
        "gamemode": "CLASSIC",
        "user_role": "CODEMAKER",
        "network_enabled": False,
        "countdown_millis": 15,
        "delay_millis": 5,
    }


# ----- GameManager: load_config / save_config -----


def test_load_config_returns_port_dict(game_manager, persist_config_port_mock, valid_config_dict):
    persist_config_port_mock.load_config_dict.return_value = valid_config_dict
    assert game_manager.load_config() == valid_config_dict
    persist_config_port_mock.load_config_dict.assert_called_once()


def test_load_config_invalid_not_accepted(game_manager, persist_config_port_mock):
    persist_config_port_mock.load_config_dict.return_value = {"gamemode": "KNOCK KNOCK"}
    with pytest.raises(ValueError):
        game_manager.load_config()


def test_save_config_valid_persisted(game_manager, persist_config_port_mock, valid_config_dict):
    game_manager.save_config(valid_config_dict)
    persist_config_port_mock.save_config_dict.assert_called_once_with(valid_config_dict)


def test_save_config_invalid_not_persisted(game_manager, persist_config_port_mock):
    with pytest.raises(ValueError):
        game_manager.save_config({"gamemode": "KNOCK KNOCK"})
    persist_config_port_mock.save_config_dict.assert_not_called()


# ----- GameManager: _validate_config -----


def test_validate_config_valid_passes(valid_config_dict):
    try:
        GameManager._validate_config(valid_config_dict)
    except Exception as e:
        pytest.fail(f"Valid config should not raise: {e}")


@pytest.mark.parametrize(
    "field, invalid_value",
    [
        ("gamemode", "KNOCK KNOCK"),
        ("user_role", "BRB"),
        ("network_enabled", "True"),
        ("countdown_millis", -10),
        ("delay_millis", -1),
    ],
)
def test_validate_config_rejects_invalid(valid_config_dict, field, invalid_value):
    invalid = {**valid_config_dict, field: invalid_value}
    with pytest.raises(ValueError):
        GameManager._validate_config(invalid)


# ----- GameManager: reset_config -----


def test_reset_config_resets_to_default_delegates(game_manager, persist_config_port_mock):
    game_manager.reset_config()
    persist_config_port_mock.reset_to_default.assert_called_once()


# ----- GameManager: interrupt_game -----


def test_interrupt_game_delegates(game_manager, persist_game_port_mock):
    fake_game_engine = MagicMock()
    fake_game_engine.create_game_persist_object.return_value = {"gamestate": "INTERRUPTED"}
    game_manager._game_engine = fake_game_engine
    game_manager.interrupt_game()
    fake_game_engine.create_game_persist_object.assert_called_once()
    persist_game_port_mock.save_game.assert_called_once_with({"gamestate": "INTERRUPTED"})


@patch("app.game_management.game_manager.GameEngine")
def test_start_game_delete_interrupted_deletes_then_starts(
    mock_engine_class,  # prevents using the real GameEngine class
    game_manager,
    persist_game_port_mock,
    persist_config_port_mock,
    assembling_players_port_mock,
    valid_config_dict,
):
    persist_config_port_mock.load_config_dict.return_value = valid_config_dict
    assembling_players_port_mock.assemble_players.return_value = (MagicMock(), MagicMock())
    game_manager.start_game_delete_interrupted()
    persist_game_port_mock.delete_game.assert_called_once()
    assembling_players_port_mock.assemble_players.assert_called_once()


# ----- GameManager: start_game -----

# need patch to mock GameEngine class and GameEngine.run() because of
# tight coupling to GameEngine


@patch("app.game_management.game_manager.GameEngine")
def test_start_game_runs_and_persists(
    mock_engine_class,
    game_manager,
    persist_config_port_mock,
    assembling_players_port_mock,
    persist_game_port_mock,
    valid_config_dict,
):
    persist_config_port_mock.load_config_dict.return_value = valid_config_dict
    codemaker, codebreaker = MagicMock(), MagicMock()
    assembling_players_port_mock.assemble_players.return_value = (codemaker, codebreaker)
    engine = mock_engine_class.return_value
    engine.create_game_persist_object.return_value = {"gamestate": "WON"}
    game_manager.start_game()
    engine.run.assert_called_once_with(codemaker, codebreaker)
    engine.create_game_persist_object.assert_called_once()
    persist_game_port_mock.save_game.assert_called_once_with({"gamestate": "WON"})
