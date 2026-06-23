import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.smoothing = 0.1

    def follow(self, target):
        target_x = target.x - self.width // 2
        target_y = target.y - self.height // 2
        self.x += (target_x - self.x) * self.smoothing
        self.y += (target_y - self.y) * self.smoothing

    def apply(self, point):
        px, py = point
        return (int(px - self.x), int(py - self.y))

    def apply_rect(self, rect):
        x, y, w, h = rect
        return pygame.Rect(int(x - self.x), int(y - self.y), w, h)
