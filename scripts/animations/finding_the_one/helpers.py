"""
Finding the One — Keyframing & Animation Helpers.

Shared functions used by every act module. These wrap low-level Blender
keyframe operations into convenient shorthand.
"""
import bpy
import math

from scripts.utils.animation import ease_in_out_cubic, lerp

from scripts.animations.finding_the_one.config import (
    PULSE_BASE_PERIOD, PULSE_BASE_AMP,
)


# ══════════════════════════════════════════════════════════════
#  KEYFRAME SHORTHAND
# ══════════════════════════════════════════════════════════════

def kf_loc(obj, x, y, frame):
    """Insert a location keyframe (Z always 0 for top-down)."""
    obj.location = (x, y, 0)
    obj.keyframe_insert(data_path="location", frame=frame)


def kf_scale(obj, s, frame):
    """Insert a uniform scale keyframe."""
    obj.scale = (s, s, s)
    obj.keyframe_insert(data_path="scale", frame=frame)


def kf_rot_z(obj, angle_rad, frame):
    """Insert a Z-rotation keyframe."""
    obj.rotation_euler[2] = angle_rad
    obj.keyframe_insert(data_path="rotation_euler", index=2, frame=frame)


def kf_emission_strength(mat, strength, frame):
    """Keyframe the emission strength of an emission material."""
    emission_node = None
    for node in mat.node_tree.nodes:
        if node.type == 'EMISSION':
            emission_node = node
            break
    if emission_node is None:
        return
    emission_node.inputs["Strength"].default_value = strength
    emission_node.inputs["Strength"].keyframe_insert("default_value", frame=frame)


def kf_emission_color(mat, r, g, b, a, frame):
    """Keyframe the RGBA color of an emission material."""
    emission_node = None
    for node in mat.node_tree.nodes:
        if node.type == 'EMISSION':
            emission_node = node
            break
    if emission_node is None:
        return
    emission_node.inputs["Color"].default_value = (r, g, b, a)
    emission_node.inputs["Color"].keyframe_insert("default_value", frame=frame)


def kf_ortho_scale(camera, scale, frame):
    """Keyframe the orthographic scale of a camera."""
    camera.data.ortho_scale = scale
    camera.data.keyframe_insert(data_path="ortho_scale", frame=frame)


# ══════════════════════════════════════════════════════════════
#  INTERPOLATION & MOVEMENT
# ══════════════════════════════════════════════════════════════

def interp(start, end, t, easing=None):
    """Interpolate between two (x, y) tuples."""
    if easing:
        t = easing(t)
    return (
        start[0] + (end[0] - start[0]) * t,
        start[1] + (end[1] - start[1]) * t,
    )


def move_along(obj, waypoints, easing=None):
    """
    Move an object through a list of (frame, x, y) waypoints.
    Interpolates between consecutive waypoints with optional easing.
    """
    for i in range(len(waypoints) - 1):
        f0, x0, y0 = waypoints[i]
        f1, x1, y1 = waypoints[i + 1]
        for f in range(f0, f1 + 1):
            t = (f - f0) / max(f1 - f0, 1)
            pos = interp((x0, y0), (x1, y1), t, easing)
            kf_loc(obj, pos[0], pos[1], f)


def lerp_value(a, b, t, easing=None):
    """Lerp a single value with optional easing."""
    if easing:
        t = easing(t)
    return a + (b - a) * t


# ══════════════════════════════════════════════════════════════
#  PULSE & SIGH
# ══════════════════════════════════════════════════════════════

def apply_pulse(obj, frame_start, frame_end, period=PULSE_BASE_PERIOD,
                amplitude=PULSE_BASE_AMP, base_scale=1.0):
    """Apply a continuous heartbeat pulse (scale oscillation) over a frame range."""
    for f in range(frame_start, frame_end + 1):
        phase = (f - frame_start) / period * 2 * math.pi
        s = base_scale + amplitude * (0.5 + 0.5 * math.sin(phase))
        kf_scale(obj, s, f)


def apply_sigh(obj, frame_start, frame_end, depth=0.08):
    """A 'sigh' — deflate then reinflate."""
    mid = (frame_start + frame_end) // 2
    for f in range(frame_start, mid + 1):
        t = (f - frame_start) / max(mid - frame_start, 1)
        s = 1.0 - depth * ease_in_out_cubic(t)
        kf_scale(obj, s, f)
    for f in range(mid, frame_end + 1):
        t = (f - mid) / max(frame_end - mid, 1)
        s = (1.0 - depth) + depth * ease_in_out_cubic(t)
        kf_scale(obj, s, f)


# ══════════════════════════════════════════════════════════════
#  ORBIT HELPERS
# ══════════════════════════════════════════════════════════════

def orbit_pair(obj_a, obj_b, center, frame_start, frame_end,
               radius_start, radius_end, rpm_start, rpm_end):
    """
    Orbit two objects around a center point (always opposite each other).
    RPM here means revolutions per 60 frames (2 seconds).
    """
    total = frame_end - frame_start
    for f in range(frame_start, frame_end + 1):
        t = (f - frame_start) / max(total, 1)
        radius = lerp(radius_start, radius_end, t)
        # Accumulate angle
        angle = 0.0
        for ff in range(frame_start, f + 1):
            tt = (ff - frame_start) / max(total, 1)
            rpm_at = lerp(rpm_start, rpm_end, tt)
            angle += rpm_at * 2 * math.pi / 60.0

        ax = center[0] + radius * math.cos(angle)
        ay = center[1] + radius * math.sin(angle)
        bx = center[0] + radius * math.cos(angle + math.pi)
        by = center[1] + radius * math.sin(angle + math.pi)

        kf_loc(obj_a, ax, ay, f)
        kf_loc(obj_b, bx, by, f)


def orbit_single(obj, center_x, center_y, frame_start, frame_end,
                 radius, revolutions, start_angle=0):
    """
    Orbit a single object around a center point.
    Smooth circular motion.
    """
    total = frame_end - frame_start
    for f in range(frame_start, frame_end + 1):
        t = (f - frame_start) / max(total, 1)
        angle = start_angle + t * revolutions * 2 * math.pi
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        kf_loc(obj, x, y, f)


# ══════════════════════════════════════════════════════════════
#  INTERPOLATION FLATTENING
# ══════════════════════════════════════════════════════════════

def set_all_linear_interpolation():
    """
    Set all object and material F-Curves to LINEAR interpolation.
    The easing is baked into the keyframe values, so Blender's
    built-in interpolation should be linear.
    """
    for obj in bpy.data.objects:
        if obj.animation_data and obj.animation_data.action:
            if hasattr(obj.animation_data.action, "fcurves"):
                for fcurve in obj.animation_data.action.fcurves:
                    for kp in fcurve.keyframe_points:
                        kp.interpolation = 'LINEAR'

    for mat in bpy.data.materials:
        if mat.node_tree and mat.node_tree.animation_data and mat.node_tree.animation_data.action:
            if hasattr(mat.node_tree.animation_data.action, "fcurves"):
                for fcurve in mat.node_tree.animation_data.action.fcurves:
                    for kp in fcurve.keyframe_points:
                        kp.interpolation = 'LINEAR'


# ══════════════════════════════════════════════════════════════
#  VIEWPORT
# ══════════════════════════════════════════════════════════════

def set_viewport_to_camera():
    """Force the 3D viewport to camera view with rendered shading."""
    import sys
    if "--background" in sys.argv or "-b" in sys.argv:
        return
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.region_3d.view_perspective = 'CAMERA'
                    space.shading.type = 'RENDERED'
