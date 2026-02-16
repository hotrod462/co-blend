"""
Bootstrap script for --watch mode.

This is executed by Blender at startup (via --python) to:
1. Install and activate the Script Watcher addon
2. Set the target animation script path
3. Trigger the initial load and start watching

Usage (called by render.sh --watch):
    blender --python addons/watch_bootstrap.py -- /absolute/path/to/script.py
"""

import bpy
import sys
import os


def bootstrap():
    # Parse the script path from argv (comes after the "--" separator)
    script_path = None
    argv = sys.argv
    if "--" in argv:
        custom_args = argv[argv.index("--") + 1:]
        if custom_args:
            script_path = custom_args[0]

    if not script_path:
        print("❌ No script path provided. Usage: blender --python watch_bootstrap.py -- /path/to/script.py")
        return

    script_path = os.path.abspath(script_path)
    if not os.path.exists(script_path):
        print(f"❌ Script not found: {script_path}")
        return

    # Step 1: Install and enable the Script Watcher addon
    addon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "script_watcher.py")

    # Register the addon directly by running it
    import importlib.util
    spec = importlib.util.spec_from_file_location("script_watcher", addon_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["script_watcher"] = module
    spec.loader.exec_module(module)
    module.register()

    print(f"✅ Script Watcher addon loaded")

    # Step 2: Set the filepath and start watching
    # We need to defer this slightly so the scene is fully initialized
    def _start_watching():
        scene = bpy.context.scene
        scene.script_watcher.filepath = script_path

        # Trigger initial load
        from script_watcher import _watcher_state, execute_script
        _watcher_state["filepath"] = script_path
        _watcher_state["is_watching"] = True
        _watcher_state["last_mtime"] = 0.0

        execute_script(script_path)

        try:
            _watcher_state["last_mtime"] = os.path.getmtime(script_path)
        except OSError:
            pass

        # Start the file watcher timer
        from script_watcher import _watch_timer
        bpy.app.timers.register(_watch_timer, first_interval=1.0)

        print(f"👀 Watching: {script_path}")
        print(f"   Press Space in the viewport to play the animation.")
        print(f"   Save the script in your editor to hot-reload.")
        return None  # Don't repeat

    bpy.app.timers.register(_start_watching, first_interval=0.5)


bootstrap()
