import math
import random
import pygame

from settings import LAP_COUNT, AI_CAR_COUNT, AI_CAR_COLORS, TRACK_DATA_PATH, POWERUP_SPAWN_INTERVAL, POWERUP_MAX_ON_TRACK
from src.core.camera import Camera
from src.core.track import Track
from src.core.track_loader import load_track_config
from src.entities.car import Car
from src.entities.ai_car import AICar
from src.entities.powerup import PowerUp
from src.ui.hud import HUD
from src.utils.collisions import car_collision_mtv

# Filas/columnas de la parrilla de salida, relativas a la linea de salida
# (waypoint 0). Las filas estan "detras" de la linea (offset hacia atras)
# para que ningun auto arranque ya cruzando la meta.
GRID_ROWS = (10, 65, 120)
GRID_COLS = (-60, 0, 60)


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
        self.powerups = []
        self._powerup_spawn_timer = 0
        config = load_track_config(TRACK_DATA_PATH)
        self.track = Track.from_config(config)
        self._create_cars()

    def _find_on_track_position(self, x, y, max_radius=80, step=4):
        if self.track.is_on_track(x, y):
            return x, y

        # Busca el punto valido mas cercano alrededor de la posicion base.
        for radius in range(step, max_radius + 1, step):
            for dx in range(-radius, radius + 1, step):
                for dy in (-radius, radius):
                    px = x + dx
                    py = y + dy
                    if self.track.is_on_track(px, py):
                        return px, py
            for dy in range(-radius + step, radius - step + 1, step):
                for dx in (-radius, radius):
                    px = x + dx
                    py = y + dy
                    if self.track.is_on_track(px, py):
                        return px, py
        return x, y

    def _spawn_powerup(self):
        for _ in range(100):
            seg = random.randint(0, self.track.n - 1)
            t = random.random()
            p1 = self.track.waypoints[seg]
            p2 = self.track.waypoints[(seg + 1) % self.track.n]
            px = p1[0] + (p2[0] - p1[0]) * t + random.uniform(-25, 25)
            py = p1[1] + (p2[1] - p1[1]) * t + random.uniform(-25, 25)
            if self.track.is_on_track(px, py):
                too_close = any(math.hypot(px - pu.x, py - pu.y) < 50 for pu in self.powerups)
                if not too_close:
                    ptype = random.choice([PowerUp.BOOST, PowerUp.SLOW])
                    self.powerups.append(PowerUp(px, py, ptype))
                    return True
        return False

    def _check_powerup_collisions(self):
        all_cars = [self.player] + self.ai_cars
        for pu in self.powerups:
            if not pu.active:
                continue
            for car in all_cars:
                if math.hypot(car.x - pu.x, car.y - pu.y) < 30:
                    car.apply_powerup(pu.type)
                    pu.active = False
                    break

    def _create_cars(self):
        """Arma la parrilla de salida con un orden y una posicion distinta
        en cada carrera: se generan varias casillas en los limites de la
        pista cerca de la linea de salida, se descartan las que caen fuera
        de pista segun la mascara y luego se baraja el resultado antes de
        repartirlo entre el jugador y las IA."""
        base = self.track.waypoints[0]
        _, _, track_dir = self.track.get_lookahead_point(0, 0.1)
        rad = math.radians(track_dir)
        perp_x, perp_y = -math.sin(rad), math.cos(rad)
        fwd_x, fwd_y = math.cos(rad), math.sin(rad)

        needed = AI_CAR_COUNT + 1
        candidates = []
        for fo in GRID_ROWS:
            origin_x = base[0] - fwd_x * fo
            origin_y = base[1] - fwd_y * fo
            for po in GRID_COLS:
                tx = origin_x + perp_x * po
                ty = origin_y + perp_y * po
                on_track_x, on_track_y = self._find_on_track_position(tx, ty)
                candidates.append((on_track_x, on_track_y))

        unique_candidates = []
        seen = set()
        for pt in candidates:
            if (round(pt[0]), round(pt[1])) not in seen:
                seen.add((round(pt[0]), round(pt[1])))
                unique_candidates.append(pt)

        pool = unique_candidates if len(unique_candidates) >= needed else candidates
        random.shuffle(pool)
        slots = pool[:needed]

        self.player = Car(slots[0][0], slots[0][1], (255, 50, 50))
        self.player.last_progress = self.track.get_progress(self.player.x, self.player.y)
        self.player.angle = track_dir

        self.ai_cars = []
        for i in range(AI_CAR_COUNT):
            sx, sy = slots[i + 1]
            color = AI_CAR_COLORS[i % len(AI_CAR_COLORS)]
            ai = AICar(sx, sy, color, self.track, 1.5, 0)
            ai.last_progress = self.track.get_progress(ai.x, ai.y)
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
        seg_idx = int(progress) % self.track.n
        car.segments_visited.add(seg_idx)
        if self.track.check_lap(progress, car.last_progress):
            if len(car.segments_visited) >= self.track.n * 0.75:
                car.lap += 1
                car.segments_visited.clear()
                if car.lap >= LAP_COUNT:
                    car.finished = True
                    label = "Jugador" if car is self.player else f"IA {self.ai_cars.index(car) + 1}"
                    self.finish_order.append((label, car.lap, True, self.race_time))
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

        self._powerup_spawn_timer += dt
        if self._powerup_spawn_timer >= POWERUP_SPAWN_INTERVAL:
            self._powerup_spawn_timer = 0
            active = sum(1 for p in self.powerups if p.active)
            if active < POWERUP_MAX_ON_TRACK:
                self._spawn_powerup()

        self._check_powerup_collisions()
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
        self.track.render(screen, self.camera)
        self.track.render_start_finish(screen, self.camera)
        self.track.draw_checkpoints(screen, self.camera)

        for pu in self.powerups:
            pu.draw(screen, self.camera)

        self.player.draw(screen, self.camera)
        for ai in self.ai_cars:
            ai.draw(screen, self.camera)

        self.hud.draw(screen, self.player, self.ai_cars, LAP_COUNT)
