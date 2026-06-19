import pytest
import random

from src.adapter.driven_adapter.for_getting_codemaker_move.cpu.cpu_codemaker import CpuCodemaker

@pytest.fixture
def codemaker():
    return CpuCodemaker()


# ---------- Codemaker: Secret Code Tests ----------


def test_codemaker_cpu_secret_code_valid_length(codemaker):
    """
    Secret code has a length of 5.
    """
    secret = codemaker.get_secret_code()

    assert len(secret) == 5

def test_codemaker_cpu_secret_code_valid_type(codemaker):
    """
    Secret code is of type list and contains only values of type int.
    """

    secret = codemaker.get_secret_code()

    assert isinstance(secret, list)
    assert all(isinstance(x, int) for x in secret)


def test_codemaker_cpu_secret_code_valid_content(codemaker):
    """
    Secret code contains only integers between 1 and 8.
    """

    secret = codemaker.get_secret_code()
    assert all(1 <= x <= 8 for x in secret)

def test_codemaker_cpu_secret_code_double_color(codemaker):
    """
    Validates that the secret code may contain duplicate color ids.
    """

    random.seed(1)
    secret = codemaker.get_secret_code()

    assert len(secret) == 5
    assert all(1 <= x <= 8 for x in secret)
    assert len(set(secret)) <= 5


# ---------- Codemaker: Feedback Tests ----------


def test_codemaker_cpu_feedback_valid_type(codemaker):
    """
    Feedback is a list and contains only values of type int.
    """
    secret = [1, 2, 3, 4, 5]
    guess = [1, 2, 3, 4, 5]
    feedback = codemaker.get_feedback(secret, guess)
    assert isinstance(feedback, list)
    assert all(isinstance(x, int) for x in feedback)


def test_codemaker_cpu_feedback_valid_content(codemaker):
    """
    Feedback contains only the values 7 (white peg) or 8 (black peg) and its length is less or equal than 5.
    """
    secret = [1, 2, 3, 4, 5]
    guess = [5, 4, 3, 2, 1]
    feedback = codemaker.get_feedback(secret, guess)
    assert all(x in (7, 8) for x in feedback)
    assert len(feedback) <= 5

def test_codemaker_cpu_feedback_full_match(codemaker):
    """
    Guess matches the secret code exactly -> 5 black pegs (8).
    """
    secret = [1, 2, 3, 4, 5]
    guess = [1, 2, 3, 4, 5]
    feedback = codemaker.get_feedback(secret, guess)
    assert sorted(feedback) == [8, 8, 8, 8, 8]

def test_codemaker_cpu_feedback_no_match(codemaker):
    """
    No color from the guess appears in the secret code.
    """
    secret = [1, 1, 1, 1, 1]
    guess = [2, 2, 2, 2, 2]
    feedback = codemaker.get_feedback(secret, guess)
    assert feedback == []

def test_codemaker_cpu_feedback_only_white_pegs(codemaker):
    """
    All colors exist but in wrong positions -> only white pegs (7).
    """
    secret = [1, 2, 3, 4, 5]
    guess = [5, 1, 2, 3, 4]
    feedback = codemaker.get_feedback(secret, guess)
    assert sorted(feedback) == [7, 7, 7, 7, 7]

def test_codemaker_cpu_feedback_mixed_black_and_white(codemaker):
    """
    Mix of correct color in correct position (black) and correct color in wrong position (white).
    """
    secret = [1, 2, 3, 4, 5]
    guess = [1, 3, 2, 4, 6]
    feedback = codemaker.get_feedback(secret, guess)
    assert sorted(feedback) == [7, 7, 8, 8] # 1|4 black, 2|3 white, 6 empty

def test_codemaker_cpu_feedback_duplicate_colors_in_guess_more_than_secret(codemaker):
    """
    Guess contains a color more often than it appears in the secret.
    white pegs are only assigned as often as the color exists in the secret and no black peg has been assigned for them.
    """
    secret = [1, 1, 2, 3, 4]
    guess = [1, 1, 1, 5, 6]
    feedback = codemaker.get_feedback(secret, guess)
    assert sorted(feedback) == [8, 8]

def test_codemaker_cpu_feedback_duplicate_colors_in_secret_more_than_guess(codemaker):
    """
    Secret contains a color multiple times, guess only once in right position.
    Only one black peg, no overcounting of duplicates in secret compared to guess.
    """
    secret = [1, 1, 2, 3, 4]
    guess = [5, 1, 5, 5, 5]
    feedback = codemaker.get_feedback(secret, guess)
    assert sorted(feedback) == [8]

def test_codemaker_cpu_feedback_duplicate_colors_only_white(codemaker):
    """
    Secret and guess contain the same color multiple times, but mostly in different positions.
    Identify correlations in position and color and identify mismatch in position to assign white pegs.
    """
    secret = [1, 1, 2, 2, 3]
    guess = [2, 2, 1, 1, 3]
    feedback = codemaker.get_feedback(secret, guess)
    assert sorted(feedback) == [7, 7, 7, 7, 8]

