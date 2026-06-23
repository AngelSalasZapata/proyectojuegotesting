import math
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TRACK_WAYPOINTS, TRACK_WIDTH,
    LAP_COUNT, AI_CAR_COUNT, AI_CAR_COLORS
)
from src.core.camera import Camera
from src.core.track import Track
from src.entities.car import Car
from src.entities.ai_car import AICar
from src.ui.hud import HUD
from src.utils.helpers import distance
from src.utils.collisions import car_collision_mtv


class RaceState:
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.camera = Camera()
        self.hud = HUD()
        self.track = None
        self.player = None
        self.ai_cars = []
        self.race_finished = False
        self.finish_order = []
        self.race_time = 0

    def enter(self):
        self.camera = Camera()
        self.hud = HUD()
        self.race_finished = False
        self.finish_order = []
        self.race_time = 0
        self.track = Track(TRACK_WAYPOINTS, TRACK_WIDTH)
        self._create_player()
        self._create_ai_cars()

    def _create_player(self):
        sp = TRACK_WAYPOINTS[0]
        self.player = Car(sp[0], sp[1], (255, 50, 50))
        self.player.last_progress = self.track.get_progress(self.player.x, self.player.y)

    def _create_ai_cars(self):
        self.ai_cars = []
        pts = TRACK_WAYPOINTS
        n = len(pts)
        for i in range(AI_CAR_COUNT):
            color = AI_CAR_COLORS[i % len(AI_CAR_COLORS)]
            wp_idx = (i + 1) * n // (AI_CAR_COUNT + 1) % n
            wp = pts[wp_idx]
            speed_mult = 0.55 + (i / max(AI_CAR_COUNT - 1, 1)) * 0.40
            ai = AICar(wp[0] + 15, wp[1] + 15, color, self.track, speed_mult, wp_idx)
            ai_progress = self.track.get_progress(ai.x, ai.y)
            ai.last_progress = ai_progress
            _, _, track_dir = self.track.get_lookahead_point(ai_progress, 0.1)
            ai.angle = track_dir
            self.ai_cars.append(ai)

    def exit(self):
        pass

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and not self.race_finished:
                    pause_state = self.state_manager.states["pause"]
                    pause_state.capture_background(pygame.display.get_surface())
                    self.state_manager.change_state("pause")

    def _update_race_progress(self, car):
        if car.finished:
            return
        progress = self.track.get_progress(car.x, car.y)
        if self.track.check_lap(progress, car.last_progress):
            car.lap += 1
            if car.lap >= LAP_COUNT:
                car.finished = True
                label = "Jugador" if car is self.player else f"IA {self.ai_cars.index(car) + 1}"
                self.finish_order.append((label, car.lap, True))
        car.last_progress = progress

    def update(self, dt):
        if self.race_finished:
            return
        self.race_time += dt

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.player.accelerate()
        if keys[pygame.K_DOWN]:
            self.player.brake()
        if keys[pygame.K_LEFT]:
            self.player.steer_left()
        if keys[pygame.K_RIGHT]:
            self.player.steer_right()

        self.player.update()
        self.track.constrain_car(self.player)
        self._update_race_progress(self.player)

        for ai in self.ai_cars:
            if not ai.finished:
                ai.update()
                self.track.constrain_car(ai)
                self._update_race_progress(ai)

        self._resolve_car_collisions()

        self.camera.follow(self.player)
        self._check_race_finish()

    def _resolve_car_collisions(self):
        cars = [self.player] + [ai for ai in self.ai_cars if not ai.finished]
        for i in range(len(cars)):
            for j in range(i + 1, len(cars)):
                result = car_collision_mtv(cars[i], cars[j])
                if result:
                    nx, ny, overlap = result
                    push = overlap / 2 + 0.5
                    cars[i].x -= nx * push
                    cars[i].y -= ny * push
                    cars[j].x += nx * push
                    cars[j].y += ny * push
                    if abs(cars[i].speed) > 0.1:
                        cars[i].speed *= 0.8
                    if abs(cars[j].speed) > 0.1:
                        cars[j].speed *= 0.8

    def _check_race_finish(self):
        if self.race_finished:
            return
        if not self.player.finished:
            return
        all_done = True
        for ai in self.ai_cars:
            if not ai.finished:
                all_done = False
                break
        if all_done:
            self.race_finished = True
            gos = self.state_manager.states["gameover"]
            gos.set_results(self.finish_order)
            self.state_manager.change_state("gameover")

    def render(self, screen):
        self.track.render_grass(screen, self.camera)
        self.track.render_road(screen, self.camera)
        self.track.render_edges(screen, self.camera)
        self.track.render_center_dashes(screen, self.camera)
        self.track.render_start_finish(screen, self.camera)
        self.track.draw_checkpoints(screen, self.camera)

        self.player.draw(screen, self.camera)
        for ai in self.ai_cars:
            ai.draw(screen, self.camera)

        self.hud.draw(screen, self.player, self.ai_cars, LAP_COUNT)
