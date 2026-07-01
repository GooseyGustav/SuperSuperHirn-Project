from app.game_model.color_code.color import Color


class Slot:
    """A single peg position in a Mastermind code.

    A Slot holds one Color value. It starts empty (color is None) and
    can be filled via set_color(). The engine reads it back via get_color().
    """

    def __init__(self, color: Color | None = None):
        self.color = color

    def is_empty(self) -> bool:
        """Return True if no color has been assigned to this slot yet.

        Returns:
            bool: True if the slot is empty, otherwise False.
        """

        return self.color is None

    def set_color(self, color_id: int) -> None:
        """Assign a color to this slot by its integer ID (1–8).

        Args:
            color_id (int): ID as an integer representing a color.
        """

        self.color = Color(color_id)

    def get_color(self) -> Color:
        """Return the Color currently held by this slot.

        Returns:
            Color: The color a slot holds.
        """

        return self.color
