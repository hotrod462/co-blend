"""
Tests for scripts/utils/scene.py — scene setup helpers.
"""
import bpy
import math
from tests.run_tests import test, assert_eq, assert_true, assert_near, assert_isinstance, assert_gt

from scripts.utils.scene import (
    reset_scene,
    clear_scene,
    setup_camera,
    setup_ortho_camera,
    setup_sun_light,
    setup_area_light,
    setup_world_color,
    setup_render,
    mathutils_vector,
)


# ──────────────────────────────────────────────
# reset_scene / clear_scene
# ──────────────────────────────────────────────

@test
def test_reset_scene_clears_objects():
    """reset_scene should remove all objects."""
    reset_scene()
    # Add some objects
    bpy.ops.mesh.primitive_cube_add()
    bpy.ops.mesh.primitive_uv_sphere_add()
    bpy.ops.object.light_add(type='POINT')
    assert_eq(len(bpy.data.objects), 3, "Should have 3 objects before reset")

    reset_scene()
    assert_eq(len(bpy.data.objects), 0, "Should have 0 objects after reset")


@test
def test_reset_scene_clears_materials():
    """reset_scene should remove all materials."""
    reset_scene()
    bpy.data.materials.new("TestMat1")
    bpy.data.materials.new("TestMat2")
    assert_eq(len(bpy.data.materials), 2)

    reset_scene()
    assert_eq(len(bpy.data.materials), 0, "Materials should be cleared")


@test
def test_reset_scene_clears_worlds():
    """reset_scene should remove all worlds."""
    reset_scene()
    bpy.data.worlds.new("TestWorld")
    assert_gt(len(bpy.data.worlds), 0)

    reset_scene()
    assert_eq(len(bpy.data.worlds), 0, "Worlds should be cleared")


@test
def test_reset_scene_resets_frame():
    """reset_scene should set the current frame to 1."""
    reset_scene()
    bpy.context.scene.frame_set(50)
    assert_eq(bpy.context.scene.frame_current, 50)

    reset_scene()
    assert_eq(bpy.context.scene.frame_current, 1, "Frame should be reset to 1")


@test
def test_clear_scene_is_alias():
    """clear_scene should behave the same as reset_scene."""
    clear_scene()
    bpy.ops.mesh.primitive_cube_add()
    assert_eq(len(bpy.data.objects), 1)

    clear_scene()
    assert_eq(len(bpy.data.objects), 0)


@test
def test_reset_scene_clears_actions():
    """reset_scene should remove all animation actions."""
    reset_scene()
    bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.active_object
    cube.keyframe_insert(data_path="location", frame=1)
    cube.keyframe_insert(data_path="location", frame=10)
    assert_gt(len(bpy.data.actions), 0, "Should have actions before reset")

    reset_scene()
    assert_eq(len(bpy.data.actions), 0, "Actions should be cleared")


@test
def test_reset_scene_idempotent():
    """Calling reset_scene twice should not error."""
    reset_scene()
    reset_scene()  # Should not raise
    assert_eq(len(bpy.data.objects), 0)


# ──────────────────────────────────────────────
# setup_camera
# ──────────────────────────────────────────────

@test
def test_setup_camera_creates_camera():
    """setup_camera should create a camera and set it as active."""
    reset_scene()
    cam = setup_camera(location=(5, -5, 3), target=(0, 0, 0))

    assert_true(cam is not None, "Camera should be returned")
    assert_eq(cam.name, "ScriptCamera")
    assert_eq(cam.type, 'CAMERA')
    assert_eq(bpy.context.scene.camera, cam, "Should be the scene camera")


@test
def test_setup_camera_has_track_constraint():
    """setup_camera should add a Track To constraint pointing at target."""
    reset_scene()
    cam = setup_camera(location=(5, -5, 3), target=(1, 1, 0))

    constraints = [c for c in cam.constraints if c.type == 'TRACK_TO']
    assert_eq(len(constraints), 1, "Should have one TRACK_TO constraint")

    track = constraints[0]
    assert_true(track.target is not None, "Constraint should have a target")
    assert_eq(track.target.name, "CameraTarget")


@test
def test_setup_camera_creates_target_empty():
    """setup_camera should create an empty at the target location."""
    reset_scene()
    target_loc = (2, 3, 1)
    setup_camera(location=(5, -5, 3), target=target_loc)

    target = bpy.data.objects.get("CameraTarget")
    assert_true(target is not None, "CameraTarget empty should exist")
    for i in range(3):
        assert_near(target.location[i], target_loc[i], tolerance=0.01)


# ──────────────────────────────────────────────
# setup_ortho_camera
# ──────────────────────────────────────────────

@test
def test_setup_ortho_camera_creates_ortho():
    """setup_ortho_camera should create an orthographic camera."""
    reset_scene()
    cam = setup_ortho_camera(location=(0, 0, 10), ortho_scale=20)

    assert_eq(cam.data.type, 'ORTHO', "Camera type should be ORTHO")
    assert_near(cam.data.ortho_scale, 20.0)
    assert_eq(cam.name, "OrthoCamera")
    assert_eq(bpy.context.scene.camera, cam)


@test
def test_setup_ortho_camera_looks_down():
    """setup_ortho_camera should point straight down the -Z axis."""
    reset_scene()
    cam = setup_ortho_camera()

    for i in range(3):
        assert_near(cam.rotation_euler[i], 0.0, tolerance=0.01,
                    msg=f"Rotation axis {i} should be 0")


# ──────────────────────────────────────────────
# Lights
# ──────────────────────────────────────────────

@test
def test_setup_sun_light():
    """setup_sun_light should create a sun lamp with correct energy."""
    reset_scene()
    sun = setup_sun_light(energy=5.0)

    assert_eq(sun.data.type, 'SUN')
    assert_near(sun.data.energy, 5.0)
    assert_eq(sun.name, "SunLight")


@test
def test_setup_area_light():
    """setup_area_light should create an area lamp with correct properties."""
    reset_scene()
    light = setup_area_light(location=(2, -2, 4), energy=150, size=2.5)

    assert_eq(light.data.type, 'AREA')
    assert_near(light.data.energy, 150.0)
    assert_near(light.data.size, 2.5)
    assert_eq(light.name, "AreaLight")


# ──────────────────────────────────────────────
# World
# ──────────────────────────────────────────────

@test
def test_setup_world_color():
    """setup_world_color should create a world with the specified background."""
    reset_scene()
    color = (0.1, 0.2, 0.3, 1.0)
    setup_world_color(color=color)

    world = bpy.context.scene.world
    assert_true(world is not None, "World should be set")
    assert_true(world.use_nodes, "World should use nodes")

    bg = world.node_tree.nodes["Background"]
    for i in range(4):
        assert_near(bg.inputs["Color"].default_value[i], color[i], tolerance=0.01)


# ──────────────────────────────────────────────
# Render settings
# ──────────────────────────────────────────────

@test
def test_setup_render_defaults():
    """setup_render should configure resolution, fps, frame range."""
    reset_scene()
    setup_render(
        engine='BLENDER_EEVEE',
        resolution=(1280, 720),
        fps=24,
        frame_start=10,
        frame_end=200,
        output_path='./output/test/',
    )

    scene = bpy.context.scene
    assert_eq(scene.render.engine, 'BLENDER_EEVEE')
    assert_eq(scene.render.resolution_x, 1280)
    assert_eq(scene.render.resolution_y, 720)
    assert_eq(scene.render.fps, 24)
    assert_eq(scene.frame_start, 10)
    assert_eq(scene.frame_end, 200)
    assert_eq(scene.render.image_settings.file_format, 'PNG')


@test
def test_setup_render_output_path_trailing_slash():
    """setup_render should ensure output path ends with /."""
    reset_scene()
    setup_render(output_path='./output/no_slash')

    assert_true(bpy.context.scene.render.filepath.endswith('/'),
                "Output path should end with /")


# ──────────────────────────────────────────────
# mathutils_vector
# ──────────────────────────────────────────────

@test
def test_mathutils_vector():
    """mathutils_vector should convert a tuple to a Vector."""
    import mathutils
    v = mathutils_vector((1.0, 2.0, 3.0))
    assert_isinstance(v, mathutils.Vector)
    assert_near(v.x, 1.0)
    assert_near(v.y, 2.0)
    assert_near(v.z, 3.0)
