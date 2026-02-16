"""
Finding the One — Act III: Discovery (Frames 1800–2460, 60s–82s)

The One appears ahead. Cautious approach, mutual recognition, joyful
orbiting (smooth circles contrasting with triangles' angular orbits),
and the payoff: flat sides align flush — The Click.

KEY: They should orbit FIRST, then join at the end (they only touch
when "The Click" happens — flat sides meeting flush).
"""
import math

from scripts.utils.animation import lerp, ease_in_out_cubic

from scripts.animations.finding_the_one.config import (
    ACT3_START, ACT3_END,
    SEEKER_SIZE, ONE_SIZE,
    ORTHO_CLICK,
)
from scripts.animations.finding_the_one.helpers import (
    kf_loc, kf_scale, kf_rot_z, kf_emission_strength,
    kf_ortho_scale, apply_pulse, lerp_value,
)


def animate_act3(seeker, seeker_mat, the_one, one_mat,
                 seeker_world_positions, seeker_y_out,
                 camera):
    """
    Frames 1800–2460: Discovery.

    The One approaches from ahead. They recognise each other, begin
    orbiting (smooth circles), spiral closer, and finally their flat
    sides align flush — The Click. They only TOUCH at the very end.

    Args:
        seeker, the_one: Blender objects
        seeker_mat, one_mat: materials
        seeker_world_positions: dict frame → world_x
        seeker_y_out: dict to populate with frame → y_position
        camera: camera object for ortho scale

    Returns:
        final_angle: the accumulated orbit angle for Act 4 continuity
    """

    # ── Beat 3.1: The One Appears Ahead (Frames 1800–1950) ───
    # The One closes from far ahead. They do NOT touch yet.
    # Gap remains at ~1.5 screen units at end of this beat.
    for f in range(1800, 1951):
        t = (f - 1800) / 150.0
        wx = seeker_world_positions.get(f, 0)

        # The One: closing from screen-relative +8 to +1.5
        # Slows down as it approaches — cautious
        if t < 0.33:
            # (+8, 0.5) closing
            lt = t / 0.33
            one_screen_x = lerp(8, 5, ease_in_out_cubic(lt))
            one_y = lerp(0.5, 0.3, lt)
        elif t < 0.53:
            # (+5, 0.3) noticing
            lt = (t - 0.33) / 0.20
            one_screen_x = lerp(5, 3, ease_in_out_cubic(lt))
            one_y = lerp(0.3, 0.2, lt)
        elif t < 0.73:
            # (+3, 0.2) approaching cautiously
            lt = (t - 0.53) / 0.20
            one_screen_x = lerp(3, 2.0, ease_in_out_cubic(lt))
            one_y = lerp(0.2, 0.1, lt)
        else:
            # Holding distance — still gap of ~2.0
            lt = (t - 0.73) / 0.27
            one_screen_x = lerp(2.0, 1.8, ease_in_out_cubic(lt))
            one_y = lerp(0.1, 0.05, lt)

        one_world_x = wx + one_screen_x
        kf_loc(the_one, one_world_x, one_y, f)
        kf_emission_strength(one_mat, 2.0, f)

        # Seeker: rising hope, smooth from valley end Y ≈ 0.1
        if t < 0.5:
            y = lerp(0.1, 0, ease_in_out_cubic(t * 2))
        else:
            y = lerp(0, 0.05, ease_in_out_cubic((t - 0.5) * 2))
        seeker_y_out[f] = y
        kf_loc(seeker, wx, y, f)

    # Both pulsing in sync from now on
    apply_pulse(seeker,  1800, 1950, period=45, amplitude=0.03)
    apply_pulse(the_one, 1800, 1950, period=45, amplitude=0.03)

    # ── Beat 3.2: Mutual Recognition (Frames 1950–2040) ──────
    # They recognise each other but maintain distance.
    # Gap narrows from ~1.8 to ~1.0 (orbit start radius)
    for f in range(1950, 2041):
        t = (f - 1950) / 90.0
        wx = seeker_world_positions.get(f, 0)

        if t < 0.33:
            # Frozen — 30 frames of stillness, feeling each other out
            one_screen_x = 1.8
            one_y = 0.05
            seeker_y = 0.05
        elif t < 0.60:
            # Tentative approach — gap shrinks but still not touching
            lt = (t - 0.33) / 0.27
            one_screen_x = lerp(1.8, 1.4, ease_in_out_cubic(lt))
            one_y = lerp(0.05, 0, lt)
            seeker_y = lerp(0.05, 0, lt)
        else:
            # Close enough for orbit — gap = ~1.2 (radius 0.6 each side)
            lt = (t - 0.60) / 0.40
            one_screen_x = lerp(1.4, 1.2, ease_in_out_cubic(lt))
            one_y = 0
            seeker_y = 0

        one_world_x = wx + one_screen_x
        kf_loc(the_one, one_world_x, one_y, f)
        seeker_y_out[f] = seeker_y
        kf_loc(seeker, wx, seeker_y, f)

    # Perfect pulse sync
    apply_pulse(seeker,  1950, 2040, period=45, amplitude=0.03)
    apply_pulse(the_one, 1950, 2040, period=45, amplitude=0.03)

    # ── Beat 3.3: First Orbit (Frames 2040–2250) ─────────────
    # SMOOTH circular orbiting — contrast with triangles' angular orbits
    # They orbit around their MIDPOINT (both move, not just one)
    # Starting radius = ~0.8 (well separated), never touching during orbit
    # Scroll near-stopped

    angle = 0.0

    for f in range(2040, 2251):
        t = (f - 2040) / 210.0
        wx = seeker_world_positions.get(f, 0)

        # Orbit center at midpoint (offset from Seeker's world X)
        cx = wx + 0.6  # midpoint between them
        cy = 0

        # Speed and radius ramps — radius stays large enough to not touch
        if f <= 2110:
            # Gentle: slow spin, radius 0.8
            rev_speed = 1.0 / 120.0
            r = 0.8
        elif f <= 2160:
            # Growing comfort
            rev_speed = 1.0 / 80.0
            st = (f - 2110) / 50.0
            r = lerp(0.8, 0.7, ease_in_out_cubic(st))
        elif f <= 2200:
            # Joyful! — still not touching (0.5 radius = 1.0 gap between surfaces)
            rev_speed = 1.0 / 40.0
            st = (f - 2160) / 40.0
            r = lerp(0.7, 0.55, ease_in_out_cubic(st))
        else:
            # Exuberant! Getting closer — 0.45 radius, still a gap
            rev_speed = 1.0 / 25.0
            st = (f - 2200) / 50.0
            r = lerp(0.55, 0.45, ease_in_out_cubic(st))

        angle += rev_speed * 2 * math.pi

        sx = cx + r * math.cos(angle)
        sy = cy + r * math.sin(angle)
        ox = cx + r * math.cos(angle + math.pi)
        oy = cy + r * math.sin(angle + math.pi)

        kf_loc(seeker, sx, sy, f)
        kf_loc(the_one, ox, oy, f)
        seeker_y_out[f] = sy

    # Joy pulse — faster, shared
    apply_pulse(seeker,  2040, 2250, period=35, amplitude=0.04)
    apply_pulse(the_one, 2040, 2250, period=35, amplitude=0.04)

    # Store the accumulated angle for Beat 3.4
    beat33_final_angle = angle

    # ── Beat 3.4: Side Alignment — "The Click" (Frames 2250–2460) ──
    # Decelerate, flat sides align, and ONLY NOW do they slide together
    # to touch flush. This is the payoff — they only touch at the end.

    angle_34 = beat33_final_angle

    for f in range(2250, 2461):
        t = (f - 2250) / 210.0
        wx = seeker_world_positions.get(f, 0)
        cx = wx + 0.6
        cy = 0

        if f <= 2300:
            # Winding down — still orbiting, radius shrinking
            st = (f - 2250) / 50.0
            rev_speed = lerp(1.0 / 25.0, 1.0 / 60.0, ease_in_out_cubic(st))
            r = lerp(0.45, 0.38, ease_in_out_cubic(st))
            angle_34 += rev_speed * 2 * math.pi
        elif f <= 2350:
            # Almost still — radius shrinks more
            st = (f - 2300) / 50.0
            rev_speed = lerp(1.0 / 60.0, 1.0 / 200.0, ease_in_out_cubic(st))
            r = lerp(0.38, 0.33, ease_in_out_cubic(st))
            angle_34 += rev_speed * 2 * math.pi
        elif f <= 2390:
            # Final quarter-turn — flat sides face each other
            # Radius approaches just-touching distance
            st = (f - 2350) / 40.0
            rev_speed = lerp(1.0 / 200.0, 0, ease_in_out_cubic(st))
            # SEEKER_SIZE/2 = 0.3, so r = 0.3 means sides touch
            r = lerp(0.33, SEEKER_SIZE / 2 + 0.03, ease_in_out_cubic(st))
            angle_34 += rev_speed * 2 * math.pi
        elif f <= 2420:
            # THE CLICK: slide together, gap → 0
            # This is the FIRST MOMENT they actually touch
            st = (f - 2390) / 30.0
            gap = lerp(0.03, 0.0, ease_in_out_cubic(st))
            r = SEEKER_SIZE / 2 + gap
        elif f <= 2440:
            # Hold perfectly flush — combined rectangle
            r = SEEKER_SIZE / 2
            # One slow rotation echo of the intro
            st = (f - 2420) / 20.0
            rot_echo = st * math.pi / 4  # quarter turn
            angle_34 += rot_echo / 20.0
        else:
            # Pulse intensifies: shared heartbeat
            r = SEEKER_SIZE / 2

        sx = cx + r * math.cos(angle_34)
        sy = cy + r * math.sin(angle_34)
        ox = cx + r * math.cos(angle_34 + math.pi)
        oy = cy + r * math.sin(angle_34 + math.pi)

        kf_loc(seeker, sx, sy, f)
        kf_loc(the_one, ox, oy, f)
        seeker_y_out[f] = sy

    # Intensifying shared pulse
    apply_pulse(seeker,  2250, 2390, period=40, amplitude=0.03)
    apply_pulse(the_one, 2250, 2390, period=40, amplitude=0.03)
    apply_pulse(seeker,  2390, 2460, period=40, amplitude=0.06)
    apply_pulse(the_one, 2390, 2460, period=40, amplitude=0.06)

    # Store the final angle and position for Act 4
    return angle_34
