import importlib
import sys
import types
from enum import IntEnum

FAKED_MODULE_NAMES = (
    "PyQt6",
    "PyQt6.QtCore",
)
MISSING_MODULE = object()


# ---------- Fake Qt classes ----------


class FakeSignal:
    """pyqtSignal replacement that records every emitted argument tuple."""

    def __init__(self, *args):
        self.emitted_values = []

    def emit(self, *args):
        self.emitted_values.append(args)


class FakeQObject:
    """QObject replacement; only construction is relevant for the emitter."""

    def __init__(self, *args, **kwargs):
        pass


class FakeQMutex:
    """QMutex replacement that counts lock and unlock calls."""

    def __init__(self):
        self.lock_count = 0
        self.unlock_count = 0

    def lock(self):
        self.lock_count += 1

    def unlock(self):
        self.unlock_count += 1


class FakeQWaitCondition:
    """QWaitCondition replacement that records wait targets and wake calls."""

    def __init__(self):
        self.waited_with = []
        self.wake_all_count = 0

    def wait(self, mutex):
        self.waited_with.append(mutex)

    def wakeAll(self):
        self.wake_all_count += 1


# ---------- Fake project classes ----------


class FakeColor(IntEnum):
    """Minimal Color enum replacement with the same integer values as production."""

    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    ORANGE = 5
    BROWN = 6
    WHITE = 7
    BLACK = 8


def install_fakes():
    """Install fake PyQt modules before importing the GUI codemaker adapter."""
    pyqt6 = types.ModuleType("PyQt6")

    qtcore = types.ModuleType("PyQt6.QtCore")
    qtcore.QMutex = FakeQMutex
    qtcore.QObject = FakeQObject
    qtcore.QWaitCondition = FakeQWaitCondition
    qtcore.pyqtSignal = FakeSignal

    sys.modules["PyQt6"] = pyqt6
    sys.modules["PyQt6.QtCore"] = qtcore


def restore_modules(previous_modules):
    """Restore sys.modules so fake PyQt modules do not leak into other tests."""
    for module_name, previous_module in previous_modules.items():
        if previous_module is MISSING_MODULE:
            sys.modules.pop(module_name, None)
        else:
            sys.modules[module_name] = previous_module


# Capture existing modules so the fake import can be fully undone afterwards.
previous_modules = {module_name: sys.modules.get(module_name, MISSING_MODULE) for module_name in FAKED_MODULE_NAMES}

install_fakes()

# Import the production adapter once while its PyQt imports point to the fakes.
sys.modules.pop(
    "adapter.driven_adapter.for_getting_codemaker_move.gui.gui_codemaker",
    None,
)
gui_codemaker = importlib.import_module("adapter.driven_adapter.for_getting_codemaker_move.gui.gui_codemaker")
sys.modules.pop(
    "adapter.driven_adapter.for_getting_codemaker_move.gui.gui_codemaker",
    None,
)
restore_modules(previous_modules)

GuiCodemaker = gui_codemaker.GuiCodemaker
Color = FakeColor


class TestGuiCodemaker:
    # ---------- __init__ ----------

    def test_init_creates_empty_state_and_synchronization_objects(self):
        """A new GUI codemaker starts empty and owns its Qt synchronization objects."""
        codemaker = GuiCodemaker()

        assert codemaker._secret_code == []
        assert codemaker._feedback_list == []
        assert isinstance(codemaker._mutex, FakeQMutex)
        assert isinstance(codemaker._wait, FakeQWaitCondition)
        assert hasattr(codemaker._qt_emitter, "secret_code_requested")
        assert hasattr(codemaker._qt_emitter, "feedback_requested")

    # ---------- submit_secret_code ----------

    def test_submit_secret_code_converts_color_values_to_ints(self):
        """submit_secret_code stores selected Color values as plain integers."""
        codemaker = GuiCodemaker()

        codemaker.submit_secret_code([Color.RED, Color.GREEN, Color.BLUE])

        assert codemaker._secret_code == [1, 2, 4]

    def test_submit_secret_code_locks_unlocks_and_wakes_wait_condition(self):
        """submit_secret_code protects the write with the mutex and wakes waiters."""
        codemaker = GuiCodemaker()

        codemaker.submit_secret_code([Color.YELLOW])

        assert codemaker._mutex.lock_count == 1
        assert codemaker._mutex.unlock_count == 1
        assert codemaker._wait.wake_all_count == 1

    # ---------- get_secret_code ----------

    def test_get_secret_code_emits_secret_code_requested(self):
        """get_secret_code asks the GUI for the secret by emitting a signal."""
        codemaker = GuiCodemaker()

        codemaker.get_secret_code()

        assert codemaker._qt_emitter.secret_code_requested.emitted_values == [()]

    def test_get_secret_code_waits_on_mutex_and_returns_secret_copy(self):
        """get_secret_code waits on the condition and returns a copy of the secret."""
        codemaker = GuiCodemaker()
        codemaker._secret_code = [1, 2, 3, 4, 5]

        result = codemaker.get_secret_code()
        result.append(6)

        assert codemaker._mutex.lock_count == 1
        assert codemaker._mutex.unlock_count == 1
        assert codemaker._wait.waited_with == [codemaker._mutex]
        assert codemaker._secret_code == [1, 2, 3, 4, 5]

    # ---------- submit_feedback ----------

    def test_submit_feedback_stores_feedback_list(self):
        """submit_feedback stores the feedback provided by the GUI unchanged."""
        codemaker = GuiCodemaker()

        codemaker.submit_feedback([Color.BLACK, Color.WHITE])

        assert codemaker._feedback_list == [Color.BLACK, Color.WHITE]

    def test_submit_feedback_locks_unlocks_and_wakes_wait_condition(self):
        """submit_feedback protects the write with the mutex and wakes waiters."""
        codemaker = GuiCodemaker()

        codemaker.submit_feedback([Color.BLACK])

        assert codemaker._mutex.lock_count == 1
        assert codemaker._mutex.unlock_count == 1
        assert codemaker._wait.wake_all_count == 1

    # ---------- get_feedback ----------

    def test_get_feedback_emits_feedback_requested_with_secret_and_guess(self):
        """get_feedback asks the GUI for feedback with the current secret and guess."""
        codemaker = GuiCodemaker()
        secret = [1, 2, 3, 4, 5]
        guess = [5, 4, 3, 2, 1]

        codemaker.get_feedback(secret, guess)

        assert codemaker._qt_emitter.feedback_requested.emitted_values == [(secret, guess)]

    def test_get_feedback_waits_on_mutex_and_returns_feedback(self):
        """get_feedback waits on the condition and returns the stored feedback."""
        codemaker = GuiCodemaker()
        codemaker._feedback_list = [8, 7]

        result = codemaker.get_feedback([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])

        assert codemaker._mutex.lock_count == 1
        assert codemaker._mutex.unlock_count == 1
        assert codemaker._wait.waited_with == [codemaker._mutex]
        assert result == [8, 7]
