import math
import pytest


class TestTrackProgress:
    """RED: escribo tests de get_progress para un Track con waypoints conocidos.
       GREEN: al implementar _track_info, get_progress, check_lap, todos pasan.
    """

    def test_progress_at_first_waypoint(self, small_track):
        wp = small_track.waypoints[0]
        p = small_track.get_progress(wp[0], wp[1])
        assert 0 <= p < 1

    def test_progress_between_first_two_waypoints(self, small_track):
        p1 = small_track.waypoints[0]
        p2 = small_track.waypoints[1]
        mid_x = (p1[0] + p2[0]) / 2
        mid_y = (p1[1] + p2[1]) / 2
        p = small_track.get_progress(mid_x, mid_y)
        assert 0.4 <= p <= 0.6

    def test_progress_returns_float(self, small_track):
        p = small_track.get_progress(150, 100)
        assert isinstance(p, float)

    def test_progress_is_monotonic_along_path(self, small_track):
        pts = [(100, 100), (200, 100), (300, 100),
               (350, 200), (400, 300), (350, 400)]
        progresses = [small_track.get_progress(x, y) for x, y in pts]
        for i in range(1, len(progresses)):
            assert progresses[i] >= progresses[i - 1], (
                f"progress decreased at point {pts[i]}: "
                f"{progresses[i-1]} -> {progresses[i]}"
            )


class TestTrackCheckLap:
    """RED: test para check_lap que detecta cruce de meta.
       GREEN: implementación simple basada en wrap-around.
    """

    def test_no_lap_without_wrap(self, small_track):
        assert small_track.check_lap(1.5, 0.5) is False

    def test_lap_detected_on_wrap(self, small_track):
        n = small_track.n
        assert small_track.check_lap(0.2, n * 0.8) is True

    def test_small_forward_no_lap(self, small_track):
        assert small_track.check_lap(0.5, 0.3) is False

    def test_lap_at_exact_half(self, small_track):
        n = small_track.n
        # Cuando last - current > n/2 exactamente
        assert small_track.check_lap(0, n * 0.6) is True


class TestTrackLookahead:
    """RED: test para get_lookahead_point.
       GREEN: devuelve (x, y, angle) dentro de la pista.
    """

    def test_lookahead_returns_tuple(self, small_track):
        result = small_track.get_lookahead_point(0, lookahead=1.0)
        assert len(result) == 3
        x, y, angle = result
        assert isinstance(x, float)
        assert isinstance(y, float)
        assert isinstance(angle, float)

    def test_lookahead_advances_position(self, small_track):
        x0, y0, _ = small_track.get_lookahead_point(0, lookahead=0)
        x1, y1, _ = small_track.get_lookahead_point(0, lookahead=1.0)
        dist = math.hypot(x1 - x0, y1 - y0)
        assert dist > 0

    def test_lookahead_full_lap_wraps(self, small_track):
        total = small_track.n
        result = small_track.get_lookahead_point(total - 0.5, lookahead=1.0)
        assert result is not None


class TestTrackCollision:
    """RED: test para is_on_track basado en máscara de píxeles.
       GREEN: al tener la máscara blanca sobre fondo negro.
    """

    def test_on_track_inside_mask(self, small_track):
        # centro de la zona blanca (10,10)-(90,90)
        assert small_track.is_on_track(50, 50) is True

    def test_off_track_outside_mask(self, small_track):
        assert small_track.is_on_track(0, 0) is False

    def test_off_track_out_of_bounds(self, small_track):
        assert small_track.is_on_track(-10, -10) is False
        assert small_track.is_on_track(500, 500) is False


class TestTrackConstrain:
    """RED: test para constrain_car que lo revierte al estar fuera de pista."""

    def test_car_on_track_not_constrained(self, small_track, car):
        car.x, car.y = 50, 50
        car.prev_x, car.prev_y = 50, 50
        result = small_track.constrain_car(car)
        assert result is False
        assert car.x == 50
        assert car.y == 50

    def test_car_off_track_is_constrained(self, small_track, car):
        car.x, car.y = 0, 0
        car.prev_x, car.prev_y = 5, 5
        result = small_track.constrain_car(car)
        assert result is True
        assert car.x != 0
        assert car.y != 0

    def test_car_speed_reduced_on_collision(self, small_track, car):
        car.x, car.y = 0, 0
        car.prev_x, car.prev_y = 5, 5
        car.speed = 10
        small_track.constrain_car(car)
        assert car.speed < 10


class TestTrackProbeAhead:
    def test_probe_returns_tuple(self, small_track):
        result = small_track.probe_ahead(50, 50, 0, 10)
        assert len(result) == 3

    def test_probe_stays_on_track(self, small_track):
        on_track, _, _ = small_track.probe_ahead(50, 50, 0, 10)
        assert on_track is True

    def test_probe_off_track(self, small_track):
        on_track, _, _ = small_track.probe_ahead(0, 0, 0, 10)
        assert on_track is False
