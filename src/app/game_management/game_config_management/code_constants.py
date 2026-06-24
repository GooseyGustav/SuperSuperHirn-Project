from enum import IntEnum


class CodeConstants(IntEnum):
    """Stores the number of positions the secret code must fill and the number of
    colors available.
    (Could be extended to include the maximum number of attempts for a Codebreaker.
    (MAX_ATTEMPTS = 10). would then be renamed BoardConstants or similarly.)
    """

    NUMBER_OF_PINS = 5
    NUMBER_OF_COLORS = 8
