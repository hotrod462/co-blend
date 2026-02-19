"""
Finding the One — Act I: The Journey Begins (Frames 330–1400)

Changes:
  - Extended duration: Handles Gap (1200–1400).
  - Entry: Hesitant drift + Y-alignment + Excitement spin (780+).
  - Exit: Sporadic/emotional comeback attempts (surge pattern).
"""
import math
import random
from scripts.utils.animation import lerp, ease_in_out_cubic, ease_out_bounce
from scripts.animations.finding_the_one.config import (
    ACT1_START, ACT1_END, FRAME_END,
    SEEKER_SIZE, RIGHT_TRI_EMISSION,
)
from scripts.animations.finding_the_one.helpers import (
    kf_loc, kf_scale, kf_rot_z, kf_emission_strength,
    apply_pulse, apply_sigh, lerp_value,
)


def animate_act1(seeker, seeker_mat, right_tri, right_tri_mat,
                 the_one, one_mat,
                 seeker_world_positions, seeker_y_out, camera):

    # ── Beat 1.1: First Steps (330–450) ──
    for f in range(330, 451):
        t = (f - 330) / 120.0
        wx = seeker_world_positions.get(f, 0)
        if t < 0.33:
            y = lerp(0, 0.5, ease_in_out_cubic(t / 0.33))
        elif t < 0.67:
            y = lerp(0.5, -0.3, ease_in_out_cubic((t - 0.33) / 0.34))
        else:
            y = lerp(-0.3, 0.2, ease_in_out_cubic((t - 0.67) / 0.33))
        seeker_y_out[f] = y
        kf_loc(seeker, wx, y, f)
    apply_pulse(seeker, 330, 450, period=45, amplitude=0.03)

    # ── Beat 1.2: Wandering (450–630) ──
    y_wp = [(450, 0.2), (500, 1.5), (540, -0.5), (570, -1.5), (600, 0.5), (630, 0.0)]
    for i in range(len(y_wp) - 1):
        f0, y0 = y_wp[i]
        f1, y1 = y_wp[i + 1]
        for f in range(f0, f1 + 1):
            t = (f - f0) / max(f1 - f0, 1)
            y = lerp(y0, y1, ease_in_out_cubic(t))
            y += 0.15 * math.sin(f * 0.13) * math.cos(f * 0.07)
            wx = seeker_world_positions.get(f, 0)
            seeker_y_out[f] = y
            kf_loc(seeker, wx, y, f)
    apply_pulse(seeker, 450, 630, period=45, amplitude=0.03)

    # ── Beat 1.3: Right-Angle Triangle Encounter (630–1200) ──

    # --- ENTRY: Hesitant Drift + Excitement + Y-Align (630–950) ---
    random.seed(111)
    
    entry_start = 630
    entry_end = 950
    
    for f in range(entry_start, entry_end + 1):
        t = (f - entry_start) / (entry_end - entry_start)
        wx = seeker_world_positions.get(f, 0)

        # Hesitant X path
        if t < 0.3:
            lt = t / 0.3
            tri_screen_x = lerp(12, 6, ease_in_out_cubic(lt))
        elif t < 0.5:
            lt = (t - 0.3) / 0.2
            tri_screen_x = lerp(6, 5.5, lt) 
        elif t < 0.8:
            lt = (t - 0.5) / 0.3
            tri_screen_x = lerp(5.5, 3.0, ease_in_out_cubic(lt))
        else:
            lt = (t - 0.8) / 0.2
            tri_screen_x = lerp(3.0, 2.0, ease_in_out_cubic(lt))

        # Organic Y drift + Final Alignment
        raw_drift_y = (0.7 * math.sin(t * 1.5 * math.pi)
                       + 0.5 * math.cos(t * 2.5 * math.pi)
                       + 0.6 * math.sin(t * 3 * math.pi) * (1.0 if t < 0.3 else 0.3))

        # Seeker notices 
        seeker_y = lerp(0, 0.2, ease_in_out_cubic(min(t * 1.2, 1.0)))
        
        # Force Y alignment at end: Triangle drift -> Seeker Y (0.2 -> 0.0 finally)
        # Seeker Y should actually be 0 for orbit.
        # Let's drop seeker to 0 at end.
        if t > 0.8:
            seeker_y = lerp(0.2, 0.0, (t-0.8)/0.2)
            
        # Triangle Y align
        if t > 0.8:
             final_drift_y = lerp(raw_drift_y, 0.0, (t-0.8)/0.2)
        else:
             final_drift_y = raw_drift_y

        # Rotation Logic (Excitement from 780, ~t=0.47)
        if t < 0.47:
            tri_rot = t * 0.8 * math.pi
            seeker_rot = 0
        else:
            # Ramps up significantly
            excitement_t = (t - 0.47) / 0.53
            tri_rot = (0.47 * 0.8 * math.pi) + excitement_t * 3.0 * math.pi # fast spin
            
            # Seeker tries to mimic
            seeker_rot = excitement_t * 2.0 * math.pi

        kf_loc(right_tri, wx + tri_screen_x, final_drift_y, f)
        kf_rot_z(right_tri, tri_rot, f)

        seeker_y_out[f] = seeker_y
        kf_loc(seeker, wx, seeker_y, f)
        kf_rot_z(seeker, seeker_rot, f)


    # --- MUTUAL ORBIT (950–1080) ---
    seeker_spin = 2.0 * math.pi # continued from above
    tri_spin = (0.47 * 0.8 * math.pi) + 3.0 * math.pi # approx 3.4 pi
    orbit_start = 950
    orbit_end = 1080
    
    for f in range(orbit_start, orbit_end + 1):
        t = (f - orbit_start) / (orbit_end - orbit_start)
        wx = seeker_world_positions.get(f, 0)
        cx = wx + 0.5
        cy = 0

        radius = lerp(2.0, 1.2, ease_in_out_cubic(t))
        angle = t * 3.0 * math.pi

        kf_loc(right_tri, cx + radius * math.cos(angle), cy + radius * math.sin(angle), f)
        kf_loc(seeker, cx + radius * math.cos(angle + math.pi), cy + radius * math.sin(angle + math.pi), f)
        seeker_y_out[f] = cy + radius * math.sin(angle + math.pi)

        seeker_spin += 0.02
        tri_spin += 0.06
        kf_rot_z(seeker, seeker_spin, f)
        kf_rot_z(right_tri, tri_spin, f)

    # --- TEASE & BONK (1080–1120) ---
    last_orbit_angle = 3.0 * math.pi
    last_radius = 1.2
    tease_start = 1080
    tease_end = 1120
    
    for f in range(tease_start, tease_end + 1):
        t = (f - tease_start) / (tease_end - tease_start)
        wx = seeker_world_positions.get(f, 0)

        seeker_spin += lerp(0.02, 0.005, t)
        tri_spin += lerp(0.06, 0.02, t)

        if t < 0.5:
            lt = t / 0.5
            angle = last_orbit_angle + lt * 0.3 * math.pi
            radius = lerp(last_radius, 0.4, ease_in_out_cubic(lt))
            cx = wx + 0.3
            cy = 0
            tri_x = cx + radius * math.cos(angle)
            tri_y = cy + radius * math.sin(angle)
            seeker_x = cx + radius * math.cos(angle + math.pi)
            seeker_y = cy + radius * math.sin(angle + math.pi)
        elif t < 0.8:
            lt = (t - 0.5) / 0.3
            gap = lerp(0.4, 0.2, ease_in_out_cubic(lt))
            tri_x = wx + gap / 2 + 0.35
            tri_y = 0
            seeker_x = wx - gap / 2 + 0.35
            seeker_y = 0
        else:
            lt = (t - 0.8) / 0.2
            tri_x = wx + 0.55 + 0.5 * ease_in_out_cubic(lt)
            tri_y = 0.3 * ease_in_out_cubic(lt)
            seeker_x = wx
            seeker_y = -0.15 * ease_in_out_cubic(lt)
            tri_spin += 0.08 * lt

        kf_loc(right_tri, tri_x, tri_y, f)
        kf_loc(seeker, seeker_x, seeker_y, f)
        kf_rot_z(seeker, seeker_spin, f)
        kf_rot_z(right_tri, tri_spin, f)
        seeker_y_out[f] = seeker_y

    # --- RECOIL & SPORADIC EXIT (1120–1250) ---
    # Extended to 1250 for slower emotional exit.
    recoil_start = 1120
    recoil_end = 1250 
    
    for f in range(recoil_start, recoil_end + 1):
        t = (f - recoil_start) / (recoil_end - recoil_start)
        wx = seeker_world_positions.get(f, 0)
        
        # Seeker Recoil (first 30%)
        if t < 0.3:
             rt = t / 0.3
             recoil_y = lerp(-0.15, 1.2, ease_out_bounce(rt))
             seeker_y_out[f] = recoil_y
             kf_loc(seeker, wx, recoil_y, f)
             seeker_spin = lerp(seeker_spin, 0, rt)
        else:
             # Hover/Recover
             seeker_y_out[f] = 1.2
             kf_loc(seeker, wx, 1.2, f)
             kf_rot_z(seeker, 0, f)
        
        # Triangle Exit: Sporadic comeback Logic
        # drift: +1.0 -> -15.0
        base_offset = lerp(1.0, -15.0, math.pow(t, 1.5))
        
        # Comeback surges: Dampening sine wave
        # Only surge right (positive)
        surge = 2.0 * (1.0 - t) * math.sin(t * 5 * math.pi)
        if surge < 0: surge = 0 # no extra left push, only hold back
        
        # Add surge to offset (holding it back from leaving)
        offset = base_offset + surge
        
        # Y drift: slowly downward
        tri_y = 0.5 - t * 2.0
        
        kf_loc(right_tri, wx + offset, tri_y, f)
        tri_spin += 0.05 * (1.0 - t) # slowing spin
        kf_rot_z(right_tri, tri_spin, f)
        
        # Fade: Start later (t > 0.7)
        if t > 0.7:
             kf_emission_strength(right_tri_mat, lerp(2.0, 0.0, (t-0.7)/0.3), f)
        else:
             kf_emission_strength(right_tri_mat, 2.0, f)
             
    # Park
    kf_loc(right_tri, -60, 10, 1251)


    # ── Beat 1.5: The Gap / Searching Again (1250–1400) ──
    # Seeker is alone, bouncing around.
    # Start at Y=1.2. End at Y=0 (Act 2 start).
    gap_start = 1250
    gap_end = 1400
    
    # Waypoints for wandering
    # 1.2 -> 0.0 -> -0.5 -> 0.0
    for f in range(gap_start, gap_end + 1):
        t = (f - gap_start) / (gap_end - gap_start)
        wx = seeker_world_positions.get(f, 0)
        
        if t < 0.3:
            y = lerp(1.2, 0.0, ease_in_out_cubic(t/0.3))
        elif t < 0.7:
            y = lerp(0.0, -0.5, ease_in_out_cubic((t-0.3)/0.4))
        else:
            y = lerp(-0.5, 0.0, ease_in_out_cubic((t-0.7)/0.3))
            
        # Add wandering noise
        noise = 0.1 * math.sin(f * 0.1)
        y += noise
        
        seeker_y_out[f] = y
        kf_loc(seeker, wx, y, f)
        
    apply_pulse(seeker, gap_start, gap_end, period=60, amplitude=0.03)


    # Convert Act 1 range for The One to hidden
    for f in range(1, ACT1_END + 1):
        kf_loc(the_one, -60, 0, f)
