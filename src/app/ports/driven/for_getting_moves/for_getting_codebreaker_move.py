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
    def get_guess(self, attempt_list: list[tuple[list[int], list[int]]]) -> list[int]:
        """Returns the Codebreaker's next guess to the App given the board so far.

        Args:
            attempt_list: every row on the board so far (each guess and its feedback).

        Returns:
            the Codebreaker's next guess as a list of ints representing the colors
            in that order.
        """

