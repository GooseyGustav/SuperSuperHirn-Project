import importlib
import sys
import types
from enum import Enum

FAKED_MODULE_NAMES = (
    "PyQt6",
    "PyQt6.QtCore",
    "PyQt6.QtGui",
    "PyQt6.QtWidgets",
    "gui.views.components.color",
    "gui.views.components.color_slots",
)
MISSING_MODULE = object()


# ---------- Fake Qt classes ----------


class FakeRect:
    def adjusted(self, *args):
        return self


class FakeWidget:
    def __init__(self, *args, **kwargs):
        self._min_w = 0
        self._min_h = 0
        self._max_w = 16777215
        self._max_h = 16777215
        self._fixed_width = None
        self.updated = False

    def setFixedSize(self, width, height):
        self._min_w = width
        self._min_h = height
        self._max_w = width
        self._max_h = height

    def setFixedWidth(self, width):
        self._fixed_width = width
        self._min_w = width
        self._max_w = width

    def minimumWidth(self):
        return self._min_w

    def minimumHeight(self):
        return self._min_h

    def maximumWidth(self):
        return self._max_w

    def maximumHeight(self):
        return self._max_h

    def setSizePolicy(self, *args):
        self.size_policy = args

    def update(self):
        self.updated = True

    def rect(self):
        return FakeRect()


class FakeLayout:
    def __init__(self, *args, **kwargs):
        self.widgets = []
        self.margins = None
        self.spacing = None

    def setContentsMargins(self, *args):
        self.margins = args

    def setSpacing(self, spacing):
        self.spacing = spacing

    def addWidget(self, widget, *args, **kwargs):
        self.widgets.append(widget)


class FakeSizePolicy:
    class Policy:
        Expanding = "Expanding"


class FakeQt:
    class PenStyle:
        NoPen = "NoPen"

    class BrushStyle:
        NoBrush = "NoBrush"

    class AlignmentFlag:
        AlignCenter = "AlignCenter"


class FakeQColor:
    def __init__(self, value):
        self.value = value


class FakeQPainter:
    class RenderHint:
        Antialiasing = "Antialiasing"

    def __init__(self, widget):
        self.widget = widget

    def setRenderHint(self, *args):
        pass

    def setBrush(self, *args):
        pass

    def setPen(self, *args):
        pass

    def drawEllipse(self, *args):
        pass


# ---------- Fake project classes ----------


class FakeColor(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    YELLOW = "yellow"
    ORANGE = "orange"
    BROWN = "brown"


class FakeColorSlot:
    def __init__(self):
        self.color = None
        self.selected = False

    def set_color(self, color):
        self.color = color

    def reset_color(self):
        self.color = None

    def set_selected(self, selected):
        self.selected = selected


def install_fakes():
    pyqt6 = types.ModuleType("PyQt6")

    qtcore = types.ModuleType("PyQt6.QtCore")
    qtcore.Qt = FakeQt

    qtgui = types.ModuleType("PyQt6.QtGui")
    qtgui.QColor = FakeQColor
    qtgui.QPainter = FakeQPainter

    qtwidgets = types.ModuleType("PyQt6.QtWidgets")
    qtwidgets.QWidget = FakeWidget
    qtwidgets.QGridLayout = FakeLayout
    qtwidgets.QHBoxLayout = FakeLayout
    qtwidgets.QVBoxLayout = FakeLayout
    qtwidgets.QSizePolicy = FakeSizePolicy

    color_module = types.ModuleType("gui.views.components.color")
    color_module.Color = FakeColor

    color_slots_module = types.ModuleType("gui.views.components.color_slots")
    color_slots_module.ColorSlot = FakeColorSlot

    sys.modules["PyQt6"] = pyqt6
    sys.modules["PyQt6.QtCore"] = qtcore
    sys.modules["PyQt6.QtGui"] = qtgui
    sys.modules["PyQt6.QtWidgets"] = qtwidgets
    sys.modules["gui.views.components.color"] = color_module
    sys.modules["gui.views.components.color_slots"] = color_slots_module


def restore_modules(previous_modules):
    for module_name, previous_module in previous_modules.items():
        if previous_module is MISSING_MODULE:
            sys.modules.pop(module_name, None)
        else:
            sys.modules[module_name] = previous_module


previous_modules = {module_name: sys.modules.get(module_name, MISSING_MODULE) for module_name in FAKED_MODULE_NAMES}

install_fakes()

sys.modules.pop("gui.views.components.game_attempt_board", None)
game_attempt_board = importlib.import_module("gui.views.components.game_attempt_board")
sys.modules.pop("gui.views.components.game_attempt_board", None)
restore_modules(previous_modules)

FeedbackPeg = game_attempt_board.FeedbackPeg
FeedbackWidget = game_attempt_board.FeedbackWidget
GuessWidget = game_attempt_board.GuessWidget
AttemptRow = game_attempt_board.AttemptRow
AttemptsBoard = game_attempt_board.AttemptsBoard
NUM_ROWS = game_attempt_board.NUM_ROWS
NUM_SLOTS = game_attempt_board.NUM_SLOTS
Color = FakeColor


def test_feedback_peg_init_and_state_changes():
    peg = FeedbackPeg()

    assert peg.state == FeedbackPeg.EMPTY
    assert peg.minimumWidth() == 14
    assert peg.minimumHeight() == 14
    assert peg.maximumWidth() == 14
    assert peg.maximumHeight() == 14

    peg.set_black()
    assert peg.state == FeedbackPeg.BLACK
    assert peg.updated is True

    peg.set_white()
    assert peg.state == FeedbackPeg.WHITE

    peg.reset()
    assert peg.state == FeedbackPeg.EMPTY


def test_feedback_peg_paint_event_branches_do_not_crash():
    peg = FeedbackPeg()

    peg.paintEvent(None)

    peg.set_black()
    peg.paintEvent(None)

    peg.set_white()
    peg.paintEvent(None)


def test_feedback_widget_creates_five_pegs_and_sets_feedback():
    widget = FeedbackWidget()

    assert len(widget.pegs) == NUM_SLOTS

    widget.set_feedback(black_count=2, white_count=2)

    assert [peg.state for peg in widget.pegs] == [
        FeedbackPeg.BLACK,
        FeedbackPeg.BLACK,
        FeedbackPeg.WHITE,
        FeedbackPeg.WHITE,
        FeedbackPeg.EMPTY,
    ]

    widget.reset()

    assert all(peg.state == FeedbackPeg.EMPTY for peg in widget.pegs)


def test_guess_widget_sets_slots_active_slot_and_reset():
    widget = GuessWidget()
    colors = [Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW, Color.ORANGE]

    assert len(widget.slots) == NUM_SLOTS

    widget.set_guess(colors)
    assert [slot.color for slot in widget.slots] == colors

    widget.set_slot(2, Color.BROWN)
    assert widget.slots[2].color == Color.BROWN

    widget.set_active_slot(3)
    assert [slot.selected for slot in widget.slots] == [
        False,
        False,
        False,
        True,
        False,
    ]

    widget.reset()
    assert all(slot.color is None for slot in widget.slots)


def test_attempt_row_delegates_to_guess_and_feedback():
    row = AttemptRow()

    row.set_slot_selected(1)
    assert row.guess.slots[1].selected is True

    row.set_guess([Color.RED, Color.GREEN])
    assert row.guess.slots[0].color == Color.RED
    assert row.guess.slots[1].color == Color.GREEN

    row.set_slot(4, Color.BLUE)
    assert row.guess.slots[4].color == Color.BLUE

    row.set_feedback(black_count=1, white_count=2)
    assert [peg.state for peg in row.feedback.pegs] == [
        FeedbackPeg.BLACK,
        FeedbackPeg.WHITE,
        FeedbackPeg.WHITE,
        FeedbackPeg.EMPTY,
        FeedbackPeg.EMPTY,
    ]

    row.reset()
    assert all(slot.color is None for slot in row.guess.slots)
    assert all(peg.state == FeedbackPeg.EMPTY for peg in row.feedback.pegs)


def test_attempts_board_creates_rows_and_updates_attempts():
    board = AttemptsBoard()

    assert board.current_row == 0
    assert len(board.rows) == NUM_ROWS

    board.set_attempt(
        row_index=2,
        colors=[Color.RED, Color.GREEN],
        black=1,
        white=1,
    )

    assert board.rows[2].guess.slots[0].color == Color.RED
    assert board.rows[2].guess.slots[1].color == Color.GREEN
    assert board.rows[2].feedback.pegs[0].state == FeedbackPeg.BLACK
    assert board.rows[2].feedback.pegs[1].state == FeedbackPeg.WHITE

    board.set_guess_slot(2, 3, Color.BLUE)
    assert board.rows[2].guess.slots[3].color == Color.BLUE

    board.set_feedback_slots(2, white=2, black=3)
    assert [peg.state for peg in board.rows[2].feedback.pegs] == [
        FeedbackPeg.BLACK,
        FeedbackPeg.BLACK,
        FeedbackPeg.BLACK,
        FeedbackPeg.WHITE,
        FeedbackPeg.WHITE,
    ]

    board.set_active_slot(2, 4)
    assert board.rows[2].guess.slots[4].selected is True

    board.reset()
    assert all(slot.color is None for row in board.rows for slot in row.guess.slots)
    assert all(peg.state == FeedbackPeg.EMPTY for row in board.rows for peg in row.feedback.pegs)
