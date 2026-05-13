# VIEWPORT PARAMETERS
WINDOW_SIZE = (900, 700)
BG_COLOR = (30, 30, 40)
FPS = 60


#TARGET PARAMETERS
TARGET_COLOR = (240, 80, 80)

#AGENT PARAMETERS
NUM_AGENTS = 25
AGENT_COLOR = (80, 200, 120)
MAX_SPEED = 2.5
AGENT_RADIUS = 6

#MOTHERSHIP PARAMETERS
USE_MOTHERSHIP = False
MOTHERSHIP_COLOR = (255, 255, 0)
MOTHERSHIP_POS = (50, 50)
MOTHERSHIP_STRENGTH = 1e-4

# If True, measurement noise will be applied to agent detection readings (not implemented yet)
MEASUREMENT_NOISE = False

DETECTION_RADIUS = 10

# ALGORITHM PARAMETERS (Adaptive Repulsion + Dynamic k-Nearest PSO)
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

# Wall repulsion parameters
# Distance (pixels) from wall where repulsion starts
WALL_MARGIN = 20
# Strength multiplier for wall repulsion
WALL_STRENGTH = 2.0


CAMERA_FOLLOW = False

SIM_TIME = 120  # seconds