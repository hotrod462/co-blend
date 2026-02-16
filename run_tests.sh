#!/bin/bash
# Run the test suite through Blender's Python.
#
# Usage:
#   ./run_tests.sh                          # run all tests
#   ./run_tests.sh tests/test_scene.py      # run a specific test file
#
# Exit code: 0 = all passed, non-zero = failures

BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🧪 Running tests via Blender..."
echo ""

if [ -n "$1" ]; then
    "$BLENDER" --background --python "$SCRIPT_DIR/tests/run_tests.py" -- "$1"
else
    "$BLENDER" --background --python "$SCRIPT_DIR/tests/run_tests.py"
fi

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "🎉 All tests passed!"
else
    echo "💥 Some tests failed (exit code $EXIT_CODE)"
fi

exit $EXIT_CODE
