"""
Finding the One — Act I: The Journey Begins (Frames 330–990, 11s–33s)

The Seeker explores the scrolling world, encounters its first mismatch
(a right-angle triangle), gets rejected, and recovers. A foreshadowing
near-miss with The One occurs in the background.
"""
import math

from scripts.utils.animation import lerp, ease_in_out_cubic, ease_out_bounce

from scripts.animations.finding_the_one.config import (
    ACT1_START, ACT1_END,
    SEEKER_SIZE, RIGHT_TRI_EMISSION,
    Y_DRIFT_EXPLORING, Y_DRIFT_AFTER_1ST,
    ORTHO_NORMAL, ORTHO_ENCOUNTER,
    SCROLL_NORMAL, SCROLL_VERY_SLOW,
)
from scripts.animations.finding_the_one.helpers import (
    kf_loc, kf_scale, kf_rot_z, kf_emission_strength,
    kf_ortho_scale, apply_pulse, apply_sigh,
    move_along, orbit_pair, lerp_value,
)


def animate_act1(seeker, seeker_mat, right_tri, right_tri_mat,
                 the_one, one_mat,
                 seeker_world_positions, seeker_y_out,
                 camera):
    """
    Frames 330–990: The Journey Begins.

    Writes Y positions into seeker_y_out dict for each frame.

    Args:
        seeker, right_tri, the_one: Blender objects
        seeker_mat, right_tri_mat, one_mat: materials
        seeker_world_positions: dict frame → world_x
        seeker_y_out: dict to populate with frame → y_position
        camera: camera object for ortho scale
    """

    # ── Beat 1.1: First Steps (Frames 330–450) ───────────────
    # Wide Y-drift showing curiosity
    for f in range(330, 451):
        t = (f - 330) / 120.0
        wx = seeker_world_positions.get(f, 0)

        # Gentle Y exploration
        if t < 0.33:
            y = lerp(0, 0.5, ease_in_out_cubic(t / 0.33))
        elif t < 0.67:
            y = lerp(0.5, -0.3, ease_in_out_cubic((t - 0.33) / 0.34))
        else:
            y = lerp(-0.3, 0.2, ease_in_out_cubic((t - 0.67) / 0.33))

        seeker_y_out[f] = y
        kf_loc(seeker, wx, y, f)

    apply_pulse(seeker, 330, 450, period=45, amplitude=0.03)

    # ── Beat 1.2: Wandering the Landscape (Frames 450–630) ───
    # Wide Y-drift ±2.0 showing curiosity
    y_waypoints_12 = [
        (450, 0.2),
        (500, 1.5),
        (540, -0.5),
        (570, -1.5),
        (600, 0.5),
        (630, 0.0),
    ]

    for i in range(len(y_waypoints_12) - 1):
        f0, y0 = y_waypoints_12[i]
        f1, y1 = y_waypoints_12[i + 1]
        for f in range(f0, f1 + 1):
            t = (f - f0) / max(f1 - f0, 1)
            y = lerp(y0, y1, ease_in_out_cubic(t))
            # Add wobble
            wobble = 0.15 * math.sin(f * 0.13) * math.cos(f * 0.07)
            y += wobble
            wx = seeker_world_positions.get(f, 0)
            seeker_y_out[f] = y
            kf_loc(seeker, wx, y, f)

    apply_pulse(seeker, 450, 630, period=45, amplitude=0.03)

    # Background Pairing #1 (frames ~480–570):
    # Two dim equilateral triangles approach, orbit, bonk, drift apart
    # (handled by background triangle system — we note it here for reference)

    # ── Beat 1.3: Right-Angle Triangle Encounter (Frames 630–870) ──
    # Triangle enters from the right — brighter than background
    # World slows during encounter

    # Triangle enters from far right, zigzags toward center (630–680)
    for f in range(630, 681):
        t = (f - 630) / 50.0
        wx = seeker_world_positions.get(f, 0)

        # Triangle starts at screen-relative +12, approaches
        tri_screen_x = lerp(12, 2, ease_in_out_cubic(t))
        # Zigzag Y: 3-4 direction changes
        zigzag_y = 1.5 * math.sin(t * 3 * math.pi)
        tri_world_x = wx + tri_screen_x
        kf_loc(right_tri, tri_world_x, zigzag_y, f)
        kf_rot_z(right_tri, math.sin(t * 4 * math.pi) * 0.4, f)

    # Seeker holds, pulse quickens (630–680)
    for f in range(630, 681):
        wx = seeker_world_positions.get(f, 0)
        y = 0
        seeker_y_out[f] = y
        kf_loc(seeker, wx, y, f)

    # Tight chaotic orbit around Seeker (680–720)
    for f in range(680, 721):
        t = (f - 680) / 40.0
        wx = seeker_world_positions.get(f, 0)
        # Triangle orbits chaotically
        angle = t * 3 * math.pi  # fast spin
        radius = 1.0
        tri_x = wx + radius * math.cos(angle)
        tri_y = radius * math.sin(angle)
        kf_loc(right_tri, tri_x, tri_y, f)
        kf_rot_z(right_tri, angle * 1.5, f)
        # Seeker watches
        seeker_y_out[f] = 0
        kf_loc(seeker, wx, 0, f)

    # THE TEASE: Flat leg faces Seeker — approaches to 0.2 gap (720–750)
    for f in range(720, 751):
        t = (f - 720) / 30.0
        wx = seeker_world_positions.get(f, 0)

        if t < 0.33:
            # Approach
            gap = lerp(1.0, 0.2, ease_in_out_cubic(t / 0.33))
            tri_x = wx + gap + 0.35
            tri_y = 0
        elif t < 0.67:
            # Hold — THE TEASE (~10 frames)
            tri_x = wx + 0.55
            tri_y = 0
        else:
            # Hypotenuse rotates into contact — BONK
            bonk_t = (t - 0.67) / 0.33
            tri_x = wx + 0.55 + 0.3 * bonk_t
            tri_y = 0.5 * bonk_t  # bounces away
            kf_rot_z(right_tri, lerp(0, math.pi / 3, bonk_t), f)

        kf_loc(right_tri, tri_x, tri_y, f)

        # Seeker leans right slightly
        seeker_y_out[f] = 0
        sx = wx + lerp(0, 0.2, ease_in_out_cubic(min(t * 3, 1.0)))
        kf_loc(seeker, sx, 0, f)

    # Recoil: Seeker jumps back (750–780)
    for f in range(750, 781):
        t = (f - 750) / 30.0
        wx = seeker_world_positions.get(f, 0)
        recoil_y = lerp(0, 1.0, ease_out_bounce(t))
        seeker_y_out[f] = recoil_y
        kf_loc(seeker, wx, recoil_y, f)

        # Triangle spins away erratically
        tri_x = wx + lerp(0.8, 2.5, t)
        tri_y = lerp(0.5, -0.5, t)
        kf_loc(right_tri, tri_x, tri_y, f)
        kf_rot_z(right_tri, t * 3, f)

    # Triangle follows erratically, overshoots (780–820)
    for f in range(780, 821):
        t = (f - 780) / 40.0
        wx = seeker_world_positions.get(f, 0)
        tri_x = wx + lerp(2.5, -1, t) + math.sin(t * 5) * 0.5
        tri_y = lerp(-0.5, 1.5, t) * math.sin(t * 3)
        kf_loc(right_tri, tri_x, tri_y, f)
        kf_rot_z(right_tri, t * 2, f)

        seeker_y_out[f] = 1.5
        kf_loc(seeker, wx, 1.5, f)

    # Triangle falls behind — scroll carries it left (820–870)
    for f in range(820, 871):
        t = (f - 820) / 50.0
        wx = seeker_world_positions.get(f, 0)
        # Triangle at fixed world-X, falls behind in the frame
        tri_world_x = seeker_world_positions.get(820, 0) + 1.5  # stops at its position
        kf_loc(right_tri, tri_world_x, lerp(1.0, 2.0, t), f)
        kf_rot_z(right_tri, 2 + t * 0.5, f)

        # Seeker: sigh, emission dips
        seeker_y_out[f] = lerp(1.5, 1.5, t)
        kf_loc(seeker, wx, 1.5, f)

    # Seeker sigh (850–870)
    apply_sigh(seeker, 850, 870, depth=0.08)

    # Park triangle offscreen
    for f in range(871, ACT1_END + 1):
        kf_loc(right_tri, -60, 10, f)

    # ── Beat 1.4: Recovery (Frames 870–990) ───────────────────
    y_recovery = [
        (870, 1.5),
        (910, 1.2),
        (950, 0.5),
        (990, 0.0),
    ]

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

    # ── Foreshadowing Near-Miss (frames ~900–990) ─────────────
    # The One drifts through TOP-RIGHT corner of frame, unseen
    for f in range(900, 991):
        t = (f - 900) / 90.0
        wx = seeker_world_positions.get(f, 0)
        # The One at Y≈3.5–4.0, screen-relative X from +8 to +2
        one_screen_x = lerp(8, 2, t)
        one_world_x = wx + one_screen_x
        one_y = lerp(3.5, 4.0, t)
        kf_loc(the_one, one_world_x, one_y, f)
        kf_emission_strength(one_mat, 2.0, f)

    # Hide The One before and after near-miss
    for f in range(1, 900):
        kf_loc(the_one, -60, 0, f)
    for f in range(991, ACT1_END + 1):
        kf_loc(the_one, -60, 0, f)
