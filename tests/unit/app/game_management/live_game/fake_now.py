class FakeNow:
    """Controllable time source for testing. Advances time without real sleeps."""

    def __init__(self, t: float = 0.0):
        self.t = t

    def __call__(self) -> float:
        return self.t

    def advance(self, millis: float) -> None:
        self.t += millis / 1000
