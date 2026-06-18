import pytest
from src.game.domain.slot import Slot
from src.game.domain.color import COLOR


def test_slot_is_empty_on_creation():
    slot = Slot()
    assert slot.isEmpty() is True

def test_slot_not_empty_after_set():
    slot = Slot()
    slot.setColor(COLOR.RED)
    assert slot.isEmpty() is False

def test_slot_get_color():
    slot = Slot()
    slot.setColor(COLOR.BLUE)
    assert slot.getColor() == COLOR.BLUE
