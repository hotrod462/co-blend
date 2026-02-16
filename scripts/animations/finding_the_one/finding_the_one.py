"""
Finding the One — A 60-second Heider-Simmel-inspired animation.

A small circle searches for its perfect match among incompatible shapes,
and finally finds another circle that mirrors its movement perfectly.

Run:
    ./render.sh scripts/animations/finding_the_one/finding_the_one.py
    ./render.sh scripts/animations/finding_the_one/finding_the_one.py --gui
    ./render.sh scripts/animations/finding_the_one/finding_the_one.py --watch
"""
import bpy
import math
import sys
import os

# ── Project root on sys.path ──
project_root = os.getcwd()
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.utils.scene import (
    clear_scene, setup_ortho_camera, setup_world_color,
    setup_render, frames_to_video,
)
from scripts.utils.materials import create_emission_material, assign_material
from scripts.utils.animation import (
    animate_property, ease_in_out_cubic, ease_out_bounce,
    set_keyframe, lerp,
)

# ══════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════

FPS = 30
FRAME_START = 1
FRAME_END = 1800  # 60 seconds

# Act boundaries
ACT_1_END = 450    # 15s — Searching
ACT_2_END = 900    # 30s — False Hopes
ACT_3_END = 1350   # 45s — Discovery
ACT_4_END = 1800   # 60s — Union

# Room bounds
ROOM_X_MIN, ROOM_X_MAX = -8, 8
ROOM_Y_MIN, ROOM_Y_MAX = -4.5, 4.5
WALL_THICKNESS = 0.08
WALL_GRAY = 0.25

# Door
DOOR_Y = ROOM_Y_MIN  # bottom wall
DOOR_X_LEFT = -5.5
DOOR_X_RIGHT = -3.5  # 2-unit gap

# Character sizes
SEEKER_RADIUS = 0.35
SQUARE_SIZE = 0.6
RECT_W, RECT_H = 0.8, 0.4
ONE_RADIUS = 0.35

# Pulse parameters
PULSE_BASE_PERIOD = 45   # frames per cycle (1.5s at 30fps)
PULSE_BASE_AMP = 0.03    # scale 1.0–1.03


# ══════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════

def kf_loc(obj, x, y, frame):
    """Insert a location keyframe (Z always 0 for top-down)."""
    obj.location = (x, y, 0)
    obj.keyframe_insert(data_path="location", frame=frame)


def kf_scale(obj, s, frame):
    """Insert a uniform scale keyframe."""
    obj.scale = (s, s, s)
    obj.keyframe_insert(data_path="scale", frame=frame)


def kf_rot_z(obj, angle_rad, frame):
    """Insert a Z-rotation keyframe."""
    obj.rotation_euler[2] = angle_rad
    obj.keyframe_insert(data_path="rotation_euler", index=2, frame=frame)


def kf_emission_strength(mat, strength, frame):
    """Keyframe the emission strength of an emission material."""
    emission_node = None
    for node in mat.node_tree.nodes:
        if node.type == 'EMISSION':
            emission_node = node
            break
    if emission_node is None:
        return
    emission_node.inputs["Strength"].default_value = strength
    emission_node.inputs["Strength"].keyframe_insert("default_value", frame=frame)


def kf_emission_color_alpha(mat, alpha, frame):
    """Keyframe the alpha channel of an emission material's color (for fading)."""
    emission_node = None
    for node in mat.node_tree.nodes:
        if node.type == 'EMISSION':
            emission_node = node
            break
    if emission_node is None:
        return
    color = list(emission_node.inputs["Color"].default_value)
    color[3] = alpha
    emission_node.inputs["Color"].default_value = color
    emission_node.inputs["Color"].keyframe_insert("default_value", frame=frame)


def interp(start, end, t, easing=None):
    """Interpolate between two (x,y) tuples."""
    if easing:
        t = easing(t)
    return (
        start[0] + (end[0] - start[0]) * t,
        start[1] + (end[1] - start[1]) * t,
    )


def move_along(obj, waypoints, easing=None):
    """
    Move an object through a list of (frame, x, y) waypoints.
    Interpolates between consecutive waypoints with optional easing.
    """
    for i in range(len(waypoints) - 1):
        f0, x0, y0 = waypoints[i]
        f1, x1, y1 = waypoints[i + 1]
        for f in range(f0, f1 + 1):
            t = (f - f0) / max(f1 - f0, 1)
            pos = interp((x0, y0), (x1, y1), t, easing)
            kf_loc(obj, pos[0], pos[1], f)


def apply_pulse(obj, frame_start, frame_end, period=PULSE_BASE_PERIOD,
                amplitude=PULSE_BASE_AMP, base_scale=1.0):
    """Apply a continuous heartbeat pulse (scale oscillation) over a frame range."""
    for f in range(frame_start, frame_end + 1):
        phase = (f - frame_start) / period * 2 * math.pi
        s = base_scale + amplitude * (0.5 + 0.5 * math.sin(phase))
        kf_scale(obj, s, f)


def apply_sigh(obj, frame_start, frame_end, depth=0.08):
    """A 'sigh' — deflate then reinflate."""
    mid = (frame_start + frame_end) // 2
    for f in range(frame_start, mid + 1):
        t = (f - frame_start) / max(mid - frame_start, 1)
        s = 1.0 - depth * ease_in_out_cubic(t)
        kf_scale(obj, s, f)
    for f in range(mid, frame_end + 1):
        t = (f - mid) / max(frame_end - mid, 1)
        s = (1.0 - depth) + depth * ease_in_out_cubic(t)
        kf_scale(obj, s, f)


def orbit_pair(obj_a, obj_b, center, frame_start, frame_end,
               radius_start, radius_end, rpm_start, rpm_end):
    """
    Orbit two objects around a center point (always opposite each other).
    RPM = revolutions per minute at 30fps (1 RPM = 1 rev per 1800 frames).
    We express RPM as revolutions per 60 frames for convenience in the storyboard.
    """
    total = frame_end - frame_start
    for f in range(frame_start, frame_end + 1):
        t = (f - frame_start) / max(total, 1)
        radius = lerp(radius_start, radius_end, t)
        # Angular velocity interpolation
        rpm = lerp(rpm_start, rpm_end, t)
        # Accumulate angle: integrate the angular velocity
        # rpm in "revs per 60 frames" → angular velocity = rpm * 2π/60 rad/frame
        # For simplicity, compute angle via quadratic integration
        angle = 0.0
        for ff in range(frame_start, f + 1):
            tt = (ff - frame_start) / max(total, 1)
            rpm_at = lerp(rpm_start, rpm_end, tt)
            angle += rpm_at * 2 * math.pi / 60.0  # per frame increment

        ax = center[0] + radius * math.cos(angle)
        ay = center[1] + radius * math.sin(angle)
        bx = center[0] + radius * math.cos(angle + math.pi)
        by = center[1] + radius * math.sin(angle + math.pi)

        kf_loc(obj_a, ax, ay, f)
        kf_loc(obj_b, bx, by, f)


# ══════════════════════════════════════════════════════════════
#  SCENE SETUP
# ══════════════════════════════════════════════════════════════

clear_scene()

setup_ortho_camera(location=(0, 0, 10), ortho_scale=20)
setup_world_color(color=(0, 0, 0, 1))
setup_render(
    engine='BLENDER_EEVEE',
    resolution=(1920, 1080),
    fps=FPS,
    frame_start=FRAME_START,
    frame_end=FRAME_END,
    output_path='./output/finding_the_one/',
)


# ══════════════════════════════════════════════════════════════
#  ROOM (WALLS)
# ══════════════════════════════════════════════════════════════

wall_mat = create_emission_material("WallMat", color=(WALL_GRAY, WALL_GRAY, WALL_GRAY, 1.0), strength=1.0)

def make_wall(name, sx, sy, lx, ly):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(lx, ly, 0))
    w = bpy.context.active_object
    w.name = name
    w.scale = (sx, sy, 1)
    assign_material(w, wall_mat)
    return w

# Top wall
make_wall("Wall_Top",    ROOM_X_MAX - ROOM_X_MIN, WALL_THICKNESS, 0, ROOM_Y_MAX)
# Bottom wall LEFT (before door)
make_wall("Wall_Bot_L",  DOOR_X_LEFT - ROOM_X_MIN, WALL_THICKNESS,
          (ROOM_X_MIN + DOOR_X_LEFT) / 2, ROOM_Y_MIN)
# Bottom wall RIGHT (after door)
make_wall("Wall_Bot_R",  ROOM_X_MAX - DOOR_X_RIGHT, WALL_THICKNESS,
          (DOOR_X_RIGHT + ROOM_X_MAX) / 2, ROOM_Y_MIN)
# Left wall
make_wall("Wall_Left",   WALL_THICKNESS, ROOM_Y_MAX - ROOM_Y_MIN, ROOM_X_MIN, 0)
# Right wall
make_wall("Wall_Right",  WALL_THICKNESS, ROOM_Y_MAX - ROOM_Y_MIN, ROOM_X_MAX, 0)


# ══════════════════════════════════════════════════════════════
#  CHARACTERS
# ══════════════════════════════════════════════════════════════

# --- Seeker (white circle) ---
seeker_mat = create_emission_material("SeekerMat", color=(1, 1, 1, 1), strength=1.0)
bpy.ops.mesh.primitive_circle_add(vertices=64, radius=SEEKER_RADIUS, location=(-10, -3, 0), fill_type='NGON')
seeker = bpy.context.active_object
seeker.name = "Seeker"
assign_material(seeker, seeker_mat)

# --- Square (gray) ---
square_mat = create_emission_material("SquareMat", color=(0.5, 0.5, 0.5, 1), strength=1.0)
bpy.ops.mesh.primitive_plane_add(size=SQUARE_SIZE, location=(10, 2, 0))
square = bpy.context.active_object
square.name = "Square"
assign_material(square, square_mat)

# --- Rectangle (darker gray) ---
rect_mat = create_emission_material("RectMat", color=(0.4, 0.4, 0.4, 1), strength=1.0)
bpy.ops.mesh.primitive_plane_add(size=1, location=(3, 6, 0))
rect = bpy.context.active_object
rect.name = "Rectangle"
rect.scale = (RECT_W, RECT_H, 1)
assign_material(rect, rect_mat)

# --- The One (white circle, identical to Seeker) ---
one_mat = create_emission_material("TheOneMat", color=(1, 1, 1, 1), strength=1.0)
bpy.ops.mesh.primitive_circle_add(vertices=64, radius=ONE_RADIUS, location=(-10, -3, 0), fill_type='NGON')
the_one = bpy.context.active_object
the_one.name = "TheOne"
assign_material(the_one, one_mat)

# Hide characters that aren't on stage yet
# (We park them offscreen and bring them in at the right time)


# ══════════════════════════════════════════════════════════════
#  ACT I — SEARCHING (Frames 1–450)
# ══════════════════════════════════════════════════════════════

# -- Beat 1.1: Entrance (1–90) --
move_along(seeker, [
    (1,  -10, -3),   # offscreen left
    (30, -6,  -3),   # through door
    (45, -5,  -2),   # hesitation drift up
    (60, -5,  -2),   # hold (pulse will handle the "breathing")
    (90, -1,   0),   # ease into room center
], easing=ease_in_out_cubic)

# Hold pulse during hesitation (45–60): scale pulse 1.0→1.05→1.0
for f in range(45, 61):
    t = (f - 45) / 15.0
    s = 1.0 + 0.05 * math.sin(t * math.pi)
    kf_scale(seeker, s, f)

# -- Beat 1.2: Wandering (90–180) --
# Meandering path with slight wobble to simulate aimless wandering
wander_keyframes = 90
for f in range(90, 181):
    t = (f - 90) / 90.0
    # Base path with sinusoidal wobble
    if t < 0.33:
        tt = t / 0.33
        x = lerp(-1, 1, ease_in_out_cubic(tt))
        y = lerp(0, 1, ease_in_out_cubic(tt))
    elif t < 0.67:
        tt = (t - 0.33) / 0.34
        x = lerp(1, 0.5, ease_in_out_cubic(tt))
        y = lerp(1, -0.5, ease_in_out_cubic(tt))
    else:
        tt = (t - 0.67) / 0.33
        x = lerp(0.5, 0, ease_in_out_cubic(tt))
        y = lerp(-0.5, 0, ease_in_out_cubic(tt))

    # Add subtle wobble (perlin-like)
    wobble_x = 0.15 * math.sin(f * 0.13) * math.cos(f * 0.07)
    wobble_y = 0.12 * math.cos(f * 0.11) * math.sin(f * 0.09)

    kf_loc(seeker, x + wobble_x, y + wobble_y, f)

# -- Beat 1.3: Square Encounter (180–360) --

# Square enters erratically from right (180–210)
# Zigzag path with sharp direction changes
square_entry = [
    (180,  10,   2),
    (190,  6,    0.5),
    (197,  4,   1.8),
    (205,  2.5,  -0.3),
    (210,  1.5,  0.5),
]
move_along(square, square_entry)  # linear (no easing = sharp)

# Square orbits Seeker abruptly (210–240)
for f in range(210, 241):
    t = (f - 210) / 30.0
    angle = t * 2 * math.pi  # one full circle in 30 frames
    radius = 1.0
    sx = 0 + radius * math.cos(angle + math.pi)  # orbit around ~(0,0)
    sy = 0 + radius * math.sin(angle + math.pi)
    kf_loc(square, sx, sy, f)
    # Jittery rotation
    rot = math.radians(15) * math.sin(f * 1.7)
    kf_rot_z(square, rot, f)

# Seeker holds + slight recoil (210–240)
for f in range(210, 241):
    t = (f - 210) / 30.0
    x = lerp(0, -0.3, ease_in_out_cubic(min(t * 2, 1.0)))
    y = lerp(0, -0.1, ease_in_out_cubic(min(t * 2, 1.0)))
    kf_loc(seeker, x, y, f)

# Square nudges into Seeker (240–270)
move_along(square, [
    (240, -0.5, 0.5),
    (250, 0.3,  0),
    (255, 0.1,  0),      # bounce back
    (270, 1.0,  0.5),
])

# Seeker recoils (240–270)
move_along(seeker, [
    (240, -0.3, -0.1),
    (250, -0.5, -0.2),   # flinch
    (255, -1.5, -0.5),   # quick jump away
    (270, -1.5, -0.5),
], easing=ease_out_bounce)

# Square follows erratically, overshoots (270–310)
move_along(square, [
    (270,  1.0,   0.5),
    (280,  -1.0,  0.2),
    (290,  -3.0,  -0.5),  # overshoots past Seeker
    (300,  -1.5,   0.3),
    (310,  -0.5,   0),
])
# Jittery rotation continues
for f in range(270, 311):
    rot = math.radians(15) * math.sin(f * 1.7)
    kf_rot_z(square, rot, f)

# Seeker backs away (270–310)
move_along(seeker, [
    (270, -1.5, -0.5),
    (290, -2.0, -0.8),
    (310, -2.5, -1.0),
], easing=ease_in_out_cubic)

# Square pauses, then exits right (310–340)
move_along(square, [
    (310, -0.5, 0),
    (320, -0.5, 0),    # pause
    (340, 10,   1),     # exit right
])

# Seeker watches (310–340)
for f in range(310, 341):
    kf_loc(seeker, -2.5, -1.0, f)

# Seeker "sigh" (340–360)
apply_sigh(seeker, 340, 360, depth=0.08)
for f in range(340, 361):
    kf_loc(seeker, -2.5, -1.0, f)

# Hide square offscreen after exit
kf_loc(square, 15, 15, 340)
for f in range(341, FRAME_END + 1):
    kf_loc(square, 15, 15, f)

# -- Beat 1.4: Recovery (360–450) --
move_along(seeker, [
    (360, -2.5, -1.0),
    (390, -2.5, -1.0),   # hold: processing
    (420, -1.0,  0.5),   # drift back
    (450,  0.5,  0.0),   # back to center
], easing=ease_in_out_cubic)

# ══════════════════════════════════════════════════════════════
#  SEEKER CONTINUOUS PULSE (Acts I–II)
#  We apply the subtle heartbeat across the whole animation,
#  then override specific sections (sigh, joy, etc.) as needed.
# ══════════════════════════════════════════════════════════════

# NOTE: We apply pulse in targeted ranges to avoid overwriting
# the scale keyframes from special moments (sighs, joy, etc.)
# Act I pulse ranges (avoiding sigh at 340–360)
apply_pulse(seeker, 1, 44, period=45, amplitude=0.03)
apply_pulse(seeker, 61, 339, period=45, amplitude=0.03)
apply_pulse(seeker, 361, 450, period=45, amplitude=0.03)


# ══════════════════════════════════════════════════════════════
#  ACT II — FALSE HOPES (Frames 450–900)
# ══════════════════════════════════════════════════════════════

# -- Beat 2.1: Rectangle Entrance (450–540) --
move_along(rect, [
    (450, 3,   6),
    (480, 3,   3),      # straight down, constant speed
    (510, 2,   1.5),    # 90° turn then diagonal
    (540, 1.2, 0.5),    # approach Seeker area
])
# Rectangle: no rotation, perfectly aligned
for f in range(450, 541):
    kf_rot_z(rect, 0, f)

# Seeker watches/holds near center during rectangle entrance
move_along(seeker, [
    (450, 0.5, 0),
    (540, 0.5, 0),
], easing=ease_in_out_cubic)

# -- Beat 2.2: Stiff Orbit (540–690) --
# Rectangle orbits in a SQUARE-shaped path (straight segments + 90° turns)
# 4 segments per revolution

def square_orbit(obj, center_x, center_y, frame_start, frame_end, radius):
    """Move in a square-shaped orbit (4 straight segments with sharp corners)."""
    total = frame_end - frame_start
    for f in range(frame_start, frame_end + 1):
        t = (f - frame_start) / max(total, 1)
        # map t to position on square perimeter
        # 4 segments: right, top, left, bottom
        seg = t * 4
        if seg < 1:
            x = center_x + radius
            y = center_y - radius + 2 * radius * seg
        elif seg < 2:
            x = center_x + radius - 2 * radius * (seg - 1)
            y = center_y + radius
        elif seg < 3:
            x = center_x - radius
            y = center_y + radius - 2 * radius * (seg - 2)
        else:
            x = center_x - radius + 2 * radius * (seg - 3)
            y = center_y - radius
        kf_loc(obj, x, y, f)

# Rectangle: square orbit at radius 1.5 (540–600)
square_orbit(rect, 0.5, 0, 540, 600, 1.5)

# Seeker tries to rotate to face Rectangle (540–600)
# Speeding up to track, but always behind
for f in range(540, 601):
    t = (f - 540) / 60.0
    # Seeker chases the Rectangle but always lags by ~30°
    lag_angle = t * 2 * math.pi - math.radians(30)
    chase_radius = 0.4  # much smaller orbit
    sx = 0.5 + chase_radius * math.cos(lag_angle)
    sy = 0 + chase_radius * math.sin(lag_angle)
    kf_loc(seeker, sx, sy, f)

# Rectangle orbit tightens (600–630)
square_orbit(rect, 0.5, 0, 600, 630, 1.0)

# Seeker overshoots, doubles back (600–630)
move_along(seeker, [
    (600,  0.5,  0.4),
    (610,  1.2,  0.3),   # overshoot
    (620,  0.2, -0.2),   # double back
    (630,  0.6, -0.1),
])

# Collision (630–660): gap shrinks, soft bump
move_along(rect, [
    (630, 1.3, 0),
    (645, 0.6, 0.1),    # approaching Seeker
    (650, 0.7, 0.15),   # bump — slight bounce
    (660, 1.2, 0.3),    # resume distance
])
move_along(seeker, [
    (630, 0.6, -0.1),
    (645, 0.55, 0),
    (650, 0.3, -0.2),   # wobble from bump
    (660, 0.1, -0.3),
])

# Rectangle resumes rigid orbit, unchanged (660–690)
square_orbit(rect, 0.5, 0, 660, 690, 1.2)

# Seeker gives up, drifts away (660–690)
move_along(seeker, [
    (660, 0.1, -0.3),
    (690, -1.0, -1.0),
], easing=ease_in_out_cubic)

# -- Beat 2.3: Sad Separation (690–810) --
# Rectangle continues orbiting at reduced speed, doesn't follow
square_orbit(rect, 0.5, 0, 690, 720, 1.0)

# Seeker drifts away sadly
move_along(seeker, [
    (690, -1.0, -1.0),
    (720, -2.0, -1.5),
    (750, -2.5, -2.0),
], easing=ease_in_out_cubic)

# Apply sadness pulse (slower pulse)
apply_pulse(seeker, 690, 810, period=55, amplitude=0.02)

# Rectangle stops, holds position (720–750)
for f in range(720, 751):
    kf_loc(rect, 1.5, 0, f)
    kf_rot_z(rect, 0, f)

# Seeker barely moves (720–750)
for f in range(720, 751):
    kf_loc(seeker, -2.5, -2.0, f)

# Rectangle exits without looking back (750–810)
move_along(rect, [
    (750, 1.5, 0),
    (780, 3,   2),
    (810, 3,   6),      # offscreen top
])
for f in range(750, 811):
    kf_rot_z(rect, 0, f)

# Seeker alone, watching (750–810)
for f in range(750, 811):
    kf_loc(seeker, -2.5, -2.0, f)

# Park rectangle offscreen
for f in range(811, FRAME_END + 1):
    kf_loc(rect, 15, 15, f)

# -- Beat 2.4: Alone Again (810–900) --
# Deeper sigh
apply_sigh(seeker, 810, 840, depth=0.06)
for f in range(810, 841):
    kf_loc(seeker, -2.5, -2.0, f)

# very slow drift toward door
move_along(seeker, [
    (840, -2.5, -2.0),
    (870, -3.0, -2.5),   # considering leaving
    (900, -3.0, -2.0),   # stops, looks back
], easing=ease_in_out_cubic)

# Slow sad pulse
apply_pulse(seeker, 841, 900, period=55, amplitude=0.02)

# Normal pulse for Act II (non-special ranges)
apply_pulse(seeker, 450, 539, period=45, amplitude=0.03)
apply_pulse(seeker, 540, 689, period=45, amplitude=0.03)


# ══════════════════════════════════════════════════════════════
#  ACT III — DISCOVERY (Frames 900–1350)
# ══════════════════════════════════════════════════════════════

# -- Beat 3.1: The One Enters (900–990) --
# Mirrors Seeker's original entrance path exactly!
move_along(the_one, [
    (1,   -10, -3),    # parked offscreen before entrance
    (899, -10, -3),    # still offscreen
    (900, -10, -3),    # entrance begins
    (930, -6,  -3),    # through door (same as Seeker)
    (950, -5,  -2),    # hesitation (same as Seeker)
    (970, -4,  -1.5),  # drifts inward
    (990, -4,  -1.5),  # THE PAUSE
], easing=ease_in_out_cubic)

# Seeker notices, slight drift toward The One
move_along(seeker, [
    (900, -3.0, -2.0),
    (950, -3.0, -2.0),  # holds still while noticing
    (970, -3.2, -1.8),  # very slight drift toward The One
    (990, -3.2, -1.8),  # THE PAUSE
], easing=ease_in_out_cubic)

# The One's pulse — same frequency as Seeker, already roughly in sync
apply_pulse(the_one, 900, 990, period=45, amplitude=0.03)
apply_pulse(seeker, 900, 990, period=45, amplitude=0.03)

# -- Beat 3.2: Mutual Recognition (990–1050) --
# Frozen pause (990–1010)
for f in range(990, 1011):
    kf_loc(the_one, -4.0, -1.5, f)
    kf_loc(seeker, -3.2, -1.8, f)

# Tentative approach (1010–1020)
move_along(the_one, [
    (1010, -4.0, -1.5),
    (1020, -3.8, -1.6),
], easing=ease_in_out_cubic)
move_along(seeker, [
    (1010, -3.2, -1.8),
    (1020, -3.4, -1.7),
], easing=ease_in_out_cubic)

# Coming together (1020–1035)
move_along(the_one, [
    (1020, -3.8, -1.6),
    (1035, -3.5, -1.5),
], easing=ease_in_out_cubic)
move_along(seeker, [
    (1020, -3.4, -1.7),
    (1035, -3.5, -1.5),
], easing=ease_in_out_cubic)

# Close but not touching (1035–1050)
# Offset slightly so they're side by side
for f in range(1035, 1051):
    kf_loc(the_one, -3.9, -1.5, f)
    kf_loc(seeker,  -3.1, -1.5, f)

# PERFECT pulse sync by frame 1020
apply_pulse(the_one, 990, 1050, period=45, amplitude=0.03)
apply_pulse(seeker,  990, 1050, period=45, amplitude=0.03)

# -- Beat 3.3: First Orbit (1050–1200) --
# Joyful orbiting with increasing speed and decreasing radius

# Orbit center drifts toward room center over time
ORBIT_CENTER_START = (-3.5, -1.5)
ORBIT_CENTER_END = (-0.5, -0.5)

for f in range(1050, 1201):
    t = (f - 1050) / 150.0

    # Orbit center drifts toward room center
    cx = lerp(ORBIT_CENTER_START[0], ORBIT_CENTER_END[0], ease_in_out_cubic(t))
    cy = lerp(ORBIT_CENTER_START[1], ORBIT_CENTER_END[1], ease_in_out_cubic(t))

    # Determine current orbit parameters based on beat subdivisions
    if f <= 1110:
        # Gentle: 1 rev per 120 frames, radius 0.8
        local_t = (f - 1050) / 60.0
        rev_speed = 1.0 / 120.0  # revolutions per frame
        radius = 0.8
    elif f <= 1140:
        # Faster: 1 rev per 60 frames, radius 0.7
        local_t = (f - 1110) / 30.0
        rev_speed = 1.0 / 60.0
        radius = 0.7
    elif f <= 1170:
        # Even faster: 1 rev per 30 frames, radius 0.5
        local_t = (f - 1140) / 30.0
        rev_speed = 1.0 / 30.0
        radius = 0.5
    else:
        # Exuberant: 1 rev per 20 frames, radius 0.4
        local_t = (f - 1170) / 30.0
        rev_speed = 1.0 / 20.0
        radius = 0.4

    # Accumulate angle from frame 1050
    angle = 0
    for ff in range(1050, f + 1):
        if ff <= 1110:
            angle += (1.0 / 120.0) * 2 * math.pi
        elif ff <= 1140:
            angle += (1.0 / 60.0) * 2 * math.pi
        elif ff <= 1170:
            angle += (1.0 / 30.0) * 2 * math.pi
        else:
            angle += (1.0 / 20.0) * 2 * math.pi

    # Smooth radius transitions
    if f <= 1110:
        r = 0.8
    elif f <= 1140:
        smooth_t = (f - 1110) / 30.0
        r = lerp(0.8, 0.7, ease_in_out_cubic(smooth_t))
    elif f <= 1170:
        smooth_t = (f - 1140) / 30.0
        r = lerp(0.7, 0.5, ease_in_out_cubic(smooth_t))
    else:
        smooth_t = (f - 1170) / 30.0
        r = lerp(0.5, 0.4, ease_in_out_cubic(smooth_t))

    kf_loc(seeker,  cx + r * math.cos(angle),           cy + r * math.sin(angle), f)
    kf_loc(the_one, cx + r * math.cos(angle + math.pi), cy + r * math.sin(angle + math.pi), f)

# Joy pulse — faster, shared
apply_pulse(seeker,  1050, 1200, period=35, amplitude=0.04)
apply_pulse(the_one, 1050, 1200, period=35, amplitude=0.04)

# -- Beat 3.4: Nose-to-Nose (1200–1350) --
# Decelerate and come to rest side by side

for f in range(1200, 1351):
    t = (f - 1200) / 150.0

    # Orbit center settles at roughly (0, 0)
    cx = lerp(-0.5, 0, ease_in_out_cubic(t))
    cy = lerp(-0.5, 0, ease_in_out_cubic(t))

    # Angular velocity decelerates
    if f <= 1230:
        rev_speed = lerp(1.0/20.0, 1.0/60.0, (f-1200)/30.0)
    elif f <= 1260:
        rev_speed = lerp(1.0/60.0, 1.0/200.0, (f-1230)/30.0)
    elif f <= 1290:
        rev_speed = lerp(1.0/200.0, 1.0/600.0, (f-1260)/30.0)
    else:
        rev_speed = 0  # stopped

    # Radius shrinks
    if f <= 1230:
        r = lerp(0.4, 0.3, (f-1200)/30.0)
    elif f <= 1260:
        r = lerp(0.3, 0.15, (f-1230)/30.0)
    elif f <= 1290:
        r = lerp(0.15, 0.05, (f-1260)/30.0)
    else:
        r = 0.05  # nearly touching

    # Accumulate angle
    angle_3_4 = 0
    for ff in range(1200, f + 1):
        if ff <= 1230:
            rs = lerp(1.0/20.0, 1.0/60.0, (ff-1200)/30.0)
        elif ff <= 1260:
            rs = lerp(1.0/60.0, 1.0/200.0, (ff-1230)/30.0)
        elif ff <= 1290:
            rs = lerp(1.0/200.0, 1.0/600.0, (ff-1260)/30.0)
        else:
            rs = 0
        angle_3_4 += rs * 2 * math.pi

    # Start from where Beat 3.3 ended — add the accumulated angle from that beat
    # (approximate final angle from 3.3)
    base_angle = 0
    for ff in range(1050, 1201):
        if ff <= 1110:
            base_angle += (1.0 / 120.0) * 2 * math.pi
        elif ff <= 1140:
            base_angle += (1.0 / 60.0) * 2 * math.pi
        elif ff <= 1170:
            base_angle += (1.0 / 30.0) * 2 * math.pi
        else:
            base_angle += (1.0 / 20.0) * 2 * math.pi

    total_angle = base_angle + angle_3_4

    kf_loc(seeker,  cx + r * math.cos(total_angle),           cy + r * math.sin(total_angle), f)
    kf_loc(the_one, cx + r * math.cos(total_angle + math.pi), cy + r * math.sin(total_angle + math.pi), f)

# Intensifying shared pulse (1320–1350)
apply_pulse(seeker,  1200, 1319, period=40, amplitude=0.03)
apply_pulse(the_one, 1200, 1319, period=40, amplitude=0.03)
apply_pulse(seeker,  1320, 1350, period=40, amplitude=0.06)
apply_pulse(the_one, 1320, 1350, period=40, amplitude=0.06)


# ══════════════════════════════════════════════════════════════
#  ACT IV — UNION (Frames 1350–1800)
# ══════════════════════════════════════════════════════════════

# We need a reference position for where they ended in Beat 3.4.
# We'll compute it once here.
_final_angle = 0
for ff in range(1050, 1201):
    if ff <= 1110: _final_angle += (1.0/120.0) * 2 * math.pi
    elif ff <= 1140: _final_angle += (1.0/60.0) * 2 * math.pi
    elif ff <= 1170: _final_angle += (1.0/30.0) * 2 * math.pi
    else: _final_angle += (1.0/20.0) * 2 * math.pi
for ff in range(1200, 1351):
    if ff <= 1230: rs = lerp(1.0/20.0, 1.0/60.0, (ff-1200)/30.0)
    elif ff <= 1260: rs = lerp(1.0/60.0, 1.0/200.0, (ff-1230)/30.0)
    elif ff <= 1290: rs = lerp(1.0/200.0, 1.0/600.0, (ff-1260)/30.0)
    else: rs = 0
    _final_angle += rs * 2 * math.pi

# Their ending positions at frame 1350
_seeker_end = (0.05 * math.cos(_final_angle), 0.05 * math.sin(_final_angle))
_one_end = (0.05 * math.cos(_final_angle + math.pi), 0.05 * math.sin(_final_angle + math.pi))

# Reposition to be side-by-side horizontally for clarity
# Seeker on the right, The One on the left, gap = 0.1
PAIR_GAP = 0.1
PAIR_CENTER = (0, 0)

seeker_x_offset = PAIR_GAP / 2 + SEEKER_RADIUS
one_x_offset = -(PAIR_GAP / 2 + ONE_RADIUS)

# -- Beat 4.1: Huddle (1350–1500) --
# Gap closes from 0.1 to 0.05, gentle sway

for f in range(1350, 1501):
    t = (f - 1350) / 150.0

    # Gap shrinks (1350–1380)
    if f <= 1380:
        gap_t = (f - 1350) / 30.0
        gap = lerp(0.1, 0.05, ease_in_out_cubic(gap_t))
    else:
        gap = 0.05

    # Pair drifts toward door (1440–1500)
    if f <= 1440:
        pair_cx = 0
        pair_cy = 0
    else:
        drift_t = (f - 1440) / 60.0
        pair_cx = lerp(0, -2, ease_in_out_cubic(drift_t))
        pair_cy = lerp(0, -1, ease_in_out_cubic(drift_t))

    # Gentle sway (1380–1500) — both sway in sync
    if f >= 1380:
        sway_t = (f - 1380) / 120.0
        sway = 0.3 * math.sin(sway_t * 3 * 2 * math.pi)  # 3 full sways
    else:
        sway = 0

    sx_off = gap / 2 + SEEKER_RADIUS * 0.5
    ox_off = -(gap / 2 + ONE_RADIUS * 0.5)

    kf_loc(seeker,  pair_cx + sx_off + sway, pair_cy, f)
    kf_loc(the_one, pair_cx + ox_off + sway, pair_cy, f)

# Strong shared pulse — love pulse
apply_pulse(seeker,  1350, 1500, period=40, amplitude=0.08)
apply_pulse(the_one, 1350, 1500, period=40, amplitude=0.08)

# Both circles brighten — emission strength 1.0 → 1.5
for f in range(1350, 1501):
    t = (f - 1350) / 150.0
    strength = lerp(1.0, 1.5, ease_in_out_cubic(t))
    kf_emission_strength(seeker_mat, strength, f)
    kf_emission_strength(one_mat, strength, f)


# -- Beat 4.2: Exit Together (1500–1650) --
# Pair glides toward door and exits side by side

exit_pair_waypoints = [
    (1500, -2,    -1),
    (1530, -3.5,  -1.5),
    (1560, -5,    -2.5),
    (1590, -7,    -3),
    (1650, -12,   -3),
]

for i in range(len(exit_pair_waypoints) - 1):
    f0, cx0, cy0 = exit_pair_waypoints[i]
    f1, cx1, cy1 = exit_pair_waypoints[i + 1]
    for f in range(f0, f1 + 1):
        t = (f - f0) / max(f1 - f0, 1)
        cx = lerp(cx0, cx1, ease_in_out_cubic(t))
        cy = lerp(cy0, cy1, ease_in_out_cubic(t))

        # Side by side, gap = 0.05
        gap = 0.05

        # Heart-shaped trail: slight wobble to create heart curve
        # The pair wobbles left-right slightly as they exit
        if f >= 1530:
            wobble_phase = (f - 1530) / 120.0
            wobble_x = 0.2 * math.sin(wobble_phase * 2 * math.pi)
            wobble_y = 0.1 * math.sin(wobble_phase * 4 * math.pi)
        else:
            wobble_x = 0
            wobble_y = 0

        kf_loc(seeker,  cx + gap/2 + SEEKER_RADIUS*0.3 + wobble_x,
               cy + wobble_y, f)
        kf_loc(the_one, cx - gap/2 - ONE_RADIUS*0.3 + wobble_x,
               cy + wobble_y, f)

apply_pulse(seeker,  1500, 1650, period=40, amplitude=0.08)
apply_pulse(the_one, 1500, 1650, period=40, amplitude=0.08)

# Keep emission bright during exit
for f in range(1500, 1651):
    kf_emission_strength(seeker_mat, 1.5, f)
    kf_emission_strength(one_mat, 1.5, f)


# -- Trail Effect (spawning fading circles every 10 frames during exit) --
trail_dots = []
for spawn_f in range(1530, 1640, 10):
    for char_idx, char_name in enumerate(["TrailSeeker", "TrailOne"]):
        # Get the position of the character at this frame
        # We calculate it the same way as above
        # Find which segment this frame falls in
        cx_trail = 0
        cy_trail = 0
        for i in range(len(exit_pair_waypoints) - 1):
            ef0, ecx0, ecy0 = exit_pair_waypoints[i]
            ef1, ecx1, ecy1 = exit_pair_waypoints[i + 1]
            if ef0 <= spawn_f <= ef1:
                et = (spawn_f - ef0) / max(ef1 - ef0, 1)
                cx_trail = lerp(ecx0, ecx1, ease_in_out_cubic(et))
                cy_trail = lerp(ecy0, ecy1, ease_in_out_cubic(et))
                break

        gap = 0.05
        wobble_phase = (spawn_f - 1530) / 120.0
        wobble_x = 0.2 * math.sin(wobble_phase * 2 * math.pi)
        wobble_y = 0.1 * math.sin(wobble_phase * 4 * math.pi)

        if char_idx == 0:
            tx = cx_trail + gap/2 + SEEKER_RADIUS*0.3 + wobble_x
        else:
            tx = cx_trail - gap/2 - ONE_RADIUS*0.3 + wobble_x
        ty = cy_trail + wobble_y

        # Create trail dot
        trail_mat = create_emission_material(
            f"TrailMat_{spawn_f}_{char_idx}",
            color=(1, 1, 1, 1),
            strength=0.4,
        )
        bpy.ops.mesh.primitive_circle_add(
            vertices=32, radius=0.15, location=(tx, ty, -0.01),
            fill_type='NGON',
        )
        dot = bpy.context.active_object
        dot.name = f"Trail_{spawn_f}_{char_name}"
        assign_material(dot, trail_mat)

        # Fade out over 30 frames
        kf_emission_strength(trail_mat, 0.4, spawn_f)
        kf_emission_strength(trail_mat, 0.0, spawn_f + 30)

        # Scale down as it fades
        kf_scale(dot, 1.0, spawn_f)
        kf_scale(dot, 0.3, spawn_f + 30)

        # Before spawn, invisible
        kf_scale(dot, 0.0, spawn_f - 1)
        kf_emission_strength(trail_mat, 0.0, spawn_f - 1)

        trail_dots.append(dot)


# -- Beat 4.3: Lingering Glow (1650–1800) --

# Park Seeker and The One offscreen after exit
for f in range(1650, FRAME_END + 1):
    kf_loc(seeker, -15, -3, f)
    kf_loc(the_one, -15, -3, f)

# Create glow plane at center
glow_mat = create_emission_material("GlowMat", color=(1, 1, 1, 1), strength=0.0)
bpy.ops.mesh.primitive_circle_add(vertices=64, radius=1.5, location=(0, 0, -0.02), fill_type='NGON')
glow = bpy.context.active_object
glow.name = "LingeringGlow"
assign_material(glow, glow_mat)

# Glow visible from 1650, fades out by 1750
kf_emission_strength(glow_mat, 0.0, 1)        # invisible before
kf_emission_strength(glow_mat, 0.0, 1649)     # invisible before
kf_emission_strength(glow_mat, 0.5, 1650)     # appear
kf_emission_strength(glow_mat, 0.5, 1700)     # hold
kf_emission_strength(glow_mat, 0.0, 1750)     # fade out

kf_scale(glow, 0.0, 1)                         # invisible before
kf_scale(glow, 0.0, 1649)
kf_scale(glow, 1.0, 1650)
kf_scale(glow, 1.2, 1750)                     # gentle grow as it fades
kf_scale(glow, 1.3, 1800)

# Walls warm up slightly (0.25 → 0.30 gray)
# We animate the wall material emission color
wall_emission = None
for node in wall_mat.node_tree.nodes:
    if node.type == 'EMISSION':
        wall_emission = node
        break

if wall_emission:
    wall_emission.inputs["Color"].default_value = (WALL_GRAY, WALL_GRAY, WALL_GRAY, 1)
    wall_emission.inputs["Color"].keyframe_insert("default_value", frame=1)
    wall_emission.inputs["Color"].default_value = (WALL_GRAY, WALL_GRAY, WALL_GRAY, 1)
    wall_emission.inputs["Color"].keyframe_insert("default_value", frame=1700)
    wall_emission.inputs["Color"].default_value = (0.3, 0.3, 0.3, 1)
    wall_emission.inputs["Color"].keyframe_insert("default_value", frame=1800)

# Fade to black at the very end (1750–1800)
# We'll add a full-screen black overlay plane that fades in
fade_mat = create_emission_material("FadeMat", color=(0, 0, 0, 1), strength=0.0)
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0.1))
fade_plane = bpy.context.active_object
fade_plane.name = "FadeToBlack"
assign_material(fade_plane, fade_mat)

# Make fadeplane transparent initially (won't block scene)
# Use the emission strength to darken; we need an actual alpha approach
# Instead, use object visibility / scale trick
kf_scale(fade_plane, 0.0, 1)
kf_scale(fade_plane, 0.0, 1749)
kf_scale(fade_plane, 1.0, 1750)
kf_emission_strength(fade_mat, 0.0, 1750)
kf_emission_strength(fade_mat, 2.0, 1800)  # Black emission covers scene


# ══════════════════════════════════════════════════════════════
#  SQUARE ROTATION WOBBLE (Act I, when on screen)
# ══════════════════════════════════════════════════════════════

# Already handled within Beat 1.3 section above


# ══════════════════════════════════════════════════════════════
#  SET INTERPOLATION TO LINEAR FOR LOCATION (crisper movement)
# ══════════════════════════════════════════════════════════════

# Set all location/scale F-Curves to LINEAR interpolation
# (the easing is baked into the keyframe values, so Blender
#  should just lerp between them without additional smoothing)
for obj in bpy.data.objects:
    if obj.animation_data and obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            for kp in fcurve.keyframe_points:
                kp.interpolation = 'LINEAR'

# Do the same for material F-Curves
for mat in bpy.data.materials:
    if mat.node_tree and mat.node_tree.animation_data and mat.node_tree.animation_data.action:
        for fcurve in mat.node_tree.animation_data.action.fcurves:
            for kp in fcurve.keyframe_points:
                kp.interpolation = 'LINEAR'


# ══════════════════════════════════════════════════════════════
#  RENDER (headless only)
# ══════════════════════════════════════════════════════════════

if "--background" in sys.argv or "-b" in sys.argv:
    print("🎬 Rendering 'Finding the One' animation frames...")
    bpy.ops.render.render(animation=True)
    print("✅ Frames rendered! Stitching video...")
    frames_to_video(
        frames_dir='./output/finding_the_one/',
        output_file='./output/finding_the_one.mp4',
        fps=FPS,
    )
else:
    print("👀 'Finding the One' loaded in GUI mode.")
    print("   Press Space in the viewport to preview the animation.")
    print("   Timeline: 1–1800 (60 seconds at 30fps)")
    print("   Tip: Use --watch mode for hot-reload during development.")
