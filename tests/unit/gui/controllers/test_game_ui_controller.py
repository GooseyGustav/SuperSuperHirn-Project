import pytest
from unittest.mock import MagicMock, patch
from gui.controllers.game_ui_controller import GameController

class TestGameController:
    def setup_method(self):
        self.patcher_view = patch("gui.controllers.game_ui_controller.GameView")
        self.patcher_main_window = patch("gui.controllers.game_ui_controller.MainWindow")
        
        mock_game_view = self.patcher_view.start()
        mock_main_window = self.patcher_main_window.start()

        # Setup mocks
        self.mock_view_instance = MagicMock()
        mock_game_view.return_value = self.mock_view_instance
        
        self.mock_main_window_instance = MagicMock()
        self.mock_adapter = MagicMock()
        self.mock_player_adapter = {"codebreaker": MagicMock()}
        
        self.mock_main_window_instance.ui_service_adapter = self.mock_adapter
        self.mock_main_window_instance.player_adapter = self.mock_player_adapter
        mock_main_window.instance.return_value = self.mock_main_window_instance

        # Instantiate controller
        self.controller = GameController()

    def teardown_method(self):
        self.patcher_view.stop()
        self.patcher_main_window.stop()

    def test_init_connects_signals(self):
        self.mock_main_window_instance.register_view.assert_called_once_with("game", self.mock_view_instance)
        self.mock_main_window_instance.navigate_to.assert_called_once_with("game")
        
        # Check signal connections
        self.mock_view_instance.exit_game_no_save_pressed.connect.assert_called_once()
        self.mock_view_instance.exit_game_save_pressed.connect.assert_called_once()
        self.mock_view_instance.restart_game_pressed.connect.assert_called_once()
        self.mock_view_instance.color_selected.connect.assert_called_once()
        self.mock_view_instance.submit_pressed.connect.assert_called_once()
        self.mock_view_instance.key_delete_pressed.connect.assert_called_once()
        self.mock_view_instance.key_enter_pressed.connect.assert_called_once()
        self.mock_view_instance.key_move_slot.connect.assert_called_once()
        self.mock_player_adapter["codebreaker"]._qt_emitter.guess_requested.connect.assert_called_once()

    def test_on_abort_game(self):
        self.controller._on_abort_game()
        self.mock_adapter.on_abort_game.assert_called_once()

    def test_on_game_aborted(self):
        self.controller._on_game_aborted()
        self.mock_main_window_instance.navigate_to.assert_called_with("home")

    def test_on_exit_game_save(self):
        self.controller._on_exit_game_save()
        self.mock_adapter.on_interrupt_game.assert_called_once()
        
    def test_on_game_interrupted(self):
        self.controller._on_game_interrupted()
        self.mock_main_window_instance.navigate_to.assert_called_with("home")

    def test_on_guess_requested(self):
        attempt_list = [("guess", [7, 8], "status")]
        self.controller._on_guess_requested(attempt_list)
        
        self.mock_view_instance.game_attempt_board.set_active_slot.assert_called_once_with(self.controller.round_index, self.controller.slot_index)
        self.mock_view_instance.set_submit_enabled.assert_called_once_with(True)
        assert self.controller.guess_list == []
        
    def test_update_board(self):
        # 8 is black, 7 is white
        attempt_list = [("guess1", [8, 8, 7], "status1"), ("guess2", [], "status2")]
        self.controller._update_board(attempt_list)
        
        self.mock_view_instance.game_attempt_board.set_feedback_slots.assert_any_call(0, 1, 2)
        self.mock_view_instance.game_attempt_board.set_feedback_slots.assert_any_call(1, 0, 0)
