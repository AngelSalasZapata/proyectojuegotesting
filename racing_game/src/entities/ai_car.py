import math
from src.entities.car import Car
from src.utils.helpers import normalize_angle
from settings import AI_SENSOR_LENGTH, AI_SENSOR_ANGLES


class AICar(Car):
    def __init__(self, x, y, color, track, speed_multiplier=1.0, start_wp=0):
        super().__init__(x, y, color)
        self.track = track
        self.max_speed *= speed_multiplier
        self.turn_speed = 4.0
        self.finished = False

    def _read_sensors(self):
        readings = []
        for offset in AI_SENSOR_ANGLES:
            angle = self.angle + offset
            on_track, px, py = self.track.probe_ahead(self.x, self.y, angle, AI_SENSOR_LENGTH)
            readings.append((on_track, offset))
        return readings

    def update(self):
        if self.finished:
            self.speed *= 0.95
            super().update()
            return

        progress, cross_dist, proj_x, proj_y, seg_idx = self.track._track_info(self.x, self.y)
        self.last_progress = progress

        sensors = self._read_sensors()

        wall_steer = 0.0
        for on_track, offset in sensors:
            if not on_track:
                wall_steer += math.copysign(1.0, -offset) * 0.6

        speed_ratio = abs(self.speed) / max(self.max_speed, 0.01)
        look = 0.8 + speed_ratio * 1.8
        look_x, look_y, track_angle = self.track.get_lookahead_point(progress, look)

        dx = look_x - self.x
        dy = look_y - self.y
        target_angle = math.degrees(math.atan2(dy, dx))

        side_correction = -cross_dist * 0.03
        target_angle += side_correction

        angle_diff = normalize_angle(target_angle - self.angle)

        steer = max(-1.0, min(1.0, angle_diff * 0.07 + wall_steer))
        if abs(self.speed) > 0.1:
            self.angle += steer * self.turn_speed * (1 if self.speed > 0 else -1)

        any_wall = any(not on for on, _ in sensors)
        abs_diff = abs(angle_diff)
        if any_wall:
            target_spd = self.max_speed * 0.20
        elif abs_diff > 50:
            target_spd = self.max_speed * 0.15
        elif abs_diff > 35:
            target_spd = self.max_speed * 0.30
        elif abs_diff > 20:
            target_spd = self.max_speed * 0.50
        elif abs_diff > 10:
            target_spd = self.max_speed * 0.75
        else:
            target_spd = self.max_speed

        target_spd = max(target_spd, self.max_speed * 0.10)

        if self.speed < target_spd:
            self.accelerate()
        elif self.speed > target_spd + 0.2:
            self.brake()

        super().update()
