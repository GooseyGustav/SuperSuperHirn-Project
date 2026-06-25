from enum import Enum


class Gamestate(Enum):
    """Enumeration of possible game states the round can be in.

    The game state describes the current lifecycle phase of a round.

    NEW:
        The game has been created but has not started yet.
    RUNNING:
        The game is currently active.
    INTERRUPTED:
        The game was paused and can be resumed later.
    WON:
        The Codebreaker has guessed the secret code correctly.
    LOST_TIMEOUT:
        The Codebreaker lost because the time limit expired.
    LOST_ATTEMPTS:
        The Codebreaker lost because the maximum number of attempts was reached.
    """

    NEW = "NEW"
    RUNNING = "RUNNING"
    INTERRUPTED = "INTERRUPTED"
    WON = "WON"
    LOST_TIMEOUT = "LOST_TIMEOUT"
    LOST_ATTEMPTS = "LOST_ATTEMPTS"
