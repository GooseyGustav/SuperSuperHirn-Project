import pytest
from src.game.domain.attempt import Attempt
from src.game.domain.code import Code
from src.game.domain.feedback import Feedback


def test_attempt_returns_code_and_feedback():
    code = Code()
    feedback = Feedback(black_pins=2, white_pins=1)
    attempt = Attempt(code, feedback)
    result_code, result_feedback = attempt.getAttempt()
    assert result_code is code
    assert result_feedback is feedback
