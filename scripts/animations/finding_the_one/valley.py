"""
Finding the One — The Valley: "Almost Gave Up" (Frames 1650–1800, 55s–60s)

The emotional hinge. 5 seconds of genuine darkness before the turn.
The Seeker is at its dimmest, the world is a pure black void, and then
a tiny glow appears on the far right edge of the frame.
"""
import math

from scripts.utils.animation import lerp, ease_in_out_cubic

from scripts.animations.finding_the_one.config import (
    VALLEY_START, VALLEY_END,
    Y_DRIFT_GAVE_UP, Y_DRIFT_REOPENING,
    ORTHO_LONELY,
)
from scripts.animations.finding_the_one.helpers import (
    kf_loc, kf_scale, kf_emission_strength, kf_ortho_scale,
    apply_pulse,
)


def animate_valley(seeker, seeker_mat, the_one, one_mat,
                   seeker_world_positions, seeker_y_out,
                   camera):
    """
    Frames 1650–1800: The Valley — "Almost Gave Up."

    Args:
        seeker, the_one: Blender objects
        seeker_mat, one_mat: materials
        seeker_world_positions: dict frame → world_x
        seeker_y_out: dict to populate with frame → y_position
        camera: camera object for ortho scale
    """

    # ── Frames 1650–1690 (first 1.3s) ────────────────────────
    # Y-drift flatlined, emission dimming, barely moving
    for f in range(1650, 1691):
        t = (f - 1650) / 40.0
        wx = seeker_world_positions.get(f, 0)
        # Flatlined Y-drift: ±0.2
        y = 0.1 * math.sin(f * 0.05)
        seeker_y_out[f] = y
        kf_loc(seeker, wx, y, f)

    # Weak pulse
    apply_pulse(seeker, 1650, 1690, period=60, amplitude=0.02)

    # ── Frames 1690–1740 (middle) ─────────────────────────────
    # Scroll nearly stopped, emission at lowest point
    # Pure black void — all backgrounds gone
    # Ortho scale → 22 (Seeker feels tiny)
    for f in range(1690, 1741):
        t = (f - 1690) / 50.0
        wx = seeker_world_positions.get(f, 0)
        # Almost no drift
        y = 0.05 * math.sin(f * 0.03)
        seeker_y_out[f] = y
        kf_loc(seeker, wx, y, f)

    # Dying heartbeat
    apply_pulse(seeker, 1690, 1740, period=70, amplitude=0.015)

    # ── Frame 1740: THE TURN ─────────────────────────────────
    # A tiny glow appears at extreme right edge
    # The One starts entering from far right
    for f in range(1740, 1771):
        t = (f - 1740) / 30.0
        wx = seeker_world_positions.get(f, 0)

        # The One: faint glow from far right
        one_screen_x = lerp(12, 9, ease_in_out_cubic(t))
        one_world_x = wx + one_screen_x
        one_y = lerp(0.5, 0.3, t)
        kf_loc(the_one, one_world_x, one_y, f)

        # Start very faint, grow brighter
        one_em = lerp(0.3, 1.2, ease_in_out_cubic(t))
        kf_emission_strength(one_mat, one_em, f)

        # Seeker: pulse skips — tiny extra beat
        y = 0.05 * math.sin(f * 0.03)
        seeker_y_out[f] = y
        kf_loc(seeker, wx, y, f)

    # ── Frames 1770–1800 ─────────────────────────────────────
    # Glow is clearly a SQUARE shape. Bright. White.
    # Seeker's emission starts recovering
    # Scroll speed increases
    for f in range(1770, 1801):
        t = (f - 1770) / 30.0
        wx = seeker_world_positions.get(f, 0)

        # The One: getting closer and brighter
        one_screen_x = lerp(9, 8, ease_in_out_cubic(t))
        one_world_x = wx + one_screen_x
        one_y = lerp(0.3, 0.2, t)
        kf_loc(the_one, one_world_x, one_y, f)

        one_em = lerp(1.2, 2.0, ease_in_out_cubic(t))
        kf_emission_strength(one_mat, one_em, f)

        # Seeker: hope stirs
        y = lerp(0, 0.1, ease_in_out_cubic(t))
        seeker_y_out[f] = y
        kf_loc(seeker, wx, y, f)

    # Quickening pulse (1770–1800)
    apply_pulse(seeker, 1740, 1770, period=50, amplitude=0.025)
    apply_pulse(seeker, 1770, 1800, period=45, amplitude=0.03)
