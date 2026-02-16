"""
Finding the One — Act III: Discovery (Frames 1800–2460)
Self-rotation that syncs, orbit center shifts to align with Act 4,
final angle locks to horizontal for smooth rectangle formation.
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
    half = SEEKER_SIZE / 2  # 0.3

    # ── Beat 3.1: The One Appears Ahead (1800–1950) ──
    for f in range(1800, 1951):
        t = (f - 1800) / 150.0
        wx = seeker_world_positions.get(f, 0)
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
    apply_pulse(seeker, 1800, 1950, period=45, amplitude=0.03)
    apply_pulse(the_one, 1800, 1950, period=45, amplitude=0.03)

    # ── Beat 3.2: Mutual Recognition (1950–2040) ──
    for f in range(1950, 2041):
        t = (f - 1950) / 90.0
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
    apply_pulse(seeker, 1950, 2040, period=45, amplitude=0.03)
    apply_pulse(the_one, 1950, 2040, period=45, amplitude=0.03)

    # ── Beat 3.3: First Orbit with SELF-ROTATION (2040–2250) ──
    # Both spin on their own axis while orbiting each other.
    # Starting at different speeds, they gradually sync — this is the magic.
    orbit_angle = 0.0
    seeker_spin = 0.0
    one_spin = 0.0

    # Initial cx_offset = 0.6 (midpoint between them)
    cx_offset_start = 0.6

    for f in range(2040, 2251):
        t = (f - 2040) / 210.0
        wx = seeker_world_positions.get(f, 0)

        # Orbit center shifts from offset 0.6 toward 0 as they get closer
        cx_offset = lerp(cx_offset_start, 0.3, ease_in_out_cubic(t))
        cx = wx + cx_offset
        cy = 0

        if f <= 2110:
            rev_speed = 1.0 / 120.0
            r = 0.8
        elif f <= 2160:
            rev_speed = 1.0 / 80.0
            st = (f - 2110) / 50.0
            r = lerp(0.8, 0.7, ease_in_out_cubic(st))
        elif f <= 2200:
            rev_speed = 1.0 / 40.0
            st = (f - 2160) / 40.0
            r = lerp(0.7, 0.55, ease_in_out_cubic(st))
        else:
            rev_speed = 1.0 / 25.0
            st = (f - 2200) / 50.0
            r = lerp(0.55, 0.45, ease_in_out_cubic(st))

        orbit_angle += rev_speed * 2 * math.pi

        sx = cx + r * math.cos(orbit_angle)
        sy = cy + r * math.sin(orbit_angle)
        ox = cx + r * math.cos(orbit_angle + math.pi)
        oy = cy + r * math.sin(orbit_angle + math.pi)

        kf_loc(seeker, sx, sy, f)
        kf_loc(the_one, ox, oy, f)
        seeker_y_out[f] = sy

        # Self-rotation: different initial speeds, gradually syncing
        seeker_rot_speed = 0.03
        one_rot_speed = lerp(0.02, 0.03, ease_in_out_cubic(t))  # syncs to seeker
        seeker_spin += seeker_rot_speed
        one_spin += one_rot_speed
        kf_rot_z(seeker, seeker_spin, f)
        kf_rot_z(the_one, one_spin, f)

    apply_pulse(seeker, 2040, 2250, period=35, amplitude=0.04)
    apply_pulse(the_one, 2040, 2250, period=35, amplitude=0.04)

    # ── Beat 3.4: The Click (2250–2460) ──
    # Decelerate orbit, shift center to 0, lock angle to horizontal,
    # align self-rotations, then slide together smoothly.

    # Calculate target angle: nearest multiple of π for horizontal alignment
    target_orbit_angle = round(orbit_angle / math.pi) * math.pi
    # Target self-rotation: nearest multiple of π/2 (square symmetry)
    target_seeker_rot = round(seeker_spin / (math.pi / 2)) * (math.pi / 2)
    target_one_rot = target_seeker_rot  # match exactly

    angle_34 = orbit_angle

    for f in range(2250, 2461):
        t = (f - 2250) / 210.0
        wx = seeker_world_positions.get(f, 0)

        # Center offset smoothly goes to 0
        cx_offset = lerp(0.3, 0.0, ease_in_out_cubic(min(t * 2.0, 1.0)))
        cx = wx + cx_offset
        cy = 0

        if f <= 2320:
            # Winding down — orbit decelerating
            st = (f - 2250) / 70.0
            rev_speed = lerp(1.0 / 25.0, 1.0 / 100.0, ease_in_out_cubic(st))
            r = lerp(0.45, 0.38, ease_in_out_cubic(st))
            angle_34 += rev_speed * 2 * math.pi
        elif f <= 2370:
            # Angle converging to target horizontal
            st = (f - 2320) / 50.0
            rev_speed = lerp(1.0 / 100.0, 0, ease_in_out_cubic(st))
            r = lerp(0.38, half + 0.05, ease_in_out_cubic(st))
            # Blend angle toward target
            angle_34 = lerp(angle_34, target_orbit_angle, ease_in_out_cubic(st * 0.8))
            angle_34 += rev_speed * 2 * math.pi
        elif f <= 2420:
            # THE CLICK: angle locked, gap closing smoothly
            st = (f - 2370) / 50.0
            angle_34 = target_orbit_angle  # locked horizontal
            gap = lerp(0.05, 0.0, ease_in_out_cubic(st))
            r = half + gap
        elif f <= 2440:
            # Hold flush — combined rectangle
            angle_34 = target_orbit_angle
            r = half
        else:
            # Pulse intensifies
            angle_34 = target_orbit_angle
            r = half

        sx = cx + r * math.cos(angle_34)
        sy = cy + r * math.sin(angle_34)
        ox = cx + r * math.cos(angle_34 + math.pi)
        oy = cy + r * math.sin(angle_34 + math.pi)

        kf_loc(seeker, sx, sy, f)
        kf_loc(the_one, ox, oy, f)
        seeker_y_out[f] = sy

        # Self-rotation converging to aligned
        if f <= 2370:
            st = (f - 2250) / 120.0
            seeker_spin += lerp(0.03, 0.005, ease_in_out_cubic(st))
            one_spin += lerp(0.03, 0.005, ease_in_out_cubic(st))
            # Blend toward target rotation
            blend = ease_in_out_cubic(min(st * 1.5, 1.0))
            cur_seeker_rot = lerp(seeker_spin, target_seeker_rot, blend * 0.5)
            cur_one_rot = lerp(one_spin, target_one_rot, blend * 0.5)
            kf_rot_z(seeker, cur_seeker_rot, f)
            kf_rot_z(the_one, cur_one_rot, f)
        else:
            # Locked to target rotation
            kf_rot_z(seeker, target_seeker_rot, f)
            kf_rot_z(the_one, target_one_rot, f)

    apply_pulse(seeker, 2250, 2390, period=40, amplitude=0.03)
    apply_pulse(the_one, 2250, 2390, period=40, amplitude=0.03)
    apply_pulse(seeker, 2390, 2460, period=40, amplitude=0.06)
    apply_pulse(the_one, 2390, 2460, period=40, amplitude=0.06)

    return target_orbit_angle, target_seeker_rot
