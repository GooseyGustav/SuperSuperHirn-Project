from app.game_model.game_mode import Gamemode


def test_game_modes():
    assert Gamemode.Classic.value == "CLASSIC"
    assert Gamemode.TIME_TRIAL.value == "TIME_TRIAL"
    assert Gamemode.BLIND_TRIAL.value == "BLIND_TRIAL"
