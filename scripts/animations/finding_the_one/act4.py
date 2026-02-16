"""
Finding the One — Act IV: Union (Frames 2460–3150)
Clean transition from Act 3's locked angle.
"""
import math
import bpy
from scripts.utils.animation import lerp, ease_in_out_cubic
from scripts.utils.materials import create_emission_material, assign_material
from scripts.animations.finding_the_one.config import (
    ACT4_START, ACT4_END, FRAME_END, SEEKER_SIZE, ONE_SIZE,
)
from scripts.animations.finding_the_one.helpers import (
    kf_loc, kf_scale, kf_rot_z, kf_emission_strength, kf_emission_color,
    apply_pulse,
)


def animate_act4(seeker, seeker_mat, the_one, one_mat,
                 seeker_world_positions, seeker_y_out,
                 camera, final_angle_info):
    """final_angle_info = (target_orbit_angle, target_rotation) from Act 3."""
    half = SEEKER_SIZE / 2
    target_orbit_angle, target_rotation = final_angle_info

    # Determine Act 4 positions from Act 3's final state:
    # At end of Act 3, center offset = 0, angle = target_orbit_angle
    # cos(k*π) = ±1, sin(k*π) = 0 → shapes are left/right of center
    cos_a = math.cos(target_orbit_angle)
    # If cos > 0: seeker is right, one is left. If cos < 0: reversed.
    # Either way, they're side by side horizontally.

    # ── Beat 4.1: Huddle (2460–2670) ──
    for f in range(2460, 2671):
        t = (f - 2460) / 210.0
        wx = seeker_world_positions.get(f, 0)

        if f < 2490:
            # Smooth 30-frame blend from orbit positions to clean side-by-side
            blend = ease_in_out_cubic((f - 2460) / 30.0)
            # Orbit-based positions at frame 2460
            orbit_sx = wx + half * cos_a
            orbit_sy = 0  # sin(k*π) ≈ 0
            orbit_ox = wx - half * cos_a
            orbit_oy = 0
            # Clean side-by-side target (seeker right, one left)
            target_sx = wx + half
            target_ox = wx - half
            sx = lerp(orbit_sx, target_sx, blend)
            ox = lerp(orbit_ox, target_ox, blend)
            sy = 0
            oy = 0
        else:
            sway_t = (f - 2490) / 180.0
            sway = 0.3 * math.sin(sway_t * 3 * 2 * math.pi)
            sx = wx + half
            ox = wx - half
            sy = sway
            oy = sway

        kf_loc(seeker, sx, sy, f)
        kf_loc(the_one, ox, oy, f)
        kf_rot_z(seeker, target_rotation, f)
        kf_rot_z(the_one, target_rotation, f)
        seeker_y_out[f] = sy

    apply_pulse(seeker, 2460, 2670, period=40, amplitude=0.06)
    apply_pulse(the_one, 2460, 2670, period=40, amplitude=0.06)

    for f in range(2460, 2671):
        t = (f - 2460) / 210.0
        em = lerp(2.0, 3.0, ease_in_out_cubic(t))
        kf_emission_strength(seeker_mat, em, f)
        kf_emission_strength(one_mat, em, f)

    # ── Beat 4.2: Accelerating Together (2670–2940) ──
    for f in range(2670, 2941):
        t = (f - 2670) / 270.0
        wx = seeker_world_positions.get(f, 0)
        sway = 0.2 * math.sin(t * 4 * 2 * math.pi)
        kf_loc(seeker, wx + half, sway, f)
        kf_loc(the_one, wx - half, sway, f)
        kf_rot_z(seeker, target_rotation, f)
        kf_rot_z(the_one, target_rotation, f)
        seeker_y_out[f] = sway

    apply_pulse(seeker, 2670, 2940, period=35, amplitude=0.04)
    apply_pulse(the_one, 2670, 2940, period=35, amplitude=0.04)

    for f in range(2670, 2941):
        kf_emission_strength(seeker_mat, 3.0, f)
        kf_emission_strength(one_mat, 3.0, f)

    # ── Trail squares (fading) ──
    trail_objects = []
    for spawn_f in range(2700, 2930, 10):
        wx = seeker_world_positions.get(spawn_f, 0)
        for ci, (cn, xo) in enumerate([("TS", half), ("TO", -half)]):
            sway = 0.2 * math.sin(((spawn_f - 2670) / 270.0) * 4 * 2 * math.pi)
            tmat = create_emission_material(f"Tr_{spawn_f}_{ci}M", color=(1,1,1,1), strength=0.5)
            bpy.ops.mesh.primitive_plane_add(size=SEEKER_SIZE * 0.6, location=(wx + xo, sway, -0.01))
            dot = bpy.context.active_object
            dot.name = f"Tr_{spawn_f}_{cn}"
            assign_material(dot, tmat)
            kf_scale(dot, 0.0, spawn_f - 1)
            kf_emission_strength(tmat, 0.0, spawn_f - 1)
            kf_scale(dot, 1.0, spawn_f)
            kf_emission_strength(tmat, 0.5, spawn_f)
            kf_scale(dot, 0.3, spawn_f + 40)
            kf_emission_strength(tmat, 0.0, spawn_f + 40)
            trail_objects.append(dot)

    # ── Beat 4.3: Into the Light (2940–3150) ──
    for f in range(2940, 3151):
        t = (f - 2940) / 210.0
        wx = seeker_world_positions.get(f, 0)
        sway = 0.1 * math.sin(t * 2 * math.pi)
        kf_loc(seeker, wx + half, sway, f)
        kf_loc(the_one, wx - half, sway, f)
        kf_rot_z(seeker, target_rotation, f)
        kf_rot_z(the_one, target_rotation, f)
        seeker_y_out[f] = sway
        em = lerp(3.0, 5.0, ease_in_out_cubic(t))
        kf_emission_strength(seeker_mat, em, f)
        kf_emission_strength(one_mat, em, f)

    apply_pulse(seeker, 2940, 3100, period=40, amplitude=0.04)
    apply_pulse(the_one, 2940, 3100, period=40, amplitude=0.04)

    # Glow overlay
    glow_mat = create_emission_material("GlowOverlayMat", color=(1,1,1,1), strength=0.0)
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0.3))
    glow = bpy.context.active_object
    glow.name = "GlowOverlay"
    assign_material(glow, glow_mat)
    kf_scale(glow, 0.0, 1)
    kf_scale(glow, 0.0, 3009)
    kf_scale(glow, 1.0, 3010)
    for f in range(3010, 3151):
        wx = seeker_world_positions.get(f, 0)
        glow.location = (wx, 0, 0.3)
        glow.keyframe_insert(data_path="location", frame=f)
    kf_emission_strength(glow_mat, 0.0, 3010)
    kf_emission_strength(glow_mat, 0.3, 3060)
    kf_emission_strength(glow_mat, 1.0, 3100)
    kf_emission_strength(glow_mat, 2.0, 3130)

    # Fade to black
    fade_mat = create_emission_material("FadeToBlackMat", color=(0,0,0,1), strength=0.0)
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
