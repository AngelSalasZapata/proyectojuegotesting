import math
import pytest
from src.utils.collisions import point_in_rect, rects_overlap, circle_rect_overlap


class TestPointInRect:
    def test_point_inside(self):
        assert point_in_rect((5, 5), (0, 0, 10, 10)) is True

    def test_point_outside(self):
        assert point_in_rect((15, 5), (0, 0, 10, 10)) is False

    def test_point_on_edge(self):
        assert point_in_rect((0, 0), (0, 0, 10, 10)) is True
        assert point_in_rect((10, 5), (0, 0, 10, 10)) is True

    def test_point_negative_rect(self):
        assert point_in_rect((-5, -5), (-10, -10, 10, 10)) is True
        assert point_in_rect((-15, -5), (-10, -10, 10, 10)) is False


class TestRectsOverlap:
    def test_overlapping(self):
        assert rects_overlap((0, 0, 10, 10), (5, 5, 10, 10)) is True

    def test_not_overlapping(self):
        assert rects_overlap((0, 0, 10, 10), (20, 20, 10, 10)) is False

    def test_touching_edges(self):
        assert rects_overlap((0, 0, 10, 10), (10, 0, 10, 10)) is False
        assert rects_overlap((0, 0, 10, 10), (9, 0, 10, 10)) is True

    def test_one_inside_other(self):
        assert rects_overlap((0, 0, 20, 20), (5, 5, 10, 10)) is True

    def test_same_rect(self):
        assert rects_overlap((0, 0, 10, 10), (0, 0, 10, 10)) is True


class TestCircleRectOverlap:
    def test_circle_inside_rect(self):
        assert circle_rect_overlap(5, 5, 3, 0, 0, 10, 10) is True

    def test_circle_far_away(self):
        assert circle_rect_overlap(50, 50, 3, 0, 0, 10, 10) is False

    def test_circle_touching_rect_edge(self):
        assert circle_rect_overlap(10, 5, 3, 0, 0, 10, 10) is True

    def test_circle_near_corner(self):
        assert circle_rect_overlap(-1, -1, 3, 0, 0, 10, 10) is True

    def test_circle_at_corner_grazing(self):
        assert circle_rect_overlap(12, 12, 2, 0, 0, 10, 10) is False

    def test_zero_radius(self):
        assert circle_rect_overlap(5, 5, 0, 0, 0, 10, 10) is True


class TestCarCollisionMTV:
    """Test SAT collision with two rotated rectangles."""

    @pytest.fixture
    def make_car(self, request):
        """Helper: create a mock car with just enough attributes for SAT."""
        class MockCar:
            def __init__(self, x, y, angle, w, h):
                self.x = x
                self.y = y
                self.angle = angle
                self.width = w
                self.height = h
            def get_corners(self):
                cos_a = math.cos(math.radians(self.angle))
                sin_a = math.sin(math.radians(self.angle))
                hw = self.width / 2
                hh = self.height / 2
                corners = []
                for dx, dy in [(hw, -hh), (hw, hh), (-hw, hh), (-hw, -hh)]:
                    wx = dx * cos_a - dy * sin_a
                    wy = dx * sin_a + dy * cos_a
                    corners.append((self.x + wx, self.y + wy))
                return corners
        return MockCar

    def test_no_collision_when_separated(self, make_car):
        from src.utils.collisions import car_collision_mtv
        c1 = make_car(0, 0, 0, 40, 20)
        c2 = make_car(100, 0, 0, 40, 20)
        assert car_collision_mtv(c1, c2) is None

    def test_collision_when_overlapping(self, make_car):
        from src.utils.collisions import car_collision_mtv
        c1 = make_car(0, 0, 0, 40, 20)
        c2 = make_car(10, 0, 0, 40, 20)
        result = car_collision_mtv(c1, c2)
        assert result is not None
        nx, ny, overlap = result
        assert overlap > 0
        assert isinstance(nx, float)
        assert isinstance(ny, float)

    def test_collision_at_angle(self, make_car):
        from src.utils.collisions import car_collision_mtv
        c1 = make_car(0, 0, 0, 40, 20)
        c2 = make_car(15, 5, 45, 40, 20)
        result = car_collision_mtv(c1, c2)
        assert result is not None

    def test_mtv_direction_from_c1_to_c2(self, make_car):
        from src.utils.collisions import car_collision_mtv
        c1 = make_car(0, 0, 0, 40, 20)
        c2 = make_car(10, 0, 0, 40, 20)
        nx, ny, _ = car_collision_mtv(c1, c2)
        dot = nx * (c2.x - c1.x) + ny * (c2.y - c1.y)
        assert dot >= 0

    def test_axis_dot_positive(self, make_car):
        from src.utils.collisions import car_collision_mtv
        c1 = make_car(0, 0, 0, 40, 20)
        c2 = make_car(-10, 0, 0, 40, 20)
        nx, ny, _ = car_collision_mtv(c1, c2)
        dot = nx * (c2.x - c1.x) + ny * (c2.y - c1.y)
        assert dot >= 0
