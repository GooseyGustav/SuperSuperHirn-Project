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
            Each row a tuple built as (guess, feedback, status) with:
                guess: list[int]    # pegs with colors guessed
                                    # (length: number_of_positions)
                feedback: list[int] # pegs with feedback colors (7 = white, 8 = black); order not relevant
                                    # (length: 0..number_of_positions)
                status:  str  # status of the attempt "FINAL" | "PROVISIONAL" (all caps)
                        In a row with PROVISIONAL feedback: differentiation between black and white pegs is hidden,
                        so the feedback pegs are all white (all 7) (length: total number of feedback pegs,
                        black + white). In a row with FINAL feedback: true feedback is shown with
                        [8] * black_pins, [7] * white_pins.
                (On length info: number_of_positions is injected in constructor by the Matchmaker.)


        Returns:
            the Codebreaker's next guess as a list of color ints.   # (length: number_of_positions)
        """
