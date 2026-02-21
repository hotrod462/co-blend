"""
Finding the One — Act II: False Hopes (Frames 1400–2400)

Changes:
  - Start shifted to 1400 (after gap).
  - Seeker mimics jerky rotation during entry.
  - Isosceles rotation is ALWAYS jerky (snapped).
  - Exit is sporadic/emotional.
  - Y-alignment at end of entry.
"""
import math
import random
from scripts.utils.animation import lerp, ease_in_out_cubic
from scripts.animations.finding_the_one.config import (
    ACT2_START, ACT2_END, FRAME_END,
    ISO_TRI_EMISSION,
)
from scripts.animations.finding_the_one.helpers import (
    kf_loc, kf_scale, kf_rot_z, kf_emission_strength,
    apply_pulse, apply_sigh, lerp_value,
)


def animate_act2(seeker, seeker_mat, iso_tri, iso_tri_mat,
                 seeker_world_positions, seeker_y_out, camera):

    # ── Beat 2.1: Isosceles Entrance — Very Hesitant (1400–1850) ──
    # 450 frames. Long, drawn out approach with pauses.
    random.seed(222)
    
    entry_start = 1500
    entry_end = 1950
    
    for f in range(entry_start, entry_end + 1):
        t = (f - entry_start) / (entry_end - entry_start)
        wx = seeker_world_positions.get(f, 0)
        
        # Multi-stage hesitant path
        if t < 0.2:
            lt = t / 0.2
            tri_screen_x = lerp(12, 9, ease_in_out_cubic(lt))
        elif t < 0.4:
            lt = (t - 0.2) / 0.2
            tri_screen_x = lerp(9, 9.5, ease_in_out_cubic(lt)) # Retreat
        elif t < 0.6:
            lt = (t - 0.4) / 0.2
            tri_screen_x = lerp(9.5, 5.0, ease_in_out_cubic(lt))
        elif t < 0.8:
            lt = (t - 0.6) / 0.2
            tri_screen_x = lerp(5.0, 5.2, ease_in_out_cubic(lt)) # Hesitate
        else:
            lt = (t - 0.8) / 0.2
            tri_screen_x = lerp(5.2, 2.0, ease_in_out_cubic(lt))

        # Seeker Pop Notice around frame 1500 (t≈0.22)
        seeker_pop_scale = 1.0
        seeker_pop_em = 2.0
        if 1600 <= f <= 1680:
            pt = (f - 1600) / 80.0
            seeker_pop_scale = 1.0 + 0.3 * math.sin(pt * math.pi)
            seeker_pop_em = 2.0 + 1.2 * math.sin(pt * math.pi)
        
        kf_scale(seeker, seeker_pop_scale, f)
        kf_emission_strength(seeker_mat, seeker_pop_em, f)

        # Organic random drift logic
        drift_y = (0.5 * math.sin(t * 1.5 * math.pi)
                   + 0.4 * math.cos(t * 3.0 * math.pi)
                   + 0.3 * math.sin(t * 4.5 * math.pi))
        drift_x_wobble = 0.4 * math.sin(t * 2.8 * math.pi)
        
        if t > 0.8:
            drift_y = lerp(drift_y, 0, (t-0.8)/0.2)

        rigid_rot = math.floor(t * 12) * (math.pi / 4)
        if t > 0.4:
            st = (t - 0.4) / 0.6
            seeker_rot = math.floor(st * 10) * (math.pi / 4) 
        else:
            seeker_rot = 0
            
        kf_loc(iso_tri, wx + tri_screen_x + drift_x_wobble, drift_y, f)
        kf_rot_z(iso_tri, rigid_rot, f)

        seeker_y = lerp(0, 0.1, ease_in_out_cubic(min(t * 1.5, 1.0)))
        if t > 0.9: seeker_y = lerp(seeker_y, 0, (t-0.9)/0.1) 
        seeker_y_out[f] = seeker_y
        kf_loc(seeker, wx, seeker_y, f)
        kf_rot_z(seeker, seeker_rot, f)

    apply_pulse(seeker, entry_start, entry_end, period=45, amplitude=0.03)

    # ── Beat 2.2: Stiff Interaction (1850–2120) ──
    orbit_start = 1950
    orbit_end = 2100
    
    for f in range(orbit_start, orbit_end + 1):
        t = (f - orbit_start) / (orbit_end - orbit_start)
        wx = seeker_world_positions.get(f, 0)
        cx = wx + lerp(1.0, 0, ease_in_out_cubic(t))
        cy = 0

        radius = lerp(1.0, 0.8, ease_in_out_cubic(t))
        angle = t * 2.5 * math.pi

        kf_loc(iso_tri, cx + radius * math.cos(angle), cy + radius * math.sin(angle), f)
        kf_loc(seeker, cx + radius * math.cos(angle + math.pi), cy + radius * math.sin(angle + math.pi), f)
        seeker_y_out[f] = cy + radius * math.sin(angle + math.pi)

        iso_rot = math.floor(angle / (math.pi/4)) * (math.pi / 4) + rigid_rot
        seeker_rot = math.floor((angle + math.pi) / (math.pi/4)) * (math.pi / 4)
        
        kf_rot_z(seeker, seeker_rot, f)
        kf_rot_z(iso_tri, iso_rot, f)
        
        # Emission Pulse
        pulse_period = lerp(50, 20, t)
        phase = (f - orbit_start) / pulse_period * 2 * math.pi
        pulse_em = 2.0 + 0.6 * (0.5 + 0.5 * math.sin(phase))
        kf_emission_strength(seeker_mat, pulse_em, f)
        kf_emission_strength(iso_tri_mat, pulse_em, f)

    # --- TEASE (2100–2150) ---
    # Orbit ended at: angle=2.5*pi, radius=0.8, cx=wx+0
    # cos(2.5*pi)=0, sin(2.5*pi)=-1
    # So iso was at (cx, -0.8), seeker at (cx, +0.8)
    tease_start = 2100
    tease_end = 2150
    
    for f in range(tease_start, tease_end + 1):
        t = (f - tease_start) / (tease_end - tease_start)
        wx = seeker_world_positions.get(f, 0)

        if t < 0.4:
            lt = t / 0.4
            # Continue from orbit end: cx drifts from 0 offset toward 0.2
            cx = wx + lerp(0, 0.2, ease_in_out_cubic(lt))
            cy = 0
            angle = 2.5 * math.pi + lt * 0.4 * math.pi
            radius = lerp(0.8, 0.6, ease_in_out_cubic(lt))
            kf_loc(iso_tri, cx + radius * math.cos(angle), cy + radius * math.sin(angle), f)
            kf_loc(seeker, cx + radius * math.cos(angle + math.pi), cy + radius * math.sin(angle + math.pi), f)
            seeker_y_out[f] = cy + radius * math.sin(angle + math.pi)
            
            iso_rot = math.floor(angle / (math.pi/4)) * (math.pi/4) + rigid_rot
            seeker_rot = math.floor((angle + math.pi) / (math.pi/4)) * (math.pi/4)
        else:
            lt = (t - 0.4) / 0.6
            # Compute positions at t=0.4 boundary for continuity
            angle_04 = 2.5 * math.pi + 0.4 * 0.4 * math.pi  # = 2.66*pi
            r_04 = 0.6
            cx_04 = wx + 0.2
            iso_start_x = cx_04 + r_04 * math.cos(angle_04)
            iso_start_y = r_04 * math.sin(angle_04)
            seeker_start_x = cx_04 + r_04 * math.cos(angle_04 + math.pi)
            seeker_start_y = r_04 * math.sin(angle_04 + math.pi)
            
            gap = lerp(0.6, 0.15, ease_in_out_cubic(lt))
            target_iso_x = wx + gap / 2 + 0.2
            target_seeker_x = wx - gap / 2 + 0.2
            kf_loc(iso_tri, lerp(iso_start_x, target_iso_x, ease_in_out_cubic(lt)),
                   lerp(iso_start_y, 0, ease_in_out_cubic(lt)), f)
            kf_loc(seeker, lerp(seeker_start_x, target_seeker_x, ease_in_out_cubic(lt)),
                   lerp(seeker_start_y, 0, ease_in_out_cubic(lt)), f)
            seeker_y_out[f] = lerp(seeker_start_y, 0, ease_in_out_cubic(lt))
            
        kf_rot_z(seeker, seeker_rot, f)
        kf_rot_z(iso_tri, iso_rot, f)
        
        # Pulse during tease
        pulse_em = 2.0 + 0.8 * (0.5 + 0.5 * math.sin(f * 0.5))
        kf_emission_strength(seeker_mat, pulse_em, f)
        kf_emission_strength(iso_tri_mat, pulse_em, f)

    apply_pulse(seeker, tease_start, tease_end, period=30, amplitude=0.04)

    # --- BONK & RECOIL (2150–2220) ---
    bonk_start = 2150
    bonk_end = 2180
    
    # End of Tease positions for continuity:
    # gap = 0.15 at t=1.0 of tease
    # iso_x_start = wx + 0.275, iso_y_start = 0
    # seeker_x_start = wx + 0.125, seeker_y_start = 0
    
    for f in range(bonk_start, bonk_end + 1):
        t = (f - bonk_start) / (bonk_end - bonk_start)
        wx = seeker_world_positions.get(f, 0)
        
        rot_offset = math.floor(t * 2) * (math.pi / 4)
        bump = 0.3 * math.sin(t * math.pi)
        
        # Start from end of tease exactly, then apply bump
        iso_x = wx + 0.275 + bump * 0.5
        iso_y = bump * 0.5
        kf_loc(iso_tri, iso_x, iso_y, f)
        
        # Seeker recoils backward
        recoil_y = -0.3 * ease_in_out_cubic(t)
        seeker_y_out[f] = recoil_y
        seeker_x = wx + 0.125 + recoil_y * 0.2
        kf_loc(seeker, seeker_x, recoil_y, f)

        kf_rot_z(seeker, seeker_rot, f)
        kf_rot_z(iso_tri, iso_rot + rot_offset, f)
        
    post_start = 2180
    post_end = 2220
    iso_rot_base = iso_rot + rot_offset
    
    for f in range(post_start, post_end + 1):
        t = (f - post_start) / (post_end - post_start)
        wx = seeker_world_positions.get(f, 0)
        
        # Continuity: At end of bonk (t=1.0), iso was at wx + 0.275, 0 (since bump=0)
        # We need to transition from that to the orbit path.
        # Let's lerp the center to wx, and radius from 0.275 to 2.5
        # The angle starts at 0 (since it was at +x, 0) and goes to 3.0*pi
        radius = lerp(0.275, 2.5, ease_in_out_cubic(t))
        orbit_angle = t * 3.0 * math.pi
        
        cx = wx
        cy = 0
        
        tri_rel_x = radius * math.cos(orbit_angle) 
        tri_rel_y = radius * math.sin(orbit_angle)
        
        kf_loc(iso_tri, cx + tri_rel_x, cy + tri_rel_y, f)
        
        cur_rot = iso_rot_base + math.floor(t * 6) * (math.pi / 4)
        kf_rot_z(iso_tri, cur_rot, f)

        # Continuity for seeker: end of bonk seeker_y was -0.3, seeker_x was wx + 0.125 - 0.06 = wx + 0.065
        seeker_y = lerp(-0.3, -1.0, ease_in_out_cubic(t))
        seeker_y_out[f] = seeker_y
        seeker_x = lerp(wx + 0.065, wx, ease_in_out_cubic(t))
        kf_loc(seeker, seeker_x, seeker_y, f)
        kf_rot_z(seeker, seeker_rot, f)

    # --- LEFT EXIT & FADE (2220–2500) ---
    exit_start = 2220
    exit_end = 2500
    last_rot = cur_rot
    
    for f in range(exit_start, exit_end + 1):
        t = (f - exit_start) / (exit_end - exit_start)
        wx = seeker_world_positions.get(f, 0)
        
        # Seeker Depression: Deepening sine wave bobbing + dimming
        base_y_trans = lerp(-1.0, -1.8, ease_in_out_cubic(min(t / 0.3, 1.0)))
        bob_amplitude = lerp(0.3, 2.0, t)
        y = base_y_trans - bob_amplitude * abs(math.sin(t * 6 * math.pi))
        
        seeker_y_out[f] = y
        kf_loc(seeker, wx, y, f)
        
        # Reset rotation to 0 gradually
        if t < 0.2:
            st = t / 0.2
            kf_rot_z(seeker, lerp(seeker_rot, 0, ease_in_out_cubic(st)), f)
        else:
            kf_rot_z(seeker, 0, f)
            
        # Dimming seeker brightness
        seeker_em = lerp(2.0, 0.4, t)
        kf_emission_strength(seeker_mat, seeker_em, f)
        
        # Triangle Exit: Sporadic leftward
        base_offset = lerp(-radius, -20.0, math.pow(t, 2)) # Negative radius prevents teleport
        surge = 2.5 * (1.0 - t) * math.sin(t * 5 * math.pi)
        if surge < 0: surge = 0
        offset = base_offset + surge
        
        # Bouncing exit
        tri_y = tri_rel_y * (1.0 - t) + 1.2 * math.sin(t * 8 * math.pi)
        kf_loc(iso_tri, wx + offset, tri_y, f)
        
        snaps = math.floor(t * 8)
        kf_rot_z(iso_tri, last_rot + snaps * (math.pi / 4), f)

        if t > 0.8:
            kf_emission_strength(iso_tri_mat, lerp(2.0, 0.0, (t-0.8)/0.2), f)
        else:
            kf_emission_strength(iso_tri_mat, 2.0, f)

    # Ghost: Isosceles lingers as faint ghost at left edge
    # Fades 0.12→0 over ~150 frames, disappears right as The One appears
    ghost_start = 2501
    ghost_end = 2650  # Clean handoff: ghost fades as The One enters
    for f in range(ghost_start, ghost_end + 1):
        gt = (f - ghost_start) / (ghost_end - ghost_start)
        wx = seeker_world_positions.get(f, 0)
        kf_loc(iso_tri, wx - 11, -0.5, f)
        kf_emission_strength(iso_tri_mat, lerp(0.12, 0.0, ease_in_out_cubic(gt)), f)
    kf_loc(iso_tri, -60, 10, ghost_end + 1)
    kf_emission_strength(iso_tri_mat, 0.0, ghost_end + 1)
    
    apply_pulse(seeker, exit_start, exit_end, period=55, amplitude=0.02)
    apply_sigh(seeker, 2300, 2350, depth=0.06)
