import pytest
from src.game.domain.code import Code
from src.game.domain.slot import Slot
from src.game.domain.color import COLOR


def test_code_length():
    code = Code()
    assert len(code.getCode()) == Code.LENGTH

def test_code_invalid_when_empty():
    code = Code()
    assert code.isValid() is False

def test_code_valid_when_all_slots_filled():
    code = Code()
    for i in range(Code.LENGTH):
        slot = Slot()
        slot.setColor(COLOR.RED)
        code.setCodeSlot(i, slot)
    assert code.isValid() is True
