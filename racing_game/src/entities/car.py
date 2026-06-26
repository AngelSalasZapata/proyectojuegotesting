import math
import pygame
import random
from settings import *


# Función auxiliar para normalizar ángulos (necesaria para el cálculo de derrape)
def normalize_angle(angle):
    while angle > 180:
        angle -= 360
    while angle < -180:
        angle += 360
    return angle


class Car:
    def __init__(self, x, y, color=CAR_COLOR):
        self.x = x
        self.y = y
        self.prev_x = x
        self.prev_y = y
        self.angle = -90
        self.speed = 0
        self.width = CAR_WIDTH
        self.height = CAR_HEIGHT
        self.color = color
        self.max_speed = CAR_MAX_SPEED
        self.acceleration = CAR_ACCELERATION
        self.brake_rate = CAR_BRAKE
        self.friction = CAR_FRICTION
        self.turn_speed = CAR_TURN_SPEED
        self.lap = 0
        self.last_progress = 0
        self.segments_visited = set()
        self.finished = False
        self._base_max_speed = self.max_speed
        self.powerup_timer = 0
        self.powerup_type = None
        self.trail_points = []
        self.is_drifting = False
        self.drift_angle = 0
        self.trail_timer = 0

    def get_center(self):
        return (self.x, self.y)

    def get_rect(self):
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )

    def get_corners(self):
        cos_a = math.cos(math.radians(self.angle))
        sin_a = math.sin(math.radians(self.angle))
        hw = self.width / 2
        hh = self.height / 2
        corners = []
        for dx, dy in [(hw, -hh), (hw, hh), (-hw, hh), (-hw, -hh)]:
            wx = dx * cos_a - dy * sin_a
            wy = dx * sin_a + dy * cos_a
            corners.append((self.x + wx, self.y + wy))
        return corners

    def accelerate(self):
        self.speed = min(self.speed + self.acceleration, self.max_speed)

    def brake(self):
        self.speed = max(self.speed - self.brake_rate, -self.max_speed / 2)

    def steer_left(self):
        if abs(self.speed) > 0.1:
            self.angle -= self.turn_speed * (1 if self.speed > 0 else -1)

    def steer_right(self):
        if abs(self.speed) > 0.1:
            self.angle += self.turn_speed * (1 if self.speed > 0 else -1)

    # ==================== POWERUPS ====================

    def apply_powerup(self, ptype):
        from src.entities.powerup import PowerUp
        if self.powerup_timer <= 0:
            self._base_max_speed = self.max_speed
        if ptype == PowerUp.BOOST:
            self.max_speed = self._base_max_speed * POWERUP_BOOST_MULTIPLIER
        else:
            self.max_speed = self._base_max_speed * POWERUP_SLOW_MULTIPLIER
        self.powerup_timer = POWERUP_DURATION_FRAMES
        self.powerup_type = ptype

    # ==================== ACTUALIZACIÓN ====================

    def update(self):
        self.prev_x = self.x
        self.prev_y = self.y
        self.speed *= self.friction
        if abs(self.speed) < 0.01:
            self.speed = 0
        rad = math.radians(self.angle)
        self.x += math.cos(rad) * self.speed
        self.y += math.sin(rad) * self.speed
        if self.powerup_timer > 0:
            self.powerup_timer -= 1
            if self.powerup_timer == 0:
                self.max_speed = self._base_max_speed
                self.powerup_type = None

        self._update_drifting()

        self._update_trail()

    def _update_drifting(self):
        """Detecta si el auto está derrapando"""
        if abs(self.speed) > 0.5:
            # Calcular ángulo de movimiento
            movement_angle = math.degrees(
                math.atan2(self.y - self.prev_y, self.x - self.prev_x)
            )
            # Diferencia entre dirección del auto y dirección de movimiento
            angle_diff = abs(normalize_angle(self.angle - movement_angle))
            self.is_drifting = angle_diff > 15 and abs(self.speed) > 1.0
        else:
            self.is_drifting = False


    def _update_trail(self):
        if abs(self.speed) > 0.5:
            if self.trail_points:
                last_x, last_y = self.trail_points[-1]
                if math.hypot(self.x - last_x, self.y - last_y) > 5:
                    self.trail_points.append((self.x, self.y))
            else:
                self.trail_points.append((self.x, self.y))

            max_points = 30
            if len(self.trail_points) > max_points:
                self.trail_points.pop(0)
        else:
            self.trail_points.clear()

    # ==================== DIBUJADO ====================

    # src/entities/car.py - Método draw_trail corregido

    def draw_trail(self, screen, camera):
        """Dibuja la estela detrás del auto"""
        # Verificar que haya suficientes puntos y que el auto tenga velocidad
        if len(self.trail_points) < 3 or abs(self.speed) < 0.5:
            return

        # Dibujar puntos como círculos con degradado
        for i in range(1, len(self.trail_points)):
            p1 = camera.apply(self.trail_points[i - 1])
            p2 = camera.apply(self.trail_points[i])

            # Verificar que los puntos sean válidos y estén separados
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            distance = math.hypot(dx, dy)

            # Si los puntos están muy cerca, saltar este segmento
            if distance < 1:
                continue

            # Calcular transparencia y tamaño según posición en la estela
            progress = i / len(self.trail_points)
            alpha = int(progress * 150)  # Más transparente al final
            size = int(2 + (1 - progress) * 4)  # Más grande al principio

            # Color según velocidad
            speed_factor = min(abs(self.speed) / self.max_speed, 1.0)
            if speed_factor > 0.7:
                # Naranja/rojo cuando va rápido
                r = 255
                g = int(150 - (speed_factor - 0.7) * 400)
                b = 50
            else:
                # Blanco/azul cuando va lento
                r = int(200 + 55 * speed_factor)
                g = int(200 - 100 * speed_factor)
                b = 255

            # Dibujar línea con transparencia usando una superficie más segura
            width = abs(p2[0] - p1[0]) + 4
            height = abs(p2[1] - p1[1]) + 4

            # Asegurar que la superficie tenga tamaño positivo
            if width < 1 or height < 1:
                continue

            try:
                # Crear surface para transparencia
                surf = pygame.Surface((width, height), pygame.SRCALPHA)
                color = (r, g, b, alpha)

                # Dibujar línea en la superficie
                start_x = abs(p1[0] - min(p1[0], p2[0]))
                start_y = abs(p1[1] - min(p1[1], p2[1]))
                end_x = abs(p2[0] - min(p1[0], p2[0]))
                end_y = abs(p2[1] - min(p1[1], p2[1]))

                pygame.draw.line(surf, color, (start_x, start_y), (end_x, end_y), size)

                # Blitear en la pantalla
                blit_x = min(p1[0], p2[0]) - 2
                blit_y = min(p1[1], p2[1]) - 2
                screen.blit(surf, (blit_x, blit_y))

            except (ValueError, pygame.error) as e:
                # Si hay error, simplemente saltamos este segmento
                continue

    # src/entities/car.py - Método draw completo (sin sombra)

    def draw(self, screen, camera):
        """Dibuja el auto completo con todos los efectos (sin sombra)"""
        # Dibujar estela primero (detrás del auto)
        self.draw_trail(screen, camera)

        # Calcular matrices de rotación
        cos_a = math.cos(math.radians(self.angle))
        sin_a = math.sin(math.radians(self.angle))
        hw = self.width / 2
        hh = self.height / 2

        # Función auxiliar para transformar coordenadas locales a globales
        def w2s(ox, oy):
            rx = ox * cos_a - oy * sin_a
            ry = ox * sin_a + oy * cos_a
            return camera.apply((self.x + rx, self.y + ry))

        # ----- 1. Ruedas -----
        wheel_gap = 2
        for side_x in (-1, 1):
            for side_y in (-1, 1):
                cx = side_x * (hw + wheel_gap)
                cy = side_y * (hh - 2)
                pts = [
                    w2s(cx + dwx * 3, cy + dwy * 3)
                    for dwx, dwy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]
                ]
                # Ruedas más oscuras si está derrapando
                wheel_color = (80, 80, 80) if self.is_drifting else (20, 20, 20)
                pygame.draw.polygon(screen, wheel_color, pts)
                # Borde de la rueda
                pygame.draw.polygon(screen, (50, 50, 50), pts, 1)

        # ----- 2. Carrocería -----
        # Body con forma deportiva (más estrecho atrás)
        rear_narrow = 2
        body = [
            w2s(hw - 1, -hh + 1),
            w2s(hw - 1, hh - 1),
            w2s(-hw + 1 + rear_narrow, hh - 1),
            w2s(-hw + 1 + rear_narrow, -hh + 1),
        ]

        # Color con efecto de brillo si tiene powerup
        if self.powerup_timer > 0 and self.powerup_type is not None:
            from src.entities.powerup import PowerUp
            if self.powerup_type == PowerUp.BOOST:
                # Efecto de brillo para boost
                body_color = (
                    min(255, self.color[0] + 50),
                    min(255, self.color[1] + 80),
                    min(255, self.color[2] + 50)
                )
            else:
                # Efecto de oscuridad para slow
                body_color = (
                    max(0, self.color[0] - 50),
                    max(0, self.color[1] - 50),
                    max(0, self.color[2] - 50)
                )
        else:
            body_color = self.color

        # Dibujar carrocería con borde
        pygame.draw.polygon(screen, body_color, body)
        # Borde de la carrocería (más brillante)
        border_color = (
            min(255, body_color[0] + 50),
            min(255, body_color[1] + 50),
            min(255, body_color[2] + 50)
        )
        pygame.draw.polygon(screen, border_color, body, 2)

        # ----- 3. Faros delanteros -----
        headlight_positions = [
            (hw - 2, -hh + 4),
            (hw - 2, hh - 4)
        ]
        for hx, hy in headlight_positions:
            hl = w2s(hx, hy)
            # Luz del faro (efecto de brillo)
            pygame.draw.circle(screen, (255, 255, 200, 100), hl, 6)
            pygame.draw.circle(screen, (255, 255, 150), hl, 3)
            pygame.draw.circle(screen, (255, 255, 255), hl, 2)

        # ----- 4. Luces traseras -----
        taillight_positions = [
            (-hw + 3, -hh + 4),
            (-hw + 3, hh - 4)
        ]
        for tx, ty in taillight_positions:
            tl = w2s(tx, ty)
            # Rojo más intenso si está frenando
            braking = self.speed < -0.2
            red_intensity = 255 if braking else 150
            pygame.draw.circle(screen, (red_intensity, 0, 0), tl, 4)
            if braking:
                pygame.draw.circle(screen, (255, 50, 50, 150), tl, 8)

        # ----- 5. Ventanas/Parabrisas -----
        # Parabrisas delantero
        windshield = [
            w2s(hw - 4, -hh + 5),
            w2s(hw - 4, -hh + 10),
            w2s(hw - 12, -hh + 10),
            w2s(hw - 12, -hh + 5),
        ]
        # Transparencia para el vidrio
        glass_surf = pygame.Surface((30, 10), pygame.SRCALPHA)
        glass_surf.fill((150, 200, 255, 180))
        # Obtener posición para el vidrio
        glass_rect = pygame.Rect(
            min(p[0] for p in windshield),
            min(p[1] for p in windshield),
            max(p[0] for p in windshield) - min(p[0] for p in windshield),
            max(p[1] for p in windshield) - min(p[1] for p in windshield)
        )
        if glass_rect.width > 0 and glass_rect.height > 0:
            screen.blit(glass_surf, glass_rect)
        pygame.draw.polygon(screen, (150, 200, 255), windshield, 1)

        # ----- 6. Línea central (indicador de dirección) -----
        front_cx = (body[0][0] + body[1][0]) // 2
        front_cy = (body[0][1] + body[1][1]) // 2
        rear_cx = (body[2][0] + body[3][0]) // 2
        rear_cy = (body[2][1] + body[3][1]) // 2

        # Línea central con efecto de velocidad
        line_color = (255, 255, 200)
        if abs(self.speed) > 2.0:
            # Línea parpadeante a alta velocidad
            if int(pygame.time.get_ticks() / 100) % 2 == 0:
                line_color = (255, 200, 100)
        pygame.draw.line(screen, line_color, (front_cx, front_cy), (rear_cx, rear_cy), 3)

        # ----- 7. Efecto de derrape (líneas de humo alrededor) -----
        if self.is_drifting:
            for i in range(3):
                angle_offset = self.angle + 90 + i * 30
                rad_offset = math.radians(angle_offset)
                dx = math.cos(rad_offset) * 20
                dy = math.sin(rad_offset) * 20
                pos = camera.apply((self.x + dx, self.y + dy))
                # Líneas de humo
                alpha = 100 - i * 30
                for r in range(3):
                    pygame.draw.circle(
                        screen,
                        (200, 200, 200, alpha),
                        (pos[0] + r * 5, pos[1] + r * 5),
                        5 - r
                    )

        # ----- 8. Powerup activo (círculo alrededor del auto) -----
        if self.powerup_timer > 0 and self.powerup_type is not None:
            from src.entities.powerup import PowerUp
            ctr = camera.apply((self.x, self.y))
            pu_color = POWERUP_BOOST_COLOR if self.powerup_type == PowerUp.BOOST else POWERUP_SLOW_COLOR

            # Círculo pulsante
            pulse = 1 + 0.2 * math.sin(pygame.time.get_ticks() / 200)
            radius = int(10 * pulse)

            # Efecto de brillo
            for r in range(radius, 0, -2):
                alpha = int(100 * (1 - r / radius))
                pygame.draw.circle(
                    screen,
                    (pu_color[0], pu_color[1], pu_color[2], alpha),
                    ctr,
                    r
                )
            pygame.draw.circle(screen, pu_color, ctr, radius, 2)
            pygame.draw.circle(screen, WHITE, ctr, radius - 2, 1)

        # ----- 9. Efecto de velocidad (líneas de viento) -----
        if abs(self.speed) > 1.5:
            speed_factor = min(abs(self.speed) / self.max_speed, 1.0)
            if random.random() < speed_factor * 0.3:
                # Líneas de viento alrededor del auto
                for i in range(2):
                    angle_wind = self.angle + 90 + random.uniform(-20, 20)
                    rad_wind = math.radians(angle_wind)
                    dist = random.uniform(20, 40)
                    dx = math.cos(rad_wind) * dist
                    dy = math.sin(rad_wind) * dist
                    start = camera.apply((self.x + dx, self.y + dy))
                    end = camera.apply((self.x + dx + math.cos(rad_wind) * 20,
                                        self.y + dy + math.sin(rad_wind) * 20))
                    alpha = int(100 * speed_factor)
                    surf = pygame.Surface((20, 2), pygame.SRCALPHA)
                    surf.fill((255, 255, 255, alpha))
                    screen.blit(surf, (start[0], start[1]))