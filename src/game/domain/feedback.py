class Feedback:
    def __init__(self, black_pins: int = 0, white_pins: int = 0):
        self._blackPins: int = black_pins
        self._whitePins: int = white_pins

    def getFeedback(self) -> tuple[int, int]:
        return (self._blackPins, self._whitePins)

    def __repr__(self):
        return f"Feedback(black={self._blackPins}, white={self._whitePins})"
