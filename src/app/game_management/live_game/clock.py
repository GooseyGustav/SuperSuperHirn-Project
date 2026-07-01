import time
from math import ceil
from typing import Callable


class Clock:
    """Passive per-move deadline object for TIME_TRIAL mode.

    Non-threaded: start() records a deadline timestamp and returns immediately.
    Expiry is checked on demand via is_expired(). The injectable `now` parameter
    acts as the test seam — pass a fake time function to advance time in tests
    without real sleeps.

    Instantiated by GameEngine, only when gamemode == TIME_TRIAL.
    """

    def __init__(self, max_time_millis: int, now: Callable[[], float] = time.monotonic) -> None:
        """
        Args:
            max_time_millis: Per-move time budget in milliseconds.
            now: Monotonic time source. Defaults to time.monotonic; override in tests.
        """

        if max_time_millis <= 0:
            raise ValueError("Time limit must be bigger than 0")

        self.max_time_millis = max_time_millis
        self._now = now
        self._deadline: float | None = None

    def reset(self) -> None:
        """Clear the deadline and restore the full time budget. Call before each move."""
        self._deadline = None

    def start(self) -> None:
        """Arm the per-move deadline: deadline = now + budget. Call immediately after reset()."""
        self._deadline = self._now() + self.max_time_millis / 1000

    def is_expired(self) -> bool:
        """Return True if the deadline has been reached. Call after get_guess() returns."""
        return self._deadline is not None and self._now() >= self._deadline

    def remaining_millis(self) -> int:
        """Return milliseconds left until the deadline, or the full budget if not yet started."""
        if self._deadline is None:
            return self.max_time_millis
        return max(0, ceil((self._deadline - self._now()) * 1000))
