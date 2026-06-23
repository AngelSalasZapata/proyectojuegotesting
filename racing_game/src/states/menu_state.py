import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, GREEN, FONT_SIZE_LARGE, FONT_SIZE_MEDIUM, FONT_NAME


class MenuState:
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.font_large = pygame.font.Font(FONT_NAME, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(FONT_NAME, FONT_SIZE_MEDIUM)

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
        screen.fill(BLACK)
        title = self.font_large.render("JUEGO DE CARRERAS", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        screen.blit(title, title_rect)

        start = self.font_medium.render("Presiona ENTER para empezar", True, GREEN)
        start_rect = start.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(start, start_rect)

        controls_title = self.font_medium.render("Controles", True, WHITE)
        controls_title_rect = controls_title.get_rect(center=(SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * 0.65)))
        screen.blit(controls_title, controls_title_rect)

        controls_text = self.font_medium.render("Flechas - Conducir | ESC - Pausa", True, (200, 200, 200))
        controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * 0.72)))
        screen.blit(controls_text, controls_rect)
