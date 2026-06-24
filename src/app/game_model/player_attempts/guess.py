from app.game_model.color_code.code import Code


class Guess:
    """The codebreaker's submitted colour sequence for one round.

    Wraps a Code object so the rest of the model can treat a player's
    guess as a typed value rather than a raw list of integers.
    """

    def __init__(self, code_guess: Code) -> None:
        self.code_guess = code_guess

    def get_code_guess(self) -> Code:
        """Return the Code that was submitted as this guess."""
        return self.code_guess
