from app.game_model.color_code.color import Color
from app.game_model.color_code.slot import Slot
from app.game_model.color_code.code import Code
from app.game_model.player_attempts.guess import Guess


def make_code(*color_ids: int) -> Code:
    slots = [Slot(Color(c)) for c in color_ids]
    return Code((len(slots), slots))


class TestGuess:
    def test_get_code_guess_returns_the_wrapped_code(self):
        code = make_code(1, 2, 3, 4, 5)
        guess = Guess(code)
        assert guess.get_code_guess() is code

    def test_get_code_guess_preserves_slot_colors(self):
        code = make_code(1, 2, 3, 4, 5)
        guess = Guess(code)
        colors = [s.get_color() for s in guess.get_code_guess().get_code()]
        assert colors == [Color.RED, Color.GREEN, Color.YELLOW, Color.BLUE, Color.ORANGE]
