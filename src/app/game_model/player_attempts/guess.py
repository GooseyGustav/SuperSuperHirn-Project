from app.game_model.color_code.code import Code


class Guess:
    """Docstring for Guess."""

    # - **Responsibility:** the codebreaker's guessed code.
    # - **Attributes PEP8:**
    #     code_guess: Code

    def __init__(self, code_guess: Code) -> None:
        self.code_guess = code_guess

    def get_code_guess(self) -> Code: ...
