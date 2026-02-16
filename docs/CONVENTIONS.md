# Conventions & Design Decisions

> Opinionated guide for how this repo works. Read this before writing a new animation.

---

## Repo Structure

```
blender-animations/
├── addons/                     # Blender addons (installed at runtime)
│   ├── script_watcher.py       # Hot-reload addon for --watch mode
│   └── watch_bootstrap.py      # Startup script for --watch mode
├── scripts/
│   ├── utils/                  # Shared helper modules (imported by animations)
│   │   ├── __init__.py
│   │   ├── scene.py            # Scene setup: camera, lighting, world, render config
│   │   ├── materials.py        # Material creation: principled, glass, emission
│   │   └── animation.py        # Easing functions, keyframe helpers
│   └── animations/             # Individual animation projects
│       ├── hello_cube.py       # Single-file animation
│       └── finding_the_one/    # Multi-file animation project
│           ├── STORYBOARD.md   # Detailed frame-by-frame script
│           └── finding_the_one.py
├── assets/                     # Imported models, textures, HDRIs (gitignored if large)
├── output/                     # Rendered frames and videos (gitignored)
├── docs/                       # This documentation
├── render.sh                   # CLI entry point
└── .gitignore
```

---

## The Three Modes

Every animation script can be run in three modes via `render.sh`:

| Mode | Command | What Happens |
|------|---------|-------------|
| **Headless** | `./render.sh script.py` | Renders all frames to PNG, stitches to MP4 via ffmpeg. No GUI. |
| **GUI** | `./render.sh script.py --gui` | Opens Blender with the scene loaded. Manual preview with Space. |
| **Watch** | `./render.sh script.py --watch` | Opens Blender + hot-reload. Saves in editor → scene auto-rebuilds. |

**Use `--watch` for development. Use headless for final renders.**

---

## Animation Script Conventions

### 1. Always Start With `clear_scene()`

Every animation script must call `clear_scene()` (or `reset_scene()`) at the top, before creating any objects. This ensures the scene is clean on both first run and hot-reload.

```python
from scripts.utils.scene import clear_scene
clear_scene()
```

### 2. Guard the Render Call

Never render unconditionally. Wrap render calls so they only fire in headless mode:

```python
import sys

if "--background" in sys.argv or "-b" in sys.argv:
    bpy.ops.render.render(animation=True)
    frames_to_video(...)
```

This prevents rendering when using `--gui` or `--watch` mode.

### 3. Top-Level Execution is Fine

Scripts are executed via `exec()` during hot-reload. Writing scene setup at the top level (not inside a `main()` function) works perfectly and is the preferred style:

```python
# ✅ Preferred — top-level execution
clear_scene()
setup_camera(...)
bpy.ops.mesh.primitive_cube_add(...)
cube = bpy.context.active_object
animate_property(cube, ...)
```

```python
# ❌ Avoid — unnecessary wrapper
def main():
    clear_scene()
    ...
main()
```

### 4. Use Project Imports, Not Relative Imports

Always import from the project root using the `scripts.utils.*` path:

```python
import sys, os
project_root = os.getcwd()
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.utils.scene import clear_scene, setup_camera, setup_render
from scripts.utils.materials import create_principled_material, assign_material
from scripts.utils.animation import animate_property, ease_in_out_cubic
```

The `sys.path` setup block should appear near the top of every animation script.

### 5. Name Your Objects

Always set `obj.name` after creating objects. This makes debugging in Blender's Outliner much easier:

```python
bpy.ops.mesh.primitive_circle_add(radius=0.35, location=(0, 0, 0))
seeker = bpy.context.active_object
seeker.name = "Seeker"  # ← Always do this
```

### 6. Use Constants for Timing

Define frame/timing constants at the top of the script:

```python
FPS = 30
FRAME_START = 1
FRAME_END = 1800  # 60 seconds

# Act boundaries
ACT_1_END = 450    # 15s
ACT_2_END = 900    # 30s
ACT_3_END = 1350   # 45s
```

### 7. Render to PNG Sequences

Blender 5.0 on macOS doesn't support setting `file_format = 'FFMPEG'` via Python in headless mode. The standard approach is:

1. Render to PNG frame sequence (via `setup_render()`)
2. Stitch to MP4 via `frames_to_video()` (uses ffmpeg CLI)

This is actually the professional workflow — it supports resuming interrupted renders and lossless intermediates.

---

## Scene Setup Conventions

### Camera

- **3D scenes**: Use `setup_camera(location, target)` — perspective camera with track-to constraint
- **2D/top-down scenes**: Use `setup_ortho_camera(location, ortho_scale)` — orthographic, looking straight down

### Render Engine

Use `BLENDER_EEVEE` for everything in this repo. It's fast enough for real-time viewport preview and good enough for final output. Only switch to `CYCLES` if you specifically need raytraced effects.

```python
setup_render(engine='BLENDER_EEVEE', ...)
```

### Materials

- Use **emission materials** for 2D/flat animations (no lighting needed)
- Use **principled BSDF** for 3D scenes with lighting
- Always use `assign_material(obj, mat)` to attach materials to objects

### World/Background

- Set via `setup_world_color(color)` — this creates a solid-color world
- For black backgrounds, use `(0, 0, 0, 1)`

---

## Hot-Reload Conventions

### What Gets Reloaded

When you save a file in VS Code and the Script Watcher detects it:

1. **All objects, materials, worlds, etc. are deleted** (via `reset_scene()`)
2. **All `scripts.utils.*` modules are reloaded** (via `importlib.reload()`)
3. **The animation script is re-executed** from scratch

This means:
- ✅ Changes to the animation script take effect immediately
- ✅ Changes to `scripts/utils/*.py` take effect immediately
- ✅ Adding new objects / changing keyframes just works
- ⚠️ Don't store persistent state across reloads (it will be lost)

### Error Handling

If your script has a syntax error or runtime error:
- The error is printed to Blender's terminal (the terminal where you ran `render.sh`)
- The error summary appears in the Script Watcher panel in Blender's sidebar
- The watcher keeps running — fix the error, save again, and it retries

### Debouncing

The watcher waits **0.5 seconds** after detecting a file change before reloading. This prevents reloading a half-written file if your editor auto-saves or does multi-step saves.

---

## File Organization for Animations

### Simple Animations

Single-file animations go directly in `scripts/animations/`:

```
scripts/animations/hello_cube.py
```

### Complex Animations

Multi-file animations get their own directory:

```
scripts/animations/finding_the_one/
├── STORYBOARD.md           # Detailed animation script
├── finding_the_one.py      # Main animation code
├── characters.py           # Character creation helpers (optional)
└── movements.py            # Movement path definitions (optional)
```

The main script file should match the directory name.

---

## Blender Version

This repo targets **Blender 5.0.1** on macOS. Key API notes:

| What | Blender 5.0 Value | Notes |
|------|--------------------|-------|
| EEVEE engine name | `'BLENDER_EEVEE'` | Was `'BLENDER_EEVEE_NEXT'` in 4.x |
| FFMPEG output | Not available via Python | Use PNG sequences + ffmpeg CLI |
| Blender path | `/Applications/Blender.app/Contents/MacOS/Blender` | Hardcoded in render.sh |
| Python version | Bundled with Blender | Not your system Python |

---

## Dependencies

| Tool | Required For | Install |
|------|-------------|---------|
| Blender 5.0+ | Everything | [blender.org](https://blender.org) |
| ffmpeg | Stitching frames to video | `brew install ffmpeg` |
