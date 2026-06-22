import itertools

from app.ports.driven.for_getting_moves.for_getting_codebreaker_move import ForGettingCodebreakerMove

CODE_LENGTH = 5
NUM_COLORS = 8
BLACK_PEG = 8
WHITE_PEG = 7

class CpuCodebreaker(ForGettingCodebreakerMove):

    # The first guess that is sent by this algorithm. It is common for Knuth Algorithm implementations
    # to start with 2 repeated numbers (and an additional third color_id, since the codes length is 5).
    _OPENING_GUESS = [1, 1, 2, 2, 3]

    def __init__(self):
            # The entire Codespace of all possible code combinations
            self._all_codes = list(
                itertools.product(range(1, NUM_COLORS + 1), repeat=CODE_LENGTH)
            )
            # TODO: Can be a file containing all possible codes.

    def get_guess(self, attemptList: list[tuple[tuple[int], tuple[int]]]) -> list[int]:
        """
        
        """
        if not attemptList:
            return list(self._OPENING_GUESS)

        candidates = self._consistent_candidates(attemptList)

        # If only one canditate remains, the secret code has been found.
        if len(candidates) == 1:
            return list(candidates[0])

        # Choose best information-gathering guess
        next_guess = self._select_minimax_guess(candidates)
        return list(next_guess)

    # ---------- Hypothesenraum ----------

    def _consistent_candidates(self, attemptList):
        """
        Filtert alle Codes des vollen Codespace auf jene, die mit JEDEM
        bisherigen (guess, feedback)-Paar der Historie konsistent sind.
        """
        candidates = self._all_codes

        for past_guess, past_feedback in attemptList:
            expected_black, expected_white = self._feedback_to_counts(past_feedback)
            candidates = [
                code for code in candidates
                if self._score(code, past_guess) == (expected_black, expected_white)
            ]

        return candidates

    @staticmethod
    def _feedback_to_counts(feedback: tuple[int]) -> tuple[int, int]:
        """
        Count the amount of black and white pegs in this single given feedback.
        Returns:
            list[int, int]: The amount of black and white pegs.
        """
        black = sum(1 for pin in feedback if pin == BLACK_PEG)
        white = sum(1 for pin in feedback if pin == WHITE_PEG)
        return black, white

    @staticmethod
    def _score(secret, guess) -> tuple[int, int]:
        """
        Calculate for each possible secret_code candidate how many black and white pegs the given guess 
        would produce.
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

    # ---------- Minimax-Auswahl (Knuth) ----------

    # Schwelle, ab der NICHT mehr alle verbleibenden Kandidaten als
    # Guess-Pool für die Minimax-Bewertung durchsucht werden, sondern nur
    # eine Stichprobe - klassischer Trade-off Knuth-Optimalitaet vs.
    # Laufzeit. Bei kleinem Kandidatenraum (typischerweise ab Runde 2-3)
    # wird ohnehin der volle Pool genutzt, da er dann schnell genug ist.
    _MINIMAX_SAMPLE_THRESHOLD = 200

    def _select_minimax_guess(self, candidates):
        """
        Waehlt den naechsten Guess nach Knuths Minimax-Strategie:
        Fuer jeden potenziellen Guess wird der Hypothesenraum nach dem
        jeweils resultierenden Feedback-Pattern partitioniert. Es gewinnt
        der Guess, dessen GROESSTE Partition (Worst Case) am KLEINSTEN ist,
        da er garantiert den meisten Informationsgewinn im schlechtesten
        Fall liefert.

        Optimierung gegenueber dem reinen Lehrbuch-Algorithmus:
        1) Als Guess-Pool wird nur die Menge der verbleibenden Kandidaten
        durchsucht statt des vollen Codespace (8^5 = 32768 Codes) - das
        reduziert die Laufzeit drastisch und liefert in der Praxis
        nahezu identische Ergebnisse, da der optimale Guess fast immer
        ohnehin im Kandidatenraum liegt.
        2) Ist der Kandidatenraum selbst noch sehr gross (typischerweise
        nur in der allerersten Runde nach dem Opening-Guess relevant),
        wird die Bewertung auf eine deterministische Stichprobe der
        Kandidaten begrenzt, um O(n^2)-Explosion zu vermeiden. Ein
        Kandidat aus dem Pool ist immer mit dabei (deterministisch via
        Slicing, kein Zufall - sonst waere get_guess nicht mehr
        deterministisch bei gleicher Historie).
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
                pattern = self._score(candidate, guess)
                partitions[pattern] = partitions.get(pattern, 0) + 1

            worst_case = max(partitions.values())

            if best_worst_case is None or worst_case < best_worst_case:
                best_worst_case = worst_case
                best_guess = guess

        return best_guess
