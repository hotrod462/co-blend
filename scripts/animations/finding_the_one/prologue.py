"""
Finding the One — Prologue: The Birth (Frames 1–330, 0s–11s)

Two right-angle triangles orbit from frame 1, spiral inward, align their
hypotenuses to form a square, the combined shape grows into a big square,
then shrinks down into the Seeker protagonist.
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

    New flow:
      - P.1–P.3: Parents orbit, spiral inward, align → form a combined shape
      - P.4: Combined shape pulses, then GROWS into a bigger square
      - P.4b: Big square SHRINKS DOWN into the small Seeker protagonist
      - P.5: Journey begins (no parent drifting away — they become the Seeker)
    """
    # ── Beats P.1 - P.3: Sophisticated Spiral Birth (Frames 1–110) ──
    # Replaced simple helpers with dynamic math for a more premium visual hook
    angle = 0
    center_y = 0
    for f in range(1, 111):
        t = (f - 1) / 109.0
        
        # Variable revolution speed (accelerates then slows for alignment)
        # RPM transitions from 1.0 -> 2.5 -> 0.5
        if t < 0.7:
            rpm = lerp(1.0, 2.5, ease_in_out_cubic(t/0.7))
        else:
            rpm = lerp(2.5, 0.5, ease_in_out_cubic((t-0.7)/0.3))
        
        angle += (rpm * 2 * math.pi / 60.0) 
        # Add a subtle "energy surge" wobble to the angle
        display_angle = angle + 0.1 * math.sin(f * 0.2)
        
        # Pulsing (non-monotonic) spiral radius
        # Base spiral: 2.5 -> 0.3
        base_radius = lerp(2.5, 0.3, ease_in_out_cubic(t))
        # Add a "breathing" pulse to the radius
        radius_pulse = 0.15 * math.sin(f * 0.15) * (1.0 - t)
        radius = base_radius + radius_pulse
        
        center_x = seeker_world_positions.get(f, 0)
        ax = center_x + radius * math.cos(display_angle)
        ay = center_y + radius * math.sin(display_angle)
        bx = center_x + radius * math.cos(display_angle + math.pi)
        by = center_y + radius * math.sin(display_angle + math.pi)
        
        kf_loc(parent_a, ax, ay, f)
        kf_loc(parent_b, bx, by, f)
        
        # Variable self-rotation (axial spin)
        # Faster than orbit, with its own rhythmic intensity
        axial_spin = angle * 1.5 + 0.2 * math.cos(f * 0.2)
        kf_rot_z(parent_a, axial_spin, f)
        kf_rot_z(parent_b, axial_spin + math.pi, f)

    # Normalize final angle for the alignment beat
    angle = display_angle
    target_angle = math.pi

    # Slide together: gap shrinks 0.3 → 0 (110–130), angle aligns to horizontal
    for f in range(110, 131):
        t = (f - 110) / 20.0
        gap = lerp(0.3, 0.0, ease_in_out_cubic(t))
        # Smoothly move from whatever angle they were at to the aligned horizontal position
        cur_angle = lerp(angle, target_angle, ease_in_out_cubic(t))
        
        ax = center_x + gap * math.cos(cur_angle)
        ay = center_y + gap * math.sin(cur_angle)
        bx = center_x + gap * math.cos(cur_angle + math.pi)
        by = center_y + gap * math.sin(cur_angle + math.pi)
        
        kf_loc(parent_a, ax, ay, f)
        kf_loc(parent_b, bx, by, f)
        
        # Aligned spin to π/2 (horizontal hypotenuse)
        # The parents are right triangles. To form a square, hypotenuses face each other.
        # This part depends on the mesh orientation, but let's lerp to a clean 90deg.
        align_rot = lerp(cur_angle, math.pi / 2, ease_in_out_cubic(t))
        kf_rot_z(parent_a, align_rot, f)
        kf_rot_z(parent_b, align_rot + math.pi, f)

    # Frame 125–130: CLICK — flush together
    for f in range(125, 131):
        kf_loc(parent_a, center_x - 0.01, center_y, f)
        kf_loc(parent_b, center_x + 0.01, center_y, f)

    # ── Beat P.4: The Birth — Big Square then Shrink (Frames 130–210) ──

    # Phase 1 (130–155): Combined shape pulses with life
    for f in range(130, 156):
        t = (f - 130) / 25.0
        if t < 0.5:
            emission = lerp(PARENT_EMISSION, 4.0, ease_in_out_cubic(t * 2))
        else:
            emission = lerp(4.0, PARENT_EMISSION, ease_in_out_cubic((t - 0.5) * 2))
        kf_emission_strength(parent_a_mat, emission, f)
        kf_emission_strength(parent_b_mat, emission, f)
        kf_loc(parent_a, center_x - 0.01, center_y, f)
        kf_loc(parent_b, center_x + 0.01, center_y, f)

    # Phase 2 (155–175): Parents GROW into a big square
    # Parents scale up while their emission stays strong.
    # Seeker appears at center, hidden (scale 0), parents envelop it.
    for f in range(155, 176):
        t = (f - 155) / 20.0
        # Parents scale up to ~1.8x to form a visually bigger square
        parent_scale = lerp(1.0, 1.8, ease_in_out_cubic(t))
        kf_scale(parent_a, parent_scale, f)
        kf_scale(parent_b, parent_scale, f)
        kf_loc(parent_a, center_x - 0.01, center_y, f)
        kf_loc(parent_b, center_x + 0.01, center_y, f)
        kf_emission_strength(parent_a_mat, PARENT_EMISSION, f)
        kf_emission_strength(parent_b_mat, PARENT_EMISSION, f)

        # Seeker starts appearing at center, tiny
        kf_loc(seeker, center_x, center_y, f)
        kf_scale(seeker, 0.0, f)
        kf_emission_strength(seeker_mat, 0.0, f)

    # Phase 3 (175–210): Big square SHRINKS down into the Seeker
    # Parents shrink and fade, Seeker grows and brightens at center
    for f in range(175, 211):
        t = (f - 175) / 35.0

        # Parents shrink from 1.8 to 0 and fade out
        parent_scale = lerp(1.8, 0.0, ease_in_out_cubic(t))
        parent_em = lerp(PARENT_EMISSION, 0.0, ease_in_out_cubic(t))
        kf_scale(parent_a, max(parent_scale, 0.001), f)
        kf_scale(parent_b, max(parent_scale, 0.001), f)
        kf_emission_strength(parent_a_mat, parent_em, f)
        kf_emission_strength(parent_b_mat, parent_em, f)
        kf_loc(parent_a, center_x - 0.01, center_y, f)
        kf_loc(parent_b, center_x + 0.01, center_y, f)

        # Seeker grows from 0 to full size and brightens
        seeker_scale = lerp(0.0, 1.0, ease_in_out_cubic(t))
        seeker_em = lerp(0.0, 2.0, ease_in_out_cubic(t))
        kf_scale(seeker, max(seeker_scale, 0.001), f)
        kf_emission_strength(seeker_mat, seeker_em, f)
        kf_loc(seeker, center_x, center_y, f)

    # ── Park parents offscreen from here on ──
    for f in range(211, PROLOGUE_END + 1):
        kf_loc(parent_a, -60, 0, f)
        kf_loc(parent_b, -60, 0, f)
        kf_scale(parent_a, 0.001, f)
        kf_scale(parent_b, 0.001, f)

    # ── Beat P.5: Departure (Frames 210–330) ─────────────────
    # Seeker alone in frame at center. Holds still, then journey begins.

    # Seeker holds at center (210–230)
    for f in range(210, 231):
        wx = seeker_world_positions.get(f, 0)
        kf_loc(seeker, wx, center_y, f)
        kf_scale(seeker, 1.0, f)
        kf_emission_strength(seeker_mat, 2.0, f)

    # Seeker heartbeat pulse begins
    apply_pulse(seeker, 220, 250, period=45, amplitude=0.03)

    # World scroll begins (230–330): handled by systems.py scroll schedule
    # Seeker position transitions to following scroll
    for f in range(230, PROLOGUE_END + 1):
        wx = seeker_world_positions.get(f, 0)
        t = (f - 230) / max(PROLOGUE_END - 230, 1)
        # Subtle organic bobbing starts immediately with the scroll
        sy = 0.15 * math.sin(f * 0.15) * t 
        kf_loc(seeker, wx, sy, f)

    # Continuous pulse for the latter half of prologue
    apply_pulse(seeker, 250, PROLOGUE_END, period=45, amplitude=0.03)
