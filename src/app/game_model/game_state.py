from enum import Enum


class Gamestate(Enum):
    """Docstring for Gamestate."""

    NEW = "NEW"
    RUNNING = "RUNNING"
    INTERRUPTED = "INTERRUPTED"
    WON = "WON"
    LOST_TIMEOUT = "LOST_TIMEOUT"
    LOST_ATTEMPTS = "LOST_ATTEMPTS"
