import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, GREEN, DARK_GREEN, RED, YELLOW, LIGHT_GRAY, FONT_SIZE_LARGE, FONT_SIZE_MEDIUM, FONT_NAME


class GameOverState:
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.font_large = pygame.font.Font(FONT_NAME, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(FONT_NAME, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(FONT_NAME, 28)
        self.results = []
        self.player_won = False

    def enter(self):
        pass

    def exit(self):
        pass

    def set_results(self, results):
        self.results = results
        self.player_won = bool(results and results[0][0] == "Jugador")

    def _format_time(self, seconds):
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 100)
        return f"{mins:02}:{secs:02}.{millis:02}"

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.state_manager.change_state("race")
                elif event.key == pygame.K_ESCAPE:
                    self.state_manager.change_state("menu")
                elif event.key == pygame.K_r:
                    self.state_manager.change_state("race")

    def update(self, dt):
        pass

    def render(self, screen):
        screen.fill(DARK_GREEN)

        # checkered top/bottom bars
        bar_colors = [BLACK, WHITE]
        for yy in (0, SCREEN_HEIGHT - 8):
            for bx in range(0, SCREEN_WIDTH, 16):
                idx = (bx // 16 + (0 if yy == 0 else 1)) % 2
                pygame.draw.rect(screen, bar_colors[idx], (bx, yy, 16, 8))

        # victory/defeat box
        title_box = pygame.Rect(0, 0, 400, 80)
        title_box.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 6)
        pygame.draw.rect(screen, BLACK, title_box, border_radius=10)
        pygame.draw.rect(screen, WHITE, title_box, 3, border_radius=10)

        if self.player_won:
            title = self.font_large.render("¡VICTORIA!", True, YELLOW)
        else:
            title = self.font_large.render("DERROTA", True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 6))
        screen.blit(title, title_rect)

        if self.results:
            # results box
            num_rows = len(self.results)
            list_box_h = 50 + num_rows * 42 + 20
            list_box = pygame.Rect(0, 0, 520, list_box_h)
            list_box.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10)
            pygame.draw.rect(screen, BLACK, list_box, border_radius=10)
            pygame.draw.rect(screen, WHITE, list_box, 3, border_radius=10)

            header = self.font_medium.render("Clasificacion Final", True, GREEN)
            header_rect = header.get_rect(center=(SCREEN_WIDTH // 2, list_box.top + 25))
            screen.blit(header, header_rect)

            for i, entry in enumerate(self.results):
                name = entry[0]
                finished = entry[2] if len(entry) > 2 else False
                race_time = entry[3] if len(entry) > 3 else 0

                # alternating row bg
                row_y = list_box.top + 55 + i * 42
                if i % 2 == 0:
                    pygame.draw.rect(screen, (10, 60, 10), (list_box.left + 8, row_y - 16, list_box.width - 16, 38), border_radius=6)

                color = YELLOW if i == 0 else WHITE
                prefix = "1°" if i == 0 else f"{i+1}°"
                if finished:
                    time_str = self._format_time(race_time)
                    label = f"{prefix}  {name}  —  {time_str}"
                else:
                    label = f"{prefix}  {name}  —  Abandono"
                text = self.font_medium.render(label, True, color)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, row_y + 2))
                screen.blit(text, text_rect)

        # bottom buttons
        restart = self.font_medium.render("Presiona ENTER o R para otra carrera", True, GREEN)
        restart_rect = restart.get_rect(center=(SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * 0.80)))
        screen.blit(restart, restart_rect)

        menu = self.font_medium.render("Presiona ESC para el menu", True, LIGHT_GRAY)
        menu_rect = menu.get_rect(center=(SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * 0.87)))
        screen.blit(menu, menu_rect)
