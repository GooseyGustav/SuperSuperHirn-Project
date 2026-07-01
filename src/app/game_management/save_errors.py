class CorruptedSaveError(Exception):
    """Persisted game save is missing keys or the JSON data is malformed."""
