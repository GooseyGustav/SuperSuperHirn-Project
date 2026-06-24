from enum import Enum


class Gamemode(Enum):
    """Enumeration of available game modes for a game round.

    A game mode defines the rules during a round.
    Exactly one game mode is active per round.

    CLASSIC:
        Standard game without additional time or feedback rules.
    TIME_TRIAL:
        Game mode with a time limit for each guess.
    BLIND_TRIAL:
        Game mode with delayed feedback.
    """

    CLASSIC = "CLASSIC"
    TIME_TRIAL = "TIME_TRIAL"
    BLIND_TRIAL = "BLIND_TRIAL"
