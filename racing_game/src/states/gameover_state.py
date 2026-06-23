import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, GREEN, RED, YELLOW, FONT_SIZE_LARGE, FONT_SIZE_MEDIUM, FONT_NAME


class GameOverState:
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.font_large = pygame.font.Font(FONT_NAME, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(FONT_NAME, FONT_SIZE_MEDIUM)
        self.results = []
        self.player_won = False

    def enter(self):
        pass

    def exit(self):
        pass

    def set_results(self, results):
        self.results = results
        self.player_won = bool(results and results[0][0] == "Jugador")

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.state_manager.change_state("race")
                elif event.key == pygame.K_ESCAPE:
                    self.state_manager.change_state("menu")

    def update(self, dt):
        pass

    def render(self, screen):
        screen.fill(BLACK)

        if self.player_won:
            title = self.font_large.render("¡VICTORIA!", True, YELLOW)
        else:
            title = self.font_large.render("DERROTA", True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 6))
        screen.blit(title, title_rect)

        if self.results:
            header = self.font_medium.render("Clasificacion Final", True, GREEN)
            header_rect = header.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
            screen.blit(header, header_rect)

            for i, (name, lap, finished) in enumerate(self.results):
                color = YELLOW if i == 0 else WHITE
                status = "Completo" if finished else "Abandono"
                label = f"{i+1}. {name} - {status}"
                text = self.font_medium.render(label, True, color)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 50 + i * 40))
                screen.blit(text, text_rect)

        restart = self.font_medium.render("Presiona ENTER para otra carrera", True, GREEN)
        restart_rect = restart.get_rect(center=(SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * 0.75)))
        screen.blit(restart, restart_rect)

        menu = self.font_medium.render("Presiona ESC para el menu", True, (200, 200, 200))
        menu_rect = menu.get_rect(center=(SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * 0.82)))
        screen.blit(menu, menu_rect)
