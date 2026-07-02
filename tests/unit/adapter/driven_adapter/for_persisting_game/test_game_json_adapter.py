import json
from pathlib import Path

import pytest

from adapter.driven_adapter.for_persisting_game.file_tool.game_json_adapter import GameJsonAdapter
from app.ports.driven.for_persisting.save_errors import CorruptedSaveError


@pytest.fixture
def valid_game_data() -> dict:
    return {
        "gamemode": "CLASSIC",
        "gamestate": "INTERRUPTED",
        "number_of_positions": 5,
        "number_of_colors": 8,
        "max_attempts": 10,
        "secret_code": [1, 2, 3, 4, 8],
        "attempt_list": [{"guess": [1, 2, 2, 2, 2], "feedback": {"black_pins": 2, "white_pins": 0, "status": "FINAL"}}],
        "remaining_time_millis": 0,
        "matchup": {},
    }


@pytest.fixture
def adapter_paths(tmp_path: Path) -> dict[str, Path]:
    return {"base_dir": tmp_path, "file_name": "test_game_save.json"}


@pytest.fixture
def adapter(adapter_paths: dict) -> GameJsonAdapter:
    return GameJsonAdapter(base_dir=adapter_paths["base_dir"], file_name=adapter_paths["file_name"])


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# ---------- GameJsonAdapter: Constructor Tests ----------


def test_constructor_uses_provided_paths(adapter_paths: dict) -> None:
    """The adapter correctly resolves and stores the provided base directory and file path."""
    adapter = GameJsonAdapter(base_dir=adapter_paths["base_dir"], file_name=adapter_paths["file_name"])
    expected_path = adapter_paths["base_dir"] / adapter_paths["file_name"]

    assert adapter.base_dir == adapter_paths["base_dir"].resolve()
    assert adapter.file_path == expected_path.resolve()


# ---------- GameJsonAdapter: save_game Tests ----------


def test_save_game_writes_json(adapter: GameJsonAdapter, valid_game_data: dict) -> None:
    """save_game writes the complete game dict as JSON to the disk."""
    adapter.save_game(valid_game_data)

    assert adapter.file_path.exists()
    assert read_json(adapter.file_path) == valid_game_data


def test_save_game_overwrites_existing_save(adapter: GameJsonAdapter, valid_game_data: dict) -> None:
    """save_game fully replaces an already existing save file."""
    write_json(adapter.file_path, {"old_data": "should disappear"})

    adapter.save_game(valid_game_data)

    assert read_json(adapter.file_path) == valid_game_data


# ---------- GameJsonAdapter: load_game Tests ----------


def test_load_game_returns_correct_dictionary(adapter: GameJsonAdapter, valid_game_data: dict) -> None:
    """load_game correctly reads and returns the JSON file as a dictionary."""
    write_json(adapter.file_path, valid_game_data)

    assert adapter.load_game() == valid_game_data


def test_load_game_raises_file_not_found(adapter: GameJsonAdapter) -> None:
    """Loading a non-existent save file raises a FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        adapter.load_game()


def test_load_game_raises_json_decode_error_on_corrupt_file(adapter: GameJsonAdapter) -> None:
    """Loading a corrupt JSON file strictly raises a CorruptedSaveError."""
    adapter.file_path.write_text("{ corrupt json ]", encoding="utf-8")

    with pytest.raises(CorruptedSaveError):
        adapter.load_game()


# ---------- GameJsonAdapter: delete_game Tests ----------


def test_delete_game_removes_existing_file(adapter: GameJsonAdapter, valid_game_data: dict) -> None:
    """delete_game successfully unlinks an existing save file."""
    write_json(adapter.file_path, valid_game_data)
    assert adapter.file_path.exists()

    adapter.delete_game()

    assert not adapter.file_path.exists()


def test_delete_game_passes_silently_if_file_missing(adapter: GameJsonAdapter) -> None:
    """delete_game does not crash if the save file is already missing."""
    if adapter.file_path.exists():
        adapter.file_path.unlink()

    try:
        adapter.delete_game()
    except Exception as e:
        pytest.fail(f"delete_game() should pass silently, but raised: {e}")
