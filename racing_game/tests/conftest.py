import os
import sys
import math
import pygame
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    os.environ["SDL_AUDIODRIVER"] = "dummy"
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ["SDL_HINT_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR"] = "0"
    pygame.init()
    pygame.display.set_mode((640, 480))
    yield
    pygame.quit()


@pytest.fixture
def sample_waypoints():
    return [
        (100, 100),
        (300, 100),
        (400, 300),
        (300, 500),
        (100, 500),
        (0, 300),
    ]


@pytest.fixture
def track_config(sample_waypoints, tmp_path):
    img_path = tmp_path / "test_track.png"
    mask_path = tmp_path / "test_mask.png"

    surf = pygame.Surface((500, 600))
    surf.fill((0, 0, 0))
    pygame.draw.polygon(surf, (80, 80, 80), [
        (20, 20), (480, 20), (480, 580), (20, 580)
    ], 0)
    pygame.image.save(surf, str(img_path))

    mask = pygame.Surface((500, 600))
    mask.fill((0, 0, 0))
    pygame.draw.polygon(mask, (255, 255, 255), [
        (20, 20), (480, 20), (480, 580), (20, 580)
    ], 0)
    pygame.image.save(mask, str(mask_path))

    return {
        "image": str(img_path),
        "mask": str(mask_path),
        "waypoints": sample_waypoints,
        "road_width": 80,
    }


@pytest.fixture
def track(track_config):
    from src.core.track import Track
    return Track.from_config(track_config)


@pytest.fixture
def car():
    from src.entities.car import Car
    return Car(200, 200)


@pytest.fixture
def simple_mask(tmp_path):
    surf = pygame.Surface((100, 100))
    surf.fill((0, 0, 0))
    pygame.draw.rect(surf, (255, 255, 255), (10, 10, 80, 80))
    path = tmp_path / "simple_mask.png"
    pygame.image.save(surf, str(path))
    return path


@pytest.fixture
def small_track(simple_mask, sample_waypoints, tmp_path):
    from src.core.track import Track
    return Track(str(simple_mask), str(simple_mask), sample_waypoints, 40)
