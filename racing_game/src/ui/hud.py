import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_NAME, FONT_SIZE_SMALL, FONT_SIZE_MEDIUM, WHITE, RED, GREEN


class HUD:
    def __init__(self):
        self.font_small = pygame.font.Font(FONT_NAME, FONT_SIZE_SMALL)
        self.font_medium = pygame.font.Font(FONT_NAME, FONT_SIZE_MEDIUM)

    def draw(self, screen, player_car, ai_cars, total_laps):
        speed = abs(player_car.speed) * 20
        speed_text = self.font_small.render(f"Velocidad: {int(speed)} km/h", True, WHITE)
        screen.blit(speed_text, (10, 10))

        lap_text = self.font_small.render(f"Vuelta: {player_car.lap + 1}/{total_laps}", True, WHITE)
        screen.blit(lap_text, (10, 40))

        position = 1
        all_cars = [(player_car, "Jugador")] + [(ai, f"IA {i+1}") for i, ai in enumerate(ai_cars)]
        sorted_cars = sorted(all_cars, key=lambda c: c[0].lap * 10000 + c[0].last_progress, reverse=True)
        for i, (car, name) in enumerate(sorted_cars):
            if car is player_car:
                position = i + 1
                break

        pos_color = GREEN if position == 1 else WHITE
        pos_text = self.font_small.render(f"Posicion: {position}/{len(all_cars)}", True, pos_color)
        screen.blit(pos_text, (10, 70))

        if player_car.finished:
            finish_text = self.font_medium.render("¡META!", True, GREEN)
            finish_rect = finish_text.get_rect(center=(SCREEN_WIDTH // 2, 30))
            screen.blit(finish_text, finish_rect)

        total_bars = len(sorted_cars)
        bar_start_y = (SCREEN_HEIGHT - total_bars * 25) // 2
        for i, (car, name) in enumerate(sorted_cars):
            bar_color = RED if car is player_car else car.color
            progress = min((car.lap + car.last_progress / 8) / total_laps, 1.0)
            bar_x = SCREEN_WIDTH - 160
            bar_y = bar_start_y + i * 25
            pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, 150, 20))
            pygame.draw.rect(screen, bar_color, (bar_x, bar_y, int(150 * progress), 20))
            label = "Jugador" if car is player_car else name
            name_text = self.font_small.render(label, True, WHITE)
            screen.blit(name_text, (bar_x, bar_y - 16))
