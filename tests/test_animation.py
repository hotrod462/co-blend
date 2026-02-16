"""
Tests for scripts/utils/animation.py — easing functions and keyframe helpers.
"""
import bpy
import math
from tests.run_tests import test, assert_eq, assert_true, assert_near, assert_gt, assert_gte

from scripts.utils.scene import reset_scene
from scripts.utils.animation import (
    ease_in_out_cubic,
    ease_in_out_quad,
    ease_out_bounce,
    ease_out_elastic,
    lerp,
    animate_property,
    set_keyframe,
)


# ──────────────────────────────────────────────
# Easing: boundary conditions
# All easing functions must satisfy f(0)=0 and f(1)=1
# ──────────────────────────────────────────────

@test
def test_ease_in_out_cubic_boundaries():
    """ease_in_out_cubic(0) should be 0, ease_in_out_cubic(1) should be 1."""
    assert_near(ease_in_out_cubic(0.0), 0.0)
    assert_near(ease_in_out_cubic(1.0), 1.0)


@test
def test_ease_in_out_cubic_midpoint():
    """ease_in_out_cubic(0.5) should be 0.5 (symmetric)."""
    assert_near(ease_in_out_cubic(0.5), 0.5)


@test
def test_ease_in_out_cubic_monotonic():
    """ease_in_out_cubic should be monotonically increasing."""
    prev = 0.0
    for i in range(1, 101):
        t = i / 100.0
        val = ease_in_out_cubic(t)
        assert_gte(val, prev, f"Should be monotonic at t={t}")
        prev = val


@test
def test_ease_in_out_quad_boundaries():
    """ease_in_out_quad(0)=0, ease_in_out_quad(1)=1."""
    assert_near(ease_in_out_quad(0.0), 0.0)
    assert_near(ease_in_out_quad(1.0), 1.0)


@test
def test_ease_in_out_quad_midpoint():
    """ease_in_out_quad(0.5) should be 0.5."""
    assert_near(ease_in_out_quad(0.5), 0.5)


@test
def test_ease_out_bounce_boundaries():
    """ease_out_bounce(0)=0, ease_out_bounce(1)=1."""
    assert_near(ease_out_bounce(0.0), 0.0)
    assert_near(ease_out_bounce(1.0), 1.0, tolerance=0.01)


@test
def test_ease_out_elastic_boundaries():
    """ease_out_elastic(0)=0, ease_out_elastic(1)=1."""
    assert_near(ease_out_elastic(0.0), 0.0)
    assert_near(ease_out_elastic(1.0), 1.0)


@test
def test_ease_out_elastic_overshoots():
    """ease_out_elastic should temporarily exceed 1.0 (elastic overshoot)."""
    found_overshoot = False
    for i in range(1, 100):
        t = i / 100.0
        if ease_out_elastic(t) > 1.001:
            found_overshoot = True
            break
    assert_true(found_overshoot, "Elastic easing should overshoot past 1.0")


# ──────────────────────────────────────────────
# Easing: shape validation
# ──────────────────────────────────────────────

@test
def test_ease_in_out_cubic_slow_start():
    """ease_in_out_cubic should start slow (value at t=0.1 < 0.1, i.e. easing in)."""
    val = ease_in_out_cubic(0.1)
    assert_true(val < 0.1, f"Expected ease-in start, got {val} at t=0.1")


@test
def test_ease_in_out_cubic_slow_end():
    """ease_in_out_cubic should end slow (value at t=0.9 > 0.9, i.e. easing out)."""
    val = ease_in_out_cubic(0.9)
    assert_true(val > 0.9, f"Expected ease-out end, got {val} at t=0.9")


# ──────────────────────────────────────────────
# lerp
# ──────────────────────────────────────────────

@test
def test_lerp_boundaries():
    """lerp at t=0 gives a, at t=1 gives b."""
    assert_near(lerp(10.0, 20.0, 0.0), 10.0)
    assert_near(lerp(10.0, 20.0, 1.0), 20.0)


@test
def test_lerp_midpoint():
    """lerp at t=0.5 gives the midpoint."""
    assert_near(lerp(0.0, 100.0, 0.5), 50.0)


@test
def test_lerp_negative():
    """lerp should work with negative values."""
    assert_near(lerp(-10.0, 10.0, 0.5), 0.0)
    assert_near(lerp(-10.0, 10.0, 0.0), -10.0)


@test
def test_lerp_quarter():
    """lerp at t=0.25 gives a quarter of the way."""
    assert_near(lerp(0.0, 8.0, 0.25), 2.0)


# ──────────────────────────────────────────────
# animate_property (tuple values — e.g. location)
# ──────────────────────────────────────────────

@test
def test_animate_property_location():
    """animate_property should keyframe location from start to end."""
    reset_scene()
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube = bpy.context.active_object

    animate_property(
        cube,
        data_path="location",
        values=((0, 0, 0), (10, 0, 0)),
        frame_start=1,
        frame_end=10,
    )

    # Check keyframes exist
    assert_true(cube.animation_data is not None, "Should have animation data")
    assert_true(cube.animation_data.action is not None, "Should have an action")

    # Verify start position at frame 1
    bpy.context.scene.frame_set(1)
    assert_near(cube.location.x, 0.0, tolerance=0.1)

    # Verify end position at frame 10
    bpy.context.scene.frame_set(10)
    assert_near(cube.location.x, 10.0, tolerance=0.1)


@test
def test_animate_property_with_easing():
    """animate_property with cubic easing should ease in at the start."""
    reset_scene()
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube = bpy.context.active_object

    animate_property(
        cube,
        data_path="location",
        values=((0, 0, 0), (100, 0, 0)),
        frame_start=1,
        frame_end=100,
        easing=ease_in_out_cubic,
    )

    # At frame 10 (t=0.09), cubic easing should give a value < linear (9)
    bpy.context.scene.frame_set(10)
    assert_true(cube.location.x < 9.0,
                f"Eased value at t=0.09 should be < linear (9). Got {cube.location.x}")

    # At the end should still be 100
    bpy.context.scene.frame_set(100)
    assert_near(cube.location.x, 100.0, tolerance=0.5)


# ──────────────────────────────────────────────
# set_keyframe
# ──────────────────────────────────────────────

@test
def test_set_keyframe_indexed():
    """set_keyframe with index should set a specific axis."""
    reset_scene()
    bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.active_object

    set_keyframe(cube, "location", 5.0, frame=1, index=0)   # X=5 at frame 1
    set_keyframe(cube, "location", 15.0, frame=30, index=0)  # X=15 at frame 30

    bpy.context.scene.frame_set(1)
    assert_near(cube.location.x, 5.0, tolerance=0.1)

    bpy.context.scene.frame_set(30)
    assert_near(cube.location.x, 15.0, tolerance=0.1)


@test
def test_set_keyframe_whole_property():
    """set_keyframe without index should set the whole property."""
    reset_scene()
    bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.active_object

    # Animate uniform scale
    set_keyframe(cube, "scale", (1.0, 1.0, 1.0), frame=1)

    bpy.context.scene.frame_set(1)
    assert_near(cube.scale.x, 1.0, tolerance=0.01)


@test
def test_set_keyframe_rotation():
    """set_keyframe should work for rotation_euler with index."""
    reset_scene()
    bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.active_object

    set_keyframe(cube, "rotation_euler", math.radians(90), frame=1, index=2)  # Z rotation

    bpy.context.scene.frame_set(1)
    assert_near(cube.rotation_euler.z, math.radians(90), tolerance=0.01)
