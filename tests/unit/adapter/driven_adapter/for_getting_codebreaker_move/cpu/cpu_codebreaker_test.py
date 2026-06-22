import pytest

from adapter.driven_adapter.for_getting_codebreaker_move.cpu.cpu_codebreaker import CpuCodebreaker

CODE_LENGTH = 5
COLOR_RANGE = range(1, 9)  # 1 - 8


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


# ---------- Codebreaker: Structural Tests ----------

def test_codebreaker_cpu_first_guess_valid_length(codebreaker):
    """
    First guess has no input and returns a code of length 5.
    """
    guess = codebreaker.get_guess([])
    assert len(guess) == CODE_LENGTH

def test_codebreaker_cpu_first_guess_valid_type(codebreaker):
    """
    Guess returns a code whose content are of type int.
    """

    guess = codebreaker.get_guess([])
    assert isinstance(guess, list)
    assert all(isinstance(x, int) for x in guess)

def test_codebreaker_cpu_first_guess_valid_content(codebreaker):
    """
    Guess contains a list of color_ids between 1 and 8 (inclusive)
    """

    guess = codebreaker.get_guess([])
    assert all(c in COLOR_RANGE for c in guess)


# ---------- Codebreaker: Functional Tests ----------

def test_codebreaker_cpu_guess_valid_after_history(codebreaker):
    """
    Guess structure is correct (type, content, value range), even after 
    feedbacks have been taken into account.
    """

    attempt_list = [
        ((1, 1, 2, 2, 3), (8, 7, 7)),
    ]
    guess = codebreaker.get_guess(attempt_list)
    assert len(guess) == CODE_LENGTH
    assert all(c in COLOR_RANGE for c in guess)

def test_codebreaker_cpu_deterministic_given_same_history(codebreaker):
    """
    Given the same history of feedbacks, the method should return the same guess every time it
    is run with the given history. It should be deterministic.
    """

    attempt_list = [
        ((1, 1, 2, 2, 3), (8, 8, 7)),
        ((1, 1, 4, 5, 2), (8, 8)),
        ((1, 6, 2, 3, 2), (8, 8, 8))
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
 
    previous_guess = (1, 2, 3, 4, 5)
    previous_feedback = (8, 8, 7, 7)  # 2 black, 2 white
 
    attempt_list = [(previous_guess, previous_feedback)]
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
        ((1, 1, 2, 2, 3), (8, 7, 7)),
        ((4, 5, 6, 7, 8), (7,))
    ]
    candidate = codebreaker.get_guess(attempt_list)
 
    for past_guess, past_feedback in attempt_list:
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
        ((1, 1, 1, 1, 1), (8, 8, 8, 8)),
        ((1, 1, 1, 1, 2), (8, 8, 8, 8)),
        ((1, 1, 1, 1, 3), (8, 8, 8, 8)),
        ((1, 1, 1, 1, 4), (8, 8, 8, 8)),
        ((1, 1, 1, 1, 5), (8, 8, 8, 8)),
        ((1, 1, 1, 1, 6), (8, 8, 8, 8)),
        ((1, 1, 1, 1, 7), (8, 8, 8, 8)),
    ]
    guess = codebreaker.get_guess(attempt_list)

    assert guess == [1, 1, 1, 1, 8]