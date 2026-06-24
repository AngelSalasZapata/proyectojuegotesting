import pygame

from settings import POWERUP_SIZE, POWERUP_BOOST_COLOR, POWERUP_SLOW_COLOR


class PowerUp:
    BOOST = 0
    SLOW = 1

    def __init__(self, x, y, ptype):
        self.x = x
        self.y = y
        self.type = ptype
        self.active = True
        self.size = POWERUP_SIZE

    def contains(self, px, py):
        return abs(px - self.x) < self.size // 2 and abs(py - self.y) < self.size // 2

    def draw(self, screen, camera):
        if not self.active:
            return
        sp = camera.apply((self.x, self.y))
        color = POWERUP_BOOST_COLOR if self.type == self.BOOST else POWERUP_SLOW_COLOR
        rect = pygame.Rect(sp[0] - self.size // 2, sp[1] - self.size // 2, self.size, self.size)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (255, 255, 255), rect, 2)
