"""
Finding the One — The Valley (Frames 2400–2550)
Smooth transition from Act 2 ending Y.
Uses dynamic relative timing based on VALLEY_START.
"""
import math
from scripts.utils.animation import lerp, ease_in_out_cubic
from scripts.animations.finding_the_one.config import VALLEY_START, VALLEY_END
from scripts.animations.finding_the_one.helpers import (
    kf_loc, kf_scale, kf_emission_strength, apply_pulse,
)


def animate_valley(seeker, seeker_mat, the_one, one_mat,
                   seeker_world_positions, seeker_y_out, camera):
    
    start = VALLEY_START
    # Define phase boundaries relative to start
    phase1_end = start + 40  # Transition down
    phase2_end = start + 90 # Flatline
    phase3_end = start + 120 # The Turn
    end = VALLEY_END        # Glow Brightens

    # Transition from Act 2 end (Y ≈ -1.8) to flatlined 0
    for f in range(start, phase1_end + 1):
        t = (f - start) / 40.0
        wx = seeker_world_positions.get(f, 0)
        base_y = lerp(-1.8, 0, ease_in_out_cubic(min(t * 2, 1.0)))
        y = base_y + 0.1 * math.sin(f * 0.05)
        seeker_y_out[f] = y
        kf_loc(seeker, wx, y, f)

    for f in range(start, phase2_end):
        kf_loc(the_one, -60, 0, f)

    apply_pulse(seeker, start, phase1_end, period=60, amplitude=0.02)

    # Middle: nearly stopped, dimmest
    for f in range(phase1_end, phase2_end + 1):
        wx = seeker_world_positions.get(f, 0)
        y = 0.05 * math.sin(f * 0.03)
        seeker_y_out[f] = y
        kf_loc(seeker, wx, y, f)
    apply_pulse(seeker, phase1_end, phase2_end, period=70, amplitude=0.015)

    # THE TURN: tiny glow from far right
    for f in range(phase2_end, phase3_end + 1):
        t = (f - phase2_end) / 30.0
        wx = seeker_world_positions.get(f, 0)
        one_sx = lerp(12, 9, ease_in_out_cubic(t))
        kf_loc(the_one, wx + one_sx, lerp(0.5, 0.3, t), f)
        kf_emission_strength(one_mat, lerp(0.3, 1.2, ease_in_out_cubic(t)), f)
        y = 0.05 * math.sin(f * 0.03)
        seeker_y_out[f] = y
        kf_loc(seeker, wx, y, f)

    # Glow brightens
    for f in range(phase3_end, end + 1):
        t = (f - phase3_end) / 30.0
        wx = seeker_world_positions.get(f, 0)
        one_sx = lerp(9, 8, ease_in_out_cubic(t))
        kf_loc(the_one, wx + one_sx, lerp(0.3, 0.2, t), f)
        kf_emission_strength(one_mat, lerp(1.2, 2.0, ease_in_out_cubic(t)), f)
        y = lerp(0, 0.1, ease_in_out_cubic(t))
        seeker_y_out[f] = y
        kf_loc(seeker, wx, y, f)

    apply_pulse(seeker, phase2_end, phase3_end, period=50, amplitude=0.025)
    apply_pulse(seeker, phase3_end, end, period=45, amplitude=0.03)
