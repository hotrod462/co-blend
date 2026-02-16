"""
Finding the One — Visual Systems.
Scrolling camera, emission curves, background management, ortho scale.
Trail lines REMOVED (not rendering properly).
"""
import bpy
import math

from scripts.utils.materials import create_emission_material, assign_material
from scripts.utils.animation import lerp, ease_in_out_cubic

from scripts.animations.finding_the_one.config import (
    FRAME_START, FRAME_END, FPS,
    CAMERA_HEIGHT, VISIBLE_HALF_WIDTH, SEEKER_SIZE,
    ORTHO_NORMAL, BG_TRI_EMISSION,
    SEEKER_EMISSION_CURVE, BG_DENSITY_CURVE,
)
from scripts.animations.finding_the_one.helpers import (
    kf_loc, kf_scale, kf_emission_strength, kf_ortho_scale,
)


# ══════════════════════════════════════════════════════════════
#  SCROLL SPEED SCHEDULE
# ══════════════════════════════════════════════════════════════

def build_scroll_schedule():
    speed_keyframes = [
        (1,    0.0), (270, 0.0), (300, 0.03), (330, 0.03),
        (630,  0.03), (680, 0.02), (720, 0.01), (750, 0.01),
        (820,  0.015), (870, 0.03),
        (990,  0.03), (1030, 0.02), (1070, 0.01), (1110, 0.01),
        (1210, 0.005), (1350, 0.015), (1390, 0.02), (1470, 0.025),
        (1500, 0.025), (1650, 0.012), (1690, 0.008),
        (1740, 0.008), (1770, 0.010), (1800, 0.020),
        (1850, 0.025), (1910, 0.01), (1950, 0.005),
        (2040, 0.005), (2250, 0.005), (2460, 0.02),
        (2500, 0.02), (2580, 0.025), (2670, 0.03),
        (2760, 0.04), (2850, 0.06), (2900, 0.08), (2940, 0.10),
        (3010, 0.10), (3060, 0.08), (3100, 0.05),
        (3130, 0.03), (3150, 0.0),
    ]

    speeds = {}
    for f in range(FRAME_START, FRAME_END + 1):
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
    for f in range(FRAME_START, FRAME_END + 1):
        world_x = seeker_world_positions.get(f, 0)
        camera.location = (world_x, 0, CAMERA_HEIGHT)
        camera.keyframe_insert(data_path="location", frame=f)


# ══════════════════════════════════════════════════════════════
#  SEEKER EMISSION CURVE
# ══════════════════════════════════════════════════════════════

def apply_seeker_emission_curve(seeker_mat):
    curve = SEEKER_EMISSION_CURVE
    for i in range(len(curve) - 1):
        f0, e0 = curve[i]
        f1, e1 = curve[i + 1]
        # Keyframe every frame for smooth transitions
        for f in range(f0, f1 + 1):
            t = (f - f0) / max(f1 - f0, 1)
            emission = lerp(e0, e1, t)
            kf_emission_strength(seeker_mat, emission, f)


# ══════════════════════════════════════════════════════════════
#  BACKGROUND TRIANGLE MANAGEMENT
# ══════════════════════════════════════════════════════════════

def _interp_density(frame):
    curve = BG_DENSITY_CURVE
    for i in range(len(curve) - 1):
        f0, d0 = curve[i]
        f1, d1 = curve[i + 1]
        if f0 <= frame <= f1:
            t = (frame - f0) / max(f1 - f0, 1)
            return lerp(d0, d1, t)
    return curve[-1][1]


def animate_background_triangles(bg_triangles, seeker_world_positions):
    """Manage BG triangle visibility/fading and add visible bobbing movement."""
    sorted_tris = sorted(bg_triangles, key=lambda t: t[2])

    # Per-triangle fade state tracking
    # Each triangle smoothly fades between 0 and BG_TRI_EMISSION
    tri_target_emission = {}
    for obj, mat, wx, wy in sorted_tris:
        tri_target_emission[id(obj)] = 0.0

    for f in range(FRAME_START, FRAME_END + 1):
        if f % 5 != 0 and f != FRAME_START:  # every 5 frames
            continue

        cam_x = seeker_world_positions.get(f, 0)
        target_density = _interp_density(f)
        view_left = cam_x - VISIBLE_HALF_WIDTH - 2
        view_right = cam_x + VISIBLE_HALF_WIDTH + 2

        visible_count = 0
        for obj, mat, wx, wy in sorted_tris:
            in_view = view_left <= wx <= view_right

            if in_view and visible_count < target_density:
                visible_count += 1
                kf_emission_strength(mat, BG_TRI_EMISSION, f)
            else:
                kf_emission_strength(mat, 0.0, f)

    # Add visible bobbing movement around home positions
    import random
    random.seed(99)
    for obj, mat, wx, wy in bg_triangles:
        rot_speed = random.uniform(-0.02, 0.02)
        drift_radius = random.uniform(0.3, 0.8)
        drift_speed_x = random.uniform(0.005, 0.015)
        drift_speed_y = random.uniform(0.005, 0.015)
        phase_x = random.uniform(0, 2 * math.pi)
        phase_y = random.uniform(0, 2 * math.pi)

        for f in range(FRAME_START, FRAME_END + 1, 3):
            angle = rot_speed * f
            obj.rotation_euler[2] = angle
            obj.keyframe_insert(data_path="rotation_euler", index=2, frame=f)

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
    for i in range(len(scale_keyframes) - 1):
        f0, s0 = scale_keyframes[i]
        f1, s1 = scale_keyframes[i + 1]
        for f in range(f0, f1 + 1):
            t = (f - f0) / max(f1 - f0, 1)
            scale = lerp(s0, s1, ease_in_out_cubic(t))
            kf_ortho_scale(camera, scale, f)
