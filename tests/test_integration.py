"""
Integration tests — test that full animation scripts work end-to-end.
"""
import bpy
import sys
import os
from tests.run_tests import test, assert_eq, assert_true, assert_gt, assert_near

from scripts.utils.scene import reset_scene

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ──────────────────────────────────────────────
# hello_cube.py integration test
# ──────────────────────────────────────────────

def _exec_script_no_render(script_path):
    """
    Execute an animation script without triggering the render.
    Temporarily strips --background/-b from sys.argv so the
    render guard `if '--background' in sys.argv` is False.
    """
    original_argv = sys.argv[:]
    sys.argv = [a for a in sys.argv if a not in ('--background', '-b')]

    original_cwd = os.getcwd()
    os.chdir(PROJECT_ROOT)

    script_globals = {
        "__file__": script_path,
        "__name__": "__main__",
        "__builtins__": __builtins__,
    }
    try:
        with open(script_path, 'r') as f:
            exec(compile(f.read(), script_path, 'exec'), script_globals)
    finally:
        os.chdir(original_cwd)
        sys.argv = original_argv


@test
def test_hello_cube_script_runs():
    """hello_cube.py should execute without errors and create objects."""
    reset_scene()

    script_path = os.path.join(PROJECT_ROOT, "scripts", "animations", "hello_cube.py")
    assert_true(os.path.exists(script_path), f"hello_cube.py should exist at {script_path}")

    _exec_script_no_render(script_path)

    # Should have created at least a cube, camera, and light
    assert_gt(len(bpy.data.objects), 0, "Script should create objects")

    found_mesh = any(obj.type == 'MESH' for obj in bpy.data.objects)
    found_camera = any(obj.type == 'CAMERA' for obj in bpy.data.objects)
    assert_true(found_mesh, "Should have at least one mesh object")
    assert_true(found_camera, "Should have a camera")


@test
def test_hello_cube_has_animation():
    """hello_cube.py should create animation keyframes."""
    reset_scene()

    script_path = os.path.join(PROJECT_ROOT, "scripts", "animations", "hello_cube.py")
    _exec_script_no_render(script_path)

    # There should be at least one action (animation data)
    assert_gt(len(bpy.data.actions), 0, "Animation should create at least one action")


# ──────────────────────────────────────────────
# Scene setup combination tests
# ──────────────────────────────────────────────

@test
def test_full_scene_setup():
    """A realistic scene setup sequence should work without conflicts."""
    from scripts.utils.scene import (
        setup_camera, setup_ortho_camera,
        setup_area_light, setup_world_color, setup_render,
    )
    from scripts.utils.materials import (
        create_principled_material, create_emission_material, assign_material,
    )
    from scripts.utils.animation import animate_property, set_keyframe

    reset_scene()

    # Setup scene
    setup_ortho_camera(location=(0, 0, 10), ortho_scale=15)
    setup_world_color((0, 0, 0, 1))
    setup_render(
        engine='BLENDER_EEVEE',
        resolution=(1920, 1080),
        fps=30,
        frame_start=1,
        frame_end=60,
    )

    # Create objects with materials
    bpy.ops.mesh.primitive_circle_add(radius=0.5, location=(0, 0, 0))
    circle = bpy.context.active_object
    circle.name = "TestCircle"
    glow = create_emission_material("CircleGlow", (1, 0.5, 0.8, 1), strength=8)
    assign_material(circle, glow)

    bpy.ops.mesh.primitive_cube_add(size=0.5, location=(3, 0, 0))
    square = bpy.context.active_object
    square.name = "TestSquare"
    mat = create_principled_material("SquareMat", (0.3, 0.5, 0.8, 1))
    assign_material(square, mat)

    # Animate
    animate_property(
        circle, "location",
        values=((0, 0, 0), (5, 5, 0)),
        frame_start=1, frame_end=60,
    )
    set_keyframe(square, "scale", 2.0, frame=1, index=0)
    set_keyframe(square, "scale", 0.5, frame=60, index=0)

    # Verify final state
    assert_eq(len(bpy.data.objects), 3, "Should have circle, square, and camera")
    assert_eq(len(bpy.data.materials), 2, "Should have 2 materials")
    assert_gt(len(bpy.data.actions), 0, "Should have animation data")

    # Check camera
    cam = bpy.context.scene.camera
    assert_true(cam is not None)
    assert_eq(cam.data.type, 'ORTHO')

    # Check world
    world = bpy.context.scene.world
    assert_true(world is not None)

    # Check render settings
    assert_eq(bpy.context.scene.render.fps, 30)
    assert_eq(bpy.context.scene.frame_end, 60)


@test
def test_double_clear_rebuild():
    """Clearing and rebuilding a scene twice should work (hot-reload simulation)."""
    from scripts.utils.scene import setup_ortho_camera, setup_world_color
    from scripts.utils.materials import create_emission_material, assign_material

    for iteration in range(2):
        reset_scene()

        setup_ortho_camera()
        setup_world_color((0, 0, 0, 1))

        bpy.ops.mesh.primitive_cube_add(location=(iteration, 0, 0))
        cube = bpy.context.active_object
        cube.name = f"Cube_{iteration}"

        mat = create_emission_material(f"Mat_{iteration}", (1, 0, 0, 1))
        assign_material(cube, mat)

    # After the second iteration, only iteration-1 objects should exist
    cube = bpy.data.objects.get("Cube_1")
    assert_true(cube is not None, "Last cube should exist")
    assert_near(cube.location.x, 1.0, tolerance=0.01)

    cube_0 = bpy.data.objects.get("Cube_0")
    assert_true(cube_0 is None, "First cube should have been cleared")
