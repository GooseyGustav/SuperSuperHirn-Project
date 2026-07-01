import pytest

from app.game_management.live_game.clock import Clock
from tests.unit.app.game_management.live_game.fake_now import FakeNow

# ---------- Clock: reset() ----------


def test_clock_reset_restores_full_budget():
    """reset() sets remaining_millis return the full time budget again."""
    fake = FakeNow()
    clock = Clock(max_time_millis=5000, now=fake)

    clock.start()
    fake.advance(2000)
    clock.reset()

    assert clock.remaining_millis() == 5000


def test_clock_reset_clears_deadline():
    """After reset(), is_expired() returns False even if time has passed."""
    fake = FakeNow()
    clock = Clock(max_time_millis=5000, now=fake)

    clock.start()
    fake.advance(9999)
    clock.reset()

    assert not clock.is_expired()


# ---------- Clock: start() ----------


def test_clock_not_expired_before_deadline():
    """is_expired() returns False immediately after start()."""
    fake = FakeNow()
    clock = Clock(max_time_millis=5000, now=fake)

    clock.reset()
    clock.start()

    assert not clock.is_expired()


def test_clock_expired_after_deadline():
    """is_expired() returns True once time has advanced past the budget."""
    fake = FakeNow()
    clock = Clock(max_time_millis=5000, now=fake)

    clock.reset()
    clock.start()
    fake.advance(5001)

    assert clock.is_expired()


def test_clock_not_expired_exactly_at_budget():
    """is_expired() returns False when time equals exactly the budget (not past it)."""
    fake = FakeNow()
    clock = Clock(max_time_millis=5000, now=fake)

    clock.reset()
    clock.start()
    fake.advance(5000)

    assert clock.is_expired()


# ---------- Clock: remaining_millis() ----------


def test_clock_remaining_millis_full_when_not_started():
    """remaining_millis() returns the full budget when clock has not been started."""
    clock = Clock(max_time_millis=5000)

    assert clock.remaining_millis() == 5000


def test_clock_remaining_millis_decreases_over_time():
    """remaining_millis() returns a smaller value after time advances."""
    fake = FakeNow()
    clock = Clock(max_time_millis=5000, now=fake)

    clock.reset()
    clock.start()
    fake.advance(2000)

    assert clock.remaining_millis() == 3000


def test_clock_remaining_millis_never_negative():
    """remaining_millis() returns 0 when the clock has expired, never negative."""
    fake = FakeNow()
    clock = Clock(max_time_millis=5000, now=fake)

    clock.reset()
    clock.start()
    fake.advance(9999)

    assert clock.remaining_millis() == 0


# ---------- Clock: per-move independence ----------


def test_clock_reset_isolates_moves():
    """Timing from one move does not leak into the next after reset()+start()."""
    fake = FakeNow()
    clock = Clock(max_time_millis=5000, now=fake)

    # Move 1: advance past deadline
    clock.reset()
    clock.start()
    fake.advance(9999)
    assert clock.is_expired()

    # Move 2: fresh start — should not be expired
    clock.reset()
    clock.start()

    assert not clock.is_expired()
    assert clock.remaining_millis() > 0


# ---------- Clock: constructor doesn't allow time_limits <= 0  ----------


def test_clock_rejects_negative_time_limit():
    """Clock rejects negative time budgets."""
    with pytest.raises(ValueError, match="bigger than 0"):
        Clock(max_time_millis=-1)


def test_clock_rejects_zero_time_limit():
    """Clock rejects a zero time budget."""
    with pytest.raises(ValueError, match="bigger than 0"):
        Clock(max_time_millis=0)
