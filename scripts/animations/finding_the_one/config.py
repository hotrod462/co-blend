"""
Finding the One — Configuration & Constants.
Single source of truth for all timing, sizing, color, and speed values.
"""
import math

# ── GLOBAL PARAMETERS ──
FPS = 30
FRAME_START = 1
FRAME_END = 3150
TOTAL_FRAMES = 3150
DURATION_SECONDS = 105

# ── ACT BOUNDARIES ──
PROLOGUE_START = 1
PROLOGUE_END = 330
ACT1_START = 330
ACT1_END = 990
ACT2_START = 990
ACT2_END = 1650
VALLEY_START = 1650
VALLEY_END = 1800
ACT3_START = 1800
ACT3_END = 2460
ACT4_START = 2460
ACT4_END = 3150

# ── SCROLL SPEEDS ──
SCROLL_STOP = 0.005
SCROLL_CRAWL = 0.008
SCROLL_VERY_SLOW = 0.01
SCROLL_SLOW = 0.015
SCROLL_NORMAL = 0.03
SCROLL_FAST = 0.04
SCROLL_FASTER = 0.06
SCROLL_RACING = 0.08
SCROLL_MAX = 0.10

# ── CHARACTER SIZES & COLORS ──
PARENT_TRI_LEG = 1.0
PARENT_FILL_GRAY = 0.9
PARENT_EMISSION = 2.0

SEEKER_SIZE = 0.6
SEEKER_FILL_GRAY = 1.0
SEEKER_EMISSION = 2.0

RIGHT_TRI_LEG = 0.7
RIGHT_TRI_FILL_GRAY = 0.45
RIGHT_TRI_EMISSION = 0.8

ISO_TRI_BASE = 0.7
ISO_TRI_HEIGHT = 0.9
ISO_TRI_FILL_GRAY = 0.4
ISO_TRI_EMISSION = 0.8

ONE_SIZE = 0.6
ONE_FILL_GRAY = 1.0
ONE_EMISSION = 2.0

# Background triangles — bigger, comparable to protagonist
BG_TRI_SIZE = 0.55
BG_TRI_FILL_GRAY_MIN = 0.2
BG_TRI_FILL_GRAY_MAX = 0.3
BG_TRI_EMISSION = 0.4
BG_TRI_COUNT = 50
BG_TRI_EXCLUSION_Y = 2.5  # no BG triangles within ±this of Y=0

# ── PULSE PARAMETERS ──
PULSE_BASE_PERIOD = 45
PULSE_BASE_AMP = 0.03

# ── ORTHOGRAPHIC SCALE SHIFTS ──
ORTHO_NORMAL = 20
ORTHO_ENCOUNTER = 18
ORTHO_LONELY = 22
ORTHO_CLICK = 16
ORTHO_WIDE = 24

# ── WORLD / CAMERA ──
CAMERA_HEIGHT = 10
WORLD_PATH_LENGTH = 110
VISIBLE_HALF_WIDTH = 10

# ── EMISSION CURVE — more dramatic changes ──
SEEKER_EMISSION_CURVE = [
    (200,  2.0),    # After birth
    (330,  2.0),    # Journey starts
    (750,  1.0),    # After 1st rejection — dramatic dip
    (870,  1.5),    # Partial recovery
    (1350, 0.6),    # After 2nd rejection — very dim
    (1500, 0.4),    # Alone
    (1690, 0.3),    # Valley — near invisible
    (1740, 0.3),    # The turn
    (1770, 0.5),    # Noticing
    (1800, 1.5),    # Hope
    (1950, 2.0),    # Full brightness
    (2460, 2.0),    # The click
    (2670, 3.0),    # Union
    (2940, 3.0),
    (3060, 5.0),
    (3150, 5.0),
]

# ── BG DENSITY CURVE ──
BG_DENSITY_CURVE = [
    (1,    0),
    (270,  0),
    (300,  3),
    (330,  7),
    (630,  8),
    (990,  10),
    (1110, 7),
    (1350, 5),
    (1500, 3),
    (1650, 1),
    (1690, 0),
    (1800, 0),
    (2460, 1),
    (2670, 2),
    (2940, 1),
    (3060, 0),
    (3150, 0),
]

# ── Y-DRIFT RANGE ──
Y_DRIFT_EXPLORING = 2.0
Y_DRIFT_AFTER_1ST = 1.5
Y_DRIFT_AFTER_2ND = 0.8
Y_DRIFT_GAVE_UP = 0.2
Y_DRIFT_REOPENING = 0.5
Y_DRIFT_PAIRED = 0.3
