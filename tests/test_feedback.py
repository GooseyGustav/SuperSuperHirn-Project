import pytest
from src.game.domain.feedback import Feedback


def test_feedback_defaults():
    fb = Feedback()
    assert fb.getFeedback() == (0, 0)

def test_feedback_values():
    fb = Feedback(black_pins=3, white_pins=1)
    assert fb.getFeedback() == (3, 1)
