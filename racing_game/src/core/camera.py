import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.smoothing = 0.08
        self.zoom = 1.5

    def follow(self, target):
        self.x += (target.x - self.x) * self.smoothing
        self.y += (target.y - self.y) * self.smoothing

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
