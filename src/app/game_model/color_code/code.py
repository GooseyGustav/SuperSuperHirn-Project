from app.game_model.color_code.color import Color
from app.game_model.color_code.slot import Slot


class Code:
    """A validated colour sequence used for both guesses and the secret code.

    Internally stores a tuple of (length: int, slots: list[Slot]).
    The length mirrors len(slots) and is kept for UML compatibility.
    """

    def __init__(self, code: tuple[int, list[Slot]]) -> None:
        """Constructs a Code Object from a tuple with the length of the code (int)
        and the list of all the slots.
        """
        self.code = code

    def __eq__(self, other: object) -> bool:
        """Return True if both codes have identical colors in every slot.

        Args:
            other (object): Object to compare with this code.

        Returns:
            bool: True if both codes have the same colors in the same order, otherwise False.
        """
        if not isinstance(other, Code):
            return NotImplemented

        return len(self.code[1]) == len(other.code[1]) and all(
            a.color == b.color for a, b in zip(self.code[1], other.code[1])
        )

    def set_code(self, code: list[int]) -> None:
        """Replace the current sequence with a new one built from integer color IDs.

        Args:
            code (list[int]): Code as a list of integers representing available colors.
        """
        slots = [Slot(Color(c)) for c in code]
        self.code = (len(slots), slots)

    def get_code(self) -> list[Slot]:
        """Return the list of Slots that make up this code.

        Returns:
            list[Slot]: List of slots representing a code.
        """
        return self.code[1]
