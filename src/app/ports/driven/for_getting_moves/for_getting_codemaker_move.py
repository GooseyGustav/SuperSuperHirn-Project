from abc import ABC, abstractmethod


class ForGettingCodemakerMove(ABC):
    """The port for getting the Codemaker's next move.
    Its move at the beginning of the game is inputting its secret code.
    Each of the following moves is the Codemaker's feedback to the
    Codebreaker's latest guess.

    Color IDs for pins of the secret code and feedback:
    1=Red, 2=Green, 3=Yello, 4=Blue, 5=Orange, 6=Brown, 7=White, 8=Black

    Note:
        The caller does not enforce the correctness of the feedback;
        mistaken or deliberately misleading feedback can be given.

    Note (project implementation):
        - Implemented by the Codemaker Adapters (src/adapter/driven_adapter/for_getting_codemaker_mov).
        - Implemented for testing App by `FakeCodemakerAdapter` (src/adapter/driven_adapter/for_getting_codemaker_mov).
        - Specific Codemaker Adapter for game round instantiated based on
            game config by `Matchmaker` (src/startup).
        - Methods called by: `GameEngine` (src/app/game_management).
    """

    @abstractmethod
    def get_secret_code(self) -> list[int]:
        """Returns the Codemaker's secret code to the app at the beginning of the game.

        Returns:
            the Codemaker's secret code as a list of ints (length constraints:
            => 1 and =< 9).
        """

    @abstractmethod
    def get_feedback(self, secret: list[int], guess: list[int]) -> list[int]:
        """Returns the Codemaker's next move to the app: feedback to the Codebreaker's
        newest guess.

        Args:
            secret: the Codemaker's secret code as a list of ints
                    (length constraints: => 1 and =< 9, = length of list returned by get_secret_code())
            guess: the Codebreaker's latest guess as a list of ints
                    (length constraints: guess.len() = secret.len()).

        Returns:
            the feedback pins as a list [number-of-BLACK-pins, number-of-WHITE-pins]
            or if game_mode = BLIND_TRIAL:
            [number-of-BLACK-pins, number-of-WHITE-pins, guess-status]
        """
