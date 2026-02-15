"""
Hello Cube — A starter animation to verify the pipeline works.

A cube spins and floats upward while changing color,
with smooth easing and a dark background.

Run:
    ./render.sh scripts/animations/hello_cube.py
    ./render.sh scripts/animations/hello_cube.py --gui
"""
import bpy
import math
import sys
import os

# ── Add the project root to sys.path so we can import our utils ──
# When Blender runs this script, the CWD is the project root (via render.sh)
project_root = os.getcwd()
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.utils.scene import clear_scene, setup_camera, setup_world_color, setup_render, setup_area_light
from scripts.utils.materials import create_principled_material, assign_material
from scripts.utils.animation import animate_property, ease_in_out_cubic, set_keyframe

# ──────────────────────────────────────────────
# Scene Setup
# ──────────────────────────────────────────────

FRAME_START = 1
FRAME_END = 150
FPS = 30

clear_scene()
setup_camera(location=(6, -6, 4), target=(0, 0, 1.5))
setup_area_light(location=(4, -3, 6), energy=300, size=4)
setup_area_light(location=(-3, 4, 3), energy=100, size=2)
setup_world_color(color=(0.02, 0.02, 0.04, 1.0))  # Dark blue-black
setup_render(
    engine='BLENDER_EEVEE_NEXT',
    resolution=(1920, 1080),
    fps=FPS,
    frame_start=FRAME_START,
    frame_end=FRAME_END,
    output_path='./output/hello_cube',
    file_format='FFMPEG',
)

# ──────────────────────────────────────────────
# Create Objects
# ──────────────────────────────────────────────

# Ground plane
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
ground_mat = create_principled_material(
    name="GroundMat",
    color=(0.08, 0.08, 0.1, 1.0),
    metallic=0.2,
    roughness=0.8,
)
assign_material(ground, ground_mat)

# The hero cube
bpy.ops.mesh.primitive_cube_add(size=1.5, location=(0, 0, 0.75))
cube = bpy.context.active_object
cube.name = "HeroCube"

cube_mat = create_principled_material(
    name="CubeMat",
    color=(0.1, 0.4, 0.9, 1.0),   # Blue
    metallic=0.6,
    roughness=0.3,
    emission_color=(0.2, 0.5, 1.0, 1.0),
    emission_strength=0.5,
)
assign_material(cube, cube_mat)

# ──────────────────────────────────────────────
# Animate
# ──────────────────────────────────────────────

# Cube floats upward with easing
animate_property(
    cube,
    data_path="location",
    values=((0, 0, 0.75), (0, 0, 3.0)),
    frame_start=FRAME_START,
    frame_end=FRAME_END,
    easing=ease_in_out_cubic,
)

# Cube rotates on Z axis (full spin) and tilts on X
for frame in range(FRAME_START, FRAME_END + 1):
    t = (frame - FRAME_START) / (FRAME_END - FRAME_START)
    eased_t = ease_in_out_cubic(t)

    # Z rotation: two full spins
    z_rot = eased_t * math.pi * 4
    set_keyframe(cube, "rotation_euler", z_rot, frame, index=2)

    # X tilt: gentle wobble
    x_rot = math.sin(t * math.pi * 6) * math.radians(15)
    set_keyframe(cube, "rotation_euler", x_rot, frame, index=0)

# ──────────────────────────────────────────────
# Render (only in headless mode)
# ──────────────────────────────────────────────

if "--background" in sys.argv or "-b" in sys.argv:
    print("🎬 Rendering animation...")
    bpy.ops.render.render(animation=True)
    print("✅ Done! Output saved to ./output/")
else:
    print("👀 Opened in GUI mode — press Space in the viewport to preview the animation.")
    print("   To render, go to Render > Render Animation (Ctrl+F12)")
