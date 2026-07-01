from unittest.mock import MagicMock, patch

import pytest

from gui.controllers.codemaker_controller import GameCodemakerController
from gui.views.components.color import Color

pytest.importorskip("PyQt6")


class TestGameCodemakerController:
    def setup_method(self):
        """Replace GUI construction and MainWindow access with controllable mocks."""
        self.patcher_view = patch("gui.controllers.codemaker_controller.GameView")
        self.patcher_main_window = patch("gui.controllers.codemaker_controller.MainWindow")

        self.mock_game_view_class = self.patcher_view.start()
        self.mock_main_window_class = self.patcher_main_window.start()

        # The controller expects a GameView with board and secret-code widgets.
        self.mock_view_instance = MagicMock()
        self.mock_view_instance.game_attempt_board = MagicMock()
        self.mock_view_instance.secret_code_widget = MagicMock()
        self.mock_game_view_class.return_value = self.mock_view_instance

        # MainWindow provides the active GUI codemaker and the admin service.
        self.mock_codemaker = MagicMock()
        self.mock_codemaker._qt_emitter = MagicMock()
        self.mock_ui_service_adapter = MagicMock()
        self.mock_main_window_instance = MagicMock()
        self.mock_main_window_instance.player_adapter = {"codemaker": self.mock_codemaker}
        self.mock_main_window_instance.ui_service_adapter = self.mock_ui_service_adapter
        self.mock_main_window_class.instance.return_value = self.mock_main_window_instance

        self.controller = GameCodemakerController()

    def teardown_method(self):
        """Stop patches so other tests see the original GUI classes again."""
        self.patcher_view.stop()
        self.patcher_main_window.stop()

    # ---------- __init__ / event wiring ----------

    def test_init_registers_game_view_and_navigates_to_game(self):
        """Constructor creates the secret-input game view and opens it."""
        self.mock_game_view_class.assert_called_once_with("secret")
        self.mock_main_window_instance.register_view.assert_called_once_with("game", self.mock_view_instance)
        self.mock_main_window_instance.navigate_to.assert_called_once_with("game")

    def test_init_loads_codemaker_and_ui_service_from_main_window(self):
        """Constructor reads codemaker and UI service dependencies from MainWindow."""
        assert self.controller.codemaker is self.mock_codemaker
        assert self.controller.ui_service_adapter is self.mock_ui_service_adapter

    def test_connect_events_connects_game_view_signals(self):
        """Constructor wires all GameView user-input signals to controller handlers."""
        self.mock_view_instance.exit_game_no_save_pressed.connect.assert_called_once()
        self.mock_view_instance.exit_game_save_pressed.connect.assert_called_once()
        self.mock_view_instance.color_selected.connect.assert_called_once()
        self.mock_view_instance.feedback_color_selected.connect.assert_called_once()
        self.mock_view_instance.submit_pressed.connect.assert_called_once()
        self.mock_view_instance.key_delete_pressed.connect.assert_called_once()
        self.mock_view_instance.key_enter_pressed.connect.assert_called_once()

    def test_connect_events_connects_codemaker_emitter_signals(self):
        """Constructor wires codemaker request signals to controller handlers."""
        self.mock_codemaker._qt_emitter.secret_code_requested.connect.assert_called_once()
        self.mock_codemaker._qt_emitter.feedback_requested.connect.assert_called_once()

    # ---------- _on_secret_code_requested ----------

    def test_on_secret_code_requested_keeps_controller_ready_for_secret_input(self):
        """Secret-code requests keep the controller in secret-entry mode."""
        self.controller._on_secret_code_requested()

        assert self.controller.codemaker_mode == "secret"
        assert self.controller.secret_list == []

    # ---------- _on_feedback_requested ----------

    def test_on_feedback_requested_updates_current_guess_on_board(self):
        """Feedback requests show the current codebreaker guess on the board."""
        with patch.object(self.controller, "update_board_current_guess") as update_board_mock:
            self.controller._on_feedback_requested([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])

        update_board_mock.assert_called_once_with([5, 4, 3, 2, 1])

    # ---------- update_board_current_guess ----------

    def test_update_board_current_guess_sets_guess_slots_in_current_row(self):
        """update_board_current_guess writes every guess color into the current row."""
        self.controller.round_index = 3

        self.controller.update_board_current_guess([1, 2, 3])

        self.mock_view_instance.game_attempt_board.set_guess_slot.assert_any_call(3, 0, 1)
        self.mock_view_instance.game_attempt_board.set_guess_slot.assert_any_call(3, 1, 2)
        self.mock_view_instance.game_attempt_board.set_guess_slot.assert_any_call(3, 2, 3)

    # ---------- _handle_color_input ----------

    def test_handle_color_input_routes_to_secret_input_in_secret_mode(self):
        """Color input is handled as secret-code input while in secret mode."""
        self.controller.codemaker_mode = "secret"

        with patch.object(self.controller, "_handle_secret_input") as secret_input_mock:
            self.controller._handle_color_input(Color.RED)

        secret_input_mock.assert_called_once_with(Color.RED)

    def test_handle_color_input_routes_to_feedback_input_in_feedback_mode(self):
        """Color input is handled as feedback input while in feedback mode."""
        self.controller.codemaker_mode = "feedback"

        with patch.object(self.controller, "_handle_feedback_input") as feedback_input_mock:
            self.controller._handle_color_input(Color.BLACK)

        feedback_input_mock.assert_called_once_with(Color.BLACK)

    # ---------- _handle_secret_input / add_color_secret_list ----------

    def test_handle_secret_input_adds_color_updates_secret_widget_and_moves_slot(self):
        """Secret input appends a color, redraws the secret widget, and advances."""
        self.controller._handle_secret_input(Color.RED)

        assert self.controller.secret_list == [Color.RED]
        assert self.controller.slot_index == 1
        self.mock_view_instance.secret_code_widget.set_guess.assert_called_once_with([Color.RED])

    def test_handle_secret_input_ignores_input_after_five_colors(self):
        """Secret input is ignored once five secret colors are already present."""
        self.controller.secret_list = [Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW, Color.ORANGE]
        self.controller.slot_index = 5

        self.controller._handle_secret_input(Color.BROWN)

        assert self.controller.secret_list == [Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW, Color.ORANGE]
        assert self.controller.slot_index == 5
        self.mock_view_instance.secret_code_widget.set_guess.assert_not_called()

    def test_add_color_secret_list_appends_until_five_colors(self):
        """add_color_secret_list enforces the maximum secret length of five."""
        self.controller.secret_list = [Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW, Color.ORANGE]

        self.controller.add_color_secret_list(Color.BROWN)

        assert self.controller.secret_list == [Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW, Color.ORANGE]

    # ---------- _handle_feedback_input / add_color_feedback_list ----------

    def test_handle_feedback_input_adds_color_and_updates_feedback_slots(self):
        """Feedback input appends a peg and redraws black/white feedback counts."""
        self.controller.round_index = 2
        self.controller.feedback_list = [Color.WHITE]

        self.controller._handle_feedback_input(Color.BLACK)

        assert self.controller.feedback_list == [Color.WHITE, Color.BLACK]
        self.mock_view_instance.game_attempt_board.set_feedback_slots.assert_called_once_with(2, 1, 1)

    def test_handle_feedback_input_ignores_input_after_five_colors(self):
        """Feedback input is ignored once five feedback pegs are already present."""
        self.controller.feedback_list = [Color.WHITE, Color.BLACK, Color.WHITE, Color.BLACK, Color.WHITE]

        self.controller._handle_feedback_input(Color.BLACK)

        assert self.controller.feedback_list == [Color.WHITE, Color.BLACK, Color.WHITE, Color.BLACK, Color.WHITE]
        self.mock_view_instance.game_attempt_board.set_feedback_slots.assert_not_called()

    def test_add_color_feedback_list_appends_until_five_colors(self):
        """add_color_feedback_list enforces the maximum feedback length of five."""
        self.controller.feedback_list = [Color.WHITE, Color.BLACK, Color.WHITE, Color.BLACK, Color.WHITE]

        self.controller.add_color_feedback_list(Color.BLACK)

        assert self.controller.feedback_list == [Color.WHITE, Color.BLACK, Color.WHITE, Color.BLACK, Color.WHITE]

    # ---------- _change_slot_index ----------

    def test_change_slot_index_clamps_to_lower_bound_zero(self):
        """Slot movement cannot move before the first slot."""
        self.controller.slot_index = 1

        self.controller._change_slot_index(-99)

        assert self.controller.slot_index == 0

    def test_change_slot_index_clamps_to_upper_bound_five(self):
        """Slot movement cannot move beyond the position after the fifth slot."""
        self.controller.slot_index = 4

        self.controller._change_slot_index(99)

        assert self.controller.slot_index == 5

    def test_change_slot_index_moves_inside_bounds(self):
        """Slot movement applies the delta when the result stays in bounds."""
        self.controller.slot_index = 2

        self.controller._change_slot_index(2)

        assert self.controller.slot_index == 4

    # ---------- _on_delete ----------

    def test_on_delete_does_nothing_when_secret_list_is_empty(self):
        """Delete has no effect when there is no secret color to remove."""
        self.controller._on_delete()

        self.mock_view_instance.game_attempt_board.set_guess_slot.assert_not_called()
        assert self.controller.slot_index == 0

    def test_on_delete_removes_last_secret_color_and_clears_board_slot(self):
        """Delete removes the latest secret color and clears its board slot."""
        self.controller.secret_list = [Color.RED, Color.GREEN, Color.BLUE]
        self.controller.slot_index = 3

        self.controller._on_delete()

        assert self.controller.secret_list == [Color.RED, Color.GREEN]
        assert self.controller.slot_index == 2
        self.mock_view_instance.game_attempt_board.set_guess_slot.assert_called_once_with(0, 2, None)

    # ---------- _on_submit in secret mode ----------

    def test_on_submit_secret_mode_does_nothing_until_secret_has_five_colors(self):
        """Secret submission is blocked until all five colors are entered."""
        self.controller.codemaker_mode = "secret"
        self.controller.secret_list = [Color.RED]

        self.controller._on_submit()

        self.mock_codemaker.submit_secret_code.assert_not_called()
        assert self.controller.codemaker_mode == "secret"

    def test_on_submit_secret_mode_submits_secret_and_switches_to_feedback_mode(self):
        """A complete secret is submitted and switches the view to feedback input."""
        self.controller.codemaker_mode = "secret"
        self.controller.secret_list = [Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW, Color.ORANGE]

        self.controller._on_submit()

        self.mock_codemaker.submit_secret_code.assert_called_once_with(
            [Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW, Color.ORANGE]
        )
        assert self.controller.codemaker_mode == "feedback"
        self.mock_view_instance._setup_color_picker.assert_called_once_with("feedback")

    # ---------- _on_submit in feedback mode ----------

    def test_on_submit_feedback_mode_submits_feedback_and_advances_round(self):
        """Feedback submission sends the pegs and prepares the next round."""
        self.controller.codemaker_mode = "feedback"
        self.controller.feedback_list = [Color.WHITE, Color.BLACK]

        self.controller._on_submit()

        self.mock_codemaker.submit_feedback.assert_called_once_with([Color.WHITE, Color.BLACK])
        assert self.controller.feedback_list == []
        assert self.controller.round_index == 1
        assert self.controller.slot_index == 0

    def test_on_submit_feedback_mode_does_not_require_five_feedback_colors(self):
        """Feedback submission allows empty or partial feedback lists."""
        self.controller.codemaker_mode = "feedback"
        self.controller.feedback_list = []

        self.controller._on_submit()

        self.mock_codemaker.submit_feedback.assert_called_once_with([])

    def test_on_submit_feedback_mode_navigates_home_when_all_feedback_is_black(self):
        """Five black feedback pegs finish the game and navigate home."""
        self.controller.codemaker_mode = "feedback"
        self.controller.feedback_list = [Color.BLACK, Color.BLACK, Color.BLACK, Color.BLACK, Color.BLACK]

        self.controller._on_submit()

        self.mock_main_window_instance.navigate_to.assert_any_call("home")

    def test_on_submit_feedback_mode_handles_pending_interrupt_and_navigates_home(self):
        """Pending save-and-exit interrupts navigate home without submitting feedback."""
        self.controller.codemaker_mode = "feedback"
        self.controller.feedback_list = [Color.WHITE]
        self.controller._pending_interrupt = True

        self.controller._on_submit()

        assert self.controller._pending_interrupt is False
        assert self.controller.round_index == 0
        assert self.controller.feedback_list == [Color.WHITE]
        self.mock_main_window_instance.navigate_to.assert_any_call("home")

    def test_on_submit_feedback_mode_navigates_home_after_tenth_round(self):
        """The controller navigates home after submitting feedback for round ten."""
        self.controller.codemaker_mode = "feedback"
        self.controller.round_index = 9
        self.controller.feedback_list = [Color.WHITE]

        self.controller._on_submit()

        assert self.controller.round_index == 10
        self.mock_main_window_instance.navigate_to.assert_any_call("home")

    # ---------- _on_move_slot ----------

    def test_on_move_slot_delegates_to_change_slot_index(self):
        """Keyboard slot movement delegates to the shared index-change helper."""
        with patch.object(self.controller, "_change_slot_index") as change_slot_mock:
            self.controller._on_move_slot(-1)

        change_slot_mock.assert_called_once_with(-1)

    # ---------- Game administration methods ----------

    def test_on_abort_game_delegates_to_ui_service_adapter(self):
        """Abort delegates the actual game-abort action to the UI service adapter."""
        self.controller._on_abort_game()

        self.mock_ui_service_adapter.on_abort_game.assert_called_once()

    def test_on_game_aborted_navigates_home(self):
        """The controller returns to home after receiving a game-aborted event."""
        self.controller._on_game_aborted()

        self.mock_main_window_instance.navigate_to.assert_called_with("home")

    def test_on_exit_game_save_sets_pending_interrupt_and_delegates_to_ui_service_adapter(self):
        """Save-and-exit marks a pending interrupt and delegates persistence work."""
        self.controller._on_exit_game_save()

        assert self.controller._pending_interrupt is True
        self.mock_ui_service_adapter.on_interrupt_game.assert_called_once()
