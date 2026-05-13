WINDOW_SIZE = (900, 700)
BG_COLOR = (30, 30, 40)
AGENT_COLOR = (80, 200, 120)
MOTHERSHIP_COLOR = (255, 255, 0)
TARGET_COLOR = (240, 80, 80)
FPS = 60
NUM_AGENTS = 25
MAX_SPEED = 2.5
AGENT_RADIUS = 6
MOTHERSHIP_POS = (50, 50)
DETECTION_RADIUS = 10
# If True, measurement noise will be applied to agent detection readings (not implemented yet)
MEASUREMENT_NOISE = False

# Algorithm parameters (Adaptive Repulsion + Dynamic k-Nearest PSO)
# Adaptive Repulsion
AR_MIN = 0.375
AR_MAX = 1
AR_DELTA = 0.01
AR_INIT = 0.8
AR_D = 6

# Dynamic k-nearest PSO
K_NEIGHBORS = 5
# K_NEIGHBORS = NUM_AGENTS - 1
OMEGA = 1.0
PSO_C = 0.5

# Velocity clamp
V_MAX = MAX_SPEED

# Wall repulsion parameters
# Distance (pixels) from wall where repulsion starts
WALL_MARGIN = 20
# Strength multiplier for wall repulsion
WALL_STRENGTH = 2.0

USE_MOTHERSHIP = False
MOTHERSHIP_STRENGTH = 1e-4

CAMERA_FOLLOW = False

SIM_TIME = 120  # seconds

USE_PYGAME = False