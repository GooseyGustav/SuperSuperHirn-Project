from app.game_management.game_config_management.code_constants import CodeConstants


def test_code_constants():
    assert CodeConstants.NUMBER_OF_COLORS == 8
    assert CodeConstants.NUMBER_OF_PINS == 5
