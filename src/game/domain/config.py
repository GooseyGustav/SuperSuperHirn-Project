class Config:
    """Repräsentiert die Spielkonfiguration."""
    def __init__(self, difficulty: str = "normal"):
        self.difficulty = difficulty

    def __repr__(self):
        return f"Config(difficulty='{self.difficulty}')"
