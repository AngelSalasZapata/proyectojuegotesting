import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, GREEN, FONT_SIZE_LARGE, FONT_SIZE_MEDIUM, FONT_NAME


class PauseState:
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.font_large = pygame.font.Font(FONT_NAME, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(FONT_NAME, FONT_SIZE_MEDIUM)
        self.background = None

    def enter(self):
        pass

    def exit(self):
        pass

    def capture_background(self, screen):
        self.background = screen.copy()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state_manager.change_state("race", enter=False)
                elif event.key == pygame.K_q:
                    self.state_manager.change_state("menu")

    def update(self, dt):
        pass

    def render(self, screen):
        if self.background:
            screen.blit(self.background, (0, 0))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

        pause_text = self.font_large.render("PAUSA", True, WHITE)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        screen.blit(pause_text, pause_rect)

        resume_text = self.font_medium.render("Presiona ESC para continuar", True, GREEN)
        resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(resume_text, resume_rect)

        quit_text = self.font_medium.render("Presiona Q para salir", True, (200, 200, 200))
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(quit_text, quit_rect)
