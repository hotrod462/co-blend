"""
Finding the One — Configuration & Constants.
Single source of truth for all timing, sizing, color, and speed values.
"""
import math

# ── GLOBAL PARAMETERS ──
FPS = 30
FRAME_START = 1
FRAME_END = 3850  # Extended to ~3850 (+100 for longer equilateral exit)
TOTAL_FRAMES = 3850
DURATION_SECONDS = 128 # approx

# ── ACT BOUNDARIES (Shifted for gaps and slower sync) ──
PROLOGUE_START = 1
PROLOGUE_END = 330

# Act 1: 330 -> 1300 (Extended exit by +100)
ACT1_START = 330
ACT1_END = 1300

# NEW GAP: 1300 -> 1500 (Seeker alone/recovery)
# Act 2 Starts at 1500
ACT2_START = 1500
ACT2_END = 2500  # 1000 frames (same duration as before)

# Valley: 2500 -> 2650
VALLEY_START = 2500
VALLEY_END = 2650

# Act 3: 2650 -> 3350 (700 frames)
ACT3_START = 2650
ACT3_END = 3350

# Act 4: 3350 -> 3850 (500 frames)
ACT4_START = 3350
ACT4_END = 3850

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
    
    (1100, 1.0),    # Act 1 Rejection
    (1250, 1.5),    # Act 1 Recovery start
    
    (1400, 1.5),    # Gap (Alone/Wandering)
    (1500, 1.5),    # Act 2 Start
    
    (2250, 0.6),    # Act 2 Rejection
    (2400, 0.4),    # Alone 
    
    (2540, 0.3),    # Valley
    (2590, 0.3),    # The turn
    (2620, 0.5),    # Noticing
    (2650, 1.5),    # Hope (Act 3 Start)
    
    (2800, 2.0),    # Full brightness
    (3350, 2.0),    # The click (Act 4 start)
    (3470, 3.0),    # Union
    (3650, 3.0),
    (3850, 5.0),    # End
]

# ── BG DENSITY CURVE ──
# Shifted keyframes
BG_DENSITY_CURVE = [
    (1,    0),
    (270,  0),
    (300,  3),
    (330,  7),
    
    # Act 1 (330-1300)
    (630,  8),
    (1300, 10),
    
    # Gap (1300-1500) - Alone
    (1400, 7),
    
    # Act 2 (1500-2500)
    (1700, 10),
    (2250, 5),    # End of Act 2 interaction
    (2400, 3),    # Alone again
    
    # Valley (2500-2650)
    (2500, 1),    
    (2550, 0),
    (2650, 0),    # Act 3 start
    
    (3350, 0),    # Act 4 start
    (3380, 5),    # Return
    (3470, 7),    # Full density
    (3650, 5),    # Fade
    (3850, 0),
]

# ── Y-DRIFT RANGE ──
Y_DRIFT_EXPLORING = 2.0
Y_DRIFT_AFTER_1ST = 1.5
Y_DRIFT_AFTER_2ND = 0.8
Y_DRIFT_GAVE_UP = 0.2
Y_DRIFT_REOPENING = 0.5
Y_DRIFT_PAIRED = 0.3
