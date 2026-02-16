"""
Finding the One — Configuration & Constants.

Single source of truth for all timing, sizing, color, and speed values.
Import this from every other module in the project.
"""
import math

# ══════════════════════════════════════════════════════════════
#  GLOBAL PARAMETERS
# ══════════════════════════════════════════════════════════════

FPS = 30
FRAME_START = 1
FRAME_END = 3150       # 105 seconds
TOTAL_FRAMES = 3150
DURATION_SECONDS = 105

# ══════════════════════════════════════════════════════════════
#  ACT BOUNDARIES (frame numbers)
# ══════════════════════════════════════════════════════════════

PROLOGUE_START = 1
PROLOGUE_END = 330       # 0s–11s

ACT1_START = 330
ACT1_END = 990           # 11s–33s

ACT2_START = 990
ACT2_END = 1650          # 33s–55s

VALLEY_START = 1650
VALLEY_END = 1800        # 55s–60s

ACT3_START = 1800
ACT3_END = 2460          # 60s–82s

ACT4_START = 2460
ACT4_END = 3150          # 82s–105s


# ══════════════════════════════════════════════════════════════
#  SCROLL SPEEDS (world units per frame)
# ══════════════════════════════════════════════════════════════

SCROLL_STOP = 0.005       # Critical moment — time stops
SCROLL_CRAWL = 0.008      # Almost stopped
SCROLL_VERY_SLOW = 0.01   # Encounter
SCROLL_SLOW = 0.015       # Contemplative
SCROLL_NORMAL = 0.03      # Calm journey
SCROLL_FAST = 0.04        # Paired, picking up
SCROLL_FASTER = 0.06      # Paired, faster
SCROLL_RACING = 0.08      # World is a blur
SCROLL_MAX = 0.10         # Racing forward together


# ══════════════════════════════════════════════════════════════
#  CHARACTER SIZES & COLORS
# ══════════════════════════════════════════════════════════════

# Parent triangles (Prologue only)
PARENT_TRI_LEG = 1.0
PARENT_FILL_GRAY = 0.9
PARENT_EMISSION = 2.0

# Seeker (protagonist square)
SEEKER_SIZE = 0.6             # side length
SEEKER_FILL_GRAY = 1.0        # white
SEEKER_EMISSION = 2.0

# Right-angle triangle (encounter 1)
RIGHT_TRI_LEG = 0.7
RIGHT_TRI_FILL_GRAY = 0.45
RIGHT_TRI_EMISSION = 0.8

# Isosceles triangle (encounter 2)
ISO_TRI_BASE = 0.7
ISO_TRI_HEIGHT = 0.9
ISO_TRI_FILL_GRAY = 0.4
ISO_TRI_EMISSION = 0.8

# The One (matching square)
ONE_SIZE = 0.6                # identical to Seeker
ONE_FILL_GRAY = 1.0
ONE_EMISSION = 2.0

# Background triangles
BG_TRI_SIZE_MIN = 0.3
BG_TRI_SIZE_MAX = 0.5
BG_TRI_FILL_GRAY_MIN = 0.2
BG_TRI_FILL_GRAY_MAX = 0.3
BG_TRI_EMISSION = 0.4
BG_TRI_COUNT = 50             # pre-placed along world path


# ══════════════════════════════════════════════════════════════
#  PULSE (heartbeat) PARAMETERS
# ══════════════════════════════════════════════════════════════

PULSE_BASE_PERIOD = 45       # frames per cycle (1.5s at 30fps)
PULSE_BASE_AMP = 0.03        # scale oscillation amplitude


# ══════════════════════════════════════════════════════════════
#  ORTHOGRAPHIC SCALE SHIFTS
# ══════════════════════════════════════════════════════════════

ORTHO_NORMAL = 20
ORTHO_ENCOUNTER = 18         # Slightly zoomed in — focused
ORTHO_LONELY = 22            # Zoomed out — Seeker feels small
ORTHO_CLICK = 16             # Tight zoom — intimate
ORTHO_WIDE = 24              # Wide — world expanding


# ══════════════════════════════════════════════════════════════
#  WORLD / CAMERA
# ══════════════════════════════════════════════════════════════

CAMERA_HEIGHT = 10            # Z position of orthographic camera
WORLD_PATH_LENGTH = 110       # ~total world units traversed
VISIBLE_HALF_WIDTH = 10       # Half the visible frame width at ortho_scale=20


# ══════════════════════════════════════════════════════════════
#  TRAIL PARAMETERS
# ══════════════════════════════════════════════════════════════

TRAIL_BRIGHTNESS_STOP = 0.2
TRAIL_BRIGHTNESS_SLOW = 0.4
TRAIL_BRIGHTNESS_NORMAL = 0.6
TRAIL_BRIGHTNESS_FAST = 1.0
TRAIL_BRIGHTNESS_RACING = 1.5

TRAIL_LENGTH_STOP = 0.1
TRAIL_LENGTH_SLOW = 0.5
TRAIL_LENGTH_NORMAL = 1.0
TRAIL_LENGTH_FAST = 2.5
TRAIL_LENGTH_RACING = 4.0


# ══════════════════════════════════════════════════════════════
#  EMISSION CURVE (Seeker emotional barometer) — frame → emission
# ══════════════════════════════════════════════════════════════

# Key emission keyframes: (frame, emission_strength)
SEEKER_EMISSION_CURVE = [
    (1,    2.0),    # Birth — bright
    (330,  2.0),    # Start of journey
    (750,  1.7),    # After 1st rejection
    (870,  1.9),    # Recovery
    (1350, 1.4),    # After 2nd rejection
    (1500, 1.2),    # Alone again
    (1690, 1.0),    # Valley — dimmest
    (1740, 1.0),    # The turn
    (1770, 1.1),    # Noticing
    (1800, 1.8),    # Hope
    (1950, 2.0),    # Full brightness restored
    (2460, 2.0),    # The click
    (2670, 3.0),    # Union — brightest
    (2940, 3.0),    # Hold
    (3060, 5.0),    # Glow expands
    (3150, 5.0),    # End
]


# ══════════════════════════════════════════════════════════════
#  BACKGROUND TRIANGLE DENSITY CURVE — frame → target visible count
# ══════════════════════════════════════════════════════════════

BG_DENSITY_CURVE = [
    (1,    0),      # Prologue — no BG yet
    (270,  0),      # First appear
    (300,  3),      # Starting to populate
    (330,  7),      # Journey begins — full density
    (630,  8),      # Exploring
    (990,  10),     # After 1st encounter — crowded
    (1110, 7),      # Normal
    (1350, 5),      # Thinning
    (1500, 3),      # Bare
    (1650, 1),      # Almost gone
    (1690, 0),      # Valley — pure void
    (1800, 0),      # Discovery
    (2460, 1),      # Pair phase — sparse
    (2670, 2),      # Accelerating
    (2940, 1),      # Fading
    (3060, 0),      # Gone
    (3150, 0),      # End
]


# ══════════════════════════════════════════════════════════════
#  Y-DRIFT RANGE (Seeker wander amplitude)
# ══════════════════════════════════════════════════════════════

Y_DRIFT_EXPLORING = 2.0       # Pre-encounters
Y_DRIFT_AFTER_1ST = 1.5       # After 1st rejection
Y_DRIFT_AFTER_2ND = 0.8       # After 2nd rejection
Y_DRIFT_GAVE_UP = 0.2         # Valley — flatlined
Y_DRIFT_REOPENING = 0.5       # The One appears
Y_DRIFT_PAIRED = 0.3          # Gentle, chosen sway
