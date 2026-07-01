import json
from pathlib import Path

import pytest

from adapter.driven_adapter.for_persisting_config.file_tool import config_json_adapter
from adapter.driven_adapter.for_persisting_config.file_tool.config_json_adapter import ConfigJsonAdapter

HARD_CODED_DEFAULT_CONFIG = {
    "gamemode": "CLASSIC",
    "user_role": "CODEBREAKER",
    "network_enabled": False,
    "countdown_millis": 0,
    "delay_millis": 0,
}


@pytest.fixture
def valid_config_dict():
    return {
        "gamemode": "BLIND_TRIAL",
        "user_role": "OBSERVER",
        "network_enabled": False,
        "countdown_millis": 30000,
        "delay_millis": 1500,
    }


@pytest.fixture
def default_config_dict():
    return {
        "gamemode": "CLASSIC",
        "user_role": "CODEBREAKER",
        "network_enabled": False,
        "countdown_millis": 0,
        "delay_millis": 0,
    }


@pytest.fixture
def adapter_paths(tmp_path):
    return {
        "base_dir": tmp_path,
        "config_file_path": tmp_path / "current_game_config.json",
        "default_file_path": tmp_path / "default_game_config.json",
    }


@pytest.fixture
def adapter(adapter_paths):
    return ConfigJsonAdapter(**adapter_paths)


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# ---------- ConfigJsonAdapter: Constructor Tests ----------


def test_constructor_uses_default_paths_in_adapter_folder():
    """The default config files are located in the adapter's file_tool folder."""
    adapter = ConfigJsonAdapter()
    adapter_folder = Path(config_json_adapter.__file__).resolve().parent

    assert adapter.base_dir == adapter_folder
    assert adapter.config_file_path == adapter_folder / "current_game_config.json"
    assert adapter.default_file_path == adapter_folder / "default_game_config.json"


def test_constructor_accepts_paths_inside_base_dir(adapter_paths):
    """Direct child file paths inside base_dir are accepted."""
    adapter = ConfigJsonAdapter(**adapter_paths)

    assert adapter.base_dir == adapter_paths["base_dir"].resolve()
    assert adapter.config_file_path == adapter_paths["config_file_path"].resolve()
    assert adapter.default_file_path == adapter_paths["default_file_path"].resolve()


def test_constructor_rejects_path_outside_base_dir(tmp_path):
    """A current config path outside base_dir is rejected."""
    with pytest.raises(ValueError, match="base_dir"):
        ConfigJsonAdapter(
            base_dir=tmp_path / "allowed",
            config_file_path=tmp_path / "current_game_config.json",
            default_file_path=tmp_path / "allowed" / "default_game_config.json",
        )


def test_constructor_rejects_default_path_outside_base_dir(tmp_path):
    """A default config path outside base_dir is rejected."""
    with pytest.raises(ValueError, match="base_dir"):
        ConfigJsonAdapter(
            base_dir=tmp_path / "allowed",
            config_file_path=tmp_path / "allowed" / "current_game_config.json",
            default_file_path=tmp_path / "default_game_config.json",
        )


# ---------- ConfigJsonAdapter: save_config_dict Tests ----------


def test_save_config_dict_writes_json(adapter, adapter_paths, valid_config_dict):
    """save_config_dict writes the complete config dict as pretty JSON."""
    adapter.save_config_dict(valid_config_dict)

    assert read_json(adapter_paths["config_file_path"]) == valid_config_dict
    saved_text = adapter_paths["config_file_path"].read_text(encoding="utf-8")
    assert "\n" in saved_text
    assert "    " in saved_text


def test_save_config_dict_overwrites_existing_current_config(adapter, adapter_paths, valid_config_dict):
    """save_config_dict fully replaces an existing current config file."""
    old_config = {**HARD_CODED_DEFAULT_CONFIG, "stale_key": "must disappear"}
    write_json(adapter_paths["config_file_path"], old_config)

    adapter.save_config_dict(valid_config_dict)

    assert read_json(adapter_paths["config_file_path"]) == valid_config_dict


# ---------- ConfigJsonAdapter: load_config_dict Tests ----------


def test_load_config_dict_loads_current_config(adapter, adapter_paths, valid_config_dict, default_config_dict):
    """load_config_dict returns the current config when it exists."""
    write_json(adapter_paths["config_file_path"], valid_config_dict)
    write_json(adapter_paths["default_file_path"], default_config_dict)

    assert adapter.load_config_dict() == valid_config_dict


def test_load_config_dict_loads_default_when_current_missing(adapter, adapter_paths, default_config_dict):
    """Missing current config falls back to default and recreates current config."""
    write_json(adapter_paths["default_file_path"], default_config_dict)

    loaded_config = adapter.load_config_dict()

    assert loaded_config == default_config_dict
    assert read_json(adapter_paths["config_file_path"]) == default_config_dict


def test_load_config_dict_loads_default_from_hardcoded_when_default_missing(adapter, adapter_paths):
    """Missing current and default files fall back to hardcoded defaults."""
    loaded_config = adapter.load_config_dict()

    assert loaded_config == HARD_CODED_DEFAULT_CONFIG
    assert read_json(adapter_paths["config_file_path"]) == HARD_CODED_DEFAULT_CONFIG
    assert read_json(adapter_paths["default_file_path"]) == HARD_CODED_DEFAULT_CONFIG


def test_load_config_dict_resets_to_default_when_current_json_corrupt(adapter, adapter_paths, default_config_dict):
    """Corrupt current JSON is replaced by the default config."""
    adapter_paths["config_file_path"].write_text("{not valid json", encoding="utf-8")
    write_json(adapter_paths["default_file_path"], default_config_dict)

    loaded_config = adapter.load_config_dict()

    assert loaded_config == default_config_dict
    assert read_json(adapter_paths["config_file_path"]) == default_config_dict


def test_load_config_dict_resets_to_default_when_default_json_corrupt(adapter, adapter_paths):
    """Corrupt default JSON is replaced by hardcoded defaults."""
    adapter_paths["default_file_path"].write_text("{not valid json", encoding="utf-8")

    loaded_config = adapter.load_config_dict()

    assert loaded_config == HARD_CODED_DEFAULT_CONFIG
    assert read_json(adapter_paths["config_file_path"]) == HARD_CODED_DEFAULT_CONFIG
    assert read_json(adapter_paths["default_file_path"]) == HARD_CODED_DEFAULT_CONFIG


# ---------- ConfigJsonAdapter: reset_to_default Tests ----------


def test_reset_to_default_overwrites_current_with_default(adapter, adapter_paths, valid_config_dict):
    """reset_to_default overwrites current config with hardcoded defaults."""
    write_json(adapter_paths["config_file_path"], valid_config_dict)

    adapter.reset_to_default()

    assert read_json(adapter_paths["config_file_path"]) == HARD_CODED_DEFAULT_CONFIG
    assert read_json(adapter_paths["default_file_path"]) == HARD_CODED_DEFAULT_CONFIG
