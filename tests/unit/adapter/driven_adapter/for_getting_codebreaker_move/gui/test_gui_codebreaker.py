import importlib
import sys
import types
from enum import IntEnum

FAKED_MODULE_NAMES = (
    "PyQt6",
    "PyQt6.QtCore",
    "gui.views.components.color",
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
    """Install fake PyQt and Color modules before importing the GUI adapter."""
    pyqt6 = types.ModuleType("PyQt6")

    qtcore = types.ModuleType("PyQt6.QtCore")
    qtcore.QMutex = FakeQMutex
    qtcore.QObject = FakeQObject
    qtcore.QWaitCondition = FakeQWaitCondition
    qtcore.pyqtSignal = FakeSignal

    color_module = types.ModuleType("gui.views.components.color")
    color_module.Color = FakeColor

    sys.modules["PyQt6"] = pyqt6
    sys.modules["PyQt6.QtCore"] = qtcore
    sys.modules["gui.views.components.color"] = color_module


def restore_modules(previous_modules):
    """Restore sys.modules so fake modules do not leak into other tests."""
    for module_name, previous_module in previous_modules.items():
        if previous_module is MISSING_MODULE:
            sys.modules.pop(module_name, None)
        else:
            sys.modules[module_name] = previous_module


# Capture existing modules so the fake import can be fully undone afterwards.
previous_modules = {module_name: sys.modules.get(module_name, MISSING_MODULE) for module_name in FAKED_MODULE_NAMES}

install_fakes()

# Import the production adapter once while PyQt and Color point to the fakes.
sys.modules.pop(
    "adapter.driven_adapter.for_getting_codebreaker_move.gui.gui_codebreaker",
    None,
)
gui_codebreaker = importlib.import_module("adapter.driven_adapter.for_getting_codebreaker_move.gui.gui_codebreaker")
sys.modules.pop(
    "adapter.driven_adapter.for_getting_codebreaker_move.gui.gui_codebreaker",
    None,
)
restore_modules(previous_modules)

GuiCodebreaker = gui_codebreaker.GuiCodebreaker
Color = FakeColor


class TestGuiCodebreaker:
    # ---------- __init__ ----------

    def test_init_creates_empty_guess_and_synchronization_objects(self):
        """A new GUI codebreaker starts empty and owns its Qt synchronization objects."""
        codebreaker = GuiCodebreaker()

        assert codebreaker._guess == []
        assert isinstance(codebreaker._mutex, FakeQMutex)
        assert isinstance(codebreaker._wait, FakeQWaitCondition)
        assert hasattr(codebreaker._qt_emitter, "guess_requested")

    # ---------- submit_guess ----------

    def test_submit_guess_converts_color_values_to_ints(self):
        """submit_guess stores the selected Color values as plain integers."""
        codebreaker = GuiCodebreaker()

        codebreaker.submit_guess([Color.RED, Color.GREEN, Color.BLUE])

        assert codebreaker._guess == [1, 2, 4]

    def test_submit_guess_locks_unlocks_and_wakes_wait_condition(self):
        """submit_guess protects the write with the mutex and wakes waiting callers."""
        codebreaker = GuiCodebreaker()

        codebreaker.submit_guess([Color.YELLOW])

        assert codebreaker._mutex.lock_count == 1
        assert codebreaker._mutex.unlock_count == 1
        assert codebreaker._wait.wake_all_count == 1

    # ---------- get_guess ----------

    def test_get_guess_emits_guess_requested_with_attempt_list(self):
        """get_guess asks the GUI for input by emitting the current attempt list."""
        codebreaker = GuiCodebreaker()
        attempt_list = [([1, 2, 3, 4, 5], [8, 7], "FINAL")]

        codebreaker.get_guess(attempt_list)

        assert codebreaker._qt_emitter.guess_requested.emitted_values == [(attempt_list,)]

    def test_get_guess_waits_on_mutex_and_returns_current_guess(self):
        """get_guess waits on the condition and returns the stored guess after waking."""
        codebreaker = GuiCodebreaker()
        codebreaker._guess = [1, 2, 3, 4, 5]

        result = codebreaker.get_guess([])

        assert codebreaker._mutex.lock_count == 1
        assert codebreaker._mutex.unlock_count == 1
        assert codebreaker._wait.waited_with == [codebreaker._mutex]
        assert result == [1, 2, 3, 4, 5]

    def test_get_guess_returns_copy_of_internal_guess(self):
        """get_guess returns a copy so callers cannot mutate the stored guess."""
        codebreaker = GuiCodebreaker()
        codebreaker._guess = [1, 2, 3, 4, 5]

        result = codebreaker.get_guess([])
        result.append(6)

        assert codebreaker._guess == [1, 2, 3, 4, 5]
