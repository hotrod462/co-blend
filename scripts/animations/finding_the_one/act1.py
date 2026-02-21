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
                 seeker_world_positions, seeker_y_out, camera,
                 bg_pairing_1=None):

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
    y_wp = [(450, 0.2), (500, 1.5), (540, -0.5), (570, -1.5), (600, 0.5), (630, 0.3)]
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

        # Hesitant X path - ends at 2.5 to match orbit
        if t < 0.3:
            lt = t / 0.3
            tri_screen_x = lerp(12, 6, ease_in_out_cubic(lt))
        elif t < 0.5:
            lt = (t - 0.3) / 0.2
            tri_screen_x = lerp(6, 5.5, lt) 
        elif t < 0.8:
            lt = (t - 0.5) / 0.3
            tri_screen_x = lerp(5.5, 3.5, ease_in_out_cubic(lt))
        else:
            lt = (t - 0.8) / 0.2
            tri_screen_x = lerp(3.5, 2.5, ease_in_out_cubic(lt))

        # Organic Y drift + Final Alignment
        raw_drift_y = (0.7 * math.sin(t * 1.5 * math.pi)
                       + 0.5 * math.cos(t * 2.5 * math.pi)
                       + 0.6 * math.sin(t * 3 * math.pi) * (1.0 if t < 0.3 else 0.3))

        # Seeker notices - reaction pop
        # Notice around f=750 (t=0.375)
        seeker_pop_scale = 1.0
        seeker_pop_em = 2.0
        if 750 <= f <= 820:
            pt = (f - 750) / 70.0
            seeker_pop_scale = 1.0 + 0.3 * math.sin(pt * math.pi)
            seeker_pop_em = 2.0 + 1.5 * math.sin(pt * math.pi)
        
        kf_scale(seeker, seeker_pop_scale, f)
        kf_emission_strength(seeker_mat, seeker_pop_em, f)

        # Seeker Y: Gentle wandering instead of sitting still
        seeker_y = lerp(0.3, 0.2, ease_in_out_cubic(min(t * 1.2, 1.0)))
        seeker_y += 0.15 * math.sin(f * 0.13) * math.cos(f * 0.07)
        if t > 0.8: seeker_y = lerp(seeker_y, 0.0, (t-0.8)/0.2)
        
        if t > 0.8: final_drift_y = lerp(raw_drift_y, 0.0, (t-0.8)/0.2)
        else: final_drift_y = raw_drift_y

        # Rotation Logic
        if t < 0.40:
            # Calm approach
            tri_rot = t * 0.8 * math.pi
            seeker_rot = 0
        elif t < 0.53:
            # Triangle excitement burst — fast spin about its own axis
            burst_t = (t - 0.40) / 0.13
            tri_rot = (0.40 * 0.8 * math.pi) + burst_t * 6.0 * math.pi
            seeker_rot = 0
        elif t < 0.65:
            # Seeker acknowledges AFTER triangle burst
            ack_t = (t - 0.53) / 0.12
            tri_rot = (0.40 * 0.8 * math.pi) + 6.0 * math.pi
            seeker_rot = ack_t * 2.5 * math.pi
        else:
            # Mutual excitement — seeker reciprocates
            excitement_t = (t - 0.65) / 0.35
            tri_rot = (0.40 * 0.8 * math.pi) + 6.0 * math.pi + excitement_t * 2.0 * math.pi
            seeker_rot = 2.5 * math.pi + excitement_t * 2.0 * math.pi

        if f == entry_end:
            final_seeker_rot = seeker_rot
            final_tri_rot = tri_rot

        kf_loc(right_tri, wx + tri_screen_x, final_drift_y, f)
        kf_rot_z(right_tri, tri_rot, f)

        seeker_y_out[f] = seeker_y
        kf_loc(seeker, wx, seeker_y, f)
        kf_rot_z(seeker, seeker_rot, f)


    # --- MUTUAL ORBIT (950–1080) ---
    seeker_spin = final_seeker_rot
    tri_spin = final_tri_rot
    orbit_start = 950
    orbit_end = 1080
    
    for f in range(orbit_start, orbit_end + 1):
        t = (f - orbit_start) / (orbit_end - orbit_start)
        wx = seeker_world_positions.get(f, 0)
        cx = wx + lerp(1.25, 0.5, ease_in_out_cubic(t))
        cy = 0

        radius = lerp(1.25, 1.2, ease_in_out_cubic(t))
        # Varied revolution speed (wobbly orbit)
        angle = t * 3.2 * math.pi + 0.4 * math.sin(t * 2 * math.pi)

        kf_loc(right_tri, cx + radius * math.cos(angle), cy + radius * math.sin(angle), f)
        kf_loc(seeker, cx + radius * math.cos(angle + math.pi), cy + radius * math.sin(angle + math.pi), f)
        seeker_y_out[f] = cy + radius * math.sin(angle + math.pi)

        # Slower and varied axial spin
        s_step = 0.07 * (1.0 + 0.5 * math.sin(t * 3 * math.pi))
        t_step = 0.11 * (1.0 + 0.5 * math.cos(t * 3 * math.pi))
        seeker_spin += s_step
        tri_spin += t_step
        kf_rot_z(seeker, seeker_spin, f)
        kf_rot_z(right_tri, tri_spin, f)
        
        # Emission Pulse: Speeds up as they get closer (radius smaller)
        pulse_period = lerp(60, 15, t)
        phase = (f - orbit_start) / pulse_period * 2 * math.pi
        pulse_em = 2.0 + 0.8 * (0.5 + 0.5 * math.sin(phase))
        kf_emission_strength(seeker_mat, pulse_em, f)
        kf_emission_strength(right_tri_mat, pulse_em, f)

        # Store angle for tease phase continuity
        if f == orbit_end:
            final_orbit_angle = angle
            final_orbit_radius = radius
            final_orbit_cx_offset = cx - wx

    # --- TEASE & BONK (1080–1120) ---
    # Compute exact positions at orbit end (f=1080) to prevent teleportation.
    # At orbit end: angle=3*pi, radius=1.2, cx=wx_1080+0.5
    tease_start = 1080
    tease_end = 1120
    
    for f in range(tease_start, tease_end + 1):
        t = (f - tease_start) / (tease_end - tease_start)
        wx = seeker_world_positions.get(f, 0)
        
        # Use stored values from orbit end for perfect continuity
        orbit_cx = wx + final_orbit_cx_offset

        seeker_spin += lerp(0.25, 0.10, t)
        tri_spin += lerp(0.35, 0.15, t)

        if t < 0.5:
            lt = t / 0.5
            # Continue orbit: angle advances slightly, radius shrinks toward contact
            angle = final_orbit_angle + lt * 0.3 * math.pi
            radius = lerp(final_orbit_radius, 0.4, ease_in_out_cubic(lt))
            # Smoothly shift cx from orbit_cx toward 0.3
            cx = wx + lerp(final_orbit_cx_offset, 0.3, ease_in_out_cubic(lt))
            cy = 0
            tri_x = cx + radius * math.cos(angle)
            tri_y = cy + radius * math.sin(angle)
            seeker_x = cx + radius * math.cos(angle + math.pi)
            seeker_y = cy + radius * math.sin(angle + math.pi)
        elif t < 0.8:
            lt = (t - 0.5) / 0.3
            # Compute positions at t=0.5 boundary for continuity
            # final_orbit_angle + 1.0 * 0.3 * pi correctly uses the actual orbital legacy
            angle_05 = final_orbit_angle + 0.3 * math.pi
            r_05 = 0.4
            cx_05 = wx + 0.3
            tri_start_x = cx_05 + r_05 * math.cos(angle_05)
            tri_start_y = r_05 * math.sin(angle_05)
            seeker_start_x = cx_05 + r_05 * math.cos(angle_05 + math.pi)
            seeker_start_y = r_05 * math.sin(angle_05 + math.pi)
            
            target_tri_x = wx - 0.2
            target_seeker_x = wx + 0.2
            tri_x = lerp(tri_start_x, target_tri_x, ease_in_out_cubic(lt))
            tri_y = lerp(tri_start_y, 0, ease_in_out_cubic(lt))
            seeker_x = lerp(seeker_start_x, target_seeker_x, ease_in_out_cubic(lt))
            seeker_y = lerp(seeker_start_y, 0, ease_in_out_cubic(lt))
        else:
            lt = (t - 0.8) / 0.2
            tri_x = wx - 0.2 - 0.85 * ease_in_out_cubic(lt)
            tri_y = 0.3 * ease_in_out_cubic(lt)
            seeker_x = lerp(wx + 0.2, wx, ease_in_out_cubic(lt))
            seeker_y = -0.15 * ease_in_out_cubic(lt)
            tri_spin += 0.08 * lt

        kf_loc(right_tri, tri_x, tri_y, f)
        kf_loc(seeker, seeker_x, seeker_y, f)
        kf_rot_z(seeker, seeker_spin, f)
        kf_rot_z(right_tri, tri_spin, f)
        seeker_y_out[f] = seeker_y
        
        # Pulse during tease
        pulse_em = 2.0 + 1.0 * (0.5 + 0.5 * math.sin(f * 0.4))
        kf_emission_strength(seeker_mat, pulse_em, f)
        kf_emission_strength(right_tri_mat, pulse_em, f)

    # --- RECOIL & SPORADIC EXIT (1120–1520) ---
    # Extended to 400 frames (~13s) for prolonged emotional incompatibility.
    recoil_start = 1120
    recoil_end = 1520

    for f in range(recoil_start, recoil_end + 1):
        t = (f - recoil_start) / (recoil_end - recoil_start)
        wx = seeker_world_positions.get(f, 0)

        if t < 0.2:
             rt = t / 0.2
             recoil_y = lerp(-0.15, 1.2, ease_out_bounce(rt))
             seeker_y_out[f] = recoil_y
             kf_loc(seeker, wx, recoil_y, f)
             seeker_spin = lerp(seeker_spin, 0, rt)
        else:
             # Stunned/Processing wobble — holds near Y=1.2 for a long time
             lt = (t - 0.2) / 0.8
             y = 1.2 + 0.04 * math.sin(f * 0.2) * (1.0 - lt)
             seeker_y_out[f] = y
             kf_loc(seeker, wx, y, f)
             kf_rot_z(seeker, 0, f)

        # Triangle Exit: 2-phase departure so both surges stay visible on-screen.
        #
        # Phase 1 (t<0.15): quick ease to -4.5 so there's clear separation from seeker
        #   before the first surge brings it back dramatically.
        # Phase 2 (t>=0.15): very slow t^2.5 drift to -14 — lingers in view for most
        #   of the exit, only accelerating off-screen in the final quarter.
        if t < 0.15:
            base_offset = lerp(-1.05, -4.5, ease_in_out_cubic(t / 0.15))
        else:
            drift_t = (t - 0.15) / 0.85
            base_offset = lerp(-4.5, -14.0, math.pow(drift_t, 2.5))

        # Surges: sin(t*4π) gives positive peaks at t≈0.125 and t≈0.625.
        # Both peaks land while the base is still within the visible area.
        # Amplitude decays gently — second surge still feels like a real comeback.
        surge_raw = 5.0 * math.pow(1.0 - t, 0.5) * math.sin(t * 4 * math.pi)

        # Soft clamp: can come within 0.8 units of seeker but not cross it.
        offset = min(base_offset + surge_raw, -0.8)

        # Y: only lifts toward seeker's Y=1.2 during positive surge peaks.
        base_tri_y = 0.4 - t * 1.6
        surge_y_pull = 0.9 * max(surge_raw / 5.0, 0.0)
        tri_y = base_tri_y + surge_y_pull

        kf_loc(right_tri, wx + offset, tri_y, f)
        tri_spin += 0.04 * (1.0 - t)
        kf_rot_z(right_tri, tri_spin, f)

        # Stays fully bright until t=0.75, then fades — mirrors the emotional weight.
        if t > 0.75:
             kf_emission_strength(right_tri_mat, lerp(2.0, 0.0, (t - 0.75) / 0.25), f)
        else:
             kf_emission_strength(right_tri_mat, 2.0, f)

    # Ghost: Right-angle triangle lingers as a faint ghost at left edge.
    # Fades 0.12 → 0 over 400 frames (past fading from memory).
    ghost_start = 1521
    ghost_end = 1921
    for f in range(ghost_start, ghost_end + 1):
        gt = (f - ghost_start) / (ghost_end - ghost_start)
        wx = seeker_world_positions.get(f, 0)
        kf_loc(right_tri, wx - 11, 0.5, f)
        kf_emission_strength(right_tri_mat, lerp(0.12, 0.0, ease_in_out_cubic(gt)), f)
    # Park fully offscreen after ghost fades
    kf_loc(right_tri, -60, 10, ghost_end + 1)
    kf_emission_strength(right_tri_mat, 0.0, ghost_end + 1)


    # ── Beat 1.5: The Gap / Searching Again (1520–1670) ──
    # Post-rejection stumble: decaying wobble → pause → cautious resumption.
    # Lonelier feel: slower pulse, reduced Y-amplitude, a moment of stillness.
    gap_start = 1520
    gap_end = 1670
    pause_start = 1570  # Seeker stops to "think"
    pause_end = 1595

    for f in range(gap_start, gap_end + 1):
        wx = seeker_world_positions.get(f, 0)
        
        if f < pause_start:
            # Stumbling away from rejection — decaying wobble
            t_stumble = (f - gap_start) / (pause_start - gap_start)
            base_y = lerp(1.2, 0.0, ease_in_out_cubic(t_stumble))
            wobble = 0.4 * math.exp(-t_stumble * 3) * math.sin(t_stumble * 12 * math.pi)
            y = base_y + wobble
        elif f <= pause_end:
            # The pause: Seeker is processing. Add a subtle "processing tremble"
            t_pause = (f - pause_start) / (pause_end - pause_start)
            # Faint high-frequency tremble
            y = 0.04 * math.sin(f * 1.5) * (1.0 - t_pause) 
        else:
            # Searching again — substantial wandering
            # Smoothly transition from zero-ish Y back into search noise
            t_resume = (f - pause_end) / (gap_end - pause_end)
            y = 0.5 * math.sin(f * 0.08) * math.cos(f * 0.05)
            y += 0.2 * math.sin(f * 0.2)
            # Ease in the noise
            y *= ease_in_out_cubic(min(t_resume * 2.0, 1.0))

        seeker_y_out[f] = y
        kf_loc(seeker, wx, y, f)

    # Tired heartbeat: slower period, smaller amplitude
    apply_pulse(seeker, gap_start, gap_end, period=85, amplitude=0.02)


    # Convert Act 1 range for The One to hidden
    for f in range(1, ACT1_END + 1):
        kf_loc(the_one, -60, 0, f)
        kf_emission_strength(one_mat, 0.0, f)

    # Near-miss cameo was removed.
    pass
