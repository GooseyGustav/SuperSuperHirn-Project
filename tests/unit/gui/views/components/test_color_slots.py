import importlib
import sys
import types

from gui.views.components.color import Color

FAKED_MODULE_NAMES = (
    "PyQt6",
    "PyQt6.QtCore",
    "PyQt6.QtGui",
    "PyQt6.QtWidgets",
)
MISSING_MODULE = object()


# ---------- Fake Qt classes ----------


class FakeRect:
    """Small QRect double used by ColorSlot.paintEvent border calculations."""

    def adjusted(self, *args):
        return self


class FakeWidget:
    """QWidget double that records sizing and repaint requests."""

    def __init__(self, *args, **kwargs):
        self._min_w = 0
        self._min_h = 0
        self._max_w = 16777215
        self._max_h = 16777215
        self.updated = False

    def setFixedSize(self, width, height):
        self._min_w = width
        self._min_h = height
        self._max_w = width
        self._max_h = height

    def minimumWidth(self):
        return self._min_w

    def minimumHeight(self):
        return self._min_h

    def maximumWidth(self):
        return self._max_w

    def maximumHeight(self):
        return self._max_h

    def update(self):
        self.updated = True

    def rect(self):
        return FakeRect()


class FakeQt:
    """Subset of Qt enum values used by ColorSlot.paintEvent."""

    class PenStyle:
        NoPen = "NoPen"

    class BrushStyle:
        NoBrush = "NoBrush"


class FakeQColor:
    """QColor double that keeps the requested color value inspectable."""

    def __init__(self, value):
        self.value = value


class FakeQPainter:
    """QPainter double that records drawing calls made by paintEvent."""

    last_instance = None

    class RenderHint:
        Antialiasing = "Antialiasing"

    def __init__(self, widget):
        self.widget = widget
        self.render_hints = []
        self.brushes = []
        self.pens = []
        self.ellipses = []
        FakeQPainter.last_instance = self

    def setRenderHint(self, hint):
        self.render_hints.append(hint)

    def setBrush(self, brush):
        self.brushes.append(brush)

    def setPen(self, pen):
        self.pens.append(pen)

    def drawEllipse(self, rect):
        self.ellipses.append(rect)


def install_fakes():
    """Install fake Qt modules before importing the ColorSlot module."""
    pyqt6 = types.ModuleType("PyQt6")

    qtcore = types.ModuleType("PyQt6.QtCore")
    qtcore.Qt = FakeQt

    qtgui = types.ModuleType("PyQt6.QtGui")
    qtgui.QColor = FakeQColor
    qtgui.QPainter = FakeQPainter

    qtwidgets = types.ModuleType("PyQt6.QtWidgets")
    qtwidgets.QWidget = FakeWidget

    sys.modules["PyQt6"] = pyqt6
    sys.modules["PyQt6.QtCore"] = qtcore
    sys.modules["PyQt6.QtGui"] = qtgui
    sys.modules["PyQt6.QtWidgets"] = qtwidgets


def restore_modules(previous_modules):
    """Restore sys.modules so fake Qt modules do not leak into other tests."""
    for module_name, previous_module in previous_modules.items():
        if previous_module is MISSING_MODULE:
            sys.modules.pop(module_name, None)
        else:
            sys.modules[module_name] = previous_module


# Capture any real modules first so the fake import can be undone afterwards.
previous_modules = {module_name: sys.modules.get(module_name, MISSING_MODULE) for module_name in FAKED_MODULE_NAMES}

install_fakes()

# Import production code once while PyQt imports point to the fakes above.
sys.modules.pop("gui.views.components.color_slots", None)
color_slots = importlib.import_module("gui.views.components.color_slots")
sys.modules.pop("gui.views.components.color_slots", None)
restore_modules(previous_modules)

ColorSlot = color_slots.ColorSlot
COLOR_MAP = color_slots.COLOR_MAP


class TestColorSlot:
    # ---------- __init__ ----------

    def test_init_sets_default_state_and_fixed_size(self):
        """A new color slot starts empty, unselected, and uses the expected size."""
        slot = ColorSlot()

        assert slot.color is None
        assert slot.selected is False
        assert slot.minimumWidth() == 30
        assert slot.minimumHeight() == 30
        assert slot.maximumWidth() == 30
        assert slot.maximumHeight() == 30

    # ---------- set_selected ----------

    def test_set_selected_updates_selection_state_and_widget(self):
        """set_selected stores the selection state and requests a repaint."""
        slot = ColorSlot()

        slot.set_selected(True)

        assert slot.selected is True
        assert slot.updated is True

    def test_set_selected_can_clear_selection(self):
        """set_selected can switch an already selected slot back to unselected."""
        slot = ColorSlot()
        slot.set_selected(True)
        slot.updated = False

        slot.set_selected(False)

        assert slot.selected is False
        assert slot.updated is True

    # ---------- set_color / reset_color ----------

    def test_set_color_updates_color_and_widget(self):
        """set_color stores the color and requests a repaint."""
        slot = ColorSlot()

        slot.set_color(Color.RED)

        assert slot.color == Color.RED
        assert slot.updated is True

    def test_reset_color_clears_color_and_updates_widget(self):
        """reset_color removes the current color and requests a repaint."""
        slot = ColorSlot()
        slot.set_color(Color.BLUE)
        slot.updated = False

        slot.reset_color()

        assert slot.color is None
        assert slot.updated is True

    # ---------- paintEvent ----------

    def test_paint_event_uses_lightgray_fill_for_empty_slot(self):
        """paintEvent paints an empty slot with neutral fill and black border."""
        slot = ColorSlot()

        slot.paintEvent(None)

        painter = FakeQPainter.last_instance
        assert painter.brushes[0].value == "lightgray"
        assert painter.pens[0] == FakeQt.PenStyle.NoPen
        assert painter.pens[1].value == "black"
        assert len(painter.ellipses) == 2

    def test_paint_event_uses_color_map_fill_for_colored_slot(self):
        """paintEvent resolves a selected Color through COLOR_MAP before painting."""
        slot = ColorSlot()
        slot.set_color(Color.ORANGE)

        slot.paintEvent(None)

        painter = FakeQPainter.last_instance
        assert painter.brushes[0].value == COLOR_MAP[Color.ORANGE]

    def test_paint_event_uses_black_border_for_selected_slot(self):
        """paintEvent keeps the border black even when the slot is selected."""
        slot = ColorSlot()
        slot.set_selected(True)

        slot.paintEvent(None)

        painter = FakeQPainter.last_instance
        assert painter.pens[1].value == "black"


def test_color_map_contains_all_supported_colors():
    """COLOR_MAP defines a paint color for every selectable Color value."""
    assert COLOR_MAP == {
        Color.RED: "red",
        Color.GREEN: "green",
        Color.YELLOW: "yellow",
        Color.BLUE: "blue",
        Color.ORANGE: "orange",
        Color.BROWN: "brown",
        Color.WHITE: "white",
        Color.BLACK: "black",
    }
