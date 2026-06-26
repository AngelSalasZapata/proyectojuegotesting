import math
import random
import pygame

from settings import *
from src.core.camera import Camera
from src.core.track import Track
from src.core.track_loader import load_track_config
from src.entities.car import Car
from src.entities.ai_car import AICar
from src.entities.powerup import PowerUp
from src.ui.hud import HUD
from src.utils.collisions import car_collision_mtv
from src.entities.particle import ParticleSystem

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
        self.particle_system = ParticleSystem()
        self.smoke_timer = 0
        self.powerups = []
        self._powerup_spawn_timer = 0

        # Efectos visuales adicionales
        self.speed_lines = []  # Para líneas de velocidad persistentes
        self.speed_line_timer = 0

    def enter(self):
        """Reinicia el estado de la carrera"""
        self.camera = Camera()
        self.hud = HUD()
        self.race_finished = False
        self.finish_order = []
        self.race_time = 0
        self.powerups = []
        self._powerup_spawn_timer = 0
        self.speed_lines = []
        self.speed_line_timer = 0

        # Cargar pista
        config = load_track_config(TRACK_DATA_PATH)
        self.track = Track.from_config(config)
        self._create_cars()

        # Inicializar sistema de partículas
        self.particle_system = ParticleSystem()
        self.smoke_timer = 0

    def _find_on_track_position(self, x, y, max_radius=80, step=4):
        """Encuentra la posición válida más cercana en la pista"""
        if self.track.is_on_track(x, y):
            return x, y

        # Búsqueda en espiral para encontrar el punto más cercano
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
        # Fallback: devolver la posición original
        return x, y

    def _spawn_powerup(self):
        """Genera un powerup en una posición aleatoria de la pista"""
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
        """Verifica colisiones entre autos y powerups"""
        all_cars = [self.player] + self.ai_cars
        for pu in self.powerups:
            if not pu.active:
                continue
            for car in all_cars:
                if math.hypot(car.x - pu.x, car.y - pu.y) < 30:
                    car.apply_powerup(pu.type)
                    pu.active = False
                    # Emitir partículas al recoger powerup
                    if pu.type == PowerUp.BOOST:
                        self.particle_system.emit_exhaust(car, 10)
                    else:
                        self.particle_system.emit_sparks(car, 10)
                    break

    def _create_cars(self):
        """Arma la parrilla de salida con posiciones aleatorias"""
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

        # Eliminar duplicados
        unique_candidates = []
        seen = set()
        for pt in candidates:
            key = (round(pt[0]), round(pt[1]))
            if key not in seen:
                seen.add(key)
                unique_candidates.append(pt)

        pool = unique_candidates if len(unique_candidates) >= needed else candidates
        random.shuffle(pool)
        slots = pool[:needed]

        # Crear auto del jugador
        self.player = Car(slots[0][0], slots[0][1], (255, 50, 50))
        self.player.last_progress = self.track.get_progress(self.player.x, self.player.y)
        self.player.angle = track_dir

        # Crear autos IA
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
        """Maneja los eventos de teclado"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and not self.race_finished:
                    pause_state = self.state_manager.states["pause"]
                    pause_state.capture_background(pygame.display.get_surface())
                    self.state_manager.change_state("pause")
                # elif event.key == pygame.K_r and not self.race_finished:
                #     # Reiniciar la carrera
                #     self.state_manager.change_state("race")

    def _update_race_progress(self, car):
        """Actualiza el progreso del auto en la pista"""
        if car.finished:
            return
        progress = self.track.get_progress(car.x, car.y)
        seg_idx = int(progress) % self.track.n
        car.segments_visited.add(seg_idx)

        if self.track.check_lap(progress, car.last_progress) and progress < 1.0:
            if len(car.segments_visited) >= self.track.n * 0.75:
                car.lap += 1
                car.segments_visited.clear()
                if car.lap >= LAP_COUNT:
                    car.finished = True
                    label = "Jugador" if car is self.player else f"IA {self.ai_cars.index(car) + 1}"
                    self.finish_order.append((label, car.lap, True, self.race_time))
        car.last_progress = progress

    def update(self, dt):
        """Actualiza el estado de la carrera"""
        if self.race_finished:
            return
        self.race_time += dt

        # --- Controles del jugador ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.player.accelerate()
        if keys[pygame.K_DOWN]:
            self.player.brake()
        if keys[pygame.K_LEFT]:
            self.player.steer_left()
        if keys[pygame.K_RIGHT]:
            self.player.steer_right()

        # --- Actualizar jugador ---
        self.player.update()
        self.track.constrain_car(self.player)
        self._update_race_progress(self.player)

        # --- Actualizar IAs ---
        for ai in self.ai_cars:
            ai.update()
            if not ai.finished:
                self.track.constrain_car(ai)
                self._update_race_progress(ai)

        # --- Powerups ---
        self._powerup_spawn_timer += dt
        if self._powerup_spawn_timer >= POWERUP_SPAWN_INTERVAL:
            self._powerup_spawn_timer = 0
            active = sum(1 for p in self.powerups if p.active)
            if active < POWERUP_MAX_ON_TRACK:
                self._spawn_powerup()

        self._check_powerup_collisions()
        self._resolve_car_collisions()

        # --- Actualizar cámara ---
        self.camera.follow(self.player)

        # --- Verificar final de carrera ---
        self._check_race_finish()

        # --- Actualizar partículas ---
        self.particle_system.update(dt)

        # --- Generar partículas según el estado del auto ---
        self.smoke_timer += dt
        if self.smoke_timer > 0.05:  # Cada 50ms
            self.smoke_timer = 0

            # Humo de escape al acelerar
            if keys[pygame.K_UP] and abs(self.player.speed) > 0.5:
                self.particle_system.emit_exhaust(self.player, 2)

            # Humo al derrapar
            if self.player.is_drifting:
                self.particle_system.emit_drift_smoke(self.player, 3)

            # Partículas para IAs
            for ai in self.ai_cars:
                if ai.is_drifting and abs(ai.speed) > 0.5:
                    self.particle_system.emit_drift_smoke(ai, 2)

        # --- Actualizar líneas de velocidad ---
        self._update_speed_lines(dt)

    def _update_speed_lines(self, dt):
        """Actualiza el efecto de líneas de velocidad"""
        self.speed_line_timer += dt

        if abs(self.player.speed) > 1.5 and self.speed_line_timer > 0.02:
            self.speed_line_timer = 0
            speed_factor = min(abs(self.player.speed) / self.player.max_speed, 1.0)

            # Crear nuevas líneas de velocidad
            num_lines = int(2 * speed_factor)
            for _ in range(num_lines):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                length = int(20 + 40 * speed_factor)
                alpha = int(80 * speed_factor)
                speed = random.uniform(3, 8) * speed_factor
                self.speed_lines.append({
                    'x': x,
                    'y': y,
                    'length': length,
                    'alpha': alpha,
                    'speed': speed,
                    'lifetime': random.uniform(0.3, 0.8)
                })

        # Actualizar líneas existentes
        for line in self.speed_lines[:]:
            line['y'] += line['speed']
            line['lifetime'] -= dt
            line['alpha'] = int(line['alpha'] * 0.98)
            if line['lifetime'] <= 0 or line['alpha'] < 5:
                self.speed_lines.remove(line)

    def _resolve_car_collisions(self):
        """Resuelve colisiones entre autos usando SAT (Separating Axis Theorem)"""
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

                    # Emitir chispas en la colisión
                    if abs(cars[i].speed) > 1.0 or abs(cars[j].speed) > 1.0:
                        mid_x = (cars[i].x + cars[j].x) / 2
                        mid_y = (cars[i].y + cars[j].y) / 2
                        self.particle_system.emit_sparks_at(mid_x, mid_y, 5)

    def _check_race_finish(self):
        """Verifica si todos los autos han terminado la carrera"""
        if self.race_finished:
            return
        if not self.player.finished:
            return

        all_done = all(ai.finished for ai in self.ai_cars)
        if all_done:
            self.race_finished = True
            gos = self.state_manager.states["gameover"]
            gos.set_results(self.finish_order)
            self.state_manager.change_state("gameover")

    def render(self, screen):
        """Renderiza todos los elementos de la carrera"""
        # --- Renderizar pista ---
        self.track.render(screen, self.camera)
        self.track.render_start_finish(screen, self.camera)
        self.track.draw_checkpoints(screen, self.camera)

        # --- Renderizar partículas (detrás de los autos) ---
        self.particle_system.render(screen, self.camera)

        # --- Renderizar líneas de velocidad ---
        for line in self.speed_lines:
            line_surf = pygame.Surface((line['length'], 2), pygame.SRCALPHA)
            line_surf.fill((255, 255, 255, line['alpha']))
            screen.blit(line_surf, (line['x'], line['y']))

        # --- Renderizar powerups ---
        for pu in self.powerups:
            pu.draw(screen, self.camera)

        # --- Renderizar autos ---
        # Primero las IAs (detrás del jugador)
        for ai in self.ai_cars:
            ai.draw(screen, self.camera)
        # Luego el jugador (encima)
        self.player.draw(screen, self.camera)

        # --- Renderizar HUD ---
        self.hud.draw(screen, self.player, self.ai_cars, LAP_COUNT)

        # --- Efecto de velocidad en los bordes (alternativo) ---
        if abs(self.player.speed) > 1.5:
            speed_factor = min(abs(self.player.speed) / self.player.max_speed, 1.0)
            # Líneas de velocidad en los bordes
            if random.random() < speed_factor * 0.2:
                for i in range(3):
                    side = random.choice(['left', 'right'])
                    if side == 'left':
                        x = random.randint(0, 50)
                    else:
                        x = random.randint(SCREEN_WIDTH - 50, SCREEN_WIDTH)
                    y = random.randint(0, SCREEN_HEIGHT)
                    length = int(30 + 50 * speed_factor)
                    alpha = int(60 * speed_factor)
                    line_surf = pygame.Surface((length, 2), pygame.SRCALPHA)
                    line_surf.fill((255, 255, 255, alpha))
                    screen.blit(line_surf, (x, y))