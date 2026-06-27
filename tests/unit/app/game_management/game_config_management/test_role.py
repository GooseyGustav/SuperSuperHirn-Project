from app.game_management.game_config_management.role import Role


def test_roles():
    assert Role.CODEBREAKER.value == "CODEBREAKER"
    assert Role.CODEMAKER.value == "CODEMAKER"
    assert Role.OBSERVER.value == "OBSERVER"
