from enum import Enum


class Color(Enum):
    """Emumeration of supported colors for the secret code and guesses.

    Use `ENUM_OBJECT.value` to access the numeric value and `ENUM_OBJECT.name` to access the color name
    as a string.
    For example: `Color.RED.value == 1` and `Color.RED.name == "RED"`.
    """

    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    ORANGE = 5
    BROWN = 6
    WHITE = 7
    BLACK = 8
