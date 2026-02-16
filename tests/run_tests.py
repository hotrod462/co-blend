"""
Test runner for blender-animations.

Since bpy is only available inside Blender's Python, all tests run through
Blender's CLI. This script implements a minimal test framework (assert-based)
and runs all test modules.

Usage:
    ./run_tests.sh                      # run all tests
    ./run_tests.sh tests/test_scene.py  # run a specific test file

Exit code 0 = all passed, 1 = failures.
"""

import sys
import os
import time
import traceback
import importlib.util

# ── Setup project root ──
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# IMPORTANT: Register this module under its package name so that
# `from tests.run_tests import test` in test files references the SAME
# module object (and the same _test_functions list) regardless of whether
# this file is executed as __main__ or imported.
import types
_this_module = sys.modules[__name__]
sys.modules["tests.run_tests"] = _this_module


# ──────────────────────────────────────────────
# Minimal Test Framework
# ──────────────────────────────────────────────

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = 0
        self.failures = []  # list of (test_name, error_msg)

    @property
    def total(self):
        return self.passed + self.failed + self.errors


_current_result = TestResult()
_test_functions = []


def test(func):
    """Decorator to mark a function as a test case."""
    _test_functions.append(func)
    return func


def assert_eq(actual, expected, msg=""):
    """Assert two values are equal."""
    if actual != expected:
        detail = f"Expected {expected!r}, got {actual!r}"
        if msg:
            detail = f"{msg}: {detail}"
        raise AssertionError(detail)


def assert_near(actual, expected, tolerance=1e-6, msg=""):
    """Assert two floats are approximately equal."""
    if abs(actual - expected) > tolerance:
        detail = f"Expected ~{expected}, got {actual} (tolerance={tolerance})"
        if msg:
            detail = f"{msg}: {detail}"
        raise AssertionError(detail)


def assert_true(value, msg=""):
    """Assert a value is truthy."""
    if not value:
        detail = f"Expected truthy, got {value!r}"
        if msg:
            detail = f"{msg}: {detail}"
        raise AssertionError(detail)


def assert_false(value, msg=""):
    """Assert a value is falsy."""
    if value:
        detail = f"Expected falsy, got {value!r}"
        if msg:
            detail = f"{msg}: {detail}"
        raise AssertionError(detail)


def assert_gt(actual, threshold, msg=""):
    """Assert actual > threshold."""
    if not (actual > threshold):
        detail = f"Expected {actual!r} > {threshold!r}"
        if msg:
            detail = f"{msg}: {detail}"
        raise AssertionError(detail)


def assert_gte(actual, threshold, msg=""):
    """Assert actual >= threshold."""
    if not (actual >= threshold):
        detail = f"Expected {actual!r} >= {threshold!r}"
        if msg:
            detail = f"{msg}: {detail}"
        raise AssertionError(detail)


def assert_isinstance(obj, cls, msg=""):
    """Assert obj is an instance of cls."""
    if not isinstance(obj, cls):
        detail = f"Expected instance of {cls.__name__}, got {type(obj).__name__}"
        if msg:
            detail = f"{msg}: {detail}"
        raise AssertionError(detail)


def run_tests(test_funcs=None):
    """Run all registered test functions and print results."""
    global _current_result
    _current_result = TestResult()

    funcs = test_funcs or _test_functions

    print(f"\n{'='*60}")
    print(f"  Running {len(funcs)} tests")
    print(f"{'='*60}\n")

    for func in funcs:
        test_name = f"{func.__module__}.{func.__name__}"
        try:
            func()
            _current_result.passed += 1
            print(f"  ✅ {test_name}")
        except AssertionError as e:
            _current_result.failed += 1
            _current_result.failures.append((test_name, str(e)))
            print(f"  ❌ {test_name}: {e}")
        except Exception as e:
            _current_result.errors += 1
            tb = traceback.format_exc()
            _current_result.failures.append((test_name, tb))
            print(f"  💥 {test_name}: {e}")
            print(f"     {tb.splitlines()[-2]}")

    return _current_result


def print_summary(result):
    """Print final test summary."""
    print(f"\n{'='*60}")
    if result.failed + result.errors == 0:
        print(f"  ✅ ALL {result.total} TESTS PASSED")
    else:
        print(f"  ❌ {result.failed} FAILED, {result.errors} ERRORS, {result.passed} passed")
        print()
        for name, msg in result.failures:
            print(f"  FAIL: {name}")
            # Only show first 3 lines of error
            for line in msg.strip().splitlines()[:3]:
                print(f"        {line}")
            print()
    print(f"{'='*60}\n")


def discover_and_run(test_dir=None, specific_file=None):
    """Discover test files and run them all."""
    global _test_functions
    _test_functions = []

    if test_dir is None:
        test_dir = os.path.dirname(os.path.abspath(__file__))

    if specific_file:
        test_files = [specific_file]
    else:
        test_files = sorted([
            os.path.join(test_dir, f)
            for f in os.listdir(test_dir)
            if f.startswith("test_") and f.endswith(".py")
        ])

    for filepath in test_files:
        module_name = os.path.splitext(os.path.basename(filepath))[0]
        print(f"\n📦 Loading: {module_name}")

        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

    result = run_tests()
    print_summary(result)

    return result.failed + result.errors


# ──────────────────────────────────────────────
# Entry point (when run via Blender)
# ──────────────────────────────────────────────

if __name__ == "__main__":
    # Parse args after "--"
    specific_file = None
    if "--" in sys.argv:
        custom_args = sys.argv[sys.argv.index("--") + 1:]
        if custom_args:
            specific_file = os.path.abspath(custom_args[0])

    failures = discover_and_run(specific_file=specific_file)
    sys.exit(failures)
