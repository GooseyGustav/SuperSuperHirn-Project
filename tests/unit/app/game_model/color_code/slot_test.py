import pytest

from app.game_model.color_code.color import Color
from app.game_model.color_code.slot import Slot


class TestSlotIsEmpty:
    def test_new_slot_without_color_is_empty(self):
        assert Slot().is_empty() is True

    def test_slot_initialised_with_color_is_not_empty(self):
        assert Slot(Color.RED).is_empty() is False


class TestSlotGetColor:
    def test_returns_color_set_at_construction(self):
        slot = Slot(Color.BLUE)
        assert slot.get_color() == Color.BLUE

    def test_returns_none_for_empty_slot(self):
        assert Slot().get_color() is None


class TestSlotSetColor:
    def test_set_color_by_valid_id_stores_correct_color(self):
        slot = Slot()
        slot.set_color(1)
        assert slot.get_color() == Color.RED

    def test_slot_is_not_empty_after_set_color(self):
        slot = Slot()
        slot.set_color(3)
        assert slot.is_empty() is False

    def test_set_color_maps_all_valid_ids(self):
        expected = [Color.RED, Color.GREEN, Color.YELLOW, Color.BLUE,
                    Color.ORANGE, Color.BROWN, Color.WHITE, Color.BLACK]
        for color_id, color in enumerate(expected, start=1):
            slot = Slot()
            slot.set_color(color_id)
            assert slot.get_color() == color

    def test_set_color_invalid_id_raises_value_error(self):
        with pytest.raises(ValueError):
            Slot().set_color(99)
