import pygame
import random
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.smoothing = 0.08
        self.zoom = 1.5
        self.shake_amount = 0
        self.shake_decay = 0.9

    def follow(self, target):
        self.x += (target.x - self.x) * self.smoothing
        self.y += (target.y - self.y) * self.smoothing

        if hasattr(target, 'speed') and abs(target.speed) > 2.0:
            speed_factor = abs(target.speed) / 5.0
            self.shake_amount = max(self.shake_amount, speed_factor * 0.5)

        # Aplicar shake
        if self.shake_amount > 0.01:
            shake_x = random.uniform(-self.shake_amount, self.shake_amount)
            shake_y = random.uniform(-self.shake_amount, self.shake_amount)
            self.x += shake_x
            self.y += shake_y
            self.shake_amount *= self.shake_decay
        else:
            self.shake_amount = 0

    def apply(self, point):
        px, py = point
        sx = (px - self.x) * self.zoom + self.width // 2
        sy = (py - self.y) * self.zoom + self.height // 2
        return (int(sx), int(sy))

    def apply_rect(self, rect):
        x, y, w, h = rect
        sx = (x - self.x) * self.zoom + self.width // 2
        sy = (y - self.y) * self.zoom + self.height // 2
        return pygame.Rect(int(sx), int(sy), int(w * self.zoom), int(h * self.zoom))
