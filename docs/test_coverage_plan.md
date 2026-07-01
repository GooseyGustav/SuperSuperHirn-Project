# Test Coverage & Strategy Plan

## 1. Analysis of Current Test Coverage

The current test coverage is at **55.19%**, which is below the required CI threshold of **70%**.

The `pytest-cov` report highlights the following modules with low or zero coverage:

### Zero Coverage (0%) - High Priority
*   `src/gui/controllers/*` (e.g., `config_controller.py`, `game_ui_controller.py`, `home_controller.py`) - Contain significant logic and are completely untested.
*   `src/gui/views/*` - UI components currently lacking instantiation or basic logic tests.
*   `src/adapter/driving_adapter/for_game_config_and_admin/gui/ui_game_config_and_admin_service.py` - Driving adapter for GUI.
*   `src/startup/supersuperhirn_runner.py` - Application entry point.
*   `src/app/supersuperhirn_app.py` - Application facade.
*   `src/app/game_management/live_game/clock.py` - Core logic component.

### Low Coverage (< 70%)
*   `src/adapter/driven_adapter/for_getting_codebreaker_move/gui/gui_codebreaker.py` (38%)
*   `src/adapter/driven_adapter/for_getting_codemaker_move/gui/gui_codemaker.py` (67%)

## 2. Unused / "Dead" Code Identification

Several modules exist in `fake/` or `test_driver/` directories. These appear to have been used during early development or manual testing but are no longer active in the application flow. While they may not directly drag down the coverage percentage if they are empty or excluded, their presence adds clutter and confusion.

**Identified potentially dead code:**
*   `src/adapter/driven_adapter/for_assembling_players/fake/fake_matchmaker.py`
*   `src/adapter/driven_adapter/for_getting_codebreaker_move/fake/fake_codebreaker_move.py`
*   `src/adapter/driven_adapter/for_getting_codemaker_move/fake/fake_codemaker_moves.py`
*   `src/adapter/driven_adapter/for_persisting_config/fake/fake_config_storage.py`
*   `src/adapter/driven_adapter/for_persisting_game/fake/fake_game_storage.py`
*   `src/adapter/driving_adapter/for_game_config_and_admin/test_driver/test_driver_game_config_and_admin.py`

**Recommendation:** Unless specifically required for future testing setups, these `fake` adapters should be removed from the codebase. Mocking frameworks (like `unittest.mock`) should be used in automated unit tests instead of maintaining manual fake implementations.

## 3. Strategy to Reach > 70% Coverage

To efficiently and sensibly increase coverage above 70%, we will follow this prioritized plan:

### Phase 1: Core App & Startup (Low Hanging Fruit)
Add tests for the relatively simple application glue code and core logic that is currently missed.
*   **Target:** `src/app/supersuperhirn_app.py`, `src/app/game_management/live_game/clock.py`, `src/startup/supersuperhirn_runner.py`.

### Phase 2: GUI Controllers (High Impact)
The GUI controllers contain a large amount of logic that orchestrates the UI and interacts with the application core. Testing these will significantly boost coverage.
*   **Target:** `src/gui/controllers/*`.
*   **Approach:** Use `unittest.mock` to mock the view components and application ports, ensuring the controller logic (state management, event handling) is tested without requiring an active Qt event loop.

### Phase 3: GUI Adapters
Test the adapters that connect the GUI to the application ports.
*   **Target:** `src/adapter/driving_adapter/for_game_config_and_admin/gui/ui_game_config_and_admin_service.py`, `gui_codebreaker.py`, `gui_codemaker.py`.

### Phase 4: Code Cleanup (Optional but Recommended)
*   Delete the `fake/` adapter folders to clean up the project structure.

### Phase 5: GUI Views (If necessary)
If coverage is still below 70% after Phase 3, add basic tests for view initialization to ensure no syntax or basic setup errors exist in the view classes.
