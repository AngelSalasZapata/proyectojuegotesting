import math
import pytest
from src.utils.helpers import normalize_angle, distance, angle_between, clamp, lerp


class TestNormalizeAngle:
    """RED: escribo tests para una función que aún no existe.
       GREEN: al implementar normalize_angle, todos pasan.
       REFACTOR: se podría optimizar con %, pero queda más legible con while.
    """

    def test_keeps_angle_in_range(self):
        assert normalize_angle(45) == 45
        assert normalize_angle(-90) == -90
        assert normalize_angle(0) == 0
        assert normalize_angle(180) == 180
        assert normalize_angle(-180) == -180

    def test_wraps_positive_overflow(self):
        assert normalize_angle(190) == -170
        assert normalize_angle(360) == 0
        assert normalize_angle(540) == 180
        assert normalize_angle(725) == 5

    def test_wraps_negative_overflow(self):
        assert normalize_angle(-190) == 170
        assert normalize_angle(-360) == 0
        assert normalize_angle(-540) == -180
        assert normalize_angle(-725) == -5

    def test_large_angles(self):
        assert normalize_angle(1080) == 0
        assert normalize_angle(1081) == 1


class TestDistance:
    def test_zero_distance(self):
        assert distance((0, 0), (0, 0)) == 0

    def test_horizontal_distance(self):
        assert distance((0, 0), (3, 0)) == 3

    def test_vertical_distance(self):
        assert distance((0, 0), (0, 4)) == 4

    def test_diagonal_distance(self):
        assert math.isclose(distance((0, 0), (3, 4)), 5)

    def test_negative_coordinates(self):
        assert math.isclose(distance((-1, -1), (2, 3)), 5)


class TestAngleBetween:
    def test_east(self):
        assert math.isclose(angle_between((0, 0), (1, 0)), 0)

    def test_north(self):
        assert math.isclose(angle_between((0, 0), (0, -1)), -90)

    def test_south(self):
        assert math.isclose(angle_between((0, 0), (0, 1)), 90)

    def test_west(self):
        assert math.isclose(angle_between((1, 0), (0, 0)), 180)


class TestClamp:
    def test_value_within_range(self):
        assert clamp(5, 0, 10) == 5

    def test_value_below_min(self):
        assert clamp(-5, 0, 10) == 0

    def test_value_above_max(self):
        assert clamp(15, 0, 10) == 10

    def test_at_boundaries(self):
        assert clamp(0, 0, 10) == 0
        assert clamp(10, 0, 10) == 10

    def test_negative_range(self):
        assert clamp(-15, -10, -5) == -10
        assert clamp(0, -10, -5) == -5

    def test_float_values(self):
        assert clamp(0.5, 0.0, 1.0) == 0.5
        assert clamp(-0.1, 0.0, 1.0) == 0.0
        assert clamp(1.5, 0.0, 1.0) == 1.0


class TestLerp:
    def test_t_zero(self):
        assert lerp(10, 20, 0) == 10

    def test_t_one(self):
        assert lerp(10, 20, 1) == 20

    def test_t_half(self):
        assert lerp(10, 20, 0.5) == 15

    def test_t_quarter(self):
        assert lerp(0, 100, 0.25) == 25

    def test_negative_range(self):
        assert lerp(-10, 10, 0.5) == 0

    def test_negative_t(self):
        assert lerp(10, 20, -0.5) == 5
