from abc import ABC, abstractmethod


class ForGettingCodebreakerMove(ABC):
    """The port for getting the Codebreaker's next guess.

    Note:
        - Implemented by the Codebreaker Adapters (src/adapter/driven_adapter/for_getting_codebreaker_move).
        - Implemented for testing App by `FakeCodebreakerAdapter`
            (src/adapter/driven_adapter/for_getting_codebreaker_move).
        - Specific Codebreaker Adapter for game round instantiated based on
        game config by `Matchmaker` (src/startup).
        - Methods called by: `GameEngine` (src/app/game_management).
    """

    @abstractmethod
    def get_guess(self, attempt_list: list[tuple[list[int], list[int], str]]) -> list[int]:
        """Returns the Codebreaker's next guess to the App given the board so far.

        Args:
            attempt_list: every row on the board so far (each guess and its feedback).
            Each row is (guess, feedback, status):
                guess: list[int]  # pegs with colors guessed
                feedback: list[int]  # pegs with feedback colors (7 = white, 8 = black); order not relevant
                status:  str  # status of the attempt "FINAL" | "PROVISIONAL"

        Returns:
            the Codebreaker's next guess as a list of color ints.
        """
