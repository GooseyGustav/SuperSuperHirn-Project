from app.game_model.color_code.color import Color


class Slot:
    """Docstring for Slot."""

    # **Responsibility:** a single peg position.
    # **Attributes PEP8:**
    #     color: Color

    def __init__(self, color: Color | None = None):
        self.color = color

    def is_empty(self) -> bool: ...

    def set_color(self, color_id: int) -> None: ...

    def get_color(self) -> Color: ...
