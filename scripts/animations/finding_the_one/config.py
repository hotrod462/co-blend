"""
Finding the One — Configuration & Constants.
Single source of truth for all timing, sizing, color, and speed values.
"""
import math

# ── GLOBAL PARAMETERS ──
FPS = 30
FRAME_START = 1
FRAME_END = 4140  # Extended: +170 (Act1 exit) + +120 (Act2 exit) = +290 downstream
TOTAL_FRAMES = 4140
DURATION_SECONDS = 138 # approx (~4140/30)

# ── ACT BOUNDARIES (Shifted for gaps and slower sync) ──
PROLOGUE_START = 1
PROLOGUE_END = 330

# Act 1: 330 -> 1300 (right-angle exit runs 1120->1520, gap follows)
ACT1_START = 330
ACT1_END = 1300

# NEW GAP: 1520 -> 1670 (Seeker alone/recovery — shifted +170)
# Act 2 Starts at 1670 (+170 from old 1500)
ACT2_START = 1670
ACT2_END = 2790  # Extended: iso exit runs 2390->2790 (400f, was 280f)

# Valley: 2790 -> 2940  (+290 from old 2500->2650)
VALLEY_START = 2790
VALLEY_END = 2940

# Act 3: 2940 -> 3640 (700 frames, +290)
ACT3_START = 2940
ACT3_END = 3640

# Act 4: 3640 -> 4140 (500 frames, +290)
ACT4_START = 3640
ACT4_END = 4140

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

    (1520, 1.5),    # Extended exit ends / Gap begins (+170)
    (1670, 1.5),    # Act 2 Start (+170)

    (2420, 0.6),    # Act 2 Rejection (bonk area, +170)
    (2600, 0.4),    # Iso exit deepens
    (2790, 0.3),    # End of iso exit / Valley start (+290)

    (2840, 0.3),    # Valley flatline
    (2890, 0.3),    # The turn
    (2910, 0.5),    # Noticing
    (2940, 1.5),    # Hope (Act 3 Start, +290)

    (3090, 2.0),    # Full brightness (+290)
    (3640, 2.0),    # The click (Act 4 start, +290)
    (3760, 3.0),    # Union (+290)
    (3940, 3.0),    # (+290)
    (4140, 5.0),    # End (+290)
]

# ── BG DENSITY CURVE ──
# Shifted keyframes
BG_DENSITY_CURVE = [
    (1,    0),
    (220,  0),
    (250,  3),
    (280,  7),

    # Act 1 (330-1300)
    (630,  8),
    (1300, 10),

    # Act 1 extended exit (1300-1520) — triangle lingers, density stays up
    (1450, 8),
    (1520, 7),

    # Gap (1520-1670) - Alone
    (1595, 6),
    (1670, 7),    # Act 2 begins

    # Act 2 (1670-2790)
    (1870, 10),   # +170
    (2420, 5),    # End of Act 2 interaction (+170)
    (2600, 3),    # Iso exit deepens

    # Valley (2790-2940)
    (2790, 1),    # +290
    (2840, 0),    # +290
    (2940, 0),    # Act 3 start (+290)

    (3640, 0),    # Act 4 start (+290)
    (3670, 5),    # Return (+290)
    (3760, 7),    # Full density (+290)
    (3940, 5),    # Fade (+290)
    (4140, 0),    # End (+290)
]

# ── Y-DRIFT RANGE ──
Y_DRIFT_EXPLORING = 2.0
Y_DRIFT_AFTER_1ST = 1.5
Y_DRIFT_AFTER_2ND = 0.8
Y_DRIFT_GAVE_UP = 0.2
Y_DRIFT_REOPENING = 0.5
Y_DRIFT_PAIRED = 0.3
