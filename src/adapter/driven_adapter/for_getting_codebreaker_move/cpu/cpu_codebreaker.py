import itertools
import random

from app.ports.driven.for_getting_moves.for_getting_codebreaker_move import ForGettingCodebreakerMove

# Alias
Code = tuple[int, int, int, int, int]
Feedback = tuple[int, ...]
Attempt = tuple[Code, Feedback, str]

class CpuCodebreaker(ForGettingCodebreakerMove):
    """
    CPU implementation of a Mastermind codebreaker using candidate elimination
    and a Knuth-style minimax strategy.

    Feedback types:

    - final:
        Exact black and white peg counts are known. Candidate filtering uses
        precise (black, white) score comparison.

    - provisional:
        Feedback pegs are displayed as white pegs only, even though some may
        actually represent black pegs. Therefore only the total number of
        matching pegs is considered reliable. Candidate filtering uses a
        relaxed total-match comparison.
    """

    CODE_LENGTH = 5
    NUM_COLORS = 8
    BLACK_PEG = 8
    WHITE_PEG = 7

    # The first guess that is sent by this algorithm. It is common for Knuth Algorithm implementations
    # to start with 2 repeated numbers (and an additional third color_id, since the codes length is 5).
    _OPENING_GUESS = (1, 1, 2, 2, 3)

    def __init__(self) -> None:
            # The entire Codespace of all possible code combinations
            self._all_codes = list(
                itertools.product(range(1, CpuCodebreaker.NUM_COLORS + 1), repeat=CpuCodebreaker.CODE_LENGTH)
            )
            self._remaining_candidates = self._all_codes.copy()

    def get_guess(self, attempt_list: list[Attempt]) -> list[int]:
        """
        Return the next guess based on the attempt history.

        Behavior:
        - If the attempt list is invalid, fall back to a minimax guess from the
        current candidate pool.
        - If no attempts have been made, return the predefined opening guess.
        - Otherwise, filter the candidate space using all previous feedback and
        select the next guess using the minimax strategy.
        """

        if not self.is_attemptList_valid(attempt_list):
            return list(self._select_minimax_guess(self._remaining_candidates))

        if not attempt_list:
            return list(self._OPENING_GUESS)

        candidates = self._calc_candidates(attempt_list)

        # If only one canditate remains, the secret code has been found.
        if len(candidates) == 1:
            return list(candidates[0])

        # Choose best information-gathering guess
        next_guess = self._select_minimax_guess(candidates)
        return list(next_guess)

    # ---------- Candidate filtering ----------

    def _calc_candidates(
        self,
        attempt_list: list[Attempt]
    ) -> list[Code]:
        """
        Reduce the current candidate space by applying every recorded attempt in
        sequence.
        Each attempt removes codes that are inconsistent with the received
        feedback:

        If filtering eliminates all candidates, a random code from the full
        codespace is returned as a fallback because the received feedback is
        internally inconsistent (due to given feedback being falsy).
        """
        candidates = self._remaining_candidates

        for attempt in attempt_list:
            guess, feedback, status = attempt

            if status == "final":
                candidates = self._filter_by_exact_feedback(candidates, guess, feedback)
            else:
                candidates = self._filter_by_provisional_feedback(candidates, guess, feedback)
            
            # Only happens, if the feedback given to a guess is falsy, hence the secret can no longer be determined.
            if not candidates:
                return [random.choice(self._all_codes)]

        self._remaining_candidates = candidates
        return candidates

    def _filter_by_exact_feedback(
        self,
        candidates: list[Code],
        guess: Code,
        feedback: Feedback
    ) -> list[Code]:
        """
        Keep only candidates that would produce exactly the same final feedback
        (black peg count and white peg count) if `guess` were evaluated against
        them as the secret code.
        """
        expected_black, expected_white = self._feedback_to_counts(feedback)
        return [
            code for code in candidates
            if self._calc_candidate_guess_final_match(code, guess) == (expected_black, expected_white)
        ]

    def _filter_by_provisional_feedback(
        self,
        candidates: list[Code],
        guess: Code,
        feedback: Feedback
    ) -> list[Code]:
        """
        Keep only candidates whose total number of matching colors equals the
        number of pegs present in the provisional feedback.

        Because provisional feedback does not reliably distinguish between black
        and white pegs, only the total number of matches is considered.
        """
        total_pegs = len(feedback)
        return [
            code for code in candidates
            if self._calc_candidate_guess_provisional_match(code, guess) == total_pegs
        ]

    # ---------- Helpers ----------

    @staticmethod
    def is_attemptList_valid(attempt_list: list[Attempt]) -> bool:
        """
        Validate the structure and contents of an attempt history.

        An attempt consists of:

            (guess, feedback, status)

        where:
        - guess is a tuple of valid color IDs (between 1 and CpuCodebreaker.NUM_COLORS)
        - feedback is a tuple containing only black and white peg values (black = 8, white = 7)
        - status is either 'final' or 'provisional'

        An empty attempt list is considered valid because it represents the
        start of a game before any guesses have been made.
        """
        
        if len(attempt_list) == 0:
            return True

        for guess, feedback, status in attempt_list:

            guess_valid = (
                isinstance(guess, tuple)
                and len(guess) == CpuCodebreaker.CODE_LENGTH
                and all(isinstance(x, int) for x in guess)
                and all(1 <= c <= CpuCodebreaker.NUM_COLORS for c in guess)
            )

            feedback_valid = (
                isinstance(feedback, tuple)
                and len(feedback) <= CpuCodebreaker.CODE_LENGTH
                and all(isinstance(f, int) for f in feedback)
                and all(f in (7, 8) for f in feedback)
            )

            status_valid = status in ("final", "provisional")

            if not (guess_valid and feedback_valid and status_valid):
                return False

        return True

    @staticmethod
    def _feedback_to_counts(feedback: Feedback) -> tuple[int, int]:
        """
        Count black and white pegs contained in a feedback tuple.

        Returns:
            tuple[int, int]:
                (black_count, white_count)
        """
        black = sum(1 for pin in feedback if pin == CpuCodebreaker.BLACK_PEG)
        white = sum(1 for pin in feedback if pin == CpuCodebreaker.WHITE_PEG)
        return black, white

    @staticmethod
    def _calc_candidate_guess_final_match(
        secret: Code, 
        guess: Code
        ) -> tuple[int, int]:
        """
        Compute the exact Mastermind score for a candidate secret code and a
        guess.

        Returns:
            tuple[int, int]:
                (black_pegs, white_pegs)

        Black-peg matches are removed before counting white pegs to prevent
        double counting as well as using min() when comparing between secret_codespace and guess_codespace.
        """
        secret = list(secret)
        guess = list(guess)

        black = sum(1 for s, g in zip(secret, guess) if s == g)

        # Removes matching pins, where the feedback would return a black peg. Only keep mismatched pegs, which
        # could potentially be part of the code, or not.
        secret_remaining = [s for s, g in zip(secret, guess) if s != g]
        guess_remaining = [g for s, g in zip(secret, guess) if s != g]

        white = 0
        # Loop over unique colors. Prevents overcounting by choosing min.
        for color in set(guess_remaining):
            white += min(secret_remaining.count(color), guess_remaining.count(color))

        return black, white
    
    @staticmethod
    def _calc_candidate_guess_provisional_match(
        secret: Code,
        guess: Code
    ) -> int:
        """
        Compute the total number of color matches between a candidate secret and
        a guess, ignoring position.

        For each color, the minimum occurrence count in the secret and guess is
        added to the total. This effectively counts all matching colors without
        distinguishing between black and white pegs.

        Returns:
            int:
                Total number of matching colors.
        """
        matches = 0
        for color in set(guess):
            matches += min(secret.count(color), guess.count(color))
        return matches

    # ---------- Minimax selection (Knuth) ----------

    _MINIMAX_SAMPLE_THRESHOLD = 200

    def _select_minimax_guess(
        self,
        candidates: list[Code]
    ) -> Code:
        """
        Select the next guess using a Knuth-style minimax strategy.

        For each potential guess, the remaining candidate space is partitioned by
        the feedback pattern that each candidate would produce. The guess whose
        largest partition is smallest is chosen, minimizing the worst-case
        number of remaining candidates.

        Performance optimizations:

        1. Only remaining candidates are considered as possible guesses instead
        of the full codespace.

        2. If the candidate space exceeds `_MINIMAX_SAMPLE_THRESHOLD`, a
        deterministic sample is evaluated instead of the full candidate pool
        to reduce runtime while maintaining deterministic behavior.
        """

        guess_pool = candidates
        if len(candidates) > self._MINIMAX_SAMPLE_THRESHOLD:
            step = max(1, len(candidates) // self._MINIMAX_SAMPLE_THRESHOLD)
            guess_pool = candidates[::step]

        best_guess = None
        best_worst_case = None

        for guess in guess_pool:
            partitions = {}
            for candidate in candidates:
                pattern = self._calc_candidate_guess_final_match(candidate, guess)
                partitions[pattern] = partitions.get(pattern, 0) + 1

            worst_case = max(partitions.values())

            if best_worst_case is None or worst_case < best_worst_case:
                best_worst_case = worst_case
                best_guess = guess

        return best_guess
