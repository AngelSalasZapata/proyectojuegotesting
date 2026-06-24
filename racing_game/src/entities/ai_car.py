import math
import random

from src.entities.car import Car
from src.utils.helpers import normalize_angle, clamp
from settings import AI_SENSOR_LENGTH, AI_SENSOR_ANGLES, AI_STEER_SMOOTHING

STUCK_SPEED_RATIO = 0.15
STUCK_PATIENCE = 2
UNSTUCK_BOOST_SPEED = 0.50
UNSTUCK_DURATION_MIN = 25
UNSTUCK_DURATION_MAX = 45
UNSTUCK_ANGLE_MIN = 35
UNSTUCK_ANGLE_MAX = 65


class AICar(Car):
    def __init__(self, x, y, color, track, speed_multiplier=1.0, start_wp=0):
        super().__init__(x, y, color)
        self.track = track
        self.max_speed *= speed_multiplier
        self.turn_speed = 0.5
        self.finished = False

        self._smoothed_steer = 0.0
        self._stuck_timer = 0
        self._recovering = False
        self._unstuck_ticks = 0
        self._recovery_angle = 0.0
        self._prev_progress = 0.0

    def _read_sensors(self):
        readings = []
        for offset in AI_SENSOR_ANGLES:
            angle = self.angle + offset
            on_track, _, _ = self.track.probe_ahead(self.x, self.y, angle, AI_SENSOR_LENGTH)
            readings.append((on_track, offset))
        return readings

    def _update_stuck_state(self, speed_ratio):
        if speed_ratio < STUCK_SPEED_RATIO:
            self._stuck_timer += 1
        else:
            self._stuck_timer = max(0, self._stuck_timer - 2)
            if self._stuck_timer == 0:
                self._recovering = False

        if self._stuck_timer > STUCK_PATIENCE and not self._recovering:
            self._recovering = True
            self._unstuck_ticks = random.randint(UNSTUCK_DURATION_MIN, UNSTUCK_DURATION_MAX)
            direction = random.choice((-1, 1))
            self._recovery_angle = direction * random.uniform(UNSTUCK_ANGLE_MIN, UNSTUCK_ANGLE_MAX)

    def _should_recover(self, speed_ratio):
        return self._recovering and self._unstuck_ticks > 0 and speed_ratio < 0.4

    def update(self):
        if self.finished:
            self.speed *= 0.95
            super().update()
            return

        sensors = self._read_sensors()

        progress, cross_dist, proj_x, proj_y, seg_idx = self.track._track_info(self.x, self.y)
        self.last_progress = progress

        current_speed_ratio = abs(self.speed) / max(self.max_speed, 0.01)
        self._update_stuck_state(current_speed_ratio)

        look = 0.8 + current_speed_ratio * 1.8
        look_x, look_y, _ = self.track.get_lookahead_point(progress, look)
        dx = look_x - self.x
        dy = look_y - self.y
        target_angle = math.degrees(math.atan2(dy, dx))
        target_angle += clamp(-cross_dist * 0.012, -15, 15)

        if self._should_recover(current_speed_ratio):
            self._unstuck_ticks -= 1
            recovery_target = normalize_angle(target_angle + self._recovery_angle)
            angle_diff = normalize_angle(recovery_target - self.angle)
            path_steer = clamp(angle_diff * 0.06, -1.0, 1.0)
            self._smoothed_steer += (path_steer - self._smoothed_steer) * 0.35
            steer = self._smoothed_steer
            self._recovering = self._unstuck_ticks > 0
        else:
            angle_diff = normalize_angle(target_angle - self.angle)
            path_steer = clamp(angle_diff * 0.06, -1.0, 1.0)
            wall_steer = 0.0
            for on_track, offset in sensors:
                if not on_track:
                    wall_steer += math.copysign(0.20, -offset)
            raw_steer = clamp(path_steer + wall_steer, -1.0, 1.0)
            self._smoothed_steer += (raw_steer - self._smoothed_steer) * 0.35
            steer = self._smoothed_steer

        if abs(self.speed) > 0.01:
            self.angle += steer * self.turn_speed * (1 if self.speed > 0 else -1)

        any_wall = any(not on for on, _ in sensors)
        abs_diff = abs(normalize_angle(target_angle - self.angle))
        if self._recovering:
            target_spd = self.max_speed * UNSTUCK_BOOST_SPEED
        elif any_wall:
            target_spd = self.max_speed * 0.65
        elif abs_diff > 50:
            target_spd = self.max_speed * 0.20
        elif abs_diff > 35:
            target_spd = self.max_speed * 0.35
        elif abs_diff > 20:
            target_spd = self.max_speed * 0.55
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
