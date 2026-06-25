import os
import pygame

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 820
FPS = 60
TITLE = "Carreras"

GREEN = (0, 180, 0)
DARK_GREEN = (0, 120, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
LIGHT_GRAY = (180, 180, 180)

TRACK_COLOR = (80, 80, 80)
TRACK_BORDER = (120, 120, 120)
TRACK_WIDTH = 200
TRACK_CURB = (200, 200, 200)

# --- Pista basada en imagen + mascara de colisiones -------------------------

TRACK_NAME = "track1"
TRACK_DATA_PATH = os.path.join(BASE_DIR, "tracks", f"{TRACK_NAME}.json")

# Color que la mascara usa para representar la superficie de pista transitable
# Cualquier pixel que no se parezca a este color se considera pared/cesped y bloquea al auto.
TRACK_MASK_DRIVABLE_COLOR = (255, 255, 255)
TRACK_MASK_COLOR_TOLERANCE = 30

# Waypoints de referencia, solo se usan si no existe tracks/track1.json
TRACK_WAYPOINTS = [
    (500, 143),
    (700, 203),
    (830, 400),
    (700, 596),
    (500, 656),
    (300, 596),
    (169, 400),
    (300, 203),
]

CAR_WIDTH = 40
CAR_HEIGHT = 20
CAR_COLOR = RED
CAR_MAX_SPEED = 2.5
CAR_ACCELERATION = 0.09
CAR_BRAKE = 0.08
CAR_FRICTION = 0.97
CAR_TURN_SPEED = 3.5
CAR_START_POS = (400, 200)

AI_CAR_COLORS = [BLUE, YELLOW, PURPLE, ORANGE, CYAN]
AI_CAR_COUNT = 5
AI_SPEED_VARIATION = 7.5
AI_TURN_SPEED = 0.3
AI_TARGET_DISTANCE = 200
AI_SLOW_DOWN_ANGLE = 30

# Sensores de pared para que la IA "vea" obstaculos
AI_SENSOR_LENGTH = 90
AI_SENSOR_ANGLES = (-35, 0, 35)
AI_STEER_SMOOTHING = 0.25

# --- Bonificadores -----------------------------------------------------------

POWERUP_SIZE = 24
POWERUP_SPAWN_INTERVAL = 3.0
POWERUP_MAX_ON_TRACK = 5
POWERUP_BOOST_COLOR = (0, 220, 0)
POWERUP_SLOW_COLOR = (220, 0, 0)
POWERUP_BOOST_MULTIPLIER = 1.5
POWERUP_SLOW_MULTIPLIER = 0.5
POWERUP_DURATION_FRAMES = 180

LAP_COUNT = 6

FONT_NAME = None
FONT_SIZE_SMALL = 24
FONT_SIZE_MEDIUM = 36
FONT_SIZE_LARGE = 72


# --- Menú ---
MENU_OPTION_COLOR = (200, 200, 200)
MENU_SELECTED_COLOR = (255, 255, 0)
MENU_BG_COLOR = (20, 20, 20)

# --- Animaciones ---
COUNTDOWN_DURATION = 3.0  # segundos
COUNTDOWN_FONT_SIZE = 120

# --- Efectos visuales ---
PARTICLE_COUNT = 20
PARTICLE_LIFETIME = 1.0  # segundos