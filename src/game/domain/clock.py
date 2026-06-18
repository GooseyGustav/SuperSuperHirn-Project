import time


class Clock:
    TIME_LIMIT: int = 60

    def __init__(self):
        self._current: int = 0
        self._start_time: float | None = None

    def startClock(self) -> None:
        self._start_time = time.time()

    def endClock(self) -> None:
        if self._start_time is not None:
            self._current = int(time.time() - self._start_time)
            self._start_time = None

    def getCurrentTime(self) -> int:
        if self._start_time is not None:
            return int(time.time() - self._start_time)
        return self._current

    def resetTime(self) -> None:
        self._current = 0
        self._start_time = None

    def __repr__(self):
        return f"Clock(current={self._current}, limit={self.TIME_LIMIT})"
