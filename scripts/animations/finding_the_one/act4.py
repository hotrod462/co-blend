"""
Finding the One — Act IV: Union (Frames 3250–3750)
Clean transition from Act 3's locked angle.
Timings updated for extended timeline (Gap phase added previously).
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

    start = ACT4_START
    beat1_end = start + 120
    beat2_end = start + 300
    end = ACT4_END

    # Determine Act 4 positions
    cos_a = math.cos(target_orbit_angle)

    # ── Beat 4.1: Huddle (start–beat1_end) ──
    for f in range(start, beat1_end + 1):
        t = (f - start) / 120.0
        wx = seeker_world_positions.get(f, 0)
        rel_f = f - start

        if rel_f < 30:
            blend = ease_in_out_cubic(rel_f / 30.0)
            orbit_sx = wx + half * cos_a
            orbit_ox = wx - half * cos_a
            # Target: Side-by-side
            sx = lerp(orbit_sx, wx + half, blend)
            ox = lerp(orbit_ox, wx - half, blend)
            sy = 0
            oy = 0
        else:
            sway_t = (rel_f - 30) / 90.0
            sway = 0.3 * math.sin(sway_t * 6 * math.pi)
            sx = wx + half
            ox = wx - half
            sy = sway
            oy = sway

        kf_loc(seeker, sx, sy, f)
        kf_loc(the_one, ox, oy, f)
        kf_rot_z(seeker, target_rotation, f)
        kf_rot_z(the_one, target_rotation, f)
        seeker_y_out[f] = sy
        
        em = lerp(2.0, 3.0, ease_in_out_cubic(t))
        kf_emission_strength(seeker_mat, em, f)
        kf_emission_strength(one_mat, em, f)

    apply_pulse(seeker, start, beat1_end, period=40, amplitude=0.06)
    apply_pulse(the_one, start, beat1_end, period=40, amplitude=0.06)

    # ── Beat 4.2: Accelerating Together (beat1_end–beat2_end) ──
    for f in range(beat1_end, beat2_end + 1):
        t = (f - beat1_end) / 180.0
        wx = seeker_world_positions.get(f, 0)
        sway = 0.2 * math.sin(t * 8 * math.pi)
        
        kf_loc(seeker, wx + half, sway, f)
        kf_loc(the_one, wx - half, sway, f)
        kf_rot_z(seeker, target_rotation, f)
        kf_rot_z(the_one, target_rotation, f)
        seeker_y_out[f] = sway
        
        kf_emission_strength(seeker_mat, 3.0, f)
        kf_emission_strength(one_mat, 3.0, f)

    apply_pulse(seeker, beat1_end, beat2_end, period=35, amplitude=0.04)
    apply_pulse(the_one, beat1_end, beat2_end, period=35, amplitude=0.04)

    # ── Trail squares (during Accel) ──
    trail_objects = []
    spawn_start = beat1_end + 20
    spawn_end = beat2_end - 10
    
    for spawn_f in range(spawn_start, spawn_end, 10):
        wx = seeker_world_positions.get(spawn_f, 0)
        for ci, (cn, xo) in enumerate([("TS", half), ("TO", -half)]):
            sway = 0.2 * math.sin(((spawn_f - beat1_end) / 180.0) * 8 * math.pi)
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

    # ── Beat 4.3: Into the Light (beat2_end–end) ──
    for f in range(beat2_end, end + 1):
        t = (f - beat2_end) / (end - beat2_end)
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

    apply_pulse(seeker, beat2_end, end, period=40, amplitude=0.04)
    apply_pulse(the_one, beat2_end, end, period=40, amplitude=0.04)

    # Glow overlay
    glow_mat = create_emission_material("GlowOverlayMat", color=(1,1,1,1), strength=0.0)
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0.3))
    glow = bpy.context.active_object
    glow.name = "GlowOverlay"
    assign_material(glow, glow_mat)
    
    glow_start = beat2_end + 40
    glow_mid = end - 50
    glow_peak = end - 20
    
    kf_scale(glow, 0.0, 1)
    kf_scale(glow, 0.0, glow_start - 1)
    kf_scale(glow, 1.0, glow_start)
    
    for f in range(glow_start, end + 1):
        wx = seeker_world_positions.get(f, 0)
        glow.location = (wx, 0, 0.3)
        glow.keyframe_insert(data_path="location", frame=f)
        
    kf_emission_strength(glow_mat, 0.0, glow_start)
    kf_emission_strength(glow_mat, 0.3, glow_mid)
    kf_emission_strength(glow_mat, 1.0, glow_peak)
    kf_emission_strength(glow_mat, 2.0, end)

    # Fade to black
    fade_mat = create_emission_material("FadeToBlackMat", color=(0,0,0,1), strength=0.0)
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0.5))
    fade = bpy.context.active_object
    fade.name = "FadeToBlack"
    assign_material(fade, fade_mat)
    
    fade_start = end - 20
    
    kf_scale(fade, 0.0, 1)
    kf_scale(fade, 0.0, fade_start - 1)
    kf_scale(fade, 1.0, fade_start)
    
    for f in range(fade_start, end + 1):
        wx = seeker_world_positions.get(f, 0)
        fade.location = (wx, 0, 0.5)
        fade.keyframe_insert(data_path="location", frame=f)
        
    kf_emission_strength(fade_mat, 0.0, fade_start)
    kf_emission_strength(fade_mat, 3.0, end)

    return trail_objects
