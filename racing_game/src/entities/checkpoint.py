import math
import pygame


class Checkpoint:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def get_center(self):
        return ((self.p1[0] + self.p2[0]) / 2, (self.p1[1] + self.p2[1]) / 2)

    def check_crossing(self, prev_pos, curr_pos):
        def ccw(A, B, C):
            return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

        return ccw(self.p1, self.p2, prev_pos) != ccw(self.p1, self.p2, curr_pos)

    def draw(self, screen, camera, color=(255, 255, 255)):
        p1 = camera.apply(self.p1)
        p2 = camera.apply(self.p2)
        pygame.draw.line(screen, color, p1, p2, 3)
