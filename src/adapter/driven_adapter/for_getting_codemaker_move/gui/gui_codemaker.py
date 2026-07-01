from app.ports.driven.for_getting_moves.for_getting_codemaker_move import ForGettingCodemakerMove


class GuiCodemaker(ForGettingCodemakerMove):

    def __init__(self): ...

    def get_secret_code(self) -> list[int]:
        pass

    def get_feedback(self, secret: list[int], guess: list[int]) -> list[int]:
        pass
