"""
Finding the One — Act IV: Union (Frames 2460–3150, 82s–105s)

The paired squares travel together, accelerating into the future.
Four trail lines, expanding glow, and the world fades to white then black.
"""
import math

import bpy
from scripts.utils.animation import lerp, ease_in_out_cubic
from scripts.utils.materials import create_emission_material, assign_material

from scripts.animations.finding_the_one.config import (
    ACT4_START, ACT4_END, FRAME_END,
    SEEKER_SIZE, ONE_SIZE,
    ORTHO_WIDE,
)
from scripts.animations.finding_the_one.helpers import (
    kf_loc, kf_scale, kf_emission_strength, kf_emission_color,
    kf_ortho_scale, apply_pulse,
)


def animate_act4(seeker, seeker_mat, the_one, one_mat,
                 seeker_world_positions, seeker_y_out,
                 camera, final_angle):
    """
    Frames 2460–3150: Union.

    Args:
        seeker, the_one: Blender objects
        seeker_mat, one_mat: materials
        seeker_world_positions: dict frame → world_x
        seeker_y_out: dict to populate with frame → y_position
        camera: camera object
        final_angle: final orbit angle from Act III for continuity
    """
    half_size = SEEKER_SIZE / 2

    # ── Beat 4.1: Huddle (Frames 2460–2670) ──────────────────
    # Flush contact, gentle sway, traveling together
    # Transition smoothly from Act 3's final angle
    for f in range(2460, 2671):
        t = (f - 2460) / 210.0
        wx = seeker_world_positions.get(f, 0)

        # Smoothly transition from orbit-based positioning to side-by-side
        # In the first ~40 frames, blend from final_angle to horizontal arrangement
        if f < 2500:
            blend = (f - 2460) / 40.0  # 0 → 1 over 40 frames
            blend = ease_in_out_cubic(blend)

            # Orbit-based position from Act 3 end
            cx = wx + 0.6
            orbit_sx = cx + half_size * math.cos(final_angle)
            orbit_sy = half_size * math.sin(final_angle)
            orbit_ox = cx + half_size * math.cos(final_angle + math.pi)
            orbit_oy = half_size * math.sin(final_angle + math.pi)

            # Target side-by-side position
            target_sx = wx + half_size
            target_sy = 0
            target_ox = wx - half_size
            target_oy = 0

            sx = lerp(orbit_sx, target_sx, blend)
            sy = lerp(orbit_sy, target_sy, blend)
            ox = lerp(orbit_ox, target_ox, blend)
            oy = lerp(orbit_oy, target_oy, blend)
        else:
            # Side by side, flush (gap=0)
            sway_t = (f - 2500) / 170.0
            sway = 0.3 * math.sin(sway_t * 3 * 2 * math.pi)

            sx = wx + half_size
            ox = wx - half_size
            sy = sway
            oy = sway

        kf_loc(seeker, sx, sy, f)
        kf_loc(the_one, ox, oy, f)
        seeker_y_out[f] = sy

    # Strong shared pulse
    apply_pulse(seeker,  2460, 2670, period=40, amplitude=0.06)
    apply_pulse(the_one, 2460, 2670, period=40, amplitude=0.06)

    # Both brighten: emission 2.0 → 3.0
    for f in range(2460, 2671):
        t = (f - 2460) / 210.0
        em = lerp(2.0, 3.0, ease_in_out_cubic(t))
        kf_emission_strength(seeker_mat, em, f)
        kf_emission_strength(one_mat, em, f)

    # ── Beat 4.2: Accelerating Together (Frames 2670–2940) ───
    # Faster than Seeker ever traveled alone, world streaming past
    for f in range(2670, 2941):
        t = (f - 2670) / 270.0
        wx = seeker_world_positions.get(f, 0)

        # Side by side, gentle sway
        sway = 0.2 * math.sin(t * 4 * 2 * math.pi)

        sx = wx + half_size
        ox = wx - half_size

        kf_loc(seeker, sx, sway, f)
        kf_loc(the_one, ox, sway, f)
        seeker_y_out[f] = sway

    apply_pulse(seeker,  2670, 2940, period=35, amplitude=0.04)
    apply_pulse(the_one, 2670, 2940, period=35, amplitude=0.04)

    # Hold bright emission
    for f in range(2670, 2941):
        kf_emission_strength(seeker_mat, 3.0, f)
        kf_emission_strength(one_mat, 3.0, f)

    # ── TRAIL EFFECT: Spawn fading trail squares every 10 frames ──
    trail_objects = []
    for spawn_f in range(2700, 2930, 10):
        wx = seeker_world_positions.get(spawn_f, 0)

        for char_idx, (char_name, x_off) in enumerate([
            ("TrailSeeker", half_size),
            ("TrailOne", -half_size),
        ]):
            tx = wx + x_off
            sway = 0.2 * math.sin(((spawn_f - 2670) / 270.0) * 4 * 2 * math.pi)
            ty = sway

            trail_mat = create_emission_material(
                f"Trail_{spawn_f}_{char_idx}Mat",
                color=(1, 1, 1, 1), strength=0.5,
            )
            bpy.ops.mesh.primitive_plane_add(
                size=SEEKER_SIZE * 0.6,
                location=(tx, ty, -0.01),
            )
            dot = bpy.context.active_object
            dot.name = f"Trail_{spawn_f}_{char_name}"
            assign_material(dot, trail_mat)

            # Before spawn: invisible
            kf_scale(dot, 0.0, spawn_f - 1)
            kf_emission_strength(trail_mat, 0.0, spawn_f - 1)

            # At spawn
            kf_scale(dot, 1.0, spawn_f)
            kf_emission_strength(trail_mat, 0.5, spawn_f)

            # Fade out over 40 frames
            kf_scale(dot, 0.3, spawn_f + 40)
            kf_emission_strength(trail_mat, 0.0, spawn_f + 40)

            trail_objects.append(dot)

    # ── Beat 4.3: Into the Light (Frames 2940–3150) ──────────
    # Glow expands, world dissolves, fade to white then black

    for f in range(2940, 3151):
        t = (f - 2940) / 210.0
        wx = seeker_world_positions.get(f, 0)

        # Pair continues together
        sway = 0.1 * math.sin(t * 2 * math.pi)
        sx = wx + half_size
        ox = wx - half_size

        kf_loc(seeker, sx, sway, f)
        kf_loc(the_one, ox, sway, f)
        seeker_y_out[f] = sway

        # Emission expands: 3.0 → 5.0
        em = lerp(3.0, 5.0, ease_in_out_cubic(t))
        kf_emission_strength(seeker_mat, em, f)
        kf_emission_strength(one_mat, em, f)

    apply_pulse(seeker,  2940, 3100, period=40, amplitude=0.04)
    apply_pulse(the_one, 2940, 3100, period=40, amplitude=0.04)

    # Create glow overlay — white fills screen (3010–3130)
    glow_mat = create_emission_material(
        "GlowOverlayMat", color=(1, 1, 1, 1), strength=0.0
    )
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0.3))
    glow = bpy.context.active_object
    glow.name = "GlowOverlay"
    assign_material(glow, glow_mat)

    # Invisible until glow starts
    kf_scale(glow, 0.0, 1)
    kf_scale(glow, 0.0, 3009)
    kf_scale(glow, 1.0, 3010)

    # Track camera during glow
    for f in range(3010, 3151):
        wx = seeker_world_positions.get(f, 0)
        glow.location = (wx, 0, 0.3)
        glow.keyframe_insert(data_path="location", frame=f)

    # Glow brightness ramp
    kf_emission_strength(glow_mat, 0.0, 3010)
    kf_emission_strength(glow_mat, 0.3, 3060)
    kf_emission_strength(glow_mat, 1.0, 3100)
    kf_emission_strength(glow_mat, 2.0, 3130)

    # Fade white → black (3130–3150)
    fade_mat = create_emission_material(
        "FadeToBlackMat", color=(0, 0, 0, 1), strength=0.0
    )
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0.5))
    fade = bpy.context.active_object
    fade.name = "FadeToBlack"
    assign_material(fade, fade_mat)

    kf_scale(fade, 0.0, 1)
    kf_scale(fade, 0.0, 3129)
    kf_scale(fade, 1.0, 3130)

    for f in range(3130, 3151):
        wx = seeker_world_positions.get(f, 0)
        fade.location = (wx, 0, 0.5)
        fade.keyframe_insert(data_path="location", frame=f)

    kf_emission_strength(fade_mat, 0.0, 3130)
    kf_emission_strength(fade_mat, 3.0, 3150)

    return trail_objects
