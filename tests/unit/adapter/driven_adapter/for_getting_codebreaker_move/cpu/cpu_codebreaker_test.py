import pytest
import unittest
from unittest.mock import patch, MagicMock
import random


from adapter.driven_adapter.for_getting_codebreaker_move.cpu.cpu_codebreaker import CpuCodebreaker

CODE_LENGTH = CpuCodebreaker.CODE_LENGTH
COLOR_RANGE = CpuCodebreaker.NUM_COLORS

# ---------- Helper ----------

@pytest.fixture
def codebreaker():
    return CpuCodebreaker()

def compute_feedback(secret, guess):
    """
    Lokale Referenzimplementierung von Pegging (unabhängig vom CpuCodemaker),
    um get_guess-Resultate auf Konsistenz mit der Historie zu prüfen.
    Liefert (black_pegs, white_pegs) als Zahlen statt Pin-Liste, da für
    Konsistenzchecks nur die Counts relevant sind.
    """
    secret = list(secret)
    guess = list(guess)
 
    black = sum(1 for s, g in zip(secret, guess) if s == g)
 
    secret_remaining = [s for s, g in zip(secret, guess) if s != g]
    guess_remaining = [g for s, g in zip(secret, guess) if s != g]
 
    white = 0
    for color in set(guess_remaining):
        white += min(secret_remaining.count(color), guess_remaining.count(color))
 
    return black, white
 
 
def feedback_pins_to_counts(feedback):
    """
    Wandelt eine Feedback-Pin-Liste (Werte 7/8) in (black, white) Counts um,
    damit sie mit compute_feedback() verglichen werden kann.
    """
    black = sum(1 for pin in feedback if pin == 8)
    white = sum(1 for pin in feedback if pin == 7)
    return black, white


# ---------- Structural Tests ----------

def test_get_guess_first_guess_valid(codebreaker):
    """
    First guess has no input.
    Returns a code of length 5.
    Returns code whose content is of type <int>.
    Returns a list containing <int> between 1 and 8.
    """
    guess = codebreaker.get_guess([])
    assert len(guess) == CODE_LENGTH
    assert isinstance(guess, list)
    assert all(isinstance(x, int) for x in guess)
    assert all(1 <= c <= COLOR_RANGE for c in guess)

# ---------- get_guess() ----------

def test_codebreaker_cpu_deterministic_given_same_history(codebreaker):
    """
    Given the same history of feedbacks, the method should return the same guess every time it
    is run with the given history. It should be deterministic.
    """

    attempt_list = [
        ([1, 1, 2, 2, 3], [8, 8, 7], ("FINAL")),
        ([1, 1, 4, 5, 2], [8, 8], ("FINAL")),
        ([1, 6, 2, 3, 2], [8, 8, 8], ("FINAL"))
    ]
    guess_a = codebreaker.get_guess(attempt_list)
    guess_b = codebreaker.get_guess(attempt_list)
    assert guess_a == guess_b

def test_codebreaker_cpu_guess_consistent_with_single_history_entry(codebreaker):
    """
    Der zurückgegebene Guess muss, wenn man ihn hypothetisch als Secret gegen
    den historischen Guess prüft, dasselbe Feedback ergeben wie in der Historie
    vermerkt. Das ist eine Kerneigenschaft von Knuth: nur Kandidaten, die mit
    der gesamten bisherigen Historie konsistent sind, kommen in Frage.
    """
 
    previous_guess = [1, 2, 3, 4, 5]
    previous_feedback = [8, 8, 7, 7]  # 2 black, 2 white
 
    attempt_list = [(previous_guess, previous_feedback, ("FINAL"))]
    candidate = codebreaker.get_guess(attempt_list)
 
    black, white = compute_feedback(previous_guess, candidate)
    expected_black, expected_white = feedback_pins_to_counts(previous_feedback)
 
    assert (black, white) == (expected_black, expected_white)

def test_codebreaker_cpu_guess_consistent_with_multiple_history_entries(codebreaker):
    """
    Bei mehreren Historieneinträgen muss der nächste Guess mit ALLEN bisherigen
    (guess, feedback)-Paaren konsistent sein.
    """
    attempt_list = [
        ([1, 1, 2, 2, 3], [8, 7, 7], ("FINAL")),
        ([4, 5, 6, 7, 8], [7,], ("FINAL"))
    ]

    candidate = codebreaker.get_guess(attempt_list)
 
    for past_guess, past_feedback, _ in attempt_list:
        black, white = compute_feedback(past_guess, candidate)
        expected_black, expected_white = feedback_pins_to_counts(past_feedback)
        assert (black, white) == (expected_black, expected_white)


def test_codebreaker_cpu_returns_secret_when_only_one_candidate_remains(codebreaker):
    """
    Wurde der Hypothesenraum durch die Historie auf genau einen möglichen Code
    reduziert (5 schwarze Pins im letzten Versuch == korrekt geraten oder
    eindeutig identifiziert), muss genau dieser Kandidat zurückgegeben werden.
    """
    attempt_list = [
        ([1, 1, 1, 1, 1], [8, 8, 8, 8], ("FINAL")),
        ([1, 1, 1, 1, 2], [8, 8, 8, 8], ("FINAL")),
        ([1, 1, 1, 1, 3], [8, 8, 8, 8], ("FINAL")),
        ([1, 1, 1, 1, 4], [8, 8, 8, 8], ("FINAL")),
        ([1, 1, 1, 1, 5], [8, 8, 8, 8], ("FINAL")),
        ([1, 1, 1, 1, 6], [8, 8, 8, 8], ("FINAL")),
        ([1, 1, 1, 1, 7], [8, 8, 8, 8], ("FINAL"))
    ]
    guess = codebreaker.get_guess(attempt_list)

    assert guess == [1, 1, 1, 1, 8]


# ---------- _calc_candidates() ----------

def test_calc_candidates_final_status_calls_exact_feedback(codebreaker):
    codebreaker._filter_by_exact_feedback = MagicMock(
        return_value=codebreaker._remaining_candidates
    )
    codebreaker._filter_by_provisional_feedback = MagicMock(
        return_value=codebreaker._remaining_candidates
    )

    guess = [1, 2, 3, 4, 5]
    feedback = [8, 8, 7]

    codebreaker._calc_candidates([(guess, feedback, "FINAL")])

    codebreaker._filter_by_exact_feedback.assert_called_once_with(
        codebreaker._remaining_candidates,
        guess,
        feedback,
    )

    codebreaker._filter_by_provisional_feedback.assert_not_called()

def test_calc_candidates_provisional_status_provisional_exact_feedback(codebreaker):
    codebreaker._filter_by_exact_feedback = MagicMock(
        return_value=codebreaker._remaining_candidates
    )
    codebreaker._filter_by_provisional_feedback = MagicMock(
        return_value=codebreaker._remaining_candidates
    )

    guess = [1, 2, 3, 4, 5]
    feedback = [8, 8, 7]

    codebreaker._calc_candidates([(guess, feedback, "PROVISIONAL")])

    codebreaker._filter_by_exact_feedback.assert_not_called()

    codebreaker._filter_by_provisional_feedback.assert_called_once_with(
        codebreaker._remaining_candidates,
        guess,
        feedback
    )

def test_calc_candidates_return_random_guess_on_empty_candidates(codebreaker):
    attempt_list = [
        ([1, 2, 3, 4, 5], [], ("FINAL")),
        ([6, 7, 8, 8, 8], [], ("FINAL")),
    ]

    candidates = codebreaker._calc_candidates(attempt_list)
    assert len(candidates) == 1


# ---------- _filter_by_exact_feedback() ----------

def test_filter_by_exact_feedback(codebreaker):
    # secret = 1, 2, 3, 4, 5

    candidates = [
        [9, 3, 9, 4, 5], # match
        [2, 2, 2, 2, 2], # no match
        [9, 2, 4, 9, 5], # match
        [9, 9, 9, 9, 9], # no match
    ]

    guess = [1, 2, 9, 3, 9]
    feedback = [8, 8, 7]

    # expected comparison values
    expected_counts = [2, 1]

    # mock feedback conversion
    codebreaker._feedback_to_counts = MagicMock(return_value=expected_counts)

    # mock evaluation function
    def eval_mock(code, _):
        if code == [9, 3, 9, 4, 5] or code == [9, 2, 4, 9, 5]:
            return [2, 1]   # matches → kept
        return [0, 0]       # does not match → filtered out

    codebreaker._calc_candidate_guess_final_match = MagicMock(side_effect=eval_mock)

    result = codebreaker._filter_by_exact_feedback(candidates, guess, feedback)

    assert result == [[9, 3, 9, 4, 5], [9, 2, 4, 9, 5]]

    codebreaker._feedback_to_counts.assert_called_once_with(feedback)
    assert codebreaker._calc_candidate_guess_final_match.call_count == 4


# ---------- _filter_by_provisional_feedback() ----------

def test_filter_by_provisional_feedback(codebreaker):
    # secret: (1, 2, 3, 4, 5)

    candidates = [
        [9, 9, 1, 2, 3], # 3 white
        [9, 1, 2, 3, 9], # 3 white
        [1, 2, 3, 9, 9], # 3 black
        [1, 2, 9, 9, 9], # 2 black
        [9, 9, 9, 9, 9], # 0 black/white
    ]

    guess = [1, 2, 3, 9, 9]
    feedback = [7, 7, 7] # Final: (8, 8, 8) | Provisional: (7, 7, 7)

    def eval_mock(code, _):
        if code == [9, 9, 1, 2, 3]:
            return 3
        if code == [9, 1, 2, 3, 9]:
            return 3
        if code == [1, 2, 3, 9, 9]:
            return 3
        return 2

    codebreaker._calc_candidate_guess_provisional_match = MagicMock(
        side_effect=eval_mock
    )

    result = codebreaker._filter_by_provisional_feedback(candidates, guess, feedback)

    assert sorted(result) == sorted([
        [9, 1, 2, 3, 9],
        [9, 9, 1, 2, 3],
        [1, 2, 3, 9, 9],
    ])

    assert codebreaker._calc_candidate_guess_provisional_match.call_count == 5