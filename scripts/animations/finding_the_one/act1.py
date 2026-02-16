"""
Finding the One — Act I: The Journey Begins (Frames 330–990)
Slower encounter with self-rotation. Triangle drifts away slowly after rejection.
"""
import math
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

    # ── Beat 1.3: Right-Angle Triangle Encounter (630–870) ──
    # Entry: zigzags toward center (630–680)
    for f in range(630, 681):
        t = (f - 630) / 50.0
        wx = seeker_world_positions.get(f, 0)
        tri_screen_x = lerp(12, 2, ease_in_out_cubic(t))
        zigzag_y = 1.5 * math.sin(t * 3 * math.pi)
        kf_loc(right_tri, wx + tri_screen_x, zigzag_y, f)
        kf_rot_z(right_tri, math.sin(t * 4 * math.pi) * 0.4, f)
        seeker_y_out[f] = 0
        kf_loc(seeker, wx, 0, f)

    # MUTUAL orbit with SELF-ROTATION (680–730) — slower, deliberate
    seeker_spin = 0.0
    tri_spin = 0.0
    for f in range(680, 731):
        t = (f - 680) / 50.0
        wx = seeker_world_positions.get(f, 0)
        cx = wx + 0.5
        cy = 0
        angle = t * 1.5 * math.pi  # slower: 0.75 revolutions (was 1.5)
        radius = 1.0

        kf_loc(right_tri, cx + radius * math.cos(angle), cy + radius * math.sin(angle), f)
        kf_loc(seeker, cx + radius * math.cos(angle + math.pi), cy + radius * math.sin(angle + math.pi), f)
        seeker_y_out[f] = cy + radius * math.sin(angle + math.pi)

        # Self-rotation: mismatched speeds
        seeker_spin += 0.02
        tri_spin += 0.06  # triangle spins 3x faster — mismatched
        kf_rot_z(seeker, seeker_spin, f)
        kf_rot_z(right_tri, tri_spin, f)

    # THE TEASE: flat leg faces Seeker (730–760)
    for f in range(730, 761):
        t = (f - 730) / 30.0
        wx = seeker_world_positions.get(f, 0)
        # Self-rotation continues
        seeker_spin += 0.02
        tri_spin += 0.06

        if t < 0.33:
            gap = lerp(1.0, 0.2, ease_in_out_cubic(t / 0.33))
            tri_x = wx + gap / 2 + 0.35
            seeker_x = wx - gap / 2 + 0.35
        elif t < 0.67:
            tri_x = wx + 0.55
            seeker_x = wx
        else:
            bonk_t = (t - 0.67) / 0.33
            tri_x = wx + 0.55 + 0.3 * bonk_t
            seeker_x = wx
            tri_spin += 0.1 * bonk_t  # extra spin on bonk

        kf_loc(right_tri, tri_x, 0.5 * max(0, (t - 0.67) / 0.33), f)
        kf_loc(seeker, seeker_x, 0, f)
        kf_rot_z(seeker, seeker_spin, f)
        kf_rot_z(right_tri, tri_spin, f)
        seeker_y_out[f] = 0

    # Recoil (760–790) — seeker stops spinning, triangle spins wildly
    for f in range(760, 791):
        t = (f - 760) / 30.0
        wx = seeker_world_positions.get(f, 0)
        recoil_y = lerp(0, 1.0, ease_out_bounce(t))
        seeker_y_out[f] = recoil_y
        kf_loc(seeker, wx, recoil_y, f)
        # Wind down seeker spin
        seeker_spin = lerp(seeker_spin, 0, ease_in_out_cubic(t))
        kf_rot_z(seeker, seeker_spin, f)

        tri_spin += 0.08
        tri_x = wx + lerp(0.8, 2.5, t)
        kf_loc(right_tri, tri_x, lerp(0.5, -0.5, t), f)
        kf_rot_z(right_tri, tri_spin, f)

    # Seeker returns to 0 rotation
    for f in range(791, 821):
        t = (f - 791) / 29.0
        wx = seeker_world_positions.get(f, 0)
        kf_rot_z(seeker, lerp(seeker_spin, 0, ease_in_out_cubic(t)), f)
        seeker_y_out[f] = 1.5
        kf_loc(seeker, wx, 1.5, f)

        # Triangle still erratic
        tri_spin += 0.04
        tri_x = wx + lerp(2.5, -1, t) + math.sin(t * 5) * 0.5
        kf_loc(right_tri, tri_x, lerp(-0.5, 1.5, t) * math.sin(t * 3), f)
        kf_rot_z(right_tri, tri_spin, f)

    # Triangle drift-away: stays at world position, slowly fades (820→1200)
    tri_anchor_x = seeker_world_positions.get(820, 0) + 1.5
    tri_anchor_y = 1.0
    kf_loc(right_tri, tri_anchor_x, tri_anchor_y, 820)
    kf_loc(right_tri, tri_anchor_x, tri_anchor_y + 1.5, 1200)  # slow Y drift
    kf_emission_strength(right_tri_mat, RIGHT_TRI_EMISSION, 820)
    kf_emission_strength(right_tri_mat, 0.0, 1200)  # fade over 380 frames
    kf_rot_z(right_tri, tri_spin, 820)
    kf_rot_z(right_tri, tri_spin + 0.5, 1200)  # gentle continued rotation

    # After fade complete, park offscreen
    kf_loc(right_tri, -60, 10, 1201)
    for f in range(1201, FRAME_END + 1, 100):
        kf_loc(right_tri, -60, 10, f)

    # Seeker during triangle drift (820–870)
    for f in range(821, 871):
        wx = seeker_world_positions.get(f, 0)
        seeker_y_out[f] = 1.5
        kf_loc(seeker, wx, 1.5, f)
    apply_sigh(seeker, 850, 870, depth=0.08)

    # ── Beat 1.4: Recovery (870–990) ──
    y_recovery = [(870, 1.5), (910, 1.2), (950, 0.5), (990, 0.0)]
    for i in range(len(y_recovery) - 1):
        f0, y0 = y_recovery[i]
        f1, y1 = y_recovery[i + 1]
        for f in range(f0, f1 + 1):
            t = (f - f0) / max(f1 - f0, 1)
            y = lerp(y0, y1, ease_in_out_cubic(t))
            wx = seeker_world_positions.get(f, 0)
            seeker_y_out[f] = y
            kf_loc(seeker, wx, y, f)
    apply_pulse(seeker, 870, 990, period=45, amplitude=0.03)

    # The One hidden for entire act
    for f in range(1, ACT1_END + 1):
        kf_loc(the_one, -60, 0, f)
