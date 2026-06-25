#
# ### `Clock` _(`live_game/`)_
#
# **Note: all times in millis.**
#
# - **Responsibility:** Time-Trial countdown / timeout against the game thread.
# - **Attributes:** **`MAX_TIME_MILLIS: int`,`remainingTimeMillis: int`.** **Methods:** `startClock()`,
# `interruptGameTimeout()` _(private)_, `resetClock()` _(private)_.
# - **Constructor (injection):** `MAX_TIME_MILLIS` is passed through the config:
# `GameEngine.gameConfig.countdownMillis → Clock.MAX_TIME_MILLIS`
# - **Instantiated by:** `GameEngine` (engaged only in `TIME_TRIAL`).


class Clock:
    """Docstring for Clock."""

    def __init__(self, max_time_millis: int) -> None:
        self.MAX_TIME_MILLIS = max_time_millis
        self.remainingTimeMillis = max_time_millis

    def start_clock(self) -> None:
        """Docstring"""

    def _interrupt_game_timeout(self) -> None: ...

    def _reset_clock(self) -> None: ...
