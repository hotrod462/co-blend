"""
Finding the One — Visual Systems.
Scrolling camera, emission curves, background management, ortho scale.
Updated for extended timeline with Gap.
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
#  SCROLL SPEED SCHEDULE (UPDATED)
# ══════════════════════════════════════════════════════════════

def build_scroll_schedule():
    speed_keyframes = [
        # Prologue & Start (1-330)
        (1,    0.0), (230, 0.0), (260, 0.03), (300, 0.03),
        (330,  0.03),
        (630,  0.03),
        (750,  0.02),
        (880,  0.01),
        (1000, 0.01),
        (1100, 0.010), # Slow through right-angle exit
        (1300, 0.010), # Keep slow — exit runs to 1520, world shouldn't rush away
        (1430, 0.010), # Midway through exit
        (1520, 0.012), # Exit ends, gap begins

        # Gap: Wandering Alone (1520-1670)
        (1595, 0.015),
        (1670, 0.030), # Entering Act 2

        # Act 2 (1670-2790)
        (1720, 0.030),
        (1870, 0.020),
        (2020, 0.010), # Crawling approach
        (2170, 0.005), # Near standstill for orbit
        (2320, 0.012), # Leaving (bonk)
        (2470, 0.010), # Iso exit — keep slow, world doesn't pull away
        (2600, 0.010), # Deep in iso exit, still slow
        (2790, 0.012), # Iso exit ends

        # Valley (2790-2940)
        (2840, 0.012),
        (2890, 0.008),
        (2940, 0.020), # Hope returns

        # Act 3 (2940-3640)
        (2990, 0.025),
        (3140, 0.010),
        (3240, 0.005), # Slow orbit/sync
        (3390, 0.005),
        (3640, 0.020), # The Click

        # Act 4 (3640-4140)
        (3740, 0.030),
        (3840, 0.060),
        (3940, 0.080),
        (3990, 0.100),
        (4090, 0.050),
        (4140, 0.000),
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
    sorted_tris = sorted(bg_triangles, key=lambda t: t[2])
    tri_target_emission = {}
    for obj, mat, wx, wy in sorted_tris:
        tri_target_emission[id(obj)] = 0.0

    for f in range(FRAME_START, FRAME_END + 1):
        if f % 5 != 0 and f != FRAME_START: 
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
    # Updated keyframes for new timeline
    # 2460 -> 3250 Act 3 Ends
    new_kf = [
        (1,    20),
        (880,  18),    # Act 1 Encounter
        (1300, 20),    # Act 1 End / Recovery
        (1670, 20),    # Gap end / Act 2 Start (+170)
        (2120, 18),    # Act 2 Encounter (orbit midpoint, +170)
        (2790, 22),    # Lonely/Valley (+290)
        (3640, 16),    # The Click (Act 3 End, +290)
        (3840, 20),    # (+290)
        (4140, 24),    # End (+290)
    ]
    
    for i in range(len(new_kf) - 1):
        f0, s0 = new_kf[i]
        f1, s1 = new_kf[i + 1]
        for f in range(f0, f1 + 1):
            t = (f - f0) / max(f1 - f0, 1)
            scale = lerp(s0, s1, ease_in_out_cubic(t))
            kf_ortho_scale(camera, scale, f)


# ══════════════════════════════════════════════════════════════
#  PARTICLE DUST (Ambient atmosphere)
# ══════════════════════════════════════════════════════════════

def animate_particle_dust(seeker_world_positions, camera):
    """Create and animate ultra-dim particle dust across the void."""
    import random as _rng
    _rng.seed(42)  # Deterministic for consistency

    NUM_PARTICLES = 25
    particles = []

    for i in range(NUM_PARTICLES):
        name = f"Dust_{i}"
        gray = _rng.uniform(0.2, 0.5)
        mat = create_emission_material(
            f"{name}Mat", color=(gray, gray, gray, 1), strength=0.0
        )
        # Tiny plane
        bpy.ops.mesh.primitive_plane_add(size=0.06, location=(0, 0, -0.01))
        obj = bpy.context.active_object
        obj.name = name
        assign_material(obj, mat)

        # Random drift parameters
        base_world_x_offset = _rng.uniform(-8, 20)  # Scattered along path
        base_y = _rng.uniform(-4.0, 4.0)
        drift_speed_x = _rng.uniform(-0.001, 0.001)  # Even slower drift
        drift_speed_y = _rng.uniform(0.0005, 0.002)   # Barely moving up
        wobble_freq = _rng.uniform(0.02, 0.05)       # Much lower frequency (slower bounce)
        wobble_amp = _rng.uniform(0.02, 0.08)        # Much lower amplitude (less bounce)
        particles.append((obj, mat, base_world_x_offset, base_y,
                          drift_speed_x, drift_speed_y, wobble_freq, wobble_amp))

    # Animate
    for f in range(FRAME_START, FRAME_END + 1):
        wx = seeker_world_positions.get(f, 0)

        # Emission follows bg density curve (fade during Valley)
        em_base = 0.08
        for j in range(len(BG_DENSITY_CURVE) - 1):
            f0, d0 = BG_DENSITY_CURVE[j]
            f1, d1 = BG_DENSITY_CURVE[j + 1]
            if f0 <= f <= f1:
                t = (f - f0) / max(f1 - f0, 1)
                density = lerp(d0, d1, t)
                em_base = 0.08 * density
                break

        for obj, mat, bxo, by, dsx, dsy, wf, wa in particles:
            x = wx + bxo + dsx * f
            y = by + dsy * f * 0.1 + wa * math.sin(f * wf)
            kf_loc(obj, x, y, f)
            kf_emission_strength(mat, em_base, f)

    return particles
