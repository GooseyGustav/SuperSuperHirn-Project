# tests/unit/application/domain/model/test_role.py
from application.domain.model.role import Role


def test_role_enum_values():
    """Testet, ob die Enum-Werte korrekt definiert sind."""
    assert Role.CODE_MAKER.value == "CodeMaker"
    assert Role.CODE_BREAKER.value == "CodeBreaker"


def test_role_descriptions():
    """Testet die korrekte Rückgabe der Beschreibungen."""
    assert "Setzt den geheimen Code" in Role.CODE_MAKER.get_description()
    assert "Versucht den geheimen Code zu erraten" in Role.CODE_BREAKER.get_description()
