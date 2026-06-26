# src/entities/particle.py

import pygame
import random
import math
from settings import WHITE, RED, YELLOW


class Particle:
    def __init__(self, x, y, color, velocity, size, lifetime):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.size = size
        self.max_lifetime = lifetime
        self.lifetime = lifetime
        self.active = True
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-5, 5)

    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.active = False
            return

        # Movimiento con deceleración
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.vx *= 0.98
        self.vy *= 0.98
        self.rotation += self.rot_speed * dt * 60

        # Reducir tamaño gradualmente
        self.size *= 0.995

    def draw(self, screen, camera):
        if not self.active:
            return

        pos = camera.apply((self.x, self.y))
        alpha = int((self.lifetime / self.max_lifetime) * 255)

        # Crear surface con transparencia
        size = max(1, int(self.size))
        surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)

        # Color con alpha
        color_with_alpha = (self.color[0], self.color[1], self.color[2], alpha)

        # Dibujar partícula (círculo o cuadrado según tipo)
        if len(self.color) > 3 and self.color[3] < 255:
            # Si el color ya tiene alpha, usarlo
            pygame.draw.circle(surf, self.color, (size, size), size)
        else:
            pygame.draw.circle(surf, color_with_alpha, (size, size), size)

        screen.blit(surf, (pos[0] - size, pos[1] - size))


class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.max_particles = 500  # Límite para rendimiento

    def _add_particle(self, particle):
        """Añade una partícula respetando el límite máximo"""
        if len(self.particles) < self.max_particles:
            self.particles.append(particle)
        else:
            # Reemplazar la partícula más antigua
            self.particles.pop(0)
            self.particles.append(particle)

    def emit_drift_smoke(self, car, count=5):
        """Humo al derrapar"""
        for _ in range(count):
            angle = random.uniform(0, 360)
            speed = random.uniform(0.5, 1.5)
            vx = car.speed * 0.5 * random.uniform(-0.3, 0.3) + math.cos(angle) * speed * 0.2
            vy = car.speed * 0.5 * random.uniform(-0.3, 0.3) + math.sin(angle) * speed * 0.2
            size = random.uniform(3, 10)
            lifetime = random.uniform(0.5, 1.5)
            gray = random.randint(150, 220)
            color = (gray, gray, gray, random.randint(100, 200))
            self._add_particle(Particle(
                car.x + random.uniform(-15, 15),
                car.y + random.uniform(-15, 15),
                color, (vx, vy), size, lifetime
            ))

    def emit_exhaust(self, car, count=3):
        """Humo de escape al acelerar"""
        if abs(car.speed) < 0.5:
            return

        rad = math.radians(car.angle)
        # Dirección hacia atrás del auto
        back_x = -math.cos(rad)
        back_y = -math.sin(rad)

        for _ in range(count):
            speed = random.uniform(0.5, 2)
            vx = back_x * speed * 0.5 + random.uniform(-0.5, 0.5)
            vy = back_y * speed * 0.5 + random.uniform(-0.5, 0.5)
            size = random.uniform(2, 6)
            lifetime = random.uniform(0.3, 1.0)
            gray = random.randint(100, 180)
            color = (gray, gray, gray, random.randint(80, 180))

            # Posición detrás del auto
            offset = 20
            px = car.x + back_x * offset + random.uniform(-5, 5)
            py = car.y + back_y * offset + random.uniform(-5, 5)

            self._add_particle(Particle(px, py, color, (vx, vy), size, lifetime))

    def emit_sparks(self, car, count=8):
        """Chispas al chocar"""
        for _ in range(count):
            angle = random.uniform(0, 360)
            speed = random.uniform(2, 8)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            size = random.uniform(1, 4)
            lifetime = random.uniform(0.2, 0.8)
            # Colores de chispa (amarillo, naranja, blanco)
            color = random.choice([
                (255, 200, 50, 255),
                (255, 150, 50, 255),
                (255, 100, 50, 255),
                (255, 255, 200, 255)
            ])
            self._add_particle(Particle(
                car.x + random.uniform(-20, 20),
                car.y + random.uniform(-20, 20),
                color, (vx, vy), size, lifetime
            ))

    def emit_sparks_at(self, x, y, count=8):
        """Chispas en una posición específica (para colisiones entre autos)"""
        for _ in range(count):
            angle = random.uniform(0, 360)
            speed = random.uniform(1, 6)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            size = random.uniform(1, 3)
            lifetime = random.uniform(0.2, 0.6)
            color = random.choice([
                (255, 200, 50, 255),
                (255, 150, 50, 255),
                (255, 100, 50, 255),
                (255, 255, 200, 255)
            ])
            self._add_particle(Particle(
                x + random.uniform(-10, 10),
                y + random.uniform(-10, 10),
                color, (vx, vy), size, lifetime
            ))

    def emit_explosion(self, x, y, count=20):
        """Explosión de partículas (para efectos especiales)"""
        for _ in range(count):
            angle = random.uniform(0, 360)
            speed = random.uniform(2, 10)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            size = random.uniform(2, 8)
            lifetime = random.uniform(0.3, 1.2)
            color = random.choice([
                (255, 200, 50, 255),
                (255, 100, 50, 255),
                (255, 50, 50, 255),
                (255, 200, 200, 255),
                (200, 200, 200, 255)
            ])
            self._add_particle(Particle(x, y, color, (vx, vy), size, lifetime))

    def emit_trail_particles(self, car, count=2):
        """Partículas de estela (opcional)"""
        if abs(car.speed) < 0.5:
            return

        rad = math.radians(car.angle)
        back_x = -math.cos(rad)
        back_y = -math.sin(rad)

        for _ in range(count):
            speed = random.uniform(0.3, 1.0)
            vx = back_x * speed * 0.3 + random.uniform(-0.3, 0.3)
            vy = back_y * speed * 0.3 + random.uniform(-0.3, 0.3)
            size = random.uniform(1, 3)
            lifetime = random.uniform(0.3, 0.7)
            # Color basado en la velocidad
            speed_factor = min(abs(car.speed) / car.max_speed, 1.0)
            r = int(150 + 105 * speed_factor)
            g = int(150 - 100 * speed_factor)
            b = 50
            color = (r, g, b, random.randint(50, 150))

            px = car.x + back_x * 15 + random.uniform(-5, 5)
            py = car.y + back_y * 15 + random.uniform(-5, 5)

            self._add_particle(Particle(px, py, color, (vx, vy), size, lifetime))

    def update(self, dt):
        """Actualiza todas las partículas"""
        # Actualizar partículas existentes
        for p in self.particles:
            p.update(dt)

        # Eliminar partículas inactivas
        self.particles = [p for p in self.particles if p.active]

        # Limitar cantidad de partículas (seguridad)
        if len(self.particles) > self.max_particles:
            self.particles = self.particles[-self.max_particles:]

    def render(self, screen, camera):
        """Renderiza todas las partículas"""
        for p in self.particles:
            p.draw(screen, camera)

    def clear(self):
        """Limpia todas las partículas"""
        self.particles.clear()