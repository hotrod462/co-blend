"""
Scene setup helpers — camera, lighting, world environment.
"""
import bpy
import math


def clear_scene():
    """Remove all objects, meshes, materials, etc. from the scene."""
    bpy.ops.wm.read_factory_settings(use_empty=True)


def setup_camera(location=(7, -7, 5), target=(0, 0, 0)):
    """
    Add a camera and point it at a target location.
    Returns the camera object.
    """
    bpy.ops.object.camera_add(location=location)
    camera = bpy.context.active_object
    camera.name = "ScriptCamera"

    # Point camera at target using a Track To constraint
    constraint = camera.constraints.new(type='TRACK_TO')
    # Create an empty at the target to track
    bpy.ops.object.empty_add(location=target)
    target_empty = bpy.context.active_object
    target_empty.name = "CameraTarget"
    constraint.target = target_empty
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'

    bpy.context.scene.camera = camera
    return camera


def setup_sun_light(energy=3.0, direction=(-0.5, -0.5, -1.0)):
    """Add a sun lamp with the given energy and direction."""
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
    sun = bpy.context.active_object
    sun.name = "SunLight"
    sun.data.energy = energy

    # Point the sun in the given direction
    dir_vec = mathutils_vector(direction)
    sun.rotation_euler = dir_vec.to_track_quat('-Z', 'Y').to_euler()
    return sun


def setup_area_light(location=(4, -4, 6), energy=200, size=3):
    """Add a soft area light."""
    bpy.ops.object.light_add(type='AREA', location=location)
    light = bpy.context.active_object
    light.name = "AreaLight"
    light.data.energy = energy
    light.data.size = size
    return light


def setup_world_color(color=(0.05, 0.05, 0.08, 1.0)):
    """Set the world background to a solid color."""
    world = bpy.data.worlds.new("ScriptWorld")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes["Background"]
    bg_node.inputs["Color"].default_value = color
    bg_node.inputs["Strength"].default_value = 1.0


def setup_render(
    engine='BLENDER_EEVEE_NEXT',
    resolution=(1920, 1080),
    fps=30,
    frame_start=1,
    frame_end=120,
    output_path='./output/',
    file_format='FFMPEG',
):
    """Configure render settings."""
    scene = bpy.context.scene
    scene.render.engine = engine
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.fps = fps
    scene.frame_start = frame_start
    scene.frame_end = frame_end
    scene.render.filepath = output_path

    if file_format == 'FFMPEG':
        scene.render.image_settings.file_format = 'FFMPEG'
        scene.render.ffmpeg.format = 'MPEG4'
        scene.render.ffmpeg.codec = 'H264'
        scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    elif file_format == 'PNG':
        scene.render.image_settings.file_format = 'PNG'


def mathutils_vector(v):
    """Convert a tuple to a mathutils.Vector."""
    import mathutils
    return mathutils.Vector(v)
