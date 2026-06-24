import math
import pygame
from settings import CAR_WIDTH, CAR_HEIGHT, CAR_COLOR, CAR_MAX_SPEED, CAR_ACCELERATION, CAR_BRAKE, CAR_FRICTION, CAR_TURN_SPEED, POWERUP_BOOST_MULTIPLIER, POWERUP_SLOW_MULTIPLIER, POWERUP_DURATION_FRAMES, POWERUP_BOOST_COLOR, POWERUP_SLOW_COLOR, WHITE


class Car:
    def __init__(self, x, y, color=CAR_COLOR):
        self.x = x
        self.y = y
        self.prev_x = x
        self.prev_y = y
        self.angle = -90
        self.speed = 0
        self.width = CAR_WIDTH
        self.height = CAR_HEIGHT
        self.color = color
        self.max_speed = CAR_MAX_SPEED
        self.acceleration = CAR_ACCELERATION
        self.brake_rate = CAR_BRAKE
        self.friction = CAR_FRICTION
        self.turn_speed = CAR_TURN_SPEED
        self.lap = 0
        self.last_progress = 0
        self.segments_visited = set()
        self.finished = False
        self._base_max_speed = self.max_speed
        self.powerup_timer = 0
        self.powerup_type = None

    def get_center(self):
        return (self.x, self.y)

    def get_rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)

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

    def accelerate(self):
        self.speed = min(self.speed + self.acceleration, self.max_speed)

    def brake(self):
        self.speed = max(self.speed - self.brake_rate, -self.max_speed / 2)

    def steer_left(self):
        if abs(self.speed) > 0.1:
            self.angle -= self.turn_speed * (1 if self.speed > 0 else -1)

    def steer_right(self):
        if abs(self.speed) > 0.1:
            self.angle += self.turn_speed * (1 if self.speed > 0 else -1)

    def apply_powerup(self, ptype):
        from src.entities.powerup import PowerUp
        if self.powerup_timer <= 0:
            self._base_max_speed = self.max_speed
        if ptype == PowerUp.BOOST:
            self.max_speed = self._base_max_speed * POWERUP_BOOST_MULTIPLIER
        else:
            self.max_speed = self._base_max_speed * POWERUP_SLOW_MULTIPLIER
        self.powerup_timer = POWERUP_DURATION_FRAMES
        self.powerup_type = ptype

    def update(self):
        self.prev_x = self.x
        self.prev_y = self.y
        self.speed *= self.friction
        if abs(self.speed) < 0.01:
            self.speed = 0
        rad = math.radians(self.angle)
        self.x += math.cos(rad) * self.speed
        self.y += math.sin(rad) * self.speed
        if self.powerup_timer > 0:
            self.powerup_timer -= 1
            if self.powerup_timer == 0:
                self.max_speed = self._base_max_speed
                self.powerup_type = None

    def draw(self, screen, camera):
        cos_a = math.cos(math.radians(self.angle))
        sin_a = math.sin(math.radians(self.angle))
        hw = self.width / 2
        hh = self.height / 2

        def w2s(ox, oy):
            rx = ox * cos_a - oy * sin_a
            ry = ox * sin_a + oy * cos_a
            return camera.apply((self.x + rx, self.y + ry))

        # 4 wheel rectangles protruding from body
        wheel_gap = 2
        for side_x in (-1, 1):
            for side_y in (-1, 1):
                cx = side_x * (hw + wheel_gap)
                cy = side_y * (hh - 2)
                pts = [w2s(cx + dwx * 3, cy + dwy * 3) for dwx, dwy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]
                pygame.draw.polygon(screen, (20, 20, 20), pts)

        # Car body (slightly narrower at rear for a sporty look)
        rear_narrow = 2
        body = [
            w2s(hw - 1, -hh + 1),
            w2s(hw - 1, hh - 1),
            w2s(-hw + 1 + rear_narrow, hh - 1),
            w2s(-hw + 1 + rear_narrow, -hh + 1),
        ]
        pygame.draw.polygon(screen, self.color, body)

        # Windshield (lighter rectangle near front)
        wdw = w2s(hw - 4, -hh + 5)
        wde = w2s(hw - 4, -hh + 10)
        wdi = w2s(hw - 12, -hh + 10)
        wdf = w2s(hw - 12, -hh + 5)
        pygame.draw.polygon(screen, (150, 200, 255), [wdw, wde, wdi, wdf])

        # Center line (front indicator)
        front_cx = (body[0][0] + body[1][0]) // 2
        front_cy = (body[0][1] + body[1][1]) // 2
        rear_cx = (body[2][0] + body[3][0]) // 2
        rear_cy = (body[2][1] + body[3][1]) // 2
        pygame.draw.line(screen, (255, 255, 200), (front_cx, front_cy), (rear_cx, rear_cy), 3)

        if self.powerup_timer > 0 and self.powerup_type is not None:
            from src.entities.powerup import PowerUp
            ctr = camera.apply((self.x, self.y))
            pu_color = POWERUP_BOOST_COLOR if self.powerup_type == PowerUp.BOOST else POWERUP_SLOW_COLOR
            pygame.draw.circle(screen, pu_color, ctr, 8)
            pygame.draw.circle(screen, WHITE, ctr, 8, 2)
