#!/bin/bash
# Convenience wrapper to run Blender with a Python script.
#
# Usage:
#   ./render.sh scripts/animations/your_script.py              # headless render
#   ./render.sh scripts/animations/your_script.py --gui        # open in Blender GUI
#   ./render.sh scripts/animations/your_script.py --watch      # GUI + hot-reload on save
#
# The --watch mode installs the Script Watcher addon, loads your script,
# and auto-reloads whenever you save in your editor. Press Space to play.

BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -z "$1" ]; then
    echo "Usage: ./render.sh <script.py> [--gui | --watch]"
    echo ""
    echo "Modes:"
    echo "  (default)  Headless render — renders frames and stitches video"
    echo "  --gui      Open in Blender GUI for manual preview"
    echo "  --watch    GUI + hot-reload — auto-reloads on file save"
    exit 1
fi

SCRIPT="$1"
shift

# Parse flags
MODE="headless"
for arg in "$@"; do
    case "$arg" in
        --gui)   MODE="gui" ;;
        --watch) MODE="watch" ;;
    esac
done

# Ensure output directory exists
mkdir -p output

case "$MODE" in
    headless)
        echo "🎬 Rendering headlessly: $SCRIPT"
        "$BLENDER" --background --python "$SCRIPT"
        ;;
    gui)
        echo "🎬 Opening in Blender GUI: $SCRIPT"
        "$BLENDER" --python "$SCRIPT"
        ;;
    watch)
        # Convert script path to absolute
        ABS_SCRIPT="$(cd "$(dirname "$SCRIPT")" && pwd)/$(basename "$SCRIPT")"
        echo "👀 Starting watch mode: $SCRIPT"
        echo "   Hot-reload is active — save your script to see changes."
        echo "   Press Space in the Blender viewport to play the animation."
        echo ""
        "$BLENDER" --python "$SCRIPT_DIR/addons/watch_bootstrap.py" -- "$ABS_SCRIPT"
        ;;
esac
