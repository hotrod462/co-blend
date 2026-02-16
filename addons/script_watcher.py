"""
Script Watcher — Blender Addon for hot-reloading animation scripts.

Watches a Python script file for changes (via mtime polling) and re-executes
it inside Blender whenever the file is saved. Designed for use with an external
editor (VS Code) while keeping Blender open for viewport preview.

Install: Edit > Preferences > Add-ons > Install from Disk > select this file.
Or use the --watch flag in render.sh to auto-install.
"""

bl_info = {
    "name": "Script Watcher",
    "author": "blender-animations",
    "version": (1, 0, 0),
    "blender": (5, 0, 0),
    "category": "Development",
    "description": "Watch and hot-reload animation scripts on file save",
}

import bpy
import os
import sys
import time
import importlib
import traceback


# ──────────────────────────────────────────────
# State
# ──────────────────────────────────────────────

_watcher_state = {
    "filepath": "",
    "last_mtime": 0.0,
    "last_reload": 0.0,
    "is_watching": False,
    "last_error": "",
    "reload_count": 0,
    "debounce_mtime": 0.0,      # mtime captured during debounce
    "debounce_pending": False,   # whether a debounce is in progress
}

POLL_INTERVAL = 1.0      # seconds between file checks
DEBOUNCE_DELAY = 0.5     # seconds to wait after detecting a change before reloading


# ──────────────────────────────────────────────
# Core: Scene Cleanup
# ──────────────────────────────────────────────

def reset_scene():
    """
    Delete all scene contents without resetting the Blender session.
    Preserves: UI layout, loaded addons, preferences.
    Removes: all objects, meshes, materials, worlds, cameras, lights,
             animation data, and orphaned data blocks.
    """
    # Deselect all, then select all and delete
    if bpy.context.mode != 'OBJECT':
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except RuntimeError:
            pass

    # Remove all objects
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)

    # Remove all meshes
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh, do_unlink=True)

    # Remove all curves
    for curve in bpy.data.curves:
        bpy.data.curves.remove(curve, do_unlink=True)

    # Remove all materials
    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat, do_unlink=True)

    # Remove all worlds
    for world in bpy.data.worlds:
        bpy.data.worlds.remove(world, do_unlink=True)

    # Remove all lights
    for light in bpy.data.lights:
        bpy.data.lights.remove(light, do_unlink=True)

    # Remove all cameras
    for cam in bpy.data.cameras:
        bpy.data.cameras.remove(cam, do_unlink=True)

    # Remove all actions (animation data)
    for action in bpy.data.actions:
        bpy.data.actions.remove(action, do_unlink=True)

    # Remove all node groups
    for ng in bpy.data.node_groups:
        bpy.data.node_groups.remove(ng, do_unlink=True)

    # Purge any remaining orphaned data blocks
    bpy.ops.outliner.orphans_purge(do_recursive=True)

    # Reset frame to 1
    bpy.context.scene.frame_set(1)


# ──────────────────────────────────────────────
# Core: Module Reloading
# ──────────────────────────────────────────────

def reload_project_modules(project_root):
    """
    Reload all imported modules from the project's scripts/ directory.
    This ensures changes to utils (scene.py, materials.py, animation.py)
    are picked up without restarting Blender.
    """
    scripts_dir = os.path.join(project_root, "scripts")
    modules_to_reload = []

    for name, module in list(sys.modules.items()):
        if module is None:
            continue
        module_file = getattr(module, '__file__', None)
        if module_file and module_file.startswith(scripts_dir):
            modules_to_reload.append((name, module))

    # Sort by name depth so parent modules reload before children
    modules_to_reload.sort(key=lambda x: x[0].count('.'))

    for name, module in modules_to_reload:
        try:
            importlib.reload(module)
        except Exception as e:
            print(f"⚠️  Failed to reload {name}: {e}")


# ──────────────────────────────────────────────
# Core: Script Execution
# ──────────────────────────────────────────────

def execute_script(filepath):
    """
    Execute an animation script file inside Blender.
    Handles scene cleanup, module reloading, and error capture.
    """
    state = _watcher_state

    # Robustly find project root by searching upwards for 'scripts/' directory
    curr = os.path.dirname(os.path.abspath(filepath))
    project_root = None
    while curr != os.path.dirname(curr):
        if os.path.isdir(os.path.join(curr, "scripts")) and os.path.isdir(os.path.join(curr, "addons")):
            project_root = curr
            break
        curr = os.path.dirname(curr)
    
    if project_root is None:
        # Fallback to old 3-level-up logic
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(filepath))))

    # Ensure project root is in sys.path
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Step 1: Clean the scene
    print(f"\n{'='*50}")
    print(f"🔄 Reloading: {os.path.basename(filepath)}")
    print(f"{'='*50}")

    reset_scene()

    # Step 2: Reload project modules (pick up changes to utils)
    reload_project_modules(project_root)

    # Step 3: Execute the script
    try:
        # Use exec with a clean globals dict that includes builtins
        script_globals = {
            "__file__": filepath,
            "__name__": "__main__",
            "__builtins__": __builtins__,
        }

        # Set CWD to project root so relative paths work
        original_cwd = os.getcwd()
        os.chdir(project_root)

        with open(filepath, 'r') as f:
            code = compile(f.read(), filepath, 'exec')
            exec(code, script_globals)

        os.chdir(original_cwd)

        state["last_error"] = ""
        state["reload_count"] += 1
        state["last_reload"] = time.time()
        print(f"✅ Reload #{state['reload_count']} successful")

        # Jump to frame 1 for preview
        bpy.context.scene.frame_set(1)

    except Exception as e:
        os.chdir(original_cwd)
        error_msg = traceback.format_exc()
        state["last_error"] = str(e)
        print(f"\n❌ Script error:\n{error_msg}")


# ──────────────────────────────────────────────
# Timer: File Watcher
# ──────────────────────────────────────────────

def _watch_timer():
    """
    Timer callback that polls the watched file for changes.
    Uses debouncing to avoid reloading a half-written file.
    """
    state = _watcher_state

    if not state["is_watching"] or not state["filepath"]:
        return None  # Stop the timer

    filepath = state["filepath"]

    if not os.path.exists(filepath):
        return POLL_INTERVAL

    try:
        current_mtime = os.path.getmtime(filepath)
    except OSError:
        return POLL_INTERVAL

    # Find project root robustly
    curr = os.path.dirname(os.path.abspath(filepath))
    project_root = None
    while curr != os.path.dirname(curr):
        if os.path.isdir(os.path.join(curr, "scripts")) and os.path.isdir(os.path.join(curr, "addons")):
            project_root = curr
            break
        curr = os.path.dirname(curr)
    if project_root is None:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(filepath)))

    # Check utils directory for changes
    utils_dir = os.path.join(project_root, "scripts", "utils")
    extra_mtime = 0.0
    if os.path.isdir(utils_dir):
        for f in os.listdir(utils_dir):
            if f.endswith('.py'):
                try:
                    mt = os.path.getmtime(os.path.join(utils_dir, f))
                    extra_mtime = max(extra_mtime, mt)
                except OSError:
                    pass

    # Also check the script's own directory for sibling modules
    # (e.g. config.py, characters.py, act1.py in a multi-file project)
    script_dir = os.path.dirname(os.path.abspath(filepath))
    if os.path.isdir(script_dir):
        for f in os.listdir(script_dir):
            if f.endswith('.py'):
                try:
                    mt = os.path.getmtime(os.path.join(script_dir, f))
                    extra_mtime = max(extra_mtime, mt)
                except OSError:
                    pass

    effective_mtime = max(current_mtime, extra_mtime)

    if effective_mtime != state["last_mtime"]:
        if not state["debounce_pending"]:
            # Start debounce — wait before reloading
            state["debounce_pending"] = True
            state["debounce_mtime"] = effective_mtime
            return DEBOUNCE_DELAY
        else:
            if effective_mtime == state["debounce_mtime"]:
                # File hasn't changed since debounce started — safe to reload
                state["debounce_pending"] = False
                state["last_mtime"] = effective_mtime
                execute_script(filepath)
            else:
                # File changed again during debounce — restart debounce
                state["debounce_mtime"] = effective_mtime
                return DEBOUNCE_DELAY

    return POLL_INTERVAL


# ──────────────────────────────────────────────
# Operators
# ──────────────────────────────────────────────

class SCRIPTWATCHER_OT_start(bpy.types.Operator):
    """Start watching the script file for changes"""
    bl_idname = "script_watcher.start"
    bl_label = "Start Watching"

    def execute(self, context):
        state = _watcher_state
        props = context.scene.script_watcher

        filepath = bpy.path.abspath(props.filepath)
        if not filepath or not os.path.exists(filepath):
            self.report({'ERROR'}, f"File not found: {filepath}")
            return {'CANCELLED'}

        state["filepath"] = filepath
        state["last_mtime"] = 0.0  # Force initial load
        state["is_watching"] = True
        state["last_error"] = ""
        state["debounce_pending"] = False

        bpy.app.timers.register(_watch_timer, first_interval=0.1)

        self.report({'INFO'}, f"Watching: {os.path.basename(filepath)}")
        return {'FINISHED'}


class SCRIPTWATCHER_OT_stop(bpy.types.Operator):
    """Stop watching for changes"""
    bl_idname = "script_watcher.stop"
    bl_label = "Stop Watching"

    def execute(self, context):
        _watcher_state["is_watching"] = False
        self.report({'INFO'}, "Stopped watching")
        return {'FINISHED'}


class SCRIPTWATCHER_OT_reload(bpy.types.Operator):
    """Manually reload the script now"""
    bl_idname = "script_watcher.reload"
    bl_label = "Reload Now"

    def execute(self, context):
        state = _watcher_state
        props = context.scene.script_watcher

        filepath = bpy.path.abspath(props.filepath)
        if not filepath or not os.path.exists(filepath):
            self.report({'ERROR'}, f"File not found: {filepath}")
            return {'CANCELLED'}

        state["filepath"] = filepath
        execute_script(filepath)
        try:
            state["last_mtime"] = os.path.getmtime(filepath)
        except OSError:
            pass

        return {'FINISHED'}


# ──────────────────────────────────────────────
# Properties
# ──────────────────────────────────────────────

class ScriptWatcherProperties(bpy.types.PropertyGroup):
    filepath: bpy.props.StringProperty(
        name="Script",
        description="Path to the animation script to watch",
        subtype='FILE_PATH',
        default="",
    )


# ──────────────────────────────────────────────
# UI Panel
# ──────────────────────────────────────────────

class SCRIPTWATCHER_PT_panel(bpy.types.Panel):
    """Script Watcher panel in the 3D Viewport sidebar"""
    bl_label = "Script Watcher"
    bl_idname = "SCRIPTWATCHER_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Watcher'

    def draw(self, context):
        layout = self.layout
        props = context.scene.script_watcher
        state = _watcher_state

        # File path
        layout.prop(props, "filepath")

        # Status
        box = layout.box()
        if state["is_watching"]:
            box.label(text="● Watching", icon='REC')
            if state["last_reload"] > 0:
                elapsed = time.time() - state["last_reload"]
                if elapsed < 60:
                    box.label(text=f"  Last reload: {elapsed:.0f}s ago")
                else:
                    box.label(text=f"  Last reload: {elapsed/60:.0f}m ago")
            box.label(text=f"  Reloads: {state['reload_count']}")
        else:
            box.label(text="○ Not watching", icon='PAUSE')

        # Error display
        if state["last_error"]:
            err_box = layout.box()
            err_box.alert = True
            err_box.label(text="⚠ Error:", icon='ERROR')
            # Truncate long errors
            err_text = state["last_error"]
            if len(err_text) > 80:
                err_text = err_text[:77] + "..."
            err_box.label(text=err_text)

        # Buttons
        row = layout.row(align=True)
        if state["is_watching"]:
            row.operator("script_watcher.stop", icon='PAUSE')
        else:
            row.operator("script_watcher.start", icon='PLAY')
        row.operator("script_watcher.reload", icon='FILE_REFRESH')


# ──────────────────────────────────────────────
# Registration
# ──────────────────────────────────────────────

classes = [
    ScriptWatcherProperties,
    SCRIPTWATCHER_OT_start,
    SCRIPTWATCHER_OT_stop,
    SCRIPTWATCHER_OT_reload,
    SCRIPTWATCHER_PT_panel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.script_watcher = bpy.props.PointerProperty(type=ScriptWatcherProperties)


def unregister():
    _watcher_state["is_watching"] = False
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.script_watcher


if __name__ == "__main__":
    register()
