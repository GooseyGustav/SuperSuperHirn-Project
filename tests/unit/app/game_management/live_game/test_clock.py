from app.game_management.live_game.clock import Clock


class TestClock:
    def test_clock_initialization(self):
        max_time = 60000
        clock = Clock(max_time_millis=max_time)
        assert clock.MAX_TIME_MILLIS == max_time
        assert clock.remainingTimeMillis == max_time

    def test_start_clock_execution(self):
        clock = Clock(max_time_millis=1000)
        # Assuming empty implementation doesn't raise errors
        clock.start_clock()

    def test_interrupt_game_timeout_execution(self):
        clock = Clock(max_time_millis=1000)
        clock._interrupt_game_timeout()

    def test_reset_clock_execution(self):
        clock = Clock(max_time_millis=1000)
        clock._reset_clock()
