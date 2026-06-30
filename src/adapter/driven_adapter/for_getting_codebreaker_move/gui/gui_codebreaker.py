from app.ports.driven.for_getting_moves.for_getting_codebreaker_move import ForGettingCodebreakerMove


class GuiCodebreaker(ForGettingCodebreakerMove):

    def __init__(self): ...

    def get_guess(self, attempt_list: list[tuple[list[int], list[int], str]]) -> list[int]:
        pass
