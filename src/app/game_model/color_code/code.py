from app.game_model.color_code.slot import Slot


class Code:
    """Docstring for Code."""

    # - **Responsibility:** a validated colour sequence (used for guesses and the secret).
    # - **Attributes PEP8:**
    #     code: tuple[int, list[Slot]]
    #     UML version: - code: Tuple<length: int, code: List<Slot>>

    def __init__(self, code: tuple[int, list[Slot]]) -> None:
        self.code = code

    def is_valid(self) -> bool: ...

    def set_code(self, code: list[int]) -> None: ...

    def get_code(self) -> list[Slot]: ...
