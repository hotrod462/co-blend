# Blender Animations

Procedural animations created with Python + Blender.

## Requirements

- **Blender 5.0.1** (installed at `/Applications/Blender.app/Contents/MacOS/Blender`)

## Usage

Run a script headlessly:

```bash
./render.sh scripts/animations/your_animation.py
```

Or with the Blender GUI for previewing:

```bash
./render.sh scripts/animations/your_animation.py --gui
```

## Project Structure

```
blender-animations/
├── scripts/
│   ├── utils/              # Shared helper modules
│   │   ├── scene.py        # Scene setup helpers (camera, lighting, world)
│   │   ├── materials.py    # Material/shader creation helpers
│   │   └── animation.py    # Easing functions, keyframe helpers
│   └── animations/         # Individual animation scripts
│       └── hello_cube.py   # Starter example
├── assets/                 # Imported models, textures, HDRIs
├── output/                 # Rendered frames and videos (gitignored)
├── render.sh               # Convenience script to run Blender
└── README.md
```

## Tips

- Use `./render.sh script.py --gui` when iterating on a scene visually
- Use `./render.sh script.py` (headless) for final renders
- EEVEE is fast for previews; switch to Cycles for photorealistic output
- Rendered output goes to `./output/` and is gitignored
