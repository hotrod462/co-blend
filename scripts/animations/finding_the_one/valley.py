"""
Finding the One — The Valley (Frames 1650–1800)
Smooth transition from Act 2 ending Y.
"""
import math
from scripts.utils.animation import lerp, ease_in_out_cubic
from scripts.animations.finding_the_one.config import VALLEY_START, VALLEY_END
from scripts.animations.finding_the_one.helpers import (
    kf_loc, kf_scale, kf_emission_strength, apply_pulse,
)


def animate_valley(seeker, seeker_mat, the_one, one_mat,
                   seeker_world_positions, seeker_y_out, camera):

    # Transition from Act 2 end (Y ≈ -0.5) to flatlined
    for f in range(1650, 1691):
        t = (f - 1650) / 40.0
        wx = seeker_world_positions.get(f, 0)
        base_y = lerp(-0.5, 0, ease_in_out_cubic(min(t * 2, 1.0)))
        y = base_y + 0.1 * math.sin(f * 0.05)
        seeker_y_out[f] = y
        kf_loc(seeker, wx, y, f)

    for f in range(1650, 1740):
        kf_loc(the_one, -60, 0, f)

    apply_pulse(seeker, 1650, 1690, period=60, amplitude=0.02)

    # Middle: nearly stopped, dimmest (1690–1740)
    for f in range(1690, 1741):
        wx = seeker_world_positions.get(f, 0)
        y = 0.05 * math.sin(f * 0.03)
        seeker_y_out[f] = y
        kf_loc(seeker, wx, y, f)
    apply_pulse(seeker, 1690, 1740, period=70, amplitude=0.015)

    # THE TURN: tiny glow from far right (1740–1770)
    for f in range(1740, 1771):
        t = (f - 1740) / 30.0
        wx = seeker_world_positions.get(f, 0)
        one_sx = lerp(12, 9, ease_in_out_cubic(t))
        kf_loc(the_one, wx + one_sx, lerp(0.5, 0.3, t), f)
        kf_emission_strength(one_mat, lerp(0.3, 1.2, ease_in_out_cubic(t)), f)
        y = 0.05 * math.sin(f * 0.03)
        seeker_y_out[f] = y
        kf_loc(seeker, wx, y, f)

    # Glow brightens (1770–1800)
    for f in range(1770, 1801):
        t = (f - 1770) / 30.0
        wx = seeker_world_positions.get(f, 0)
        one_sx = lerp(9, 8, ease_in_out_cubic(t))
        kf_loc(the_one, wx + one_sx, lerp(0.3, 0.2, t), f)
        kf_emission_strength(one_mat, lerp(1.2, 2.0, ease_in_out_cubic(t)), f)
        y = lerp(0, 0.1, ease_in_out_cubic(t))
        seeker_y_out[f] = y
        kf_loc(seeker, wx, y, f)

    apply_pulse(seeker, 1740, 1770, period=50, amplitude=0.025)
    apply_pulse(seeker, 1770, 1800, period=45, amplitude=0.03)
