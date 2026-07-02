class CorruptedSaveError(Exception):
    """Persisted game save is missing keys or the JSON data is malformed.

    At the app boundary, can be shared by app and adapters.
    Raised by the game-persistence adapter if malformed JSON data to resume
    game from and by GameEngine.resume() if structurally corrupt data,
    surfaced through GameManager to the driving adapter (GUI).
    """
