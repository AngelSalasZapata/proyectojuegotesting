import math
import pygame
from settings import TRACK_WIDTH, TRACK_COLOR, GREEN, DARK_GREEN, WHITE, BLACK
from src.entities.checkpoint import Checkpoint


def _compute_offset_polygon(points, half_width):
    n = len(points)
    result = []
    for i in range(n):
        p0 = points[(i - 1) % n]
        p1 = points[i]
        p2 = points[(i + 1) % n]
        d_prev = (p1[0] - p0[0], p1[1] - p0[1])
        d_next = (p2[0] - p1[0], p2[1] - p1[1])
        len_prev = math.hypot(*d_prev)
        len_next = math.hypot(*d_next)
        if len_prev < 0.001 or len_next < 0.001:
            result.append(p1)
            continue
        u_prev = (d_prev[0] / len_prev, d_prev[1] / len_prev)
        u_next = (d_next[0] / len_next, d_next[1] / len_next)
        perp_prev = (-u_prev[1], u_prev[0])
        perp_next = (-u_next[1], u_next[0])
        mx = perp_prev[0] + perp_next[0]
        my = perp_prev[1] + perp_next[1]
        ml = math.hypot(mx, my)
        if ml < 0.001:
            result.append((p1[0] + perp_prev[0] * half_width, p1[1] + perp_prev[1] * half_width))
            continue
        mx /= ml
        my /= ml
        dot = perp_prev[0] * mx + perp_prev[1] * my
        if abs(dot) < 0.001:
            dot = 0.001
        offset = half_width / dot
        max_offset = abs(half_width) * 4
        if abs(offset) > max_offset:
            offset = max_offset if offset > 0 else -max_offset
        result.append((p1[0] + mx * offset, p1[1] + my * offset))
    return result


class Track:
    def __init__(self, waypoints, road_width):
        self.waypoints = waypoints
        self.road_width = road_width
        self.hw = road_width / 2
        self.n = len(waypoints)

        self.outer_road = _compute_offset_polygon(waypoints, self.hw)
        self.inner_road = _compute_offset_polygon(waypoints, -self.hw)
        self.road_polygon = self.outer_road + self.inner_road[::-1]

        grass_margin = 60
        self.outer_grass = _compute_offset_polygon(waypoints, self.hw + grass_margin)
        self.grass_polygon = self.outer_grass + self.outer_road[::-1]

        self.inner_edge = _compute_offset_polygon(waypoints, -(self.hw - 4))
        self.outer_edge = _compute_offset_polygon(waypoints, self.hw - 4)
        self.edge_polygon = self.outer_edge + self.inner_edge[::-1]

        self.checkpoints = self._create_checkpoints()
        self.dash_positions = self._compute_dashes()

        self._seg_lengths = []
        self._total_length = 0
        for i in range(self.n):
            p1 = waypoints[i]
            p2 = waypoints[(i + 1) % self.n]
            seg_len = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            self._seg_lengths.append(seg_len)
            self._total_length += seg_len

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

    def _compute_dashes(self):
        dashes = []
        for i in range(self.n):
            p1 = self.waypoints[i]
            p2 = self.waypoints[(i + 1) % self.n]
            seg_len = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            num = max(2, int(seg_len / 45))
            spacing = seg_len / num
            for d in range(num):
                if d % 2 == 0:
                    continue
                t = (d * spacing) / seg_len
                x = p1[0] + (p2[0] - p1[0]) * t
                y = p1[1] + (p2[1] - p1[1]) * t
                angle = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
                dashes.append((x, y, angle))
        return dashes

    def get_progress(self, x, y):
        info = self._track_info(x, y)
        return info[0]

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

    def constrain_car(self, car):
        progress, dist, proj_x, proj_y, seg_idx = self._track_info(car.x, car.y)
        margin = 5
        max_allowed = self.hw - margin
        if dist > max_allowed:
            if dist > 0.001:
                ratio = max_allowed / dist
                car.x = proj_x + (car.x - proj_x) * ratio
                car.y = proj_y + (car.y - proj_y) * ratio
            if car.speed > 0.3:
                car.speed *= 0.95
            return True
        return False

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
        if last_progress - current_progress > half:
            return True
        return False

    def render_grass(self, screen, camera):
        screen.fill(DARK_GREEN)
        pts = [camera.apply(p) for p in self.grass_polygon]
        if len(pts) < 3:
            return
        pygame.draw.polygon(screen, GREEN, pts)

    def render_road(self, screen, camera):
        pts = [camera.apply(p) for p in self.road_polygon]
        if len(pts) < 3:
            return
        pygame.draw.polygon(screen, TRACK_COLOR, pts)

    def render_edges(self, screen, camera):
        pts = [camera.apply(p) for p in self.edge_polygon]
        if len(pts) < 3:
            return
        pygame.draw.polygon(screen, WHITE, pts)

    def render_center_dashes(self, screen, camera):
        dash_len = 32
        for x, y, angle in self.dash_positions:
            sp = camera.apply((x, y))
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            p1 = (int(sp[0] - cos_a * dash_len / 2), int(sp[1] - sin_a * dash_len / 2))
            p2 = (int(sp[0] + cos_a * dash_len / 2), int(sp[1] + sin_a * dash_len / 2))
            pygame.draw.line(screen, (220, 220, 220), p1, p2, 3)

    def render_start_finish(self, screen, camera):
        if not self.checkpoints:
            return
        cp = self.checkpoints[0]
        p1 = camera.apply(cp.p1)
        p2 = camera.apply(cp.p2)
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        seg_len = math.hypot(dx, dy)
        if seg_len < 1:
            return
        ux = dx / seg_len
        uy = dy / seg_len
        tx = -uy
        ty = ux
        thickness = 14
        num = max(2, int(seg_len / thickness))
        overlap = 0.03
        for s in range(num):
            t0 = max(0, s / num - overlap)
            t1 = min(1, (s + 1) / num + overlap)
            sx1 = p1[0] + dx * t0
            sy1 = p1[1] + dy * t0
            sx2 = p1[0] + dx * t1
            sy2 = p1[1] + dy * t1
            hw = thickness * 0.6
            corners = [
                (sx1 + tx * hw, sy1 + ty * hw),
                (sx2 + tx * hw, sy2 + ty * hw),
                (sx2 - tx * hw, sy2 - ty * hw),
                (sx1 - tx * hw, sy1 - ty * hw),
            ]
            color = BLACK if (s % 2 == 0) else WHITE
            pygame.draw.polygon(screen, color, corners)

    def draw_checkpoints(self, screen, camera):
        for cp in self.checkpoints[1:]:
            cp.draw(screen, camera, (50, 50, 50))
