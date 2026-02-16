"""
Finding the One — Visual Systems.

Continuous systems that span the entire animation:
- Scrolling camera tracking
- Corner trail lines
- Seeker emission curve (emotional barometer)
- Background triangle density / fade management
- Orthographic scale animation

These are applied AFTER all per-act choreography is done.
"""
import bpy
import math

from scripts.utils.materials import create_emission_material, assign_material
from scripts.utils.animation import lerp, ease_in_out_cubic

from scripts.animations.finding_the_one.config import (
    FRAME_START, FRAME_END, FPS,
    CAMERA_HEIGHT, VISIBLE_HALF_WIDTH,
    ORTHO_NORMAL,
    BG_TRI_EMISSION,
    SEEKER_EMISSION_CURVE,
    BG_DENSITY_CURVE,
    TRAIL_LENGTH_STOP, TRAIL_LENGTH_SLOW, TRAIL_LENGTH_NORMAL,
    TRAIL_LENGTH_FAST, TRAIL_LENGTH_RACING,
    TRAIL_BRIGHTNESS_STOP, TRAIL_BRIGHTNESS_SLOW, TRAIL_BRIGHTNESS_NORMAL,
    TRAIL_BRIGHTNESS_FAST, TRAIL_BRIGHTNESS_RACING,
    SEEKER_SIZE,
)
from scripts.animations.finding_the_one.helpers import (
    kf_loc, kf_scale, kf_emission_strength, kf_ortho_scale,
    kf_emission_color, lerp_value,
)


# ══════════════════════════════════════════════════════════════
#  SCROLL SPEED SCHEDULE
# ══════════════════════════════════════════════════════════════

def build_scroll_schedule():
    """
    Build a frame-by-frame scroll speed schedule.
    Returns a dict: frame → cumulative_world_x (the Seeker's world X position).

    The scroll speed determines how fast the world moves. Since the camera
    tracks the Seeker, this is equivalent to the Seeker's world-space velocity.
    """
    # Key scroll speed waypoints: (frame, speed_in_units_per_frame)
    speed_keyframes = [
        (1,    0.0),      # Prologue — no scrolling
        (270,  0.0),      # Still in prologue
        (300,  0.03),     # Scroll begins
        (330,  0.03),     # Normal journey

        # Act 1 — exploring
        (630,  0.03),     # Before encounter 1
        (680,  0.02),     # Encounter slows
        (720,  0.01),     # Close encounter
        (750,  0.01),     # Bonk
        (820,  0.015),    # Moving on
        (870,  0.03),     # Resumed

        # Act 2 — false hopes
        (990,  0.03),     # Before encounter 2
        (1030, 0.02),     # Encounter 2 approach
        (1070, 0.01),     # Close
        (1110, 0.01),     # Interaction
        (1210, 0.005),    # The tease — near stop
        (1350, 0.015),    # Moving on
        (1390, 0.02),     # separation
        (1470, 0.025),    # continuing

        # Valley
        (1500, 0.025),    # Alone again
        (1650, 0.012),    # Decelerating
        (1690, 0.008),    # Crawling
        (1740, 0.008),    # The turn
        (1770, 0.010),    # Noticing
        (1800, 0.020),    # Hope

        # Act 3 — discovery
        (1850, 0.025),    # Approaching
        (1910, 0.01),     # The pause
        (1950, 0.005),    # Frozen
        (2040, 0.005),    # Orbit begins (near-stopped)
        (2250, 0.005),    # Still orbiting
        (2460, 0.02),     # The click — resume

        # Act 4 — union
        (2500, 0.02),     # Huddle
        (2580, 0.025),
        (2670, 0.03),     # Accelerating
        (2760, 0.04),
        (2850, 0.06),
        (2900, 0.08),
        (2940, 0.10),     # Racing

        # Final
        (3010, 0.10),
        (3060, 0.08),
        (3100, 0.05),
        (3130, 0.03),
        (3150, 0.0),      # End
    ]

    # Interpolate speed at every frame
    speeds = {}
    for f in range(FRAME_START, FRAME_END + 1):
        # Find surrounding keyframes
        prev_kf = speed_keyframes[0]
        next_kf = speed_keyframes[-1]
        for i in range(len(speed_keyframes) - 1):
            if speed_keyframes[i][0] <= f <= speed_keyframes[i + 1][0]:
                prev_kf = speed_keyframes[i]
                next_kf = speed_keyframes[i + 1]
                break

        if prev_kf[0] == next_kf[0]:
            speed = prev_kf[1]
        else:
            t = (f - prev_kf[0]) / (next_kf[0] - prev_kf[0])
            speed = lerp(prev_kf[1], next_kf[1], t)
        speeds[f] = speed

    # Integrate to get cumulative X position
    positions = {}
    world_x = 0.0
    for f in range(FRAME_START, FRAME_END + 1):
        world_x += speeds[f]
        positions[f] = world_x

    return positions, speeds


# ══════════════════════════════════════════════════════════════
#  CAMERA TRACKING
# ══════════════════════════════════════════════════════════════

def setup_scrolling_camera(camera, seeker_world_positions):
    """
    Animate camera X to track the Seeker's world X position each frame.
    Camera Y stays at 0, Z at CAMERA_HEIGHT.
    """
    for f in range(FRAME_START, FRAME_END + 1):
        world_x = seeker_world_positions.get(f, 0)
        kf_loc(camera, world_x, 0, f)
        # Override Z since kf_loc sets Z=0 for top-down
        camera.location[2] = CAMERA_HEIGHT
        camera.keyframe_insert(data_path="location", index=2, frame=f)


def animate_seeker_world_position(seeker, world_positions, y_positions):
    """
    Set the Seeker's world-space position each frame.
    X comes from scroll integration, Y from per-act choreography.
    """
    for f in range(FRAME_START, FRAME_END + 1):
        wx = world_positions.get(f, 0)
        wy = y_positions.get(f, 0)
        kf_loc(seeker, wx, wy, f)


# ══════════════════════════════════════════════════════════════
#  SEEKER EMISSION CURVE
# ══════════════════════════════════════════════════════════════

def apply_seeker_emission_curve(seeker_mat):
    """
    Animate the Seeker's emission strength across the full timeline
    based on the emotional barometer curve defined in config.
    """
    curve = SEEKER_EMISSION_CURVE
    for i in range(len(curve) - 1):
        f0, e0 = curve[i]
        f1, e1 = curve[i + 1]
        for f in range(f0, f1 + 1):
            t = (f - f0) / max(f1 - f0, 1)
            emission = lerp(e0, e1, t)
            kf_emission_strength(seeker_mat, emission, f)


# ══════════════════════════════════════════════════════════════
#  BACKGROUND TRIANGLE MANAGEMENT
# ══════════════════════════════════════════════════════════════

def _interp_density(frame):
    """Get the target BG triangle density at a given frame."""
    curve = BG_DENSITY_CURVE
    for i in range(len(curve) - 1):
        f0, d0 = curve[i]
        f1, d1 = curve[i + 1]
        if f0 <= frame <= f1:
            t = (frame - f0) / max(f1 - f0, 1)
            return lerp(d0, d1, t)
    return curve[-1][1]


def animate_background_triangles(bg_triangles, seeker_world_positions):
    """
    Manage background triangle positions and visibility.

    Each BG triangle has a fixed world position. As the camera scrolls,
    they appear from the right and exit left. We also fade them based
    on the density curve — when density drops, distant triangles fade out.

    Triangles gently bob around their home positions with visible movement.

    Args:
        bg_triangles: list of (obj, mat, world_x, world_y) from characters.py
        seeker_world_positions: dict of frame → world_x from scroll schedule
    """
    # Sort by world_x so we can control which ones are "active"
    sorted_tris = sorted(bg_triangles, key=lambda t: t[2])

    for f in range(FRAME_START, FRAME_END + 1):
        cam_x = seeker_world_positions.get(f, 0)
        target_density = _interp_density(f)

        # Determine which triangles are in view range
        view_left = cam_x - VISIBLE_HALF_WIDTH - 2  # slight buffer
        view_right = cam_x + VISIBLE_HALF_WIDTH + 2

        visible_count = 0
        for obj, mat, wx, wy in sorted_tris:
            in_view = view_left <= wx <= view_right

            if in_view and visible_count < target_density:
                # Show this triangle
                visible_count += 1
                # Position is fixed in world space — Blender handles it
                # We only need to manage emission (fade in/out)
                if f % 10 == 0 or f == FRAME_START:  # Keyframe every 10 frames for perf
                    kf_emission_strength(mat, BG_TRI_EMISSION, f)
            else:
                # Fade out or keep hidden
                if f % 10 == 0 or f == FRAME_START:
                    kf_emission_strength(mat, 0.0, f)

    # Add visible movement to each BG triangle — bobbing around home positions
    import random
    random.seed(99)
    for obj, mat, wx, wy in bg_triangles:
        # Each triangle gets its own movement pattern
        rot_speed = random.uniform(-0.02, 0.02)      # radians per frame — 10x bigger
        drift_radius = random.uniform(0.3, 0.8)       # how far they bob from home
        drift_speed_x = random.uniform(0.005, 0.015)  # bob frequency X
        drift_speed_y = random.uniform(0.005, 0.015)  # bob frequency Y
        phase_x = random.uniform(0, 2 * math.pi)      # phase offset
        phase_y = random.uniform(0, 2 * math.pi)

        for f in range(FRAME_START, FRAME_END + 1, 3):  # every 3 frames for perf
            # Gentle rotation
            angle = rot_speed * f
            obj.rotation_euler[2] = angle
            obj.keyframe_insert(data_path="rotation_euler", index=2, frame=f)

            # Bob around home position in a figure-8 / lissajous pattern
            bob_x = drift_radius * math.sin(drift_speed_x * f + phase_x)
            bob_y = drift_radius * math.cos(drift_speed_y * f + phase_y)
            obj.location[0] = wx + bob_x
            obj.location[1] = wy + bob_y
            obj.keyframe_insert(data_path="location", index=0, frame=f)
            obj.keyframe_insert(data_path="location", index=1, frame=f)


# ══════════════════════════════════════════════════════════════
#  ORTHOGRAPHIC SCALE ANIMATION
# ══════════════════════════════════════════════════════════════

def apply_ortho_scale_shifts(camera, scale_keyframes):
    """
    Animate the camera's orthographic scale.

    Args:
        camera: the Blender camera object
        scale_keyframes: list of (frame, ortho_scale) tuples
    """
    for i in range(len(scale_keyframes) - 1):
        f0, s0 = scale_keyframes[i]
        f1, s1 = scale_keyframes[i + 1]
        for f in range(f0, f1 + 1):
            t = (f - f0) / max(f1 - f0, 1)
            scale = lerp(s0, s1, ease_in_out_cubic(t))
            kf_ortho_scale(camera, scale, f)


# ══════════════════════════════════════════════════════════════
#  CORNER TRAIL LINES
# ══════════════════════════════════════════════════════════════

def create_trail_lines(seeker, the_one=None):
    """
    Create the trailing glow lines from the Seeker's left corners.
    Returns trail objects for later animation.

    In the paired phase (Act IV), four trail lines are used.
    """
    trails = []
    half = SEEKER_SIZE / 2  # Use actual seeker size

    for i, (name, y_off) in enumerate([
        ("TrailTopLeft", half),
        ("TrailBotLeft", -half),
    ]):
        mat = create_emission_material(
            f"{name}Mat", color=(1, 1, 1, 1), strength=0.6
        )
        bpy.ops.mesh.primitive_plane_add(size=1, location=(-50, 0, -0.005))
        trail = bpy.context.active_object
        trail.name = name
        trail.scale = (1.0, 0.02, 1)  # thin horizontal line
        assign_material(trail, mat)
        trails.append((trail, mat, y_off))

    return trails


def animate_trail_lines(trails, seeker_world_positions, scroll_speeds, paired_from=None):
    """
    Animate trail line length and brightness based on scroll speed.

    Trails are positioned relative to the Seeker and extend leftward.
    Only visible when the Seeker is actively scrolling (prologue excluded).

    Args:
        trails: list of (trail_obj, mat, y_offset) from create_trail_lines
        seeker_world_positions: frame → world_x
        scroll_speeds: frame → speed
        paired_from: frame number when pairing happens (4 trails active)
    """
    # Trails should only appear after the prologue scrolling begins
    TRAIL_VISIBLE_FROM = 300

    for f in range(FRAME_START, FRAME_END + 1):
        if f % 2 != 0 and f != FRAME_START:  # every 2 frames for smoother display
            continue

        speed = scroll_speeds.get(f, 0)
        wx = seeker_world_positions.get(f, 0)

        # Before scrolling starts, hide trails completely
        if f < TRAIL_VISIBLE_FROM:
            for trail, mat, y_off in trails:
                trail.location = (-60, 0, -0.005)
                trail.keyframe_insert(data_path="location", frame=f)
                trail.scale = (0.01, 0.02, 1)
                trail.keyframe_insert(data_path="scale", frame=f)
                kf_emission_strength(mat, 0.0, f)
            continue

        # Map speed to trail length and brightness
        if speed <= 0.005:
            length = TRAIL_LENGTH_STOP
            brightness = TRAIL_BRIGHTNESS_STOP
        elif speed <= 0.015:
            t = (speed - 0.005) / 0.01
            length = lerp(TRAIL_LENGTH_STOP, TRAIL_LENGTH_SLOW, t)
            brightness = lerp(TRAIL_BRIGHTNESS_STOP, TRAIL_BRIGHTNESS_SLOW, t)
        elif speed <= 0.03:
            t = (speed - 0.015) / 0.015
            length = lerp(TRAIL_LENGTH_SLOW, TRAIL_LENGTH_NORMAL, t)
            brightness = lerp(TRAIL_BRIGHTNESS_SLOW, TRAIL_BRIGHTNESS_NORMAL, t)
        elif speed <= 0.06:
            t = (speed - 0.03) / 0.03
            length = lerp(TRAIL_LENGTH_NORMAL, TRAIL_LENGTH_FAST, t)
            brightness = lerp(TRAIL_BRIGHTNESS_NORMAL, TRAIL_BRIGHTNESS_FAST, t)
        else:
            t = min((speed - 0.06) / 0.04, 1.0)
            length = lerp(TRAIL_LENGTH_FAST, TRAIL_LENGTH_RACING, t)
            brightness = lerp(TRAIL_BRIGHTNESS_FAST, TRAIL_BRIGHTNESS_RACING, t)

        for trail, mat, y_off in trails:
            # Trail position: left of Seeker, at the corner's Y offset
            half = SEEKER_SIZE / 2
            trail_x = wx - half - length / 2  # anchored at left edge of square
            trail.location = (trail_x, y_off, -0.005)
            trail.keyframe_insert(data_path="location", frame=f)
            trail.scale = (max(length, 0.05), 0.02, 1)
            trail.keyframe_insert(data_path="scale", frame=f)
            kf_emission_strength(mat, brightness, f)


# ══════════════════════════════════════════════════════════════
#  FADE TO BLACK / WHITE
# ══════════════════════════════════════════════════════════════

def create_fade_overlay():
    """
    Create a large overlay plane for fade-to-white and fade-to-black effects.
    Returns (obj, mat).
    """
    mat = create_emission_material("FadeOverlayMat", color=(1, 1, 1, 1), strength=0.0)
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0.5))
    obj = bpy.context.active_object
    obj.name = "FadeOverlay"
    assign_material(obj, mat)

    # Start invisible
    kf_scale(obj, 0.0, FRAME_START)

    return obj, mat
