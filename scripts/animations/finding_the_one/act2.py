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
    
    entry_start = 1400
    entry_end = 1850
    
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

        # Organic random drift logic
        drift_y = (0.5 * math.sin(t * 1.5 * math.pi)
                   + 0.4 * math.cos(t * 3.0 * math.pi)
                   + 0.3 * math.sin(t * 4.5 * math.pi))
        drift_x_wobble = 0.4 * math.sin(t * 2.8 * math.pi)
        
        # Y-Alignment: Force drift to approach 0 at end
        if t > 0.8:
            drift_y = lerp(drift_y, 0, (t-0.8)/0.2)

        # Rigid rotation (snapped) - Frame based
        # 12 snaps over t=0..1 means ~37 frames/snap. Let's start slow.
        rigid_rot = math.floor(t * 12) * (math.pi / 4)
        
        # Seeker mimics (starts midway)
        if t > 0.4:
            st = (t - 0.4) / 0.6
            # Slightly off-cadence mimicry
            seeker_rot = math.floor(st * 10) * (math.pi / 4) 
        else:
            seeker_rot = 0
            
        kf_loc(iso_tri, wx + tri_screen_x + drift_x_wobble, drift_y, f)
        kf_rot_z(iso_tri, rigid_rot, f)

        # Seeker notices very slowly
        seeker_y = lerp(0, 0.1, ease_in_out_cubic(min(t * 1.5, 1.0)))
        if t > 0.9: seeker_y = lerp(seeker_y, 0, (t-0.9)/0.1) # Align to 0
        seeker_y_out[f] = seeker_y
        kf_loc(seeker, wx, seeker_y, f)
        kf_rot_z(seeker, seeker_rot, f)

    apply_pulse(seeker, entry_start, entry_end, period=45, amplitude=0.03)

    # ── Beat 2.2: Stiff Interaction (1850–2120) ──
    seeker_spin = 0.0 # reset for smooth orbit? No, keep it jerky?
    # User said: "maintain the jerky rotation... entrance, pairing, departure"
    # So both should be jerky? Or just Triangle?
    # User said: "have both... rotate about their centres... maintain the jerky rotation... that the isosceles triangle comes in with throughout all of its screen time"
    # Implies Triangle = Jerky. Seeker = Mimics (so Jerky).
    
    # Let's use a global snap counter for both for Act 2.
    snap_frame_offset = 0

    # --- Circular Orbit (1850–2000) ---
    orbit_start = 1850
    orbit_end = 2000
    
    for f in range(orbit_start, orbit_end + 1):
        t = (f - orbit_start) / (orbit_end - orbit_start)
        wx = seeker_world_positions.get(f, 0)
        cx, cy = wx, 0

        radius = lerp(2.0, 1.5, ease_in_out_cubic(t))
        angle = t * 2.5 * math.pi

        kf_loc(iso_tri, cx + radius * math.cos(angle), cy + radius * math.sin(angle), f)
        kf_loc(seeker, cx + radius * math.cos(angle + math.pi), cy + radius * math.sin(angle + math.pi), f)
        seeker_y_out[f] = cy + radius * math.sin(angle + math.pi)

        # Jerky Rotation
        # Spin increases over time (angle increases)
        # Map angle to 45 deg snaps
        iso_rot = math.floor(angle / (math.pi/4)) * (math.pi / 4) + rigid_rot
        seeker_rot = math.floor((angle + math.pi) / (math.pi/4)) * (math.pi / 4)
        
        kf_rot_z(seeker, seeker_rot, f)
        kf_rot_z(iso_tri, iso_rot, f)

    # --- TEASE (2000–2050) ---
    last_orbit_angle = 2.5 * math.pi
    last_radius = 1.5
    tease_start = 2000
    tease_end = 2050
    
    last_iso_rot = iso_rot
    last_seeker_rot = seeker_rot
    
    for f in range(tease_start, tease_end + 1):
        t = (f - tease_start) / (tease_end - tease_start)
        wx = seeker_world_positions.get(f, 0)

        if t < 0.4:
            lt = t / 0.4
            angle = last_orbit_angle + lt * 0.4 * math.pi
            radius = lerp(last_radius, 0.6, ease_in_out_cubic(lt))
            cx = wx + 0.3
            cy = 0
            kf_loc(iso_tri, cx + radius * math.cos(angle), cy + radius * math.sin(angle), f)
            kf_loc(seeker, cx + radius * math.cos(angle + math.pi)*0.3, cy, f)
            seeker_y_out[f] = cy
            
            cur_angle_iso = last_orbit_angle + lt * 0.4 * math.pi
            iso_rot = math.floor(cur_angle_iso / (math.pi/4)) * (math.pi/4) + rigid_rot
            seeker_rot = math.floor((cur_angle_iso + math.pi) / (math.pi/4)) * (math.pi/4)

        else:
            lt = (t - 0.4) / 0.6
            gap = lerp(0.6, 0.15, ease_in_out_cubic(lt))
            kf_loc(iso_tri, wx + gap / 2 + 0.2, 0, f)
            kf_loc(seeker, wx - gap / 2 + 0.2, 0, f)
            seeker_y_out[f] = 0
            # Freeze rotation
            
        kf_rot_z(seeker, seeker_rot, f)
        kf_rot_z(iso_tri, iso_rot, f)

    apply_pulse(seeker, tease_start, tease_end, period=30, amplitude=0.04)

    # --- BONK & RECOIL (2050–2120) ---
    bonk_start = 2050
    bonk_end = 2080
    
    for f in range(bonk_start, bonk_end + 1):
        t = (f - bonk_start) / (bonk_end - bonk_start)
        wx = seeker_world_positions.get(f, 0)
        
        rot_offset = math.floor(t * 2) * (math.pi / 4) # 1 snap
        bump = 0.3 * math.sin(t * math.pi)
        
        kf_loc(iso_tri, wx + 0.5 + bump, bump * 0.5, f)
        recoil_y = -0.3 * ease_in_out_cubic(t)
        seeker_y_out[f] = recoil_y
        kf_loc(seeker, wx + recoil_y * 0.2, recoil_y, f)

        # Seeker stops syncing
        # Triangle snaps once
        kf_rot_z(seeker, seeker_rot, f)
        kf_rot_z(iso_tri, iso_rot + rot_offset, f)
        
    post_start = 2080
    post_end = 2120
    iso_rot_base = iso_rot + rot_offset
    
    for f in range(post_start, post_end + 1):
        t = (f - post_start) / (post_end - post_start)
        wx = seeker_world_positions.get(f, 0)
        
        radius = lerp(1.0, 2.5, ease_in_out_cubic(t)) 
        orbit_angle = t * 1.5 * math.pi
        
        tri_rel_x = radius * math.cos(orbit_angle) 
        tri_rel_y = radius * math.sin(orbit_angle)
        
        kf_loc(iso_tri, wx + tri_rel_x, tri_rel_y, f)
        
        # Consistent jerky spin
        cur_rot = iso_rot_base + math.floor(t * 3) * (math.pi / 4)
        kf_rot_z(iso_tri, cur_rot, f)

        seeker_y_out[f] = lerp(-0.3, -1.0, ease_in_out_cubic(t))
        kf_loc(seeker, wx, seeker_y_out[f], f)
        kf_rot_z(seeker, seeker_rot, f) # stuck

    # --- LEFT EXIT & FADE (2120–2400) ---
    # Sporadic surges
    exit_start = 2120
    exit_end = 2400
    last_rot = cur_rot
    
    for f in range(exit_start, exit_end + 1):
        t = (f - exit_start) / (exit_end - exit_start)
        wx = seeker_world_positions.get(f, 0)
        
        # Seeker sadness
        if t < 0.3:
             y = lerp(-1.0, -1.8, ease_in_out_cubic(t/0.3))
        else:
             y = -1.8
        seeker_y_out[f] = y
        kf_loc(seeker, wx, y, f)
        
        # Triangle Exit: Sporadic leftward
        base_offset = lerp(2.5, -20.0, math.pow(t, 2))
        
        # Surges (trying to come back right)
        surge = 2.0 * (1.0 - t) * math.sin(t * 4 * math.pi)
        if surge < 0: surge = 0
        
        offset = base_offset + surge
        
        kf_loc(iso_tri, wx + offset, 0, f)
        
        # Still jerky spinning
        snaps = math.floor(t * 5)
        kf_rot_z(iso_tri, last_rot + snaps * (math.pi / 4), f)

        if t > 0.8:
            kf_emission_strength(iso_tri_mat, lerp(2.0, 0.0, (t-0.8)/0.2), f)
        else:
            kf_emission_strength(iso_tri_mat, 2.0, f)

    # Park offscreen
    kf_loc(iso_tri, -60, 10, 2401)
    
    apply_pulse(seeker, exit_start, exit_end, period=55, amplitude=0.02)
    apply_sigh(seeker, 2200, 2250, depth=0.06)
