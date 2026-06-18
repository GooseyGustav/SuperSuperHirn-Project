import pytest
from src.game.domain.color import COLOR


def test_color_values_exist():
    assert COLOR.RED.value == 1
    assert COLOR.GREEN.value == 2
    assert COLOR.BLACK.value == 8

def test_color_count():
    assert len(COLOR) == 8
