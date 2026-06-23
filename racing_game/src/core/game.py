import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, BLACK
from src.core.state_manager import StateManager
from src.states.menu_state import MenuState
from src.states.race_state import RaceState
from src.states.pause_state import PauseState
from src.states.gameover_state import GameOverState


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        self.state_manager = StateManager()
        self.state_manager.add_state("menu", MenuState(self.state_manager))
        self.state_manager.add_state("race", RaceState(self.state_manager))
        self.state_manager.add_state("pause", PauseState(self.state_manager))
        self.state_manager.add_state("gameover", GameOverState(self.state_manager))
        self.state_manager.change_state("menu")

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            self.state_manager.handle_events(events)
            self.state_manager.update(dt)
            self.state_manager.render(self.screen)

            pygame.display.flip()

        pygame.quit()
