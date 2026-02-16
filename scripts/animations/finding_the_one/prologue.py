"""
Finding the One — Prologue: The Birth (Frames 1–330, 0s–11s)

Two right-angle triangles orbit from frame 1, spiral inward, align their
hypotenuses to form a rectangle, pulse with life, and birth the Seeker.
The parent drifts away, and the journey begins.
"""
import math

from scripts.utils.animation import lerp, ease_in_out_cubic

from scripts.animations.finding_the_one.config import (
    PROLOGUE_END, PARENT_EMISSION,
)
from scripts.animations.finding_the_one.helpers import (
    kf_loc, kf_scale, kf_rot_z, kf_emission_strength,
    apply_pulse, orbit_pair, move_along,
)


def animate_prologue(parent_a, parent_a_mat, parent_b, parent_b_mat,
                     seeker, seeker_mat, seeker_world_positions):
    """
    Frames 1–330: The Birth.

    Args:
        parent_a, parent_b: parent triangle objects
        parent_a_mat, parent_b_mat: their materials
        seeker: the Seeker square object
        seeker_mat: Seeker's material
        seeker_world_positions: dict frame → world_x (for positioning)
    """
    # ── Beat P.1: Immediate Motion (Frames 1–30) ─────────────
    # Two triangles ALREADY orbiting at frame 1
    # Center of screen = Seeker's starting world position (≈0)
    center_x = seeker_world_positions.get(1, 0)
    center_y = 0

    # Orbit at radius 2.0, ~1 revolution per 60 frames
    orbit_pair(parent_a, parent_b, (center_x, center_y),
               frame_start=1, frame_end=30,
               radius_start=2.0, radius_end=2.0,
               rpm_start=1.0, rpm_end=1.0)

    # ── Beat P.2: Spiral Inward (Frames 30–90) ───────────────
    # Radius 2.0 → 1.0 (frames 30–60)
    orbit_pair(parent_a, parent_b, (center_x, center_y),
               frame_start=30, frame_end=60,
               radius_start=2.0, radius_end=1.0,
               rpm_start=1.0, rpm_end=1.5)

    # Radius 1.0 → 0.5 (frames 60–90)
    orbit_pair(parent_a, parent_b, (center_x, center_y),
               frame_start=60, frame_end=90,
               radius_start=1.0, radius_end=0.5,
               rpm_start=1.5, rpm_end=2.0)

    # ── Beat P.3: The Alignment (Frames 90–130) ──────────────
    # Spin slows, triangles align hypotenuses (90–110)
    orbit_pair(parent_a, parent_b, (center_x, center_y),
               frame_start=90, frame_end=110,
               radius_start=0.5, radius_end=0.3,
               rpm_start=2.0, rpm_end=0.5)

    # Slide together: gap shrinks 0.3 → 0 (110–130)
    for f in range(110, 131):
        t = (f - 110) / 20.0
        gap = lerp(0.3, 0.0, ease_in_out_cubic(t))
        # Rotate to align hypotenuses facing each other
        # Parent A on left, Parent B on right
        align_angle = lerp(0, math.pi / 2, ease_in_out_cubic(t))
        kf_loc(parent_a, center_x - gap, center_y, f)
        kf_loc(parent_b, center_x + gap, center_y, f)
        kf_rot_z(parent_a, align_angle, f)
        kf_rot_z(parent_b, align_angle + math.pi, f)

    # Frame 125–130: CLICK — flush together forming rectangle
    for f in range(125, 131):
        kf_loc(parent_a, center_x - 0.01, center_y, f)
        kf_loc(parent_b, center_x + 0.01, center_y, f)

    # ── Beat P.4: The Birth (Frames 130–200) ─────────────────
    # Combined shape pulses: emission 2.0 → 4.0 → 2.0 (130–160)
    for f in range(130, 161):
        t = (f - 130) / 30.0
        if t < 0.5:
            emission = lerp(PARENT_EMISSION, 4.0, ease_in_out_cubic(t * 2))
        else:
            emission = lerp(4.0, PARENT_EMISSION, ease_in_out_cubic((t - 0.5) * 2))
        kf_emission_strength(parent_a_mat, emission, f)
        kf_emission_strength(parent_b_mat, emission, f)
        # Hold parents in place
        kf_loc(parent_a, center_x - 0.01, center_y, f)
        kf_loc(parent_b, center_x + 0.01, center_y, f)

    # Seeker separates from center (160–200)
    # Parent dims, child brightens
    for f in range(160, 201):
        t = (f - 160) / 40.0
        # Parent dims
        parent_em = lerp(PARENT_EMISSION, 0.8, ease_in_out_cubic(t))
        kf_emission_strength(parent_a_mat, parent_em, f)
        kf_emission_strength(parent_b_mat, parent_em, f)

        # Seeker brightens and separates downward
        seeker_em = lerp(0.0, 2.0, ease_in_out_cubic(t))
        kf_emission_strength(seeker_mat, seeker_em, f)

        # Seeker emerges from center
        sep = lerp(0, 0.8, ease_in_out_cubic(t))
        kf_loc(seeker, center_x, center_y - sep, f)

        # Parents hold position
        kf_loc(parent_a, center_x - 0.01, center_y, f)
        kf_loc(parent_b, center_x + 0.01, center_y, f)

        # Seeker scale grows from tiny to full
        s = lerp(0.1, 1.0, ease_in_out_cubic(t))
        kf_scale(seeker, s, f)

    # ── Beat P.5: Departure (Frames 200–330) ─────────────────
    # Parent rectangle drifts left and off-screen (200–240)
    for f in range(200, 241):
        t = (f - 200) / 40.0
        parent_x = lerp(center_x, center_x - 15, ease_in_out_cubic(t))
        kf_loc(parent_a, parent_x - 0.01, center_y, f)
        kf_loc(parent_b, parent_x + 0.01, center_y, f)
        # Continue dimming
        parent_em = lerp(0.8, 0.0, ease_in_out_cubic(t))
        kf_emission_strength(parent_a_mat, parent_em, f)
        kf_emission_strength(parent_b_mat, parent_em, f)

    # Park parents offscreen for the rest
    for f in range(241, PROLOGUE_END + 1):
        kf_loc(parent_a, -60, 0, f)
        kf_loc(parent_b, -60, 0, f)

    # Seeker alone in frame, holds still (240–270)
    for f in range(200, 271):
        wx = seeker_world_positions.get(f, 0)
        kf_loc(seeker, wx, center_y - 0.8, f)

    # Seeker heartbeat pulse begins (240–270)
    apply_pulse(seeker, 240, 270, period=45, amplitude=0.03)

    # World scroll begins (300–330): handled by systems.py scroll schedule
    # Seeker position transitions to following scroll
    for f in range(270, PROLOGUE_END + 1):
        wx = seeker_world_positions.get(f, 0)
        # Gentle drift to center Y
        t = (f - 270) / max(PROLOGUE_END - 270, 1)
        sy = lerp(center_y - 0.8, 0, ease_in_out_cubic(t))
        kf_loc(seeker, wx, sy, f)

    # Continuous pulse for the latter half of prologue
    apply_pulse(seeker, 270, PROLOGUE_END, period=45, amplitude=0.03)
