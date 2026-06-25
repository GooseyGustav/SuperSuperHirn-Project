import pytest

from app.game_model.color_code.color import Color
from app.game_model.color_code.slot import Slot
from app.game_model.color_code.code import Code


def make_code(*color_ids: int) -> Code:
    """Build a Code from a sequence of integer color IDs."""
    slots = [Slot(Color(c)) for c in color_ids]
    return Code((len(slots), slots))


class TestCodeGetCode:
    def test_returns_list_of_slots(self):
        code = make_code(1, 2, 3, 4, 5)
        result = code.get_code()
        assert isinstance(result, list)
        assert all(isinstance(s, Slot) for s in result)

    def test_slots_carry_correct_colors(self):
        code = make_code(1, 2, 3, 4, 5)
        colors = [s.get_color() for s in code.get_code()]
        assert colors == [Color.RED, Color.GREEN, Color.YELLOW, Color.BLUE, Color.ORANGE]


class TestCodeSetCode:
    def test_set_code_replaces_slots(self):
        code = make_code(1, 1, 1, 1, 1)
        code.set_code([2, 3, 4, 5, 6])
        colors = [s.get_color() for s in code.get_code()]
        assert colors == [Color.GREEN, Color.YELLOW, Color.BLUE, Color.ORANGE, Color.BROWN]

    def test_set_code_updates_length_in_tuple(self):
        code = make_code(1, 2, 3)
        code.set_code([4, 5, 6, 7, 8])
        assert code.code[0] == 5

    def test_set_code_invalid_id_raises_value_error(self):
        code = make_code(1, 2, 3, 4, 5)
        with pytest.raises(ValueError):
            code.set_code([1, 2, 3, 4, 99])


class TestCodeEq:
    def test_equal_codes_with_same_colors(self):
        assert make_code(1, 2, 3, 4, 5) == make_code(1, 2, 3, 4, 5)

    def test_different_colors_are_not_equal(self):
        assert make_code(1, 2, 3, 4, 5) != make_code(1, 2, 3, 4, 6)

    def test_comparing_with_non_code_returns_not_implemented(self):
        result = make_code(1, 2, 3, 4, 5).__eq__("not a code")
        assert result is NotImplemented
