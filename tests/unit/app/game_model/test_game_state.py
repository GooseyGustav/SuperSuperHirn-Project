from app.game_model.game_state import Gamestate


def test_game_states():
    assert Gamestate.INTERRUPTED.value == "INTERRUPTED"
    assert Gamestate.NEW.value == "NEW"
    assert Gamestate.RUNNING.value == "RUNNING"
    assert Gamestate.WON.value == "WON"
    assert Gamestate.LOST_ATTEMPTS.value == "LOST_ATTEMPTS"
    assert Gamestate.LOST_TIMEOUT.value == "LOST_TIMEOUT"
