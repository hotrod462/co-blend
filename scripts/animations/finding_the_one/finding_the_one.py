"""
Finding the One — Main Animation Script (v4)

A 105-second black-and-white Heider-Simmel-inspired animation about a
small square journeying through a world of triangles, searching for
its perfect match.

Run:
    ./render.sh scripts/animations/finding_the_one/finding_the_one.py
    ./render.sh scripts/animations/finding_the_one/finding_the_one.py --gui
    ./render.sh scripts/animations/finding_the_one/finding_the_one.py --watch

Architecture:
    This is the orchestrator. It imports all modules and calls them
    in order. Each act is a separate file for maintainability.

    config.py       → All constants and timing
    helpers.py      → Keyframing shortcuts (kf_loc, kf_scale, etc.)
    characters.py   → Shape creation factories
    systems.py      → Scrolling camera, trails, emission curves, BG management
    prologue.py     → Frames 1–330
    act1.py         → Frames 330–990
    act2.py         → Frames 990–1650
    valley.py       → Frames 1650–1800
    act3.py         → Frames 1800–2460
    act4.py         → Frames 2460–3150
"""
import bpy
import sys
import os

# ── Project root on sys.path ──
project_root = os.getcwd()
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# ── Utility imports ──
from scripts.utils.scene import (
    clear_scene, setup_ortho_camera, setup_world_color,
    setup_render, frames_to_video,
)

# ── Project imports ──
from scripts.animations.finding_the_one.config import (
    FPS, FRAME_START, FRAME_END,
    ORTHO_NORMAL, ORTHO_ENCOUNTER, ORTHO_LONELY, ORTHO_CLICK, ORTHO_WIDE,
    CAMERA_HEIGHT,
)
from scripts.animations.finding_the_one.helpers import (
    set_all_linear_interpolation, set_viewport_to_camera,
)
from scripts.animations.finding_the_one.characters import (
    create_parent_triangles,
    create_seeker,
    create_right_angle_triangle,
    create_isosceles_triangle,
    create_the_one,
    create_background_triangles,
)
from scripts.animations.finding_the_one.systems import (
    build_scroll_schedule,
    setup_scrolling_camera,
    apply_seeker_emission_curve,
    animate_background_triangles,
    apply_ortho_scale_shifts,
)
from scripts.animations.finding_the_one.prologue import animate_prologue
from scripts.animations.finding_the_one.act1 import animate_act1
from scripts.animations.finding_the_one.act2 import animate_act2
from scripts.animations.finding_the_one.valley import animate_valley
from scripts.animations.finding_the_one.act3 import animate_act3
from scripts.animations.finding_the_one.act4 import animate_act4


# ══════════════════════════════════════════════════════════════
#  SCENE SETUP
# ══════════════════════════════════════════════════════════════

clear_scene()
setup_world_color(color=(0, 0, 0, 1))

camera = setup_ortho_camera(
    location=(0, 0, CAMERA_HEIGHT),
    ortho_scale=ORTHO_NORMAL,
)

setup_render(
    resolution=(1920, 1080),
    fps=FPS,
    frame_start=FRAME_START,
    frame_end=FRAME_END,
    output_path='./output/finding_the_one',
)


# ══════════════════════════════════════════════════════════════
#  BUILD SCROLL SCHEDULE
# ══════════════════════════════════════════════════════════════

seeker_world_positions, scroll_speeds = build_scroll_schedule()


# ══════════════════════════════════════════════════════════════
#  CREATE CHARACTERS
# ══════════════════════════════════════════════════════════════

parents = create_parent_triangles()
parent_a, parent_a_mat = parents[0]
parent_b, parent_b_mat = parents[1]

seeker, seeker_mat = create_seeker()
right_tri, right_tri_mat = create_right_angle_triangle()
iso_tri, iso_tri_mat = create_isosceles_triangle()
the_one, one_mat = create_the_one()
bg_triangles = create_background_triangles()


# (Trail lines removed — not rendering properly)


# ══════════════════════════════════════════════════════════════
#  CHOREOGRAPHY — Execute each act in order
# ══════════════════════════════════════════════════════════════

# Dict to accumulate Seeker's Y position across acts
seeker_y_positions = {}


# ── Prologue (1–330) ──
print("🎬 Building Prologue...")
animate_prologue(
    parent_a, parent_a_mat, parent_b, parent_b_mat,
    seeker, seeker_mat, seeker_world_positions,
)
# Prologue handles its own Y positioning; fill in for systems
for f in range(1, 331):
    seeker_y_positions[f] = 0  # approximate


# ── Act I (330–990) ──
print("🎬 Building Act I...")
animate_act1(
    seeker, seeker_mat, right_tri, right_tri_mat,
    the_one, one_mat,
    seeker_world_positions, seeker_y_positions,
    camera,
)


# ── Act II (990–1650) ──
print("🎬 Building Act II...")
animate_act2(
    seeker, seeker_mat, iso_tri, iso_tri_mat,
    seeker_world_positions, seeker_y_positions,
    camera,
)


# ── The Valley (1650–1800) ──
print("🎬 Building The Valley...")
animate_valley(
    seeker, seeker_mat, the_one, one_mat,
    seeker_world_positions, seeker_y_positions,
    camera,
)


# ── Act III (1800–2460) ──
print("🎬 Building Act III...")
final_angle = animate_act3(
    seeker, seeker_mat, the_one, one_mat,
    seeker_world_positions, seeker_y_positions,
    camera,
)


# ── Act IV (2460–3150) ──
print("🎬 Building Act IV...")
animate_act4(
    seeker, seeker_mat, the_one, one_mat,
    seeker_world_positions, seeker_y_positions,
    camera, final_angle,
)


# ══════════════════════════════════════════════════════════════
#  GLOBAL SYSTEMS (span entire timeline, applied after acts)
# ══════════════════════════════════════════════════════════════

print("🎬 Applying global systems...")

# Camera tracking — follows Seeker's world X position
setup_scrolling_camera(camera, seeker_world_positions)

# Seeker emission curve (emotional barometer)
apply_seeker_emission_curve(seeker_mat)

# Background triangle density and fading
animate_background_triangles(bg_triangles, seeker_world_positions)

# (Trail lines removed)

# Orthographic scale shifts for emotional moments
ortho_keyframes = [
    (1,    ORTHO_NORMAL),
    (630,  ORTHO_NORMAL),
    (680,  ORTHO_ENCOUNTER),    # Encounter 1
    (870,  ORTHO_NORMAL),       # Recovery
    (1070, ORTHO_ENCOUNTER),    # Encounter 2
    (1350, ORTHO_NORMAL),       # Separation
    (1690, ORTHO_LONELY),       # Valley — Seeker feels small
    (1800, ORTHO_NORMAL),       # Discovery begins
    (1950, ORTHO_CLICK),        # Mutual recognition — intimate
    (2250, ORTHO_CLICK),        # During orbit
    (2460, ORTHO_NORMAL),       # Union
    (2670, ORTHO_NORMAL),       # Accelerating
    (2850, ORTHO_WIDE),         # World expanding
    (3100, ORTHO_WIDE),         # Hold
    (3150, ORTHO_WIDE),         # End
]
apply_ortho_scale_shifts(camera, ortho_keyframes)


# ══════════════════════════════════════════════════════════════
#  POLISH
# ══════════════════════════════════════════════════════════════

print("🎬 Applying polish...")
set_all_linear_interpolation()
set_viewport_to_camera()

print("✅ 'Finding the One' (v4) scene built successfully!")
print(f"   Timeline: {FRAME_START}–{FRAME_END} ({FRAME_END // FPS}s at {FPS}fps)")


# ══════════════════════════════════════════════════════════════
#  RENDER (headless only)
# ══════════════════════════════════════════════════════════════

if "--background" in sys.argv or "-b" in sys.argv:
    print(f"🎬 Rendering 'Finding the One' directly to video...")
    print(f"   Output: {bpy.context.scene.render.filepath}")
    bpy.ops.render.render(animation=True)
    print("✅ Render complete!")
else:
    print("👀 'Finding the One' loaded in GUI mode.")
    print("   Press Space in the viewport to preview the animation.")
    print(f"   Timeline: {FRAME_START}–{FRAME_END} ({FRAME_END // FPS} seconds at {FPS}fps)")
    print("   Tip: Use --watch mode for hot-reload during development.")
