class TimeoutInterrupt(Exception):
    """Raised by the codebreaker adapter when the player's input time has expired.

    The GameEngine catches this to transition the game to Gamestate.LOST_TIMEOUT.
    In this branch only test doubles raise it; the real raiser is the future GUI adapter.
    """
