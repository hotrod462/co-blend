"""
Finding the One — Act III: Discovery (Frames 2550–3250)
Self-rotation syncs, orbit shifts, angle locks.
Uses dynamic timing based on Config (extended duration).
"""
import math
from scripts.utils.animation import lerp, ease_in_out_cubic
from scripts.animations.finding_the_one.config import (
    ACT3_START, ACT3_END, SEEKER_SIZE, ONE_SIZE,
)
from scripts.animations.finding_the_one.helpers import (
    kf_loc, kf_scale, kf_rot_z, kf_emission_strength,
    apply_pulse, lerp_value,
)


def animate_act3(seeker, seeker_mat, the_one, one_mat,
                 seeker_world_positions, seeker_y_out, camera):
    half = SEEKER_SIZE / 2
    
    start = ACT3_START
    beat1_end = start + 150
    beat2_end = start + 240
    beat3_end = start + 450
    end = ACT3_END
    
    click_duration = end - beat3_end # 250 frames

    # ── Beat 3.1: The One Appears Ahead (start -> +150) ──
    for f in range(start, beat1_end + 1):
        t = (f - start) / 150.0
        wx = seeker_world_positions.get(f, 0)
        
        # Multi-stage approach
        if t < 0.33:
            lt = t / 0.33
            one_sx = lerp(8, 5, ease_in_out_cubic(lt))
            one_y = lerp(0.5, 0.3, lt)
        elif t < 0.53:
            lt = (t - 0.33) / 0.20
            one_sx = lerp(5, 3, ease_in_out_cubic(lt))
            one_y = lerp(0.3, 0.2, lt)
        elif t < 0.73:
            lt = (t - 0.53) / 0.20
            one_sx = lerp(3, 2.0, ease_in_out_cubic(lt))
            one_y = lerp(0.2, 0.1, lt)
        else:
            lt = (t - 0.73) / 0.27
            one_sx = lerp(2.0, 1.6, ease_in_out_cubic(lt))
            one_y = lerp(0.1, 0.05, lt)
            
        kf_loc(the_one, wx + one_sx, one_y, f)
        kf_emission_strength(one_mat, 2.0, f)
        
        if t < 0.5:
            y = lerp(0.1, 0, ease_in_out_cubic(t * 2))
        else:
            y = lerp(0, 0.05, ease_in_out_cubic((t - 0.5) * 2))
        seeker_y_out[f] = y
        kf_loc(seeker, wx, y, f)
        
    apply_pulse(seeker, start, beat1_end, period=45, amplitude=0.03)
    apply_pulse(the_one, start, beat1_end, period=45, amplitude=0.03)

    # ── Beat 3.2: Mutual Recognition (+150 -> +240) ──
    for f in range(beat1_end, beat2_end + 1):
        t = (f - beat1_end) / 90.0
        wx = seeker_world_positions.get(f, 0)
        
        if t < 0.33:
            one_sx = 1.6
            one_y = 0.05
            sy = 0.05
        elif t < 0.60:
            lt = (t - 0.33) / 0.27
            one_sx = lerp(1.6, 1.4, ease_in_out_cubic(lt))
            one_y = lerp(0.05, 0, lt)
            sy = lerp(0.05, 0, lt)
        else:
            lt = (t - 0.60) / 0.40
            one_sx = lerp(1.4, 1.2, ease_in_out_cubic(lt))
            one_y = 0
            sy = 0
            
        kf_loc(the_one, wx + one_sx, one_y, f)
        seeker_y_out[f] = sy
        kf_loc(seeker, wx, sy, f)
        
    apply_pulse(seeker, beat1_end, beat2_end, period=45, amplitude=0.03)
    apply_pulse(the_one, beat1_end, beat2_end, period=45, amplitude=0.03)

    # ── Beat 3.3: First Orbit (+240 -> +450) ──
    # Starts to sync rotation.
    orbit_angle = 0.0
    seeker_spin = 0.0
    one_spin = 0.0
    cx_offset_start = 0.6

    for f in range(beat2_end, beat3_end + 1):
        t = (f - beat2_end) / 210.0
        wx = seeker_world_positions.get(f, 0)

        cx_offset = lerp(cx_offset_start, 0.3, ease_in_out_cubic(t))
        cx = wx + cx_offset
        cy = 0
        
        rel_f = f - beat2_end
        
        if rel_f <= 70:
            rev_speed = 1.0 / 120.0
            r = 0.8
        elif rel_f <= 120:
            rev_speed = 1.0 / 80.0
            st = (rel_f - 70) / 50.0
            r = lerp(0.8, 0.7, ease_in_out_cubic(st))
        elif rel_f <= 160:
            rev_speed = 1.0 / 40.0
            st = (rel_f - 120) / 40.0
            r = lerp(0.7, 0.55, ease_in_out_cubic(st))
        else: # up to 210
            rev_speed = 1.0 / 25.0
            st = (rel_f - 160) / 50.0
            r = lerp(0.55, 0.45, ease_in_out_cubic(st))

        orbit_angle += rev_speed * 2 * math.pi

        sx = cx + r * math.cos(orbit_angle)
        sy = cy + r * math.sin(orbit_angle)
        ox = cx + r * math.cos(orbit_angle + math.pi)
        oy = cy + r * math.sin(orbit_angle + math.pi)

        kf_loc(seeker, sx, sy, f)
        kf_loc(the_one, ox, oy, f)
        seeker_y_out[f] = sy

        seeker_rot_speed = 0.03
        one_rot_speed = lerp(0.02, 0.03, ease_in_out_cubic(t))
        seeker_spin += seeker_rot_speed
        one_spin += one_rot_speed
        kf_rot_z(seeker, seeker_spin, f)
        kf_rot_z(the_one, one_spin, f)
        
        # Emission Pulse: Speeds up
        pulse_period = lerp(45, 12, t)
        phase = (f - beat2_end) / pulse_period * 2 * math.pi
        pulse_em = 2.0 + 1.0 * (0.5 + 0.5 * math.sin(phase))
        kf_emission_strength(seeker_mat, pulse_em, f)
        kf_emission_strength(one_mat, pulse_em, f)

    apply_pulse(seeker, beat2_end, beat3_end, period=35, amplitude=0.04)
    apply_pulse(the_one, beat2_end, beat3_end, period=35, amplitude=0.04)

    # ── Beat 3.4: The Click (+450 -> End) ──
    # Extended to 250 frames for slower alignment.
    target_orbit_angle = round(orbit_angle / math.pi) * math.pi
    target_seeker_rot = round(seeker_spin / (math.pi / 2)) * (math.pi / 2)
    target_one_rot = target_seeker_rot

    angle_34 = orbit_angle
    
    for f in range(beat3_end, end + 1):
        t = (f - beat3_end) / click_duration
        wx = seeker_world_positions.get(f, 0)
        rel_f = f - beat3_end

        cx_offset = lerp(0.3, 0.0, ease_in_out_cubic(min(t * 2.0, 1.0)))
        cx = wx + cx_offset
        cy = 0

        # Phase 1: Decel (0-70)
        if rel_f <= 70:
            st = rel_f / 70.0
            rev_speed = lerp(1.0 / 25.0, 1.0 / 100.0, ease_in_out_cubic(st))
            r = lerp(0.45, 0.38, ease_in_out_cubic(st))
            angle_34 += rev_speed * 2 * math.pi
            # Pulsing continues
            pulse_em = 2.0 + 1.0 * (0.5 + 0.5 * math.sin(f * 0.6))
            kf_emission_strength(seeker_mat, pulse_em, f)
            kf_emission_strength(one_mat, pulse_em, f)
            
        # Phase 2: Angle Align (70-150) -- SLOWER (80 frames)
        elif rel_f <= 150:
            st = (rel_f - 70) / 80.0
            rev_speed = lerp(1.0 / 100.0, 0, ease_in_out_cubic(st))
            r = lerp(0.38, half + 0.05, ease_in_out_cubic(st))
            angle_34 = lerp(angle_34, target_orbit_angle, ease_in_out_cubic(st * 0.8))
            angle_34 += rev_speed * 2 * math.pi
            # Pulse fades out
            pulse_em = 2.0 + lerp(1.0, 0, st) * (0.5 + 0.5 * math.sin(f * 0.6))
            kf_emission_strength(seeker_mat, pulse_em, f)
            kf_emission_strength(one_mat, pulse_em, f)
            
        # Phase 3: Gap Close (150-200) -- Clean (50 frames)
        elif rel_f <= 200:
            st = (rel_f - 150) / 50.0
            angle_34 = target_orbit_angle
            gap = lerp(0.05, 0.0, ease_in_out_cubic(st))
            r = half + gap
            # NO PULSE: Static brightness (solid connection)
            kf_emission_strength(seeker_mat, 2.0, f)
            kf_emission_strength(one_mat, 2.0, f)
            
        # Phase 4: Hold (200-250)
        else:
            angle_34 = target_orbit_angle
            r = half
            kf_emission_strength(seeker_mat, 2.0, f)
            kf_emission_strength(one_mat, 2.0, f)

        sx = cx + r * math.cos(angle_34)
        sy = cy + r * math.sin(angle_34)
        ox = cx + r * math.cos(angle_34 + math.pi)
        oy = cy + r * math.sin(angle_34 + math.pi)

        kf_loc(seeker, sx, sy, f)
        kf_loc(the_one, ox, oy, f)
        seeker_y_out[f] = sy

        # Sync Rotation (slower now too)
        if rel_f <= 150:
            st = rel_f / 150.0 
            blend = ease_in_out_cubic(st)
            seeker_spin += lerp(0.03, 0.005, blend)
            one_spin += lerp(0.03, 0.005, blend)
            
            cur_seeker_rot = lerp(seeker_spin, target_seeker_rot, blend * 0.8) 
            cur_one_rot = lerp(one_spin, target_one_rot, blend * 0.8)
            
            if rel_f > 140:
                snap_t = (rel_f - 140)/10.0
                cur_seeker_rot = lerp(cur_seeker_rot, target_seeker_rot, snap_t)
                cur_one_rot = lerp(cur_one_rot, target_one_rot, snap_t)
            
            kf_rot_z(seeker, cur_seeker_rot, f)
            kf_rot_z(the_one, cur_one_rot, f)
        else:
            kf_rot_z(seeker, target_seeker_rot, f)
            kf_rot_z(the_one, target_one_rot, f)

    apply_pulse(seeker, beat3_end, beat3_end + 140, period=40, amplitude=0.03)
    apply_pulse(the_one, beat3_end, beat3_end + 140, period=40, amplitude=0.03)
    apply_pulse(seeker, beat3_end + 140, end, period=40, amplitude=0.06)
    apply_pulse(the_one, beat3_end + 140, end, period=40, amplitude=0.06)

    return target_orbit_angle, target_seeker_rot
