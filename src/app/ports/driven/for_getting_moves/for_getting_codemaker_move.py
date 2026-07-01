from abc import ABC, abstractmethod


class ForGettingCodemakerMove(ABC):
    """The port for getting the Codemaker's next move.
    Its move at the beginning of the game is inputting its secret code.
    Each of the following moves is the Codemaker's feedback to the
    Codebreaker's latest guess.

    Color IDs for pins of the secret code and feedback:
    1=Red, 2=Green, 3=Yellow, 4=Blue, 5=Orange, 6=Brown, 7=White, 8=Black

    Note:
        The caller does not enforce the correctness of the feedback;
        mistaken or deliberately misleading feedback can be given.

    Note (project implementation):
        - Implemented by the Codemaker Adapters (src/adapter/driven_adapter/for_getting_codemaker_move).
        - Implemented for testing App by `FakeCodemakerAdapter` (src/adapter/driven_adapter/for_getting_codemaker_move).
        - Specific Codemaker Adapter for game round instantiated based on
            game config by `Matchmaker` (src/startup).
        - Methods called by: `GameEngine` (src/app/game_management).
    """

    @abstractmethod
    def get_secret_code(self) -> list[int]:
        """Returns the Codemaker's secret code to the app at the beginning of the game.

        Returns:
            the Codemaker's secret code as a list of ints.
        """

    @abstractmethod
    def get_feedback(self, secret: list[int], guess: list[int]) -> list[int]:
        """Returns the Codemaker's next move to the app: feedback to the Codebreaker's
        newest guess.

        Args:
            secret: the Codemaker's secret code as a list of ints
            guess: the Codebreaker's latest guess as a list of ints
            (Length of both: number_of_positions; number_of_positions: injected in constructor by the Matchmaker.)

        Returns:
            the feedback as a peg list of color ints (7 = white, 8 = black),
            e.g. [8, 8, 7] for a guess with 2 black pegs and 1 white peg.
            (Length: 0..number_of_positions;  number_of_positions: injected in constructor by the Matchmaker.)
            peg position in list is not relevant.
            (Provisional/final status is not returned here, as that is set by the model.)
        """
