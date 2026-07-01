import json
from pathlib import Path

from app.ports.driven.for_persisting.for_persisting_game import ForPersistingGame


class GameJsonAdapter(ForPersistingGame):
    """Adapter to persist the game state as a JSON file.

    This class handles writing and reading the flat game dictionary to and
    from the file system. It explicitly propagates FileNotFoundError and
    JSONDecodeError so the caller (GameManager) can handle missing or
    corrupt save files appropriately.
    """

    def __init__(self, base_dir: str | Path | None = None, file_name: str = "current_game_save.json") -> None:
        """Initialize the game storage adapter.

        Args:
            base_dir: The directory where the save file should be stored.
                      Defaults to the directory of this python file.
            file_name: The name of the save file.
        """
        # Resolve the base directory, or use the directory of this adapter file.
        self.base_dir = Path(base_dir).resolve() if base_dir is not None else Path(__file__).resolve().parent
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.file_path = self.base_dir / file_name

    def save_game(self, game_data: dict) -> None:
        """Saves the provided game dictionary to disk as a JSON file."""
        with self.file_path.open("w", encoding="utf-8") as json_file:
            json.dump(game_data, json_file, indent=4)
            json_file.write("\n")

    def load_game(self) -> dict:
        """Loads the game dictionary from the JSON file on disk.

        Returns:
            dict: The parsed game data.

        Raises:
            FileNotFoundError: If the save file does not exist.
            json.JSONDecodeError: If the file exists but contains invalid JSON.
        """
        with self.file_path.open("r", encoding="utf-8") as json_file:
            return json.load(json_file)

    def delete_game(self) -> None:
        """Deletes the save file if it exists. Passes silently otherwise."""
        if self.file_path.exists():
            self.file_path.unlink()
