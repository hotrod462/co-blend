"""
Animation helpers — easing functions, keyframe utilities.
"""
import bpy
import math


# ──────────────────────────────────────────────
# Easing functions (t goes from 0.0 to 1.0)
# ──────────────────────────────────────────────

def ease_in_out_cubic(t):
    """Smooth acceleration then deceleration."""
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 3) / 2


def ease_in_out_quad(t):
    """Quadratic ease in-out."""
    if t < 0.5:
        return 2 * t * t
    else:
        return 1 - pow(-2 * t + 2, 2) / 2


def ease_out_bounce(t):
    """Bouncy ease out."""
    n1 = 7.5625
    d1 = 2.75
    if t < 1 / d1:
        return n1 * t * t
    elif t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    elif t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    else:
        t -= 2.625 / d1
        return n1 * t * t + 0.984375


def ease_out_elastic(t):
    """Elastic overshoot ease out."""
    if t == 0 or t == 1:
        return t
    return pow(2, -10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi) / 3) + 1


def lerp(a, b, t):
    """Linear interpolation between a and b."""
    return a + (b - a) * t


# ──────────────────────────────────────────────
# Keyframe helpers
# ──────────────────────────────────────────────

def animate_property(obj, data_path, values, frame_start=1, frame_end=120, easing=None):
    """
    Animate a property from values[0] to values[1] over a frame range.

    Args:
        obj: The Blender object
        data_path: Property path, e.g. "location", "rotation_euler"
        values: Tuple of (start_value, end_value) — can be floats or tuples
        frame_start: First frame
        frame_end: Last frame
        easing: Optional easing function (defaults to linear)
    """
    total_frames = frame_end - frame_start

    for frame in range(frame_start, frame_end + 1):
        t = (frame - frame_start) / total_frames if total_frames > 0 else 1.0
        if easing:
            t = easing(t)

        bpy.context.scene.frame_set(frame)

        start_val = values[0]
        end_val = values[1]

        # Handle tuple values (e.g., location = (x, y, z))
        if isinstance(start_val, (tuple, list)):
            prop = getattr(obj, data_path)
            for i in range(len(start_val)):
                prop[i] = lerp(start_val[i], end_val[i], t)
                obj.keyframe_insert(data_path=data_path, index=i, frame=frame)
        else:
            setattr(obj, data_path, lerp(start_val, end_val, t))
            obj.keyframe_insert(data_path=data_path, frame=frame)


def set_keyframe(obj, data_path, value, frame, index=-1):
    """Set a single keyframe on a property at the given frame."""
    bpy.context.scene.frame_set(frame)

    if index >= 0:
        getattr(obj, data_path)[index] = value
        obj.keyframe_insert(data_path=data_path, index=index, frame=frame)
    else:
        setattr(obj, data_path, value)
        obj.keyframe_insert(data_path=data_path, frame=frame)
