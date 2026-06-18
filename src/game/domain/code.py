from .slot import Slot


class Code:
    LENGTH: int = 4

    def __init__(self):
        self._code: tuple[Slot, ...] = tuple(Slot() for _ in range(self.LENGTH))

    def isValid(self) -> bool:
        return all(not slot.isEmpty() for slot in self._code)

    def setCodeSlot(self, index: int, slot: Slot) -> None:
        slots = list(self._code)
        slots[index] = slot
        self._code = tuple(slots)

    def getCode(self) -> tuple[Slot, ...]:
        return self._code

    def __repr__(self):
        return f"Code(slots={self._code})"
