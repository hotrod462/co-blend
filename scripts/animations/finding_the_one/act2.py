"""
Finding the One — Act II: False Hopes (Frames 990–1650)
Slower encounter, self-rotation, triangle drifts away slowly.
"""
import math
from scripts.utils.animation import lerp, ease_in_out_cubic
from scripts.animations.finding_the_one.config import (
    ACT2_START, ACT2_END, FRAME_END,
    ISO_TRI_EMISSION,
)
from scripts.animations.finding_the_one.helpers import (
    kf_loc, kf_scale, kf_rot_z, kf_emission_strength,
    apply_pulse, apply_sigh, lerp_value,
)


def animate_act2(seeker, seeker_mat, iso_tri, iso_tri_mat,
                 seeker_world_positions, seeker_y_out, camera):

    # ── Beat 2.1: Isosceles Entrance (990–1110) ──
    for f in range(990, 1111):
        t = (f - 990) / 120.0
        wx = seeker_world_positions.get(f, 0)
        if t < 0.33:
            lt = t / 0.33
            tri_sx = lerp(12, 6, lt)
            tri_y = lerp(3, 1.5, lt)
        elif t < 0.67:
            lt = (t - 0.33) / 0.34
            tri_sx = lerp(6, 3, lt)
            tri_y = lerp(1.5, 0.5, lt)
        else:
            lt = (t - 0.67) / 0.33
            tri_sx = lerp(3, 1.5, lt)
            tri_y = lerp(0.5, 0.2, lt)
        kf_loc(iso_tri, wx + tri_sx, tri_y, f)
        kf_rot_z(iso_tri, 0, f)
        seeker_y_out[f] = 0
        kf_loc(seeker, wx, 0, f)
    apply_pulse(seeker, 990, 1110, period=45, amplitude=0.03)

    # ── Beat 2.2: Stiff Interaction with SELF-ROTATION (1110–1350) ──
    seeker_spin = 0.0
    tri_spin = 0.0

    # Mutual angular orbit (1110–1180) — slower
    for f in range(1110, 1181):
        t = (f - 1110) / 70.0
        wx = seeker_world_positions.get(f, 0)
        cx, cy = wx, 0
        radius = 1.5
        seg = t * 3  # 0.75 loops (was 4 segments = 1 loop)
        if seg < 1:
            ox = radius
            oy = -radius + 2 * radius * seg
        elif seg < 2:
            ox = radius - 2 * radius * (seg - 1)
            oy = radius
        else:
            ox = -radius
            oy = radius - 2 * radius * (seg - 2)

        kf_loc(iso_tri, cx + ox, cy + oy, f)
        kf_loc(seeker, cx - ox, cy - oy, f)
        seeker_y_out[f] = cy - oy

        # Self-rotation: seeker smooth, triangle rigid/mechanical
        seeker_spin += 0.02
        tri_spin += 0.012  # rigid, slightly slower — mechanical
        kf_rot_z(seeker, seeker_spin, f)
        kf_rot_z(iso_tri, tri_spin, f)

    # Orbit tightens (1180–1220) — slower
    for f in range(1180, 1221):
        t = (f - 1180) / 40.0
        wx = seeker_world_positions.get(f, 0)
        radius = lerp(1.5, 1.0, t)
        cx, cy = wx, 0
        seg = t * 3
        if seg < 1:
            ox = radius
            oy = -radius + 2 * radius * seg
        elif seg < 2:
            ox = radius - 2 * radius * (seg - 1)
            oy = radius
        else:
            ox = -radius
            oy = radius - 2 * radius * (seg - 2)

        kf_loc(iso_tri, cx + ox, cy + oy, f)
        kf_loc(seeker, cx - ox, cy - oy, f)
        seeker_y_out[f] = cy - oy

        seeker_spin += 0.02
        tri_spin += 0.012
        kf_rot_z(seeker, seeker_spin, f)
        kf_rot_z(iso_tri, tri_spin, f)

    # THE TEASE: wide base faces Seeker (1220–1270)
    for f in range(1220, 1271):
        t = (f - 1220) / 50.0
        wx = seeker_world_positions.get(f, 0)
        if t < 0.2:
            lt = t / 0.2
            gap = lerp(1.0, 0.5, ease_in_out_cubic(lt))
        else:
            lt = (t - 0.2) / 0.8
            gap = lerp(0.5, 0.15, ease_in_out_cubic(min(lt * 1.5, 1.0)))
        kf_loc(iso_tri, wx + gap / 2 + 0.2, 0, f)
        kf_loc(seeker, wx - gap / 2 + 0.2, 0, f)
        seeker_y_out[f] = 0

        seeker_spin += 0.02
        tri_spin += 0.012
        kf_rot_z(seeker, seeker_spin, f)
        kf_rot_z(iso_tri, tri_spin, f)

    apply_pulse(seeker, 1220, 1270, period=30, amplitude=0.04)

    # Rotation reveals taper — BONK (1270–1300)
    for f in range(1270, 1301):
        t = (f - 1270) / 30.0
        wx = seeker_world_positions.get(f, 0)
        rot = lerp(0, math.pi / 4, ease_in_out_cubic(t))
        bump = 0.3 * math.sin(t * math.pi)
        kf_loc(iso_tri, wx + 0.5 + bump, bump * 0.5, f)
        recoil_y = -0.3 * ease_in_out_cubic(t)
        seeker_y_out[f] = recoil_y
        kf_loc(seeker, wx + recoil_y * 0.2, recoil_y, f)

        # Wind down seeker spin, triangle keeps rigid
        seeker_spin = lerp(seeker_spin, 0, t * 0.5)
        tri_spin += 0.012
        kf_rot_z(seeker, seeker_spin, f)
        kf_rot_z(iso_tri, tri_spin + rot, f)

    # Wind seeker rotation back to 0 (1300–1320)
    for f in range(1300, 1321):
        t = (f - 1300) / 20.0
        kf_rot_z(seeker, lerp(seeker_spin, 0, ease_in_out_cubic(t)), f)

    # Triangle resumes orbit, doesn't care (1300–1360)
    for f in range(1300, 1361):
        t = (f - 1300) / 60.0
        wx = seeker_world_positions.get(f, 0)
        seg = t * 2
        radius = 1.2
        tri_ox = radius * math.cos(seg * math.pi)
        tri_oy = radius * math.sin(seg * math.pi)
        kf_loc(iso_tri, wx + tri_ox, tri_oy, f)
        tri_spin += 0.012
        kf_rot_z(iso_tri, tri_spin, f)
        seeker_y_out[f] = lerp(-0.3, -1.0, ease_in_out_cubic(t))
        kf_loc(seeker, wx, seeker_y_out[f], f)

    apply_pulse(seeker, 1270, 1360, period=50, amplitude=0.02)

    # ── Beat 2.3: Triangle drifts away slowly (1360–1700) ──
    tri_anchor_x = seeker_world_positions.get(1360, 0) + 1.2
    tri_anchor_y = 0.0
    kf_loc(iso_tri, tri_anchor_x, tri_anchor_y, 1360)
    kf_loc(iso_tri, tri_anchor_x, tri_anchor_y - 1.5, 1700)  # drift down
    kf_emission_strength(iso_tri_mat, ISO_TRI_EMISSION, 1360)
    kf_emission_strength(iso_tri_mat, 0.0, 1700)
    kf_rot_z(iso_tri, tri_spin, 1360)
    kf_rot_z(iso_tri, tri_spin + 0.5, 1700)

    # Park offscreen after fade
    kf_loc(iso_tri, -60, 10, 1701)
    for f in range(1701, FRAME_END + 1, 100):
        kf_loc(iso_tri, -60, 10, f)

    # Seeker drifts sadly (1360–1500)
    for f in range(1360, 1501):
        t = (f - 1360) / 140.0
        wx = seeker_world_positions.get(f, 0)
        if t < 0.33:
            y = lerp(-1.0, -1.5, ease_in_out_cubic(t / 0.33))
        else:
            y = -1.5
        seeker_y_out[f] = y
        kf_loc(seeker, wx, y, f)
    apply_pulse(seeker, 1360, 1500, period=55, amplitude=0.02)

    # ── Beat 2.4: Alone Again (1500–1650) ──
    for f in range(1500, 1651):
        t = (f - 1500) / 150.0
        wx = seeker_world_positions.get(f, 0)
        if t < 0.27:
            y = -1.5
        elif t < 0.53:
            y = lerp(-1.5, -2.0, ease_in_out_cubic((t - 0.27) / 0.26))
        elif t < 0.80:
            y = lerp(-2.0, -1.5, ease_in_out_cubic((t - 0.53) / 0.27))
        else:
            y = lerp(-1.5, -0.5, ease_in_out_cubic((t - 0.80) / 0.20))
        seeker_y_out[f] = y
        kf_loc(seeker, wx, y, f)
    apply_sigh(seeker, 1500, 1540, depth=0.06)
    apply_pulse(seeker, 1540, 1650, period=55, amplitude=0.02)
