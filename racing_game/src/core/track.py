import math
import os

import pygame

from settings import WHITE, BLACK, DARK_GREEN, TRACK_MASK_DRIVABLE_COLOR, TRACK_MASK_COLOR_TOLERANCE
from src.entities.checkpoint import Checkpoint


class Track:
    """Pista basada en una imagen visual + una mascara de colisiones.

    La mascara es una imagen del mismo tamano/posicion que la imagen
    visual donde el color definido en TRACK_MASK_DRIVABLE_COLOR marca la
    superficie transitable; todo lo demas (paredes, cesped, islas
    centrales, etc.) bloquea al auto. Esto permite representar cualquier
    forma de pista (con paredes internas incluidas) sin depender de la
    geometria simplificada de poligono-por-offset que se usaba antes.

    El recorrido (waypoints) sigue existiendo, pero ahora se usa solo para
    el seguimiento de ruta de la IA y el calculo de progreso/vueltas, no
    para dibujar ni para las colisiones.
    """

    def __init__(self, image_path, mask_path, waypoints, road_width):
        self.waypoints = [tuple(p) for p in waypoints]
        self.road_width = road_width
        self.hw = road_width / 2
        self.n = len(self.waypoints)

        self.image = self._load_image(image_path)
        self.mask_surface = self._load_image(mask_path)
        self.mask_width = self.mask_surface.get_width()
        self.mask_height = self.mask_surface.get_height()

        self.checkpoints = self._create_checkpoints()

        self._seg_lengths = []
        self._total_length = 0
        for i in range(self.n):
            p1 = self.waypoints[i]
            p2 = self.waypoints[(i + 1) % self.n]
            seg_len = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            self._seg_lengths.append(seg_len)
            self._total_length += seg_len

    @staticmethod
    def _load_image(path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"No se encontro el archivo de pista: {path}")
        return pygame.image.load(path).convert_alpha()

    @classmethod
    def from_config(cls, config):
        return cls(config["image"], config["mask"], config["waypoints"], config["road_width"])

    def _create_checkpoints(self):
        cps = []
        for i in range(self.n):
            p1 = self.waypoints[i]
            p2 = self.waypoints[(i + 1) % self.n]
            mid = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
            angle = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
            perp = angle + math.pi / 2
            ox = math.cos(perp) * self.hw
            oy = math.sin(perp) * self.hw
            cps.append(Checkpoint((mid[0] + ox, mid[1] + oy), (mid[0] - ox, mid[1] - oy)))
        return cps

    # --- progreso / seguimiento de ruta (basado en waypoints, no en imagen) ---

    def get_progress(self, x, y):
        return self._track_info(x, y)[0]

    def _track_info(self, x, y):
        best_seg = 0
        best_dist = float("inf")
        best_t = 0
        best_px = x
        best_py = y
        for i in range(self.n):
            p1 = self.waypoints[i]
            p2 = self.waypoints[(i + 1) % self.n]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            seg_len_sq = dx * dx + dy * dy
            if seg_len_sq < 0.001:
                continue
            t = ((x - p1[0]) * dx + (y - p1[1]) * dy) / seg_len_sq
            t = max(0.0, min(1.0, t))
            proj_x = p1[0] + dx * t
            proj_y = p1[1] + dy * t
            d = math.hypot(x - proj_x, y - proj_y)
            if d < best_dist:
                best_dist = d
                best_seg = i
                best_t = t
                best_px = proj_x
                best_py = proj_y
        return (best_seg + best_t, best_dist, best_px, best_py, best_seg)

    def get_lookahead_point(self, progress, lookahead=2.0):
        target = progress + lookahead
        seg = int(target) % self.n
        t = target - int(target)
        p1 = self.waypoints[seg]
        p2 = self.waypoints[(seg + 1) % self.n]
        x = p1[0] + (p2[0] - p1[0]) * t
        y = p1[1] + (p2[1] - p1[1]) * t
        angle = math.degrees(math.atan2(p2[1] - p1[1], p2[0] - p1[0]))
        return (x, y, angle)

    def check_lap(self, current_progress, last_progress):
        half = self.n / 2
        return last_progress - current_progress > half

    # --- colisiones basadas en la mascara de pixeles ---------------------

    def is_on_track(self, x, y):
        """True si el punto (x, y) cae sobre superficie transitable segun
        la mascara. Fuera de los limites de la imagen siempre es pared."""
        ix, iy = int(x), int(y)
        if ix < 0 or iy < 0 or ix >= self.mask_width or iy >= self.mask_height:
            return False
        color = self.mask_surface.get_at((ix, iy))
        tol = TRACK_MASK_COLOR_TOLERANCE
        target = TRACK_MASK_DRIVABLE_COLOR
        return (
            abs(color[0] - target[0]) <= tol
            and abs(color[1] - target[1]) <= tol
            and abs(color[2] - target[2]) <= tol
        )

    def probe_ahead(self, x, y, angle_deg, distance):
        """Lanza un punto de prueba a `distance` en la direccion
        `angle_deg` desde (x, y) e indica si cae sobre pista transitable.
        Se usa para que la IA detecte paredes antes de tocarlas."""
        rad = math.radians(angle_deg)
        px = x + math.cos(rad) * distance
        py = y + math.sin(rad) * distance
        return self.is_on_track(px, py), px, py

    def constrain_car(self, car):
        points = car.get_corners() + [(car.x, car.y)]
        hit_wall = any(not self.is_on_track(px, py) for px, py in points)

        if hit_wall:
            car.x = car.prev_x
            car.y = car.prev_y
            _, dist, proj_x, proj_y, _ = self._track_info(car.x, car.y)
            if dist > 1:
                dx = proj_x - car.x
                dy = proj_y - car.y
                d = math.hypot(dx, dy)
                if d > 0.001:
                    nudge = min(dist, 6.0)
                    car.x += (dx / d) * nudge
                    car.y += (dy / d) * nudge
            car.speed *= 0.90
        return hit_wall

    # --- render ------------------------------------------------------------

    def render(self, screen, camera):
        screen.fill(DARK_GREEN)
        pos = camera.apply((0, 0))
        if not hasattr(self, '_scaled') or self._last_zoom != camera.zoom:
            self._scaled = pygame.transform.scale(
                self.image,
                (int(self.image.get_width() * camera.zoom),
                 int(self.image.get_height() * camera.zoom))
            )
            self._last_zoom = camera.zoom
        screen.blit(self._scaled, pos)

    def render_start_finish(self, screen, camera):
        if not self.checkpoints:
            return
        self.checkpoints[0].draw(screen, camera, WHITE)

    def draw_checkpoints(self, screen, camera):
        for cp in self.checkpoints[1:]:
            cp.draw(screen, camera, (50, 50, 50))
