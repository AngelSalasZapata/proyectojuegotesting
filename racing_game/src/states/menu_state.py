import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, GREEN, DARK_GREEN, RED, FONT_SIZE_LARGE, FONT_SIZE_MEDIUM, FONT_NAME, POWERUP_BOOST_COLOR, POWERUP_SLOW_COLOR, LIGHT_GRAY, GRAY


class MenuState:
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.font_large = pygame.font.Font(FONT_NAME, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(FONT_NAME, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(FONT_NAME, 28)

    def enter(self):
        pass

    def exit(self):
        pass

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.state_manager.change_state("race")
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

    def update(self, dt):
        pass

    def render(self, screen):
        screen.fill(DARK_GREEN)

        # decorative lines top/bottom
        for y in (0, SCREEN_HEIGHT - 6):
            pygame.draw.rect(screen, WHITE, (0, y, SCREEN_WIDTH, 4))
            pygame.draw.rect(screen, BLACK, (0, y + 4, SCREEN_WIDTH, 2))

        # title background box
        title_box = pygame.Rect(0, 0, 600, 90)
        title_box.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 - 10)
        pygame.draw.rect(screen, BLACK, title_box, border_radius=12)
        inner = title_box.inflate(-6, -6)
        pygame.draw.rect(screen, GRAY, inner, border_radius=10)
        pygame.draw.rect(screen, WHITE, inner, 3, border_radius=10)

        title = self.font_large.render("JUEGO DE CARRERAS", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 - 10))
        screen.blit(title, title_rect)

        # start prompt with blinking effect using pulsing green
        start = self.font_medium.render("Presiona ENTER para empezar", True, GREEN)
        start_rect = start.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(start, start_rect)

        # draw small car icon next to start text
        car_points = [
            (SCREEN_WIDTH // 2 + 200, SCREEN_HEIGHT // 2 - 10),
            (SCREEN_WIDTH // 2 + 240, SCREEN_HEIGHT // 2 - 10),
            (SCREEN_WIDTH // 2 + 250, SCREEN_HEIGHT // 2),
            (SCREEN_WIDTH // 2 + 240, SCREEN_HEIGHT // 2 + 10),
            (SCREEN_WIDTH // 2 + 200, SCREEN_HEIGHT // 2 + 10),
        ]
        pygame.draw.polygon(screen, RED, car_points)
        pygame.draw.circle(screen, BLACK, (SCREEN_WIDTH // 2 + 207, SCREEN_HEIGHT // 2 - 3), 3)
        pygame.draw.circle(screen, BLACK, (SCREEN_WIDTH // 2 + 207, SCREEN_HEIGHT // 2 + 3), 3)
        pygame.draw.circle(screen, BLACK, (SCREEN_WIDTH // 2 + 240, SCREEN_HEIGHT // 2 - 3), 3)
        pygame.draw.circle(screen, BLACK, (SCREEN_WIDTH // 2 + 240, SCREEN_HEIGHT // 2 + 3), 3)

        # separator line
        sep_y = int(SCREEN_HEIGHT * 0.60)
        pygame.draw.line(screen, WHITE, (200, sep_y), (SCREEN_WIDTH - 200, sep_y), 2)

        # controls section box
        ctrl_y = int(SCREEN_HEIGHT * 0.65)
        ctrl_box = pygame.Rect(340, ctrl_y - 15, 600, 60)
        pygame.draw.rect(screen, BLACK, ctrl_box, border_radius=8)
        pygame.draw.rect(screen, WHITE, ctrl_box, 2, border_radius=8)

        controls_title = self.font_medium.render("Controles", True, WHITE)
        controls_title_rect = controls_title.get_rect(center=(SCREEN_WIDTH // 2, ctrl_y + 5))
        screen.blit(controls_title, controls_title_rect)

        controls_text = self.font_medium.render("Flechas - Conducir | ESC - Pausa", True, LIGHT_GRAY)
        controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH // 2, ctrl_y + 42))
        screen.blit(controls_text, controls_rect)

        # separator line
        sep_y2 = int(SCREEN_HEIGHT * 0.77)
        pygame.draw.line(screen, WHITE, (200, sep_y2), (SCREEN_WIDTH - 200, sep_y2), 2)

        # powerup section box
        pu_y = int(SCREEN_HEIGHT * 0.82)
        pu_box = pygame.Rect(340, pu_y - 10, 600, 80)
        pygame.draw.rect(screen, BLACK, pu_box, border_radius=8)
        pygame.draw.rect(screen, WHITE, pu_box, 2, border_radius=8)

        pu_title = self.font_medium.render("Bonificadores", True, WHITE)
        pu_title_rect = pu_title.get_rect(center=(SCREEN_WIDTH // 2, pu_y + 5))
        screen.blit(pu_title, pu_title_rect)

        boost_text = self.font_small.render(
            "Cuadrado Verde - Aumenta la velocidad", True, POWERUP_BOOST_COLOR
        )
        boost_rect = boost_text.get_rect(center=(SCREEN_WIDTH // 2, pu_y + 40))
        screen.blit(boost_text, boost_rect)

        slow_text = self.font_small.render(
            "Cuadrado Rojo - Reduce la velocidad", True, POWERUP_SLOW_COLOR
        )
        slow_rect = slow_text.get_rect(center=(SCREEN_WIDTH // 2, pu_y + 68))
        screen.blit(slow_text, slow_rect)
