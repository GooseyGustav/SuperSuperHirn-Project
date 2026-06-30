import json
from json import JSONDecodeError
from pathlib import Path

from app.ports.driven.for_persisting.for_persisting_config import ForPersistingConfig


class ConfigJsonAdapter(ForPersistingConfig):
    DEFAULT_CONFIG = {
        "gamemode": "CLASSIC",
        "user_role": "CODEBREAKER",
        "network_enabled": False,
        "countdown_millis": 0,
        "delay_millis": 0,
    }

    def __init__(
        self,
        base_dir: str | Path | None = None,
        config_file_path: str | Path | None = None,
        default_file_path: str | Path | None = None,
    ) -> None:
        """Initialize the ConfigJsonAdapter.

        The adapter uses `base_dir` as the directory for the default configuration
        file names if no explicit file paths are provided. This is especially useful
        in tests, where temporary directories or test-specific JSON files can be used.

        Args:
            base_dir: Base directory used for default JSON file paths. If `None`,
                the directory containing this adapter file is used.
            config_file_path: Path to the current game configuration JSON file.
                If `None`, `current_game_config.json` inside `base_dir` is used.
            default_file_path: Path to the default game configuration JSON file.
                If `None`, `default_game_config.json` inside `base_dir` is used.

        Raises:
            ValueError: _description_
            ValueError: _description_
        """

        # Resolve the base directory, or use the directory of this adapter file.
        self.base_dir = Path(base_dir).resolve() if base_dir is not None else Path(__file__).resolve().parent

        # Resolve the path to the current game configuration file.
        self.config_file_path = (
            Path(config_file_path).resolve()
            if config_file_path is not None
            else self.base_dir / "current_game_config.json"
        )

        # Resolve the path to the default game configuration file.
        self.default_file_path = (
            Path(default_file_path).resolve()
            if default_file_path is not None
            else self.base_dir / "default_game_config.json"
        )

        # TODO Error-handling ?
        if self.config_file_path.parent != self.base_dir:
            raise ValueError("config_file_path must be directly inside base_dir")

        if self.default_file_path.parent != self.base_dir:
            raise ValueError("default_file_path must be directly inside base_dir")

        self.base_dir.mkdir(parents=True, exist_ok=True)

    def load_config_dict(self) -> dict:
        try:
            return self._read_json_dict(self.config_file_path)
        except (FileNotFoundError, JSONDecodeError, ValueError):
            default_config = self._load_default_config()
            self.save_config_dict(default_config)
            return default_config

    def save_config_dict(self, config_dict: dict) -> None:
        self._write_json_dict(self.config_file_path, config_dict)

    def reset_to_default(self) -> None:
        default_config = self.DEFAULT_CONFIG.copy()
        self._write_json_dict(self.default_file_path, default_config)
        self._write_json_dict(self.config_file_path, default_config)

    def _load_default_config(self) -> dict:
        try:
            return self._read_json_dict(self.default_file_path)
        except (FileNotFoundError, JSONDecodeError, ValueError):
            default_config = self.DEFAULT_CONFIG.copy()
            self._write_json_dict(self.default_file_path, default_config)
            return default_config

    @staticmethod
    def _read_json_dict(path: Path) -> dict:
        with path.open("r", encoding="utf-8") as json_file:
            data = json.load(json_file)

        if not isinstance(data, dict):
            raise ValueError("Config JSON must contain an object.")

        return data

    @staticmethod
    def _write_json_dict(path: Path, config_dict: dict) -> None:
        with path.open("w", encoding="utf-8") as json_file:
            json.dump(config_dict, json_file, indent=4)
            json_file.write("\n")
