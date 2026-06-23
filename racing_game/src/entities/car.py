import math
import pygame
from settings import CAR_WIDTH, CAR_HEIGHT, CAR_COLOR, CAR_MAX_SPEED, CAR_ACCELERATION, CAR_BRAKE, CAR_FRICTION, CAR_TURN_SPEED


class Car:
    def __init__(self, x, y, color=CAR_COLOR):
        self.x = x
        self.y = y
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
        self.finished = False

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

    def update(self):
        self.speed *= self.friction
        if abs(self.speed) < 0.01:
            self.speed = 0
        rad = math.radians(self.angle)
        self.x += math.cos(rad) * self.speed
        self.y += math.sin(rad) * self.speed

    def draw(self, screen, camera):
        corners = self.get_corners()
        screen_corners = [camera.apply(c) for c in corners]
        pygame.draw.polygon(screen, self.color, screen_corners)
        front_cx = (screen_corners[0][0] + screen_corners[1][0]) // 2
        front_cy = (screen_corners[0][1] + screen_corners[1][1]) // 2
        rear_cx = (screen_corners[2][0] + screen_corners[3][0]) // 2
        rear_cy = (screen_corners[2][1] + screen_corners[3][1]) // 2
        pygame.draw.line(screen, (255, 255, 200), (front_cx, front_cy), (rear_cx, rear_cy), 3)
