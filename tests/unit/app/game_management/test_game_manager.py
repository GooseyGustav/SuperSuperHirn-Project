from unittest.mock import MagicMock, patch

import pytest

from app.game_management.game_manager import GameManager
from app.game_model.game_state import Gamestate
from app.ports.driven.for_assembling_players import ForAssemblingPlayers
from app.ports.driven.for_persisting.for_persisting_config import ForPersistingConfig
from app.ports.driven.for_persisting.for_persisting_game import ForPersistingGame
from app.ports.driven.for_persisting.save_errors import CorruptedSaveError

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
#

# number constants
COUNTDOWN_MILLIS_DEFAULT = 15000
DELAY_MILLIS_DEFAULT = 500
COUNTDOWN_MILLIS_ZERO = 0
DELAY_MILLIS_ZERO = 0


class _SyncExecutor:
    """Test double for `game_management.ThreadExecutor` that runs work inline instead of
    on a thread.

    GameManager.start_game() calls `_configure_and_run()`, whose real `self.executor` is a
    daemon thread (`ThreadExecutor`) so the GUI is responsive.
    In tests: race condition where assert runs before thread finishes --> tests fail.
    Solution: fake executor that runs synchronously. `_SyncExecutor.run(method)` executes
    `method` synchronously --> state final as soon aas `stat_game()` returns.
    Real executor swapped for test double by `game_manager` fixture.
    """

    def run(self, method):
        method()


@pytest.fixture
def game_manager(persist_config_port_mock, assembling_players_port_mock, persist_game_port_mock):
    """GameManager fixture with mocks for all driven ports and a synchronous executor.

    Real `ThreadExecutor` runs `start_game()` on a daemon thread. Here: swap `executor`
    with `_SyncExecutor` so `start_game()` paths always run synchronously --> asserts
    deterministic, no `sleep` hack needed. Covers all calls that `start_game()` makes
    (incl. when `restart_game()` and `start_game_delete_interrupted()` call start_game()).
    """
    gm = GameManager(persist_config_port_mock, assembling_players_port_mock, persist_game_port_mock)
    gm.executor = _SyncExecutor()
    return gm


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
def valid_config_dict():
    return {
        "gamemode": "CLASSIC",
        "user_role": "CODEMAKER",
        "network_enabled": False,
        "countdown_millis": COUNTDOWN_MILLIS_DEFAULT,
        "delay_millis": DELAY_MILLIS_DEFAULT,
    }


@pytest.fixture
def config_dict_valid_network_on():
    return {
        "gamemode": "CLASSIC",
        "user_role": "CODEBREAKER",
        "network_enabled": True,
        "countdown_millis": COUNTDOWN_MILLIS_ZERO,
        "delay_millis": DELAY_MILLIS_ZERO,
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


def test_validate_config_network_allows_codebreaker_and_observer(valid_config_dict):
    valid_cb = {**valid_config_dict, "network_enabled": True, "user_role": "CODEBREAKER"}
    GameManager._validate_config(valid_cb)

    valid_obs = {**valid_config_dict, "network_enabled": True, "user_role": "OBSERVER"}
    GameManager._validate_config(valid_obs)


def test_validate_config_network_forbids_codemaker(valid_config_dict):
    invalid = {**valid_config_dict, "network_enabled": True, "user_role": "CODEMAKER"}
    with pytest.raises(ValueError, match="only valid with user_role set to CODEBREAKER or OBSERVER"):
        GameManager._validate_config(invalid)


# ----- GameManager: reset_config -----


def test_reset_config_resets_to_default_delegates(game_manager, persist_config_port_mock):
    game_manager.reset_config()
    persist_config_port_mock.reset_to_default.assert_called_once()


# ----- GameManager: start_game -----

# need patch to mock GameEngine class and GameEngine.run() because of
# tight coupling to GameEngine


@patch("app.game_management.game_manager.GameEngine")
def test_start_game_runs_no_errors(
    mock_engine_class,
    game_manager,
    persist_config_port_mock,
    assembling_players_port_mock,
    persist_game_port_mock,
    valid_config_dict,
):

    # Arrange
    persist_config_port_mock.load_config_dict.return_value = valid_config_dict
    codemaker, codebreaker = MagicMock(), MagicMock()
    assembling_players_port_mock.assemble_players.return_value = (codemaker, codebreaker)
    engine = mock_engine_class.return_value

    # Act
    game_manager.start_game()

    # Assert
    engine.run.assert_called_once_with(codemaker, codebreaker)  # no errors


@pytest.mark.parametrize("run_error", [ValueError("illegal move"), TypeError("not a list")])
@patch("app.game_management.game_manager.GameEngine")
def test_start_game_illegal_move_aborts_without_saving(
    mock_engine_class,
    run_error,
    game_manager,
    persist_config_port_mock,
    assembling_players_port_mock,
    persist_game_port_mock,
    valid_config_dict,
):

    # Arrange
    persist_config_port_mock.load_config_dict.return_value = valid_config_dict
    assembling_players_port_mock.assemble_players.return_value = (MagicMock(), MagicMock())
    engine = mock_engine_class.return_value
    engine.run.side_effect = run_error  # illegal move flagged by engine

    # Act
    game_manager.start_game()  # should not raise error (abort handled internally)

    # Assert
    import time

    time.sleep(0.05)

    persist_game_port_mock.save_game.assert_not_called()
    assert game_manager._game_engine is None
    assert game_manager._config_manager is None


# TODO: solve threading (add thread in test)
#
# @patch("app.game_management.game_manager.GameEngine")
# def test_resume_interrupted_illegal_move_aborts_without_saving(
#     mock_engine_class,
#     game_manager,
#     persist_config_port_mock,
#     assembling_players_port_mock,
#     persist_game_port_mock,
#     valid_config_dict,
# ):
#
#     # Arrange
#     persist_config_port_mock.load_config_dict.return_value = valid_config_dict
#     persist_game_port_mock.load_game.return_value = {"matchup": {}}
#     assembling_players_port_mock.assemble_players.return_value = (MagicMock(), MagicMock())
#     engine = mock_engine_class.return_value
#     engine.run.side_effect = ValueError("illegal move")
#
#     # Act
#     game_manager.resume_interrupted()
#
#     # Assert
#     persist_game_port_mock.save_game.assert_not_called()
#     assert game_manager._game_engine is None
#


@patch("app.game_management.game_manager.GameEngine")
def test_resume_interrupted_corrupt_save_raises_and_resets(
    mock_engine_class,
    game_manager,
    persist_config_port_mock,
    persist_game_port_mock,
    valid_config_dict,
):
    # Arrange
    persist_config_port_mock.load_config_dict.return_value = valid_config_dict
    persist_game_port_mock.load_game.return_value = {"matchup": {}}
    engine = mock_engine_class.return_value
    engine.resume.side_effect = CorruptedSaveError("corrupt save")

    # Act (new: no raise)
    assert game_manager.resume_interrupted() is True

    persist_game_port_mock.save_game.assert_not_called()


def test_resume_interrupted_missing_save_returns_quietly(
    game_manager,
    persist_game_port_mock,
):
    # Arrange
    persist_game_port_mock.load_game.side_effect = FileNotFoundError

    # Act (must not raise)
    game_manager.resume_interrupted()

    # Assert
    persist_game_port_mock.save_game.assert_not_called()
    assert game_manager._game_engine is None


# ------- GameManager: abort_game() works correctly  --------


def test_abort_game_resets_engine_and_config_manager(game_manager):
    engine = MagicMock()
    game_manager._game_engine = engine
    game_manager._config_manager = MagicMock()

    game_manager.abort_game()

    engine.interrupt_game.assert_called_once()
    assert game_manager._game_engine is None
    assert game_manager._config_manager is None


# ------- GameManager: restart_game() works correctly  --------


@patch("app.game_management.game_manager.GameEngine")
def test_restart_game_aborts_then_starts(
    mock_engine_class, game_manager, persist_config_port_mock, assembling_players_port_mock, valid_config_dict
):
    persist_config_port_mock.load_config_dict.return_value = valid_config_dict
    assembling_players_port_mock.assemble_players.return_value = (MagicMock(), MagicMock())

    game_manager.restart_game()

    assembling_players_port_mock.assemble_players.assert_called_once()  # start_game() called assembleplayers port
    mock_engine_class.return_value.run.assert_called_once()


# ----- GameManager: interrupt_game -----


def test_interrupt_game_delegates(game_manager, persist_game_port_mock):
    fake_game_engine = MagicMock()
    fake_game_engine.get_game_obj.return_value.game_state = Gamestate.INTERRUPTED
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


# --- GameManager: game persistence for interrupted game (and only interrupted) ---


@patch("app.game_management.game_manager.GameEngine")
def test_interrupted_during_run_is_persisted(
    mock_engine_class,
    game_manager,
    persist_config_port_mock,
    assembling_players_port_mock,
    persist_game_port_mock,
    valid_config_dict,
):

    # Arrange
    persist_config_port_mock.load_config_dict.return_value = valid_config_dict
    codemaker, codebreaker = MagicMock(), MagicMock()
    assembling_players_port_mock.assemble_players.return_value = (codemaker, codebreaker)
    engine = mock_engine_class.return_value
    engine.get_game_obj.return_value.game_state = Gamestate.INTERRUPTED
    engine.create_game_persist_object.return_value = {"gamestate": Gamestate.INTERRUPTED}

    # Act
    game_manager.start_game()

    # Assert
    engine.run.assert_called_once_with(codemaker, codebreaker)
    engine.create_game_persist_object.assert_called_once()
    persist_game_port_mock.save_game.assert_called_once_with({"gamestate": Gamestate.INTERRUPTED})


@pytest.mark.parametrize("game_state", [Gamestate.WON, Gamestate.LOST_ATTEMPTS, Gamestate.LOST_TIMEOUT])
@patch("app.game_management.game_manager.GameEngine")
def test_finished_game_not_persisted(
    mock_engine_class,
    game_state,
    game_manager,
    persist_config_port_mock,
    assembling_players_port_mock,
    persist_game_port_mock,
    valid_config_dict,
):
    persist_config_port_mock.load_config_dict.return_value = valid_config_dict
    assembling_players_port_mock.assemble_players.return_value = (MagicMock(), MagicMock())
    engine = mock_engine_class.return_value
    engine.get_game_obj.return_value.game_state = game_state

    game_manager.start_game()
    persist_game_port_mock.save_game.assert_not_called()


def test_no_active_game_interrupt_game_does_not_persist(game_manager, persist_game_port_mock):
    game_manager._game_engine = None
    game_manager.interrupt_game()
    persist_game_port_mock.save_game.assert_not_called()


def test_interrupt_network_game_not_persisted(game_manager, persist_game_port_mock):
    game_manager._network_enabled = True
    game_manager._game_engine = MagicMock()
    game_manager.interrupt_game()
    persist_game_port_mock.save_game.assert_not_called()


# ----- GameManager: _normalize_address -----


@pytest.mark.parametrize(
    "incoming_address, expected_normalized_address",
    [
        ("1.2.3.4:8080", "http://1.2.3.4:8080"),  # add http scheme to IP:port
        ("example.com:9000", "http://example.com:9000"),  # add http scheme to hostname:port
        ("supersuperhirn-online.org", "http://supersuperhirn-online.org"),  # add http scheme to hostname
        ("  1.2.3.4:8080  ", "http://1.2.3.4:8080"),  # strip whitepspaces and add http scheme
        ("http://x.com", "http://x.com"),  # incoming http scheme preserved
        ("https://x.com", "https://x.com"),  # incoming https scheme preserved
    ],
)
def test_normalize_address_valid_addresses(incoming_address, expected_normalized_address):
    assert GameManager._normalize_address(incoming_address) == expected_normalized_address


@pytest.mark.parametrize("empty_address", ["", "   ", None])
def test_normalize_address_empty_raises(empty_address):
    with pytest.raises(ValueError, match="empty"):
        GameManager._normalize_address(empty_address)


# ----- GameManager: _validate_normalized_network_address (input already normalized, has "http(s)://") -----


@pytest.mark.parametrize(
    "valid_address",
    [
        "http://1.2.3.4:8080",
        "http://141.45.39.64:5001",
        "http://example.com:9000",
        "http://supersuperhirn-online.org",
    ],
)
def test_validate_valid_addresses_no_raise(valid_address):
    GameManager._validate_normalized_network_address(valid_address)


@pytest.mark.parametrize(
    "invalid_address, error_message",
    [
        ("http://1.2.3.4", "port"),
        ("http://1.2.3.4:8080:8080", "port"),
        ("http://1.2.3.4:abc", "port"),
        ("http://supersuperhirn-online.org:abc", "port"),
        ("http://", "host"),
    ],
)
def test_validate_bad_addresses_raises(invalid_address, error_message):
    with pytest.raises(ValueError, match=error_message):
        GameManager._validate_normalized_network_address(invalid_address)


# ----- GameManager: verify GameManager catches/raises errors as it should -----


def _wire_mockies_and_patchies_with_fixtures(
    game_manager,
    persist_config_port_mock,
    assembling_players_port_mock,
    some_config_dict,
):
    persist_config_port_mock.load_config_dict.return_value = some_config_dict
    assembling_players_port_mock.assemble_players.return_value = (MagicMock(), MagicMock())


@patch("app.game_management.game_manager.threading.Thread")
@patch("app.game_management.game_manager.ConfigManager")
@patch("app.game_management.game_manager.GameEngine")
def test_run_connection_error_reraised_to_caller_through_driving_port(
    game_engine_mock,
    config_manager_mock,
    mock_thread,
    game_manager,
    persist_config_port_mock,
    assembling_players_port_mock,
    config_dict_valid_network_on,
):
    mock_thread.side_effect = lambda target, daemon: MagicMock(start=target)
    _wire_mockies_and_patchies_with_fixtures(
        game_manager, persist_config_port_mock, assembling_players_port_mock, config_dict_valid_network_on
    )

    game_engine_mock.return_value.run.side_effect = ConnectionError("lost")

    with pytest.raises(ConnectionError):
        game_manager.start_network_game("1.2.3.4:8080", "team13", "CODEBREAKER")


@patch("app.game_management.game_manager.threading.Thread")
@patch("app.game_management.game_manager.ConfigManager")
@patch("app.game_management.game_manager.GameEngine")
def test_run_illegal_move_value_error_caught_by_game_manager_internally(
    game_engine_mock,
    config_manager_mock,
    mock_thread,
    game_manager,
    persist_config_port_mock,
    assembling_players_port_mock,
    config_dict_valid_network_on,
):
    mock_thread.side_effect = lambda target, daemon: MagicMock(start=target)
    _wire_mockies_and_patchies_with_fixtures(
        game_manager, persist_config_port_mock, assembling_players_port_mock, config_dict_valid_network_on
    )

    game_engine_mock.return_value.run.side_effect = ValueError("illegal move")

    # no raise! (internal catch)
    game_manager.start_network_game("1.2.3.4:8080", "team13", "CODEBREAKER")
    assert game_manager._game_engine is None  # check clean up was done


@patch("app.game_management.game_manager.threading.Thread")
@patch("app.game_management.game_manager.ConfigManager")
@patch("app.game_management.game_manager.GameEngine")
def test_assemble_players_connection_error_reraised_to_caller_through_driving_port(
    game_engine_mock,
    config_manager_mock,
    mock_thread,
    game_manager,
    persist_config_port_mock,
    assembling_players_port_mock,
    config_dict_valid_network_on,
):
    mock_thread.side_effect = lambda target, daemon: MagicMock(start=target)
    persist_config_port_mock.load_config_dict.return_value = config_dict_valid_network_on
    assembling_players_port_mock.assemble_players.side_effect = ConnectionError("unreachable")
    with pytest.raises(ConnectionError):
        game_manager.start_network_game("1.2.3.4:8080", "team13", "CODEBREAKER")


# ---- GameManager: exit_application() works correctly ------


@pytest.mark.parametrize("game_state", [Gamestate.WON, Gamestate.LOST_ATTEMPTS, Gamestate.LOST_TIMEOUT])
def test_exit_application_interrupts_and_exits(game_manager, game_state):
    engine = MagicMock()
    engine.get_game_obj.return_value.game_state = game_state
    game_manager._game_engine = engine

    with pytest.raises(SystemExit):
        game_manager.exit_application()

    engine.interrupt_game.assert_called_once()
    game_manager._persist_game_port.assert_not_called()


def test_exit_application_aborts_without_saving(game_manager, persist_game_port_mock):
    engine = MagicMock()
    engine.get_game_obj.return_value.game_state = Gamestate.INTERRUPTED
    game_manager._game_engine = engine

    with pytest.raises(SystemExit):
        game_manager.exit_application()

    engine.interrupt_game.assert_called_once()  # abort_game
    persist_game_port_mock.save_game.assert_not_called()
