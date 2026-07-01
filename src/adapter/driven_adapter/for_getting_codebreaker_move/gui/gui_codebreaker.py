from PyQt6.QtCore import QMutex, QObject, QWaitCondition, pyqtSignal

from app.ports.driven.for_getting_moves.for_getting_codebreaker_move import ForGettingCodebreakerMove
from gui.views.components.color import Color


class GuiCodebreaker(ForGettingCodebreakerMove):

    def __init__(self):
        super().__init__()
        self._qt_emitter = _GuiCodebreakerEmitter()

        self._mutex = QMutex()
        self._wait = QWaitCondition()
        self._guess: list[int] = []

    def get_guess(self, attempt_list) -> list[int]:
        self._qt_emitter.guess_requested.emit(attempt_list)  # → GameController informieren
        self._mutex.lock()
        self._wait.wait(self._mutex)  # schläft bis submit_guess()
        result = list(self._guess)
        self._mutex.unlock()
        return result

    def submit_guess(self, guess: list[Color]):  # GameController ruft das auf
        self._mutex.lock()
        self._guess = [int(c) for c in guess]
        self._mutex.unlock()
        self._wait.wakeAll()


class _GuiCodebreakerEmitter(QObject):
    guess_requested = pyqtSignal(list)

    def __init__(self):
        super().__init__()
