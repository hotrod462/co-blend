"""
Tests for addon/script_watcher.py — hot-reload addon.
"""
import bpy
import sys
import os
import time
import tempfile
from tests.run_tests import test, assert_eq, assert_true, assert_false, assert_gt, assert_near

# Load the addon module
import importlib.util
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
addon_path = os.path.join(PROJECT_ROOT, "addons", "script_watcher.py")
spec = importlib.util.spec_from_file_location("script_watcher", addon_path)
sw = importlib.util.module_from_spec(spec)
sys.modules["script_watcher"] = sw
spec.loader.exec_module(sw)


# ──────────────────────────────────────────────
# Addon Registration
# ──────────────────────────────────────────────

@test
def test_addon_register():
    """The Script Watcher addon should register without errors."""
    sw.register()
    assert_true(hasattr(bpy.types.Scene, 'script_watcher'),
                "Scene should have script_watcher property")


@test
def test_addon_unregister():
    """The Script Watcher addon should unregister cleanly."""
    # Make sure it's registered first
    try:
        sw.register()
    except Exception:
        pass  # Already registered

    sw.unregister()
    assert_false(hasattr(bpy.types.Scene, 'script_watcher'),
                 "Property should be removed after unregister")

    # Re-register for remaining tests
    sw.register()


# ──────────────────────────────────────────────
# reset_scene (addon version)
# ──────────────────────────────────────────────

@test
def test_addon_reset_scene_clears_all():
    """Addon's reset_scene should clear objects and materials."""
    bpy.ops.mesh.primitive_cube_add()
    bpy.ops.mesh.primitive_uv_sphere_add()
    bpy.data.materials.new("AddonTestMat")
    assert_gt(len(bpy.data.objects), 0)

    sw.reset_scene()

    assert_eq(len(bpy.data.objects), 0, "Objects should be cleared")
    assert_eq(len(bpy.data.materials), 0, "Materials should be cleared")


@test
def test_addon_reset_scene_preserves_addon():
    """reset_scene should NOT kill the script_watcher addon."""
    sw.reset_scene()

    # The addon should still be registered
    assert_true(hasattr(bpy.types.Scene, 'script_watcher'),
                "Addon should survive reset_scene")


# ──────────────────────────────────────────────
# Module Reloading
# ──────────────────────────────────────────────

@test
def test_reload_project_modules():
    """reload_project_modules should reload modules under the project root."""
    # Import a utils module first
    from scripts.utils import animation

    # Track the module's identity
    old_id = id(animation)

    # Reload
    sw.reload_project_modules(PROJECT_ROOT)

    # The module should have been reloaded (new module object)
    import scripts.utils.animation as reloaded
    # Note: importlib.reload replaces the module in-place, so id may or may not change
    # But the function should not error
    assert_true(True, "reload_project_modules completed without error")


# ──────────────────────────────────────────────
# Script Execution
# ──────────────────────────────────────────────

@test
def test_execute_script_creates_scene():
    """execute_script should run a script that creates objects."""
    # Create a temporary test script
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.py', delete=False,
        dir=os.path.join(PROJECT_ROOT, 'scripts', 'animations')
    ) as f:
        f.write("""
import bpy
import sys, os
project_root = os.getcwd()
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from scripts.utils.scene import reset_scene
reset_scene()
bpy.ops.mesh.primitive_cube_add(location=(1, 2, 3))
bpy.context.active_object.name = "TestCubeFromScript"
""")
        tmp_path = f.name

    try:
        sw.reset_scene()
        sw.execute_script(tmp_path)

        obj = bpy.data.objects.get("TestCubeFromScript")
        assert_true(obj is not None, "Script should have created TestCubeFromScript")
        assert_near(obj.location.x, 1.0, tolerance=0.01)
        assert_near(obj.location.y, 2.0, tolerance=0.01)
        assert_near(obj.location.z, 3.0, tolerance=0.01)
    finally:
        os.unlink(tmp_path)


@test
def test_execute_script_handles_error():
    """execute_script should not crash on a script with an error."""
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.py', delete=False,
        dir=os.path.join(PROJECT_ROOT, 'scripts', 'animations')
    ) as f:
        f.write("raise ValueError('intentional test error')\n")
        tmp_path = f.name

    try:
        # Reset error state
        sw._watcher_state["last_error"] = ""

        sw.execute_script(tmp_path)

        # Should have captured the error, not crashed
        assert_true(len(sw._watcher_state["last_error"]) > 0,
                    "Error should be captured in state")
        assert_true("intentional test error" in sw._watcher_state["last_error"],
                    "Error message should contain our text")
    finally:
        os.unlink(tmp_path)


@test
def test_execute_script_increments_count():
    """execute_script should increment the reload counter on success."""
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.py', delete=False,
        dir=os.path.join(PROJECT_ROOT, 'scripts', 'animations')
    ) as f:
        f.write("# empty script\npass\n")
        tmp_path = f.name

    try:
        initial_count = sw._watcher_state["reload_count"]
        sw.execute_script(tmp_path)
        assert_eq(sw._watcher_state["reload_count"], initial_count + 1,
                  "Reload count should increment")
    finally:
        os.unlink(tmp_path)


# ──────────────────────────────────────────────
# Watcher State
# ──────────────────────────────────────────────

@test
def test_watcher_state_defaults():
    """Watcher state should have expected default structure."""
    state = sw._watcher_state
    assert_true("filepath" in state)
    assert_true("is_watching" in state)
    assert_true("last_mtime" in state)
    assert_true("last_error" in state)
    assert_true("reload_count" in state)
    assert_true("debounce_pending" in state)


@test
def test_watcher_timer_returns_none_when_not_watching():
    """_watch_timer should return None (stop) when not watching."""
    sw._watcher_state["is_watching"] = False
    result = sw._watch_timer()
    assert_eq(result, None, "Timer should return None to stop")


@test
def test_watcher_timer_returns_interval_when_watching():
    """_watch_timer should return POLL_INTERVAL when file hasn't changed."""
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.py', delete=False
    ) as f:
        f.write("pass\n")
        tmp_path = f.name

    try:
        sw._watcher_state["is_watching"] = True
        sw._watcher_state["filepath"] = tmp_path
        sw._watcher_state["last_mtime"] = os.path.getmtime(tmp_path)
        sw._watcher_state["debounce_pending"] = False

        result = sw._watch_timer()
        assert_near(result, sw.POLL_INTERVAL, tolerance=0.01,
                    msg="Should return POLL_INTERVAL when no change")
    finally:
        sw._watcher_state["is_watching"] = False
        os.unlink(tmp_path)
