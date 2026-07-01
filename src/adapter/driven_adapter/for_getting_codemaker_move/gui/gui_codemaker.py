from PyQt6.QtCore import QMutex, QObject, QWaitCondition, pyqtSignal

from app.ports.driven.for_getting_moves.for_getting_codemaker_move import ForGettingCodemakerMove


class GuiCodemaker(ForGettingCodemakerMove):

    def __init__(self):
        super().__init__()
        self._qt_emitter = _GuiCodebreakerEmitter()

        self._mutex = QMutex()
        self._wait = QWaitCondition()
        self._secret_code: list[int] = []
        self._feedback_list: list[int] = []

    def get_secret_code(self) -> list[int]:
        self._qt_emitter.secret_code_requested.emit()  # → GameController informieren
        self._mutex.lock()
        self._wait.wait(self._mutex)  # schläft bis submit_guess()
        result = list(self._secret_code)
        self._mutex.unlock()
        return result

    def submit_secret_code(self, secret_code: list[int]):  # GameController ruft das auf
        self._mutex.lock()
        self._secret_code = [int(c) for c in secret_code]
        self._mutex.unlock()
        self._wait.wakeAll()

    def get_feedback(self, secret: list[int], guess: list[int]) -> list[int]:
        self._qt_emitter.feedback_requested.emit(secret, guess)  # → GameController informieren
        self._mutex.lock()
        self._wait.wait(self._mutex)  # schläft bis submit_guess()
        result = self._feedback_list
        self._mutex.unlock()
        return result

    def submit_feedback(self, feedback: list[int]):
        self._mutex.lock()
        self._feedback_list = feedback
        self._mutex.unlock()
        self._wait.wakeAll()


class _GuiCodebreakerEmitter(QObject):
    secret_code_requested = pyqtSignal()
    feedback_requested = pyqtSignal(list, list)

    def __init__(self):
        super().__init__()
