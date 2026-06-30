from app.ports.driven.for_persisting.for_persisting_config import ForPersistingConfig


class ConfigJsonAdapter(ForPersistingConfig):
    def __init__(self):
        pass

    def load_config_dict(self) -> dict:
                return {
                    "gamemode":             "CLASSIC",   # CLASSIC | TIME_TRIAL | BLIND_TRIAL
                    "user_role":            "CODEBREAKER",   # CODEMAKER | CODEBREAKER | OBSERVER
                    "network_enabled":      False,
                    "countdown_millis":     1000,   # TIME_TRIAL countdown time, milliseconds
                    "delay_millis":         1000,   # OBSERVER mode: ms between auto-moves so progress is visible
                }

    def save_config_dict(self, config_dict: dict) -> None:
        print(f"JSON Config Driven Adapter. Dummy Save of {config_dict}")

    def reset_to_default(self) -> None:
        print("JSON Config Driven Adapter. Reset config file to default")
