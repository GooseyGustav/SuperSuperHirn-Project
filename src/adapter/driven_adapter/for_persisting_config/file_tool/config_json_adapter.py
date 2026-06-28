from app.ports.driven.for_persisting.for_persisting_config import ForPersistingConfig


class ConfigJsonAdapter(ForPersistingConfig):
    def __init__(self):
        pass

    def load_config_dict(self) -> dict:
        return {}

    def save_config_dict(self, config_dict: dict) -> None:
        print(f"JSON Config Driven Adapter. Dummy Save of {config_dict}")

    def reset_to_default(self) -> None:
        print("JSON Config Driven Adapter. Reset config file to default")
