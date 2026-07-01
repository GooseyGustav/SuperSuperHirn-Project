# Implementation Plan: Test Coverage Clean Up

This document outlines the specific code changes and unit tests to be implemented in the `feature/coverage_cleanUp` branch to achieve > 70% test coverage.

## 1. Code Cleanup (Removing Dead Code)
The following directories contain dummy/fake implementations that are no longer used in the main application flow and artificially complicate the project structure. They will be deleted:
- `src/adapter/driven_adapter/for_assembling_players/fake/`
- `src/adapter/driven_adapter/for_getting_codebreaker_move/fake/`
- `src/adapter/driven_adapter/for_getting_codemaker_move/fake/`
- `src/adapter/driven_adapter/for_persisting_config/fake/`
- `src/adapter/driven_adapter/for_persisting_game/fake/`
- `src/adapter/driving_adapter/for_game_config_and_admin/test_driver/`

## 2. Unit Tests to Implement

### Phase 1: Core Logic & Startup

#### `tests/unit/app/test_supersuperhirn_app.py`
Target: `src/app/supersuperhirn_app.py`
- **Test 1:** `test_app_initializes_game_manager_with_ports`: Verify that `SupersuperhirnApp` correctly instantiates the `GameManager` using the provided mock driven ports.
- **Test 2:** `test_for_game_administration_returns_game_manager`: Verify that calling `for_game_administration()` returns the internal `GameManager` instance.
- **Test 3:** `test_for_game_configuration_returns_game_manager`: Verify that calling `for_game_configuration()` returns the internal `GameManager` instance.

#### `tests/unit/app/game_management/live_game/test_clock.py`
Target: `src/app/game_management/live_game/clock.py`
- **Test 1:** `test_clock_initialization`: Verify `MAX_TIME_MILLIS` and `remainingTimeMillis` are set correctly upon instantiation.
- **Test 2:** `test_start_clock_execution`: Verify the `start_clock` method can be called without errors (even if currently empty).
- **Test 3:** `test_interrupt_game_timeout_execution`: Verify internal method call.
- **Test 4:** `test_reset_clock_execution`: Verify internal method call.

#### `tests/unit/startup/test_supersuperhirn_runner.py`
Target: `src/startup/supersuperhirn_runner.py`
*(Requires patching `PyQt6.QtWidgets.QApplication` and `MainWindow` to prevent actual GUI rendering during tests)*
- **Test 1:** `test_runner_initializes_components`: Verify that adapters, Matchmaker, SupersuperhirnApp, and MainWindow are instantiated correctly during `__init__`.
- **Test 2:** `test_connect_gui_adapter_to_ui`: Verify that the callback correctly passes the player adapter to the `MainWindow.set_ui_adapter` method.

### Phase 2: GUI Adapters

#### `tests/unit/adapter/driving_adapter/for_game_config_and_admin/gui/test_ui_game_config_and_admin_service.py`
Target: `src/adapter/driving_adapter/for_game_config_and_admin/gui/ui_game_config_and_admin_service.py`
*(Mock `ForConfiguringGame` and `ForGameAdministration`)*
- **Test 1:** `test_on_load_config_delegates`: Verify it calls `for_configuring_game.load_config()`.
- **Test 2:** `test_on_save_config_delegates`: Verify it calls `for_configuring_game.save_config(data)`.
- **Test 3:** `test_on_reset_config_delegates`: Verify it calls `for_configuring_game.reset_config()`.
- **Test 4:** `test_on_start_game_delegates`: Verify it calls `for_game_administration.start_game()`.
- **Test 5:** `test_on_start_game_delete_interrupted_delegates`: Verify it calls `for_game_administration.start_game_delete_interrupted()`.
- **Test 6:** `test_on_interrupt_game_delegates`: Verify it calls `for_game_administration.interrupt_game()`.
- **Test 7:** `test_on_abort_game_delegates`: Verify it calls `for_game_administration.abort_game()`.
- **Test 8:** `test_on_start_network_game_delegates`: Verify it calls `for_game_administration.start_network_game(ip, id)`.

### Phase 3: GUI Controllers
*(Note: Controller tests will heavily mock the View classes to isolate controller logic without triggering PyQt6 visual rendering)*

#### `tests/unit/gui/controllers/test_config_controller.py`
Target: `src/gui/controllers/config_controller.py`
- **Test 1:** `test_init_connects_signals`: Verify that the controller connects to the view's signals (e.g., save, reset, back).
- **Test 2:** `test_on_save_clicked`: Mock view input fields and verify it constructs the correct config dictionary and passes it to the UI adapter.
- **Test 3:** `test_on_reset_clicked`: Verify it calls `ui_adapter.on_reset_config()` and triggers a view reload.

#### `tests/unit/gui/controllers/test_home_controller.py`
Target: `src/gui/controllers/home_controller.py`
- **Test 1:** `test_init_connects_signals`: Verify signal connections (start game, config, etc.).
- **Test 2:** `test_start_classic_game`: Verify it triggers the main window to switch to the game view and calls `ui_adapter.on_start_game()`.
- **Test 3:** `test_start_network_game`: Verify it extracts IP and GamerID from the view and calls `ui_adapter.on_start_network_game()`.

#### `tests/unit/gui/controllers/test_game_ui_controller.py`
Target: `src/gui/controllers/game_ui_controller.py`
- **Test 1:** `test_init_setup`: Verify it connects abort/interrupt signals and initializes the board based on the game state.
- **Test 2:** `test_on_abort_game`: Verify it calls the UI adapter and switches the view back to home.
- **Test 3:** `test_on_interrupt_game`: Verify it calls the UI adapter and switches view.
- **Test 4:** `test_update_board_state`: Verify it correctly translates a domain `GameState` object into view updates (pins, attempts remaining).

#### `tests/unit/gui/controllers/test_credits_controller.py`
Target: `src/gui/controllers/credits_controller.py`
- **Test 1:** `test_back_button_navigation`: Verify clicking back in credits asks the main window to return to the home view.

---
**Execution Note:** Once approved, we will create the `feature/coverage_cleanUp` branch and implement these files exactly as specified.
