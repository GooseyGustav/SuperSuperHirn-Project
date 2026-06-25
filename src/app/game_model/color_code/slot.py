from app.game_model.color_code.color import Color


class Slot:
    """A single peg position in a Mastermind code.

    A Slot holds one Color value. It starts empty (color is None) and
    can be filled via set_color(). The engine reads it back via get_color().
    """

    def __init__(self, color: Color | None = None):
        self.color = color

    def is_empty(self) -> bool:
        """Return True if no color has been assigned to this slot yet."""
        return self.color is None

    def set_color(self, color_id: int) -> None:
        """Assign a color to this slot by its integer ID (1–8).

        Raises ValueError if color_id does not map to a known Color.
        """
        self.color = Color(color_id)

    def get_color(self) -> Color:
        """Return the Color currently held by this slot.

        Raises AttributeError if the slot is empty — check is_empty() first.
        """
        return self.color
