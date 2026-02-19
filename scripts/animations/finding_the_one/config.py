"""
Finding the One — Configuration & Constants.
Single source of truth for all timing, sizing, color, and speed values.
"""
import math

# ── GLOBAL PARAMETERS ──
FPS = 30
FRAME_START = 1
FRAME_END = 3750  # Extended to ~3750 (+250 frames for gaps and slower sync)
TOTAL_FRAMES = 3750
DURATION_SECONDS = 125 # approx

# ── ACT BOUNDARIES (Shifted for gaps and slower sync) ──
PROLOGUE_START = 1
PROLOGUE_END = 330

# Act 1: 330 -> 1200 (Unchanged duration, but exit logic changes)
ACT1_START = 330
ACT1_END = 1200

# NEW GAP: 1200 -> 1400 (Seeker alone/recovery)
# Act 2 Starts at 1400
ACT2_START = 1400
ACT2_END = 2400  # 1000 frames (same duration as before)

# Valley: 2400 -> 2550
VALLEY_START = 2400
VALLEY_END = 2550

# Act 3: 2550 -> 3250 (Extended by ~40 frames for slower sync)
# Was 660 frames (2350->3010). Now 700 frames.
ACT3_START = 2550
ACT3_END = 3250

# Act 4: 3250 -> 3750 (500 frames)
ACT4_START = 3250
ACT4_END = 3750

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

# Updated Emission to 2.0 (Partners)
RIGHT_TRI_LEG = 0.7
RIGHT_TRI_FILL_GRAY = 0.45
RIGHT_TRI_EMISSION = 2.0

# Updated Emission to 2.0 (Partners)
ISO_TRI_BASE = 0.7
ISO_TRI_HEIGHT = 0.9
ISO_TRI_FILL_GRAY = 0.4
ISO_TRI_EMISSION = 2.0

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
# Shifted keyframes to match new Act timing + Gap
SEEKER_EMISSION_CURVE = [
    (200,  2.0),    # After birth
    (330,  2.0),    # Journey starts
    
    (1000, 1.0),    # Act 1 Rejection
    (1150, 1.5),    # Act 1 Recovery start
    
    (1300, 1.5),    # Gap (Alone/Wandering)
    (1400, 1.5),    # Act 2 Start
    
    (2150, 0.6),    # Act 2 Rejection
    (2300, 0.4),    # Alone 
    
    (2440, 0.3),    # Valley
    (2490, 0.3),    # The turn
    (2520, 0.5),    # Noticing
    (2550, 1.5),    # Hope (Act 3 Start)
    
    (2700, 2.0),    # Full brightness
    (3250, 2.0),    # The click (Act 4 start)
    (3370, 3.0),    # Union
    (3550, 3.0),
    (3750, 5.0),    # End
]

# ── BG DENSITY CURVE ──
# Shifted keyframes
BG_DENSITY_CURVE = [
    (1,    0),
    (270,  0),
    (300,  3),
    (330,  7),
    
    # Act 1 (330-1200)
    (630,  8),
    (1200, 10),
    
    # Gap (1200-1400) - Alone
    (1300, 7),
    
    # Act 2 (1400-2400)
    (1600, 10),
    (2150, 5),    # End of Act 2 interaction
    (2300, 3),    # Alone again
    
    # Valley (2400-2550)
    (2400, 1),    
    (2450, 0),
    (2550, 0),    # Act 3 start
    
    (3250, 0),    # Act 4 start
    (3280, 5),    # Return
    (3370, 7),    # Full density
    (3550, 5),    # Fade
    (3750, 0),
]

# ── Y-DRIFT RANGE ──
Y_DRIFT_EXPLORING = 2.0
Y_DRIFT_AFTER_1ST = 1.5
Y_DRIFT_AFTER_2ND = 0.8
Y_DRIFT_GAVE_UP = 0.2
Y_DRIFT_REOPENING = 0.5
Y_DRIFT_PAIRED = 0.3
