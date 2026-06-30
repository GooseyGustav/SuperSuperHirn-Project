from app.ports.driven.for_persisting.for_persisting_game import ForPersistingGame


class GameJsonAdapter(ForPersistingGame):
    def __init__(self):
        pass

    def save_game(self, game_data: dict) -> None:
        print(f"Saving Game Data {game_data}")

    def load_game(self) -> dict:
        print("Returning dict for load_game")
        return {}

    def delete_game(self) -> None:
        print("Deleting Game Persist Data")
