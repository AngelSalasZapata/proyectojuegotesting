import math
import pytest
from unittest.mock import MagicMock, patch

from src.entities.ai_car import AICar, STUCK_SPEED_RATIO, STUCK_PATIENCE
from settings import AI_SENSOR_ANGLES


@pytest.fixture
def mock_track():
    track = MagicMock()
    track.probe_ahead.return_value = (True, 50, 50)
    track.waypoints = [(100, 100), (300, 100), (400, 300), (300, 500),
                       (100, 500), (0, 300)]
    track.n = 6
    track._track_info.return_value = (0.5, 10, 200, 200, 0)
    track.get_lookahead_point.return_value = (300, 100, 0)
    track.is_on_track.return_value = True
    return track


@pytest.fixture
def ai_car(mock_track):
    return AICar(200, 200, (0, 0, 255), mock_track, speed_multiplier=1.5)


class TestAICarInit:
    """RED: test de inicialización del AICar.
       GREEN: implementar AICar.__init__.
    """

    def test_extends_car(self, ai_car):
        from src.entities.car import Car
        assert isinstance(ai_car, Car)

    def test_speed_multiplied(self, ai_car):
        from settings import CAR_MAX_SPEED
        assert ai_car.max_speed == CAR_MAX_SPEED * 1.5

    def test_turn_speed_set(self, ai_car):
        assert ai_car.turn_speed == 0.5

    def test_not_finished_initially(self, ai_car):
        assert ai_car.finished is False

    def test_not_recovering_initially(self, ai_car):
        assert ai_car._recovering is False


class TestAICarSensors:
    """RED: test de _read_sensors.
       GREEN: implementar con probe_ahead del track.
    """

    def test_sensors_return_three_readings(self, ai_car, mock_track):
        readings = ai_car._read_sensors()
        assert len(readings) == len(AI_SENSOR_ANGLES)

    def test_sensor_readings_have_correct_format(self, ai_car):
        readings = ai_car._read_sensors()
        for on_track, offset in readings:
            assert isinstance(on_track, bool)
            assert isinstance(offset, (int, float))

    def test_sensor_calls_probe_ahead(self, ai_car, mock_track):
        ai_car._read_sensors()
        assert mock_track.probe_ahead.call_count == len(AI_SENSOR_ANGLES)

    def test_sensor_detects_off_track(self, ai_car, mock_track):
        mock_track.probe_ahead.return_value = (False, 0, 0)
        readings = ai_car._read_sensors()
        assert all(not on_track for on_track, _ in readings)


class TestAICarStuckRecovery:
    """RED: test de _update_stuck_state.
       GREEN: implementar lógica de stuck → recovery.
    """

    def test_not_stuck_at_high_speed(self, ai_car):
        ai_car._update_stuck_state(1.0)
        assert ai_car._recovering is False

    def test_stuck_timer_increments_at_low_speed(self, ai_car):
        ai_car._update_stuck_state(0.0)
        assert ai_car._stuck_timer == 1

    def test_stuck_timer_resets_at_high_speed(self, ai_car):
        ai_car._stuck_timer = 5
        ai_car._update_stuck_state(1.0)
        assert ai_car._stuck_timer < 5

    def test_recovery_triggers_after_patience(self, ai_car):
        for _ in range(STUCK_PATIENCE + 2):
            ai_car._update_stuck_state(0.0)
        assert ai_car._recovering is True

    def test_recovery_does_not_trigger_before_patience(self, ai_car):
        for _ in range(STUCK_PATIENCE):
            ai_car._update_stuck_state(0.0)
        assert ai_car._recovering is False

    def test_recovery_exits_when_speed_returns(self, ai_car):
        for _ in range(STUCK_PATIENCE + 2):
            ai_car._update_stuck_state(0.0)
        assert ai_car._recovering is True
        for _ in range(10):
            ai_car._update_stuck_state(1.0)
        assert ai_car._recovering is False

    def test_unstuck_ticks_set_on_recovery(self, ai_car):
        for _ in range(STUCK_PATIENCE + 2):
            ai_car._update_stuck_state(0.0)
        assert ai_car._unstuck_ticks > 0


class TestAICarUpdate:
    """RED: test de update() de AICar.
       GREEN: implementar el loop de steering + speed control.
    """

    def test_update_moves_car(self, ai_car, mock_track):
        ai_car.angle = 0
        ai_car.speed = 2.0
        x0, y0 = ai_car.x, ai_car.y
        ai_car.update()
        assert (ai_car.x, ai_car.y) != (x0, y0) or ai_car.speed != 2.0

    def test_finished_car_slows(self, ai_car, mock_track):
        ai_car.finished = True
        ai_car.speed = 5.0
        ai_car.update()
        assert ai_car.speed < 5.0

    def test_update_does_not_crash(self, ai_car, mock_track):
        ai_car.update()
