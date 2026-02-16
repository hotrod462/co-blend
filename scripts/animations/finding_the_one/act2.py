"""
Finding the One — Act II: False Hopes (Frames 990–1650, 33s–55s)

The Seeker encounters an isosceles triangle — rigid, mechanical, with a
wide base that almost matches. The tease is stronger and longer. After
the second rejection, the Seeker sinks deeper into sadness. Background
triangles start thinning out.
"""
import math

from scripts.utils.animation import lerp, ease_in_out_cubic

from scripts.animations.finding_the_one.config import (
    ACT2_START, ACT2_END,
    ISO_TRI_EMISSION,
    Y_DRIFT_AFTER_1ST, Y_DRIFT_AFTER_2ND,
    ORTHO_ENCOUNTER,
)
from scripts.animations.finding_the_one.helpers import (
    kf_loc, kf_scale, kf_rot_z, kf_emission_strength,
    kf_ortho_scale, apply_pulse, apply_sigh,
    move_along, lerp_value,
)


def animate_act2(seeker, seeker_mat, iso_tri, iso_tri_mat,
                 seeker_world_positions, seeker_y_out,
                 camera):
    """
    Frames 990–1650: False Hopes.

    Args:
        seeker, iso_tri: Blender objects
        seeker_mat, iso_tri_mat: materials
        seeker_world_positions: dict frame → world_x
        seeker_y_out: dict to populate with frame → y_position
        camera: camera object for ortho scale
    """

    # ── Beat 2.1: Isosceles Entrance (Frames 990–1110) ───────
    # Enters from upper-right, rigid mechanical approach
    # Transition: Seeker ends Act I at Y=0, start smoothly from there
    for f in range(990, 1111):
        t = (f - 990) / 120.0
        wx = seeker_world_positions.get(f, 0)

        if t < 0.33:
            # Enter from (+12, 3), straight down to (+6, 1.5)
            lt = t / 0.33
            tri_screen_x = lerp(12, 6, lt)
            tri_y = lerp(3, 1.5, lt)
        elif t < 0.67:
            # (+6, 1.5) → (+3, 0.5), 90° turn
            lt = (t - 0.33) / 0.34
            tri_screen_x = lerp(6, 3, lt)
            tri_y = lerp(1.5, 0.5, lt)
        else:
            # (+3, 0.5) → (+1.5, 0.2), slow approach
            lt = (t - 0.67) / 0.33
            tri_screen_x = lerp(3, 1.5, lt)
            tri_y = lerp(0.5, 0.2, lt)

        tri_world_x = wx + tri_screen_x
        kf_loc(iso_tri, tri_world_x, tri_y, f)
        # Rigid: no rotation wobble
        kf_rot_z(iso_tri, 0, f)

        # Seeker holds near center
        seeker_y_out[f] = 0
        kf_loc(seeker, wx, 0, f)

    apply_pulse(seeker, 990, 1110, period=45, amplitude=0.03)

    # ── Beat 2.2: Stiff Interaction (Frames 1110–1350) ────────
    # MUTUAL angular orbit — both orbit around midpoint with square-shaped paths
    # (1110–1170): radius 1.5, angular orbit
    for f in range(1110, 1171):
        t = (f - 1110) / 60.0
        wx = seeker_world_positions.get(f, 0)

        # Center point between them
        cx = wx
        cy = 0

        # Square-shaped orbit for angular/mechanical feel
        seg = t * 4
        radius = 1.5
        if seg < 1:
            ox = radius
            oy = -radius + 2 * radius * seg
        elif seg < 2:
            ox = radius - 2 * radius * (seg - 1)
            oy = radius
        elif seg < 3:
            ox = -radius
            oy = radius - 2 * radius * (seg - 2)
        else:
            ox = -radius + 2 * radius * (seg - 3)
            oy = -radius

        # Triangle and Seeker orbit opposite each other
        kf_loc(iso_tri, cx + ox, cy + oy, f)
        kf_loc(seeker, cx - ox, cy - oy, f)
        kf_rot_z(iso_tri, 0, f)
        seeker_y_out[f] = cy - oy

    # (1170–1210): Orbit tightens to 1.0, still angular, mutual
    for f in range(1170, 1211):
        t = (f - 1170) / 40.0
        wx = seeker_world_positions.get(f, 0)
        radius = lerp(1.5, 1.0, t)

        cx = wx
        cy = 0

        seg = t * 4
        if seg < 1:
            ox = radius
            oy = -radius + 2 * radius * seg
        elif seg < 2:
            ox = radius - 2 * radius * (seg - 1)
            oy = radius
        elif seg < 3:
            ox = -radius
            oy = radius - 2 * radius * (seg - 2)
        else:
            ox = -radius + 2 * radius * (seg - 3)
            oy = -radius

        # Both orbit opposite each other
        kf_loc(iso_tri, cx + ox, cy + oy, f)
        kf_loc(seeker, cx - ox, cy - oy, f)
        seeker_y_out[f] = cy - oy

    # THE STRONGER TEASE: Wide base faces Seeker — 0.15 gap (1210–1260)
    # 50 frames! Almost matches!
    for f in range(1210, 1261):
        t = (f - 1210) / 50.0
        wx = seeker_world_positions.get(f, 0)

        # Transition from final orbit position to face-to-face
        if t < 0.2:
            # Settle from orbit to aligned approach
            lt = t / 0.2
            gap = lerp(1.0, 0.5, ease_in_out_cubic(lt))
            tri_x = wx + gap / 2 + 0.2
            tri_y = 0
            seeker_x = wx - gap / 2 + 0.2
            seeker_y = 0
        else:
            # Hold close, base facing Seeker
            lt = (t - 0.2) / 0.8
            gap = lerp(0.5, 0.15, ease_in_out_cubic(min(lt * 1.5, 1.0)))
            tri_x = wx + gap / 2 + 0.2
            tri_y = 0
            seeker_x = wx - gap / 2 + 0.2
            seeker_y = 0

        kf_loc(iso_tri, tri_x, tri_y, f)
        kf_rot_z(iso_tri, 0, f)  # base faces Seeker
        seeker_y_out[f] = seeker_y
        kf_loc(seeker, seeker_x, seeker_y, f)

    apply_pulse(seeker, 1210, 1260, period=30, amplitude=0.04)

    # Rotation reveals taper — flush breaks (1260–1290)
    for f in range(1260, 1291):
        t = (f - 1260) / 30.0
        wx = seeker_world_positions.get(f, 0)

        # Triangle rotates, revealing the taper
        rot = lerp(0, math.pi / 4, ease_in_out_cubic(t))
        kf_rot_z(iso_tri, rot, f)
        # Soft bump
        bump = 0.3 * math.sin(t * math.pi)
        kf_loc(iso_tri, wx + 0.5 + bump, bump * 0.5, f)

        # Seeker wobbles, recoils
        recoil_y = -0.3 * ease_in_out_cubic(t)
        seeker_y_out[f] = recoil_y
        kf_loc(seeker, wx + recoil_y * 0.2, recoil_y, f)

    # Triangle resumes rigid orbit, doesn't care (1290–1350)
    for f in range(1290, 1351):
        t = (f - 1290) / 60.0
        wx = seeker_world_positions.get(f, 0)

        seg = t * 2  # slower orbit
        radius = 1.2
        tri_ox = radius * math.cos(seg * math.pi)
        tri_oy = radius * math.sin(seg * math.pi)

        kf_loc(iso_tri, wx + tri_ox, tri_oy, f)
        kf_rot_z(iso_tri, 0, f)

        # Seeker drifts away
        seeker_y_out[f] = lerp(-0.3, -1.0, ease_in_out_cubic(t))
        kf_loc(seeker, wx, seeker_y_out[f], f)

    apply_pulse(seeker, 1260, 1350, period=50, amplitude=0.02)

    # ── Beat 2.3: Sad Separation (Frames 1350–1500) ──────────
    for f in range(1350, 1501):
        t = (f - 1350) / 150.0
        wx = seeker_world_positions.get(f, 0)

        # Triangle falls behind (scroll carries it left)
        tri_world_x = seeker_world_positions.get(1350, 0) + 1.2
        tri_y = lerp(0, 2, t)  # drifts up and away
        kf_loc(iso_tri, tri_world_x, tri_y, f)
        kf_rot_z(iso_tri, 0, f)

        # Fade triangle emission
        tri_em = lerp(ISO_TRI_EMISSION, 0.0, ease_in_out_cubic(t))
        kf_emission_strength(iso_tri_mat, tri_em, f)

        # Seeker drifts sadly — smooth transition from -1.0
        if t < 0.33:
            y = lerp(-1.0, -1.5, ease_in_out_cubic(t / 0.33))
        elif t < 0.67:
            y = -1.5
        else:
            y = -1.5
        seeker_y_out[f] = y
        kf_loc(seeker, wx, y, f)

    apply_pulse(seeker, 1350, 1500, period=55, amplitude=0.02)

    # Park triangle offscreen
    for f in range(1501, ACT2_END + 1):
        kf_loc(iso_tri, -60, 10, f)

    # ── Beat 2.4: Alone Again (Frames 1500–1650) ─────────────
    for f in range(1500, 1651):
        t = (f - 1500) / 150.0
        wx = seeker_world_positions.get(f, 0)

        # Deep sadness, sinking — smooth from -1.5
        if t < 0.27:
            y = -1.5  # hold
        elif t < 0.53:
            y = lerp(-1.5, -2.0, ease_in_out_cubic((t - 0.27) / 0.26))
        elif t < 0.80:
            y = lerp(-2.0, -1.5, ease_in_out_cubic((t - 0.53) / 0.27))
        else:
            y = lerp(-1.5, -0.5, ease_in_out_cubic((t - 0.80) / 0.20))

        seeker_y_out[f] = y
        kf_loc(seeker, wx, y, f)

    # Sigh at start
    apply_sigh(seeker, 1500, 1540, depth=0.06)
    apply_pulse(seeker, 1540, 1650, period=55, amplitude=0.02)
