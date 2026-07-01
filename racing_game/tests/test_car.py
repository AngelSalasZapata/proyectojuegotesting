import math
import pytest
from unittest.mock import patch, MagicMock
from src.entities.car import Car


class TestCarPhysics:
    """RED: tests de física del auto (acelerar, frenar, girar, fricción).
       GREEN: implementar en Car. REFACTOR: separar constantes a settings.
    """

    def test_initial_speed_is_zero(self, car):
        assert car.speed == 0

    def test_initial_position(self, car):
        assert car.x == 200
        assert car.y == 200

    def test_initial_angle(self, car):
        assert car.angle == -90

    def test_accelerate_increases_speed(self, car):
        car.accelerate()
        assert car.speed > 0

    def test_accelerate_caps_at_max_speed(self, car):
        for _ in range(1000):
            car.accelerate()
        assert car.speed <= car.max_speed

    def test_brake_decreases_positive_speed(self, car):
        car.speed = 2.0
        car.brake()
        assert car.speed < 2.0

    def test_brake_floors_at_half_negative_max(self, car):
        car.speed = -100
        car.brake()
        assert car.speed >= -car.max_speed / 2

    def test_friction_applied_on_update(self, car):
        car.speed = 2.0
        car.update()
        assert car.speed < 2.0

    def test_friction_eventually_stops_car(self, car):
        car.speed = 5.0
        for _ in range(500):
            car.update()
        assert abs(car.speed) < 0.1

    def test_prev_position_saved_on_update(self, car):
        car.x = 10
        car.y = 20
        car.update()
        assert car.prev_x == 10
        assert car.prev_y == 20


class TestCarSteering:
    def test_steer_left_changes_angle(self, car):
        car.speed = 1.0
        car.angle = 0
        car.steer_left()
        assert car.angle < 0

    def test_steer_right_changes_angle(self, car):
        car.speed = 1.0
        car.angle = 0
        car.steer_right()
        assert car.angle > 0

    def test_steer_does_nothing_when_stopped(self, car):
        car.speed = 0
        car.angle = 0
        car.steer_left()
        assert car.angle == 0
        car.steer_right()
        assert car.angle == 0

    def test_steer_inverts_in_reverse(self, car):
        car.speed = -1.0
        car.angle = 0
        car.steer_left()
        assert car.angle > 0

    def test_steer_turn_speed_applied(self, car):
        car.speed = 1.0
        car.angle = 0
        car.steer_left()
        assert car.angle == -car.turn_speed


class TestCarCorners:
    def test_get_corners_returns_four_points(self, car):
        corners = car.get_corners()
        assert len(corners) == 4

    def test_all_corners_are_tuples(self, car):
        corners = car.get_corners()
        for c in corners:
            assert isinstance(c, tuple) and len(c) == 2

    def test_corners_form_rectangle(self, car):
        corners = car.get_corners()
        cx = sum(p[0] for p in corners) / 4
        cy = sum(p[1] for p in corners) / 4
        assert math.isclose(cx, car.x, abs_tol=0.01)
        assert math.isclose(cy, car.y, abs_tol=0.01)

    def test_corners_rotate_with_angle(self, car):
        car.angle = 0
        corners_0 = car.get_corners()
        car.angle = 90
        corners_90 = car.get_corners()
        assert corners_0 != corners_90


class TestCarPowerups:
    """RED: tests de apply_powerup y expiración del timer."""

    @pytest.fixture
    def car_with_powerup_mocks(self, car):
        with patch.object(car, 'POWERUP_BOOST_MULTIPLIER', 1.5), \
             patch.object(car, 'POWERUP_SLOW_MULTIPLIER', 0.5), \
             patch.object(car, 'POWERUP_DURATION_FRAMES', 180):
            yield car

    @pytest.fixture
    def car_with_boost(self, car):
        with patch('src.entities.car.POWERUP_BOOST_MULTIPLIER', 1.5), \
             patch('src.entities.car.POWERUP_SLOW_MULTIPLIER', 0.5), \
             patch('src.entities.car.POWERUP_DURATION_FRAMES', 180):
            from src.entities.powerup import PowerUp
            car.apply_powerup(PowerUp.BOOST)
            yield car

    @pytest.fixture
    def car_with_slow(self, car):
        with patch('src.entities.car.POWERUP_BOOST_MULTIPLIER', 1.5), \
             patch('src.entities.car.POWERUP_SLOW_MULTIPLIER', 0.5), \
             patch('src.entities.car.POWERUP_DURATION_FRAMES', 180):
            from src.entities.powerup import PowerUp
            car.apply_powerup(PowerUp.SLOW)
            yield car

    def test_boost_increases_max_speed(self, car_with_boost):
        assert car_with_boost.max_speed > car_with_boost._base_max_speed

    def test_slow_decreases_max_speed(self, car_with_slow):
        assert car_with_slow.max_speed < car_with_slow._base_max_speed

    def test_powerup_timer_set(self, car_with_boost):
        assert car_with_boost.powerup_timer > 0

    def test_powerup_type_stored(self, car_with_boost):
        from src.entities.powerup import PowerUp
        assert car_with_boost.powerup_type == PowerUp.BOOST

    def test_timer_expiry_restores_max_speed(self, car):
        with patch('src.entities.car.POWERUP_BOOST_MULTIPLIER', 1.5), \
             patch('src.entities.car.POWERUP_SLOW_MULTIPLIER', 0.5), \
             patch('src.entities.car.POWERUP_DURATION_FRAMES', 180):
            from src.entities.powerup import PowerUp
            base = car.max_speed
            car.apply_powerup(PowerUp.BOOST)
            assert car.max_speed > base
            car.powerup_timer = 1
            car.update()
            assert car.powerup_timer == 0
            car.update()
            assert car.max_speed == base

    def test_successive_boost_stacks_correctly(self, car):
        with patch('src.entities.car.POWERUP_BOOST_MULTIPLIER', 1.5), \
             patch('src.entities.car.POWERUP_SLOW_MULTIPLIER', 0.5), \
             patch('src.entities.car.POWERUP_DURATION_FRAMES', 180):
            from src.entities.powerup import PowerUp
            base = car.max_speed
            car.apply_powerup(PowerUp.BOOST)
            boosted = car.max_speed
            car.powerup_timer = 1
            car.update()
            car.update()
            car.apply_powerup(PowerUp.BOOST)
            assert car.max_speed == boosted
