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
    engine='BLENDER_EEVEE',
    resolution=(1920, 1080),
    fps=30,
    frame_start=1,
    frame_end=120,
    output_path='./output/frames/',
    file_format='PNG',
):
    """
    Configure render settings.

    Renders to PNG frame sequences by default, which is more robust than
    direct FFMPEG output (supports resuming interrupted renders, lossless
    intermediate frames, and flexible re-encoding).

    Use frames_to_video() after rendering to stitch frames into an MP4.
    """
    scene = bpy.context.scene
    scene.render.engine = engine
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.fps = fps
    scene.frame_start = frame_start
    scene.frame_end = frame_end

    # Ensure output path ends with a separator for frame numbering
    if not output_path.endswith('/'):
        output_path += '/'
    scene.render.filepath = output_path

    scene.render.image_settings.file_format = file_format
    if file_format == 'PNG':
        scene.render.image_settings.color_mode = 'RGBA'
        scene.render.image_settings.compression = 15


def frames_to_video(frames_dir='./output/frames/', output_file='./output/animation.mp4', fps=30):
    """
    Stitch rendered PNG frames into an MP4 video using ffmpeg CLI.
    Call this after bpy.ops.render.render(animation=True).

    Requires ffmpeg to be installed (brew install ffmpeg).
    """
    import subprocess
    import glob
    import os

    # Find the frame pattern (Blender outputs as 0001.png, 0002.png, etc.)
    frames = sorted(glob.glob(os.path.join(frames_dir, '*.png')))
    if not frames:
        print(f"⚠️  No PNG frames found in {frames_dir}")
        return

    print(f"🎬 Stitching {len(frames)} frames into {output_file}...")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    cmd = [
        'ffmpeg', '-y',                         # Overwrite output
        '-framerate', str(fps),                  # Input framerate
        '-i', os.path.join(frames_dir, '%04d.png'),  # Frame pattern
        '-c:v', 'libx264',                      # H.264 codec
        '-crf', '18',                            # Quality (lower = better, 18 is visually lossless)
        '-pix_fmt', 'yuv420p',                   # Compatibility
        '-preset', 'medium',                     # Encoding speed/quality tradeoff
        output_file,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Video saved to {output_file}")
    else:
        print(f"❌ ffmpeg failed: {result.stderr}")
        print("   Make sure ffmpeg is installed: brew install ffmpeg")


def mathutils_vector(v):
    """Convert a tuple to a mathutils.Vector."""
    import mathutils
    return mathutils.Vector(v)
