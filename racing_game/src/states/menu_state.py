import pygame
from settings import *
import math

class MenuState:
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.font_large = pygame.font.Font(FONT_NAME, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(FONT_NAME, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(FONT_NAME, 28)

        # Opciones del menú
        self.options = ["Iniciar Carrera", "Controles", "Salir"]
        self.selected_index = 0
        self.animation_time = 0

        # Colores para efectos
        self.title_color = WHITE
        self.title_phase = 0

    def enter(self):
        self.selected_index = 0
        self.animation_time = 0

    def exit(self):
        pass

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                elif event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    self._execute_option(self.selected_index)
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

    def _execute_option(self, index):
        if index == 0:  # Iniciar Carrera
            self.state_manager.change_state("race")
        elif index == 1:  # Controles - AHORA FUNCIONA!
            self.state_manager.change_state("controls")
        elif index == 2:  # Salir
            pygame.quit()
            exit()

    def update(self, dt):
        self.animation_time += dt
        # Efecto de pulsación en el título
        self.title_phase += dt * 2
        brightness = abs(math.sin(self.title_phase)) * 50 + 200
        self.title_color = (brightness, brightness, brightness)

    # src/states/menu_state.py

    def render(self, screen):
        screen.fill(DARK_GREEN)

        # --- Banda decorativa superior ---
        for y in range(0, 8, 2):
            pygame.draw.rect(screen, WHITE if y % 4 == 0 else BLACK,
                             (0, y, SCREEN_WIDTH, 2))

        # --- Título con efecto de sombra ---
        title_text = "🏎️ JUEGO DE CARRERAS 🏎️"

        # Sombra
        shadow = self.font_large.render(title_text, True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(SCREEN_WIDTH // 2 + 4, SCREEN_HEIGHT // 4 + 4))
        screen.blit(shadow, shadow_rect)

        # Texto principal
        title = self.font_large.render(title_text, True, self.title_color)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        screen.blit(title, title_rect)

        # --- Línea decorativa ---
        pygame.draw.line(screen, WHITE, (200, SCREEN_HEIGHT // 4 + 50),
                         (SCREEN_WIDTH - 200, SCREEN_HEIGHT // 4 + 50), 2)

        # --- Menú de opciones ---
        option_y_start = SCREEN_HEIGHT // 2 - 30
        for i, option in enumerate(self.options):
            # Caja de la opción
            box_width = 300
            box_height = 50
            box_x = SCREEN_WIDTH // 2 - box_width // 2
            box_y = option_y_start + i * (box_height + 15)

            # Color según selección
            is_selected = (i == self.selected_index)
            bg_color = (60, 60, 60) if is_selected else (30, 30, 30)
            border_color = YELLOW if is_selected else WHITE

            # Dibujar caja con efecto de resplandor
            if is_selected:
                # Sombra de la caja seleccionada
                for offset in range(3, 0, -1):
                    glow_rect = pygame.Rect(box_x - offset, box_y - offset,
                                            box_width + offset * 2, box_height + offset * 2)
                    pygame.draw.rect(screen, (255, 255, 0, 50), glow_rect, border_radius=8)

            pygame.draw.rect(screen, bg_color, (box_x, box_y, box_width, box_height),
                             border_radius=8)
            pygame.draw.rect(screen, border_color, (box_x, box_y, box_width, box_height),
                             3, border_radius=8)

            # Texto de la opción
            text_color = YELLOW if is_selected else WHITE
            option_text = self.font_medium.render(option, True, text_color)

            # Añadir flecha si está seleccionado
            if is_selected:
                arrow = self.font_medium.render("▶", True, YELLOW)
                screen.blit(arrow, (box_x - 40, box_y + 10))

            text_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + box_height // 2))
            screen.blit(option_text, text_rect)

        # --- Sección de información (Powerups) ---
        info_y = SCREEN_HEIGHT - 160

        # Fondo semitransparente
        info_surface = pygame.Surface((600, 120), pygame.SRCALPHA)
        info_surface.fill((0, 0, 0, 180))
        screen.blit(info_surface, (SCREEN_WIDTH // 2 - 300, info_y))
        pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 - 300, info_y, 600, 120), 2, border_radius=8)

        # Título de powerups
        pu_title = self.font_small.render("POWERUPS", True, WHITE)
        screen.blit(pu_title, (SCREEN_WIDTH // 2 - pu_title.get_width() // 2, info_y + 10))

        # Iconos y descripciones
        boost_icon = pygame.Rect(SCREEN_WIDTH // 2 - 200, info_y + 45, 20, 20)
        pygame.draw.rect(screen, POWERUP_BOOST_COLOR, boost_icon)
        boost_text = self.font_small.render("Aceleración", True, POWERUP_BOOST_COLOR)
        screen.blit(boost_text, (SCREEN_WIDTH // 2 - 160, info_y + 45))

        slow_icon = pygame.Rect(SCREEN_WIDTH // 2 + 80, info_y + 45, 20, 20)
        pygame.draw.rect(screen, POWERUP_SLOW_COLOR, slow_icon)
        slow_text = self.font_small.render("Frenado", True, POWERUP_SLOW_COLOR)
        screen.blit(slow_text, (SCREEN_WIDTH // 2 + 120, info_y + 45))

        # --- Controles rápidos ---
        controls_y = info_y + 85
        controls_text = self.font_small.render("⬆⬇⬅➡  Mover  |  ESC  Pausa", True, LIGHT_GRAY)
        controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH // 2, controls_y))
        screen.blit(controls_text, controls_rect)

        # --- Banda decorativa inferior ---
        for y in range(SCREEN_HEIGHT - 8, SCREEN_HEIGHT, 2):
            pygame.draw.rect(screen, WHITE if y % 4 == 0 else BLACK,
                             (0, y, SCREEN_WIDTH, 2))