import pygame
from settings import *
import math

class ControlsState:
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.font_large = pygame.font.Font(FONT_NAME, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(FONT_NAME, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(FONT_NAME, 28)
        self.alpha = 0
        self.fade_speed = 0

        # Colores para los controles
        self.key_color = (50, 50, 200)  # Azul para teclas
        self.key_border = (150, 150, 255)
        self.action_color = WHITE

        # Controles a mostrar
        self.controls = [
            ("Movimiento", "UP/DOWN/LEFT/RIGHT", "Acelerar / Frenar / Girar"), #Acelerar / Frenar / Girar
            # ("Powerups", "P", "Activar powerup (si está disponible)"),
            ("Pausa", "ESC", "Pausar el juego"),
            ("Menú", "Q", "Volver al menú principal (en pausa)"),
            ("Reiniciar", "R", "Reiniciar carrera (en game over)"),
        ]
        self._anim_timer = 0

    def enter(self):
        self.alpha = 0

    def exit(self):
        pass

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Cualquier tecla vuelve al menú
                if event.key in [pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE]:
                    self.state_manager.change_state("menu")

    def update(self, dt):
        if self.alpha < 255:
            self.alpha = min(255, self.alpha + self.fade_speed * dt * 60)

    def _draw_key_capsule(self, screen, text, x, y, width=80, height=45):
        """Dibuja una tecla con estilo moderno"""
        # Sombra
        shadow_rect = pygame.Rect(x + 3, y + 3, width, height)
        pygame.draw.rect(screen, (0, 0, 0), shadow_rect, border_radius=8)

        # Fondo de la tecla
        key_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, self.key_color, key_rect, border_radius=8)
        pygame.draw.rect(screen, self.key_border, key_rect, 2, border_radius=8)

        # Efecto de brillo en la parte superior
        highlight = pygame.Rect(x + 4, y + 2, width - 8, height // 3)
        pygame.draw.rect(screen, (100, 100, 255, 50), highlight, border_radius=4)

        # Texto de la tecla
        text_surface = self.font_medium.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        screen.blit(text_surface, text_rect)

    # src/states/controls_state.py

    # src/states/controls_state.py

    def render(self, screen):
        screen.fill(DARK_GREEN)

        # --- Líneas decorativas de velocidad (fondo) ---
        for i in range(0, SCREEN_HEIGHT, 30):
            alpha = 30 + (i % 60)
            line_surf = pygame.Surface((SCREEN_WIDTH, 2), pygame.SRCALPHA)
            line_surf.fill((255, 255, 255, alpha))
            screen.blit(line_surf, (0, i))

        # --- Título con sombra ---
        title_text = "🎮 CONTROLES"

        # Sombra
        shadow = self.font_large.render(title_text, True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(SCREEN_WIDTH // 2 + 3, 83))
        screen.blit(shadow, shadow_rect)

        # Título principal
        title = self.font_large.render(title_text, True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title, title_rect)

        # Línea decorativa debajo del título
        pygame.draw.line(screen, WHITE, (SCREEN_WIDTH // 2 - 150, 115),
                         (SCREEN_WIDTH // 2 + 150, 115), 2)

        # --- Lista de controles ---
        start_y = 150
        y_offset = 65

        for i, (category, keys, description) in enumerate(self.controls):
            y_pos = start_y + i * y_offset

            # Fondo de la fila (alternando colores)
            box_rect = pygame.Rect(80, y_pos - 5, SCREEN_WIDTH - 160, 50)
            color_alpha = (30, 30, 30, 180) if i % 2 == 0 else (20, 20, 20, 150)
            box_surf = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
            box_surf.fill(color_alpha)
            screen.blit(box_surf, (box_rect.x, box_rect.y))
            pygame.draw.rect(screen, (80, 80, 80), box_rect, 1, border_radius=5)

            # Categoría (izquierda)
            cat_text = self.font_small.render(category, True, YELLOW)
            screen.blit(cat_text, (100, y_pos + 12))

            # Teclas (centro) - AHORA CON TEXTO SIMPLE
            if category == "Movimiento":
                # Dibujar teclas con texto "UP", "DOWN", "LEFT", "RIGHT"
                key_labels = ["UP", "DOWN", "LEFT", "RIGHT"]
                key_start_x = 260
                for j, label in enumerate(key_labels):
                    key_x = key_start_x + j * 50
                    # Fondo de la tecla
                    key_rect = pygame.Rect(key_x, y_pos + 5, 42, 30)
                    pygame.draw.rect(screen, (40, 40, 180), key_rect, border_radius=5)
                    pygame.draw.rect(screen, (100, 100, 255), key_rect, 2, border_radius=5)
                    # Texto de la tecla
                    key_text = self.font_small.render(label, True, WHITE)
                    key_rect_text = key_text.get_rect(center=(key_x + 21, y_pos + 20))
                    screen.blit(key_text, key_rect_text)
            else:
                # Tecla simple (cápsula)
                key_rect = pygame.Rect(280, y_pos + 5, 70, 30)
                pygame.draw.rect(screen, (40, 40, 180), key_rect, border_radius=15)
                pygame.draw.rect(screen, (100, 100, 255), key_rect, 2, border_radius=15)
                key_text = self.font_small.render(keys, True, WHITE)
                key_rect_text = key_text.get_rect(center=(315, y_pos + 20))
                screen.blit(key_text, key_rect_text)

            # Descripción (derecha)
            desc_text = self.font_small.render(description, True, LIGHT_GRAY)
            screen.blit(desc_text, (400, y_pos + 14))

        # --- Diagrama de flechas (dibujado con pygame) ---
        diagram_y = start_y + len(self.controls) * y_offset + 20

        # Fondo del diagrama
        diagram_rect = pygame.Rect(0, 0, 350, 160)
        diagram_rect.center = (SCREEN_WIDTH // 2, diagram_y + 80)
        diagram_surf = pygame.Surface((diagram_rect.width, diagram_rect.height), pygame.SRCALPHA)
        diagram_surf.fill((0, 0, 0, 150))
        screen.blit(diagram_surf, (diagram_rect.x, diagram_rect.y))
        pygame.draw.rect(screen, (80, 80, 80), diagram_rect, 2, border_radius=10)

        # Título del diagrama
        diagram_title = self.font_small.render("CONTROLES DE MOVIMIENTO", True, WHITE)
        diagram_title_rect = diagram_title.get_rect(center=(SCREEN_WIDTH // 2, diagram_y + 15))
        screen.blit(diagram_title, diagram_title_rect)

        # Dibujar flechas en forma de cruz USANDO PYGAME
        center_x = SCREEN_WIDTH // 2
        center_y = diagram_y + 87

        # Flecha ARRIBA
        arrow_up = [(center_x, center_y - 40), (center_x - 10, center_y - 25), (center_x + 10, center_y - 25)]
        pygame.draw.polygon(screen, (100, 150, 255), arrow_up)
        pygame.draw.polygon(screen, WHITE, arrow_up, 2)

        # Flecha ABAJO
        arrow_down = [(center_x, center_y + 40), (center_x - 10, center_y + 25), (center_x + 10, center_y + 25)]
        pygame.draw.polygon(screen, (100, 150, 255), arrow_down)
        pygame.draw.polygon(screen, WHITE, arrow_down, 2)

        # Flecha IZQUIERDA
        arrow_left = [(center_x - 40, center_y), (center_x - 25, center_y - 10), (center_x - 25, center_y + 10)]
        pygame.draw.polygon(screen, (100, 150, 255), arrow_left)
        pygame.draw.polygon(screen, WHITE, arrow_left, 2)

        # Flecha DERECHA
        arrow_right = [(center_x + 40, center_y), (center_x + 25, center_y - 10), (center_x + 25, center_y + 10)]
        pygame.draw.polygon(screen, (100, 150, 255), arrow_right)
        pygame.draw.polygon(screen, WHITE, arrow_right, 2)

        # Círculo central
        pygame.draw.circle(screen, (30, 30, 150), (center_x, center_y), 15)
        pygame.draw.circle(screen, (100, 150, 255), (center_x, center_y), 15, 2)

        # Texto explicativo
        help_text = "Usa las flechas del teclado para controlar tu vehículo"
        help_surface = self.font_small.render(help_text, True, LIGHT_GRAY)
        help_rect = help_surface.get_rect(center=(SCREEN_WIDTH // 2, diagram_y + 165))
        screen.blit(help_surface, help_rect)

        # --- Botón para volver (con efecto) ---
        back_y = diagram_y + 195
        back_rect = pygame.Rect(0, 0, 300, 50)
        back_rect.center = (SCREEN_WIDTH // 2, back_y)

        # Sombra del botón
        shadow_rect = back_rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(screen, (0, 0, 0), shadow_rect, border_radius=8)

        # Botón principal
        pygame.draw.rect(screen, (0, 100, 0), back_rect, border_radius=8)
        pygame.draw.rect(screen, GREEN, back_rect, 2, border_radius=8)

        # Texto del botón
        back_text = self.font_medium.render("Presiona ESC para volver", True, WHITE)
        back_rect_text = back_text.get_rect(center=(SCREEN_WIDTH // 2, back_y + 25))
        screen.blit(back_text, back_rect_text)

        # --- Efecto de brillo en el botón (animación) ---
        if not hasattr(self, '_anim_timer'):
            self._anim_timer = 0
        self._anim_timer += 0.02

        shine_x = 50 + abs(math.sin(self._anim_timer)) * (back_rect.width - 100)
        shine_rect = pygame.Rect(back_rect.x + shine_x, back_rect.y + 5, 40, back_rect.height - 10)
        shine_surf = pygame.Surface((shine_rect.width, shine_rect.height), pygame.SRCALPHA)
        shine_surf.fill((255, 255, 255, 30))
        screen.blit(shine_surf, (shine_rect.x, shine_rect.y))