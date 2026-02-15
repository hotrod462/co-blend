#!/bin/bash
# Convenience wrapper to run Blender with a Python script.
#
# Usage:
#   ./render.sh scripts/animations/hello_cube.py          # headless render
#   ./render.sh scripts/animations/hello_cube.py --gui     # open in Blender GUI

BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"

if [ -z "$1" ]; then
    echo "Usage: ./render.sh <script.py> [--gui]"
    echo ""
    echo "Options:"
    echo "  --gui    Open in Blender GUI instead of headless mode"
    exit 1
fi

SCRIPT="$1"
shift

# Check if --gui flag is present
GUI_MODE=false
for arg in "$@"; do
    if [ "$arg" = "--gui" ]; then
        GUI_MODE=true
    fi
done

# Ensure output directory exists
mkdir -p output

if [ "$GUI_MODE" = true ]; then
    echo "🎬 Opening in Blender GUI: $SCRIPT"
    "$BLENDER" --python "$SCRIPT"
else
    echo "🎬 Rendering headlessly: $SCRIPT"
    "$BLENDER" --background --python "$SCRIPT"
fi
