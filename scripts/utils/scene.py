"""
Scene setup helpers — camera, lighting, world environment.
"""
import bpy
import math


def reset_scene():
    """
    Remove all scene contents without resetting the Blender session.

    This is the hot-reload-safe version: it preserves the UI layout,
    loaded addons, and preferences. Use this instead of clear_scene()
    when working with the Script Watcher addon.
    """
    # Ensure we're in object mode
    if bpy.context.mode != 'OBJECT':
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except RuntimeError:
            pass

    # Remove all objects
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)

    # Remove all data blocks by type
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh, do_unlink=True)
    for curve in bpy.data.curves:
        bpy.data.curves.remove(curve, do_unlink=True)
    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat, do_unlink=True)
    for world in bpy.data.worlds:
        bpy.data.worlds.remove(world, do_unlink=True)
    for light in bpy.data.lights:
        bpy.data.lights.remove(light, do_unlink=True)
    for cam in bpy.data.cameras:
        bpy.data.cameras.remove(cam, do_unlink=True)
    for action in bpy.data.actions:
        bpy.data.actions.remove(action, do_unlink=True)
    for ng in bpy.data.node_groups:
        bpy.data.node_groups.remove(ng, do_unlink=True)

    # Purge orphaned data blocks
    bpy.ops.outliner.orphans_purge(do_recursive=True)

    # Reset timeline
    bpy.context.scene.frame_set(1)


def clear_scene():
    """
    Remove all scene contents. Alias for reset_scene().

    Uses the hot-reload-safe approach so it works with both
    headless rendering and --watch mode.
    """
    reset_scene()


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


def setup_ortho_camera(location=(0, 0, 10), ortho_scale=20):
    """
    Add a top-down orthographic camera looking straight down.
    Ideal for 2D animation scenes.

    Args:
        location: Camera position (default: 10 units above origin)
        ortho_scale: Width of the orthographic view in Blender units
    Returns the camera object.
    """
    bpy.ops.object.camera_add(location=location)
    camera = bpy.context.active_object
    camera.name = "OrthoCamera"
    camera.rotation_euler = (0, 0, 0)  # Looking straight down (-Z)
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = ortho_scale

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
    output_path='./output/render',
    file_format='FFMPEG',
):
    """
    Configure render settings optimized for Blender 5.0 and Apple Silicon.

    Defaults to FFMPEG direct video export for speed on modern hardware,
    but supports PNG sequences for robust production rendering.
    """
    scene = bpy.context.scene
    
    # 1. Hardware Optimization (Apple Silicon Metal)
    try:
        cycles_prefs = bpy.context.preferences.addons['cycles'].preferences
        cycles_prefs.compute_device_type = 'METAL'
        # Refresh devices and enable GPU
        cycles_prefs.get_devices()
        for device in cycles_prefs.devices:
            if device.type == 'METAL':
                device.use = True
        scene.cycles.device = 'GPU'
    except Exception as e:
        print(f"⚠️ Could not enable Metal GPU: {e}")

    # 2. Engine Setup
    # Blender 5.0 uses EEVEE as the primary real-time engine (formerly EEVEE_NEXT)
    scene.render.engine = engine

    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.fps = fps
    scene.frame_start = frame_start
    scene.frame_end = frame_end

    # 3. Output Configuration
    image_settings = scene.render.image_settings
    
    if file_format == 'FFMPEG':
        # Blender 5.0 requires setting media_type to 'VIDEO' before setting format to 'FFMPEG'
        if hasattr(image_settings, "media_type"):
            image_settings.media_type = 'VIDEO'
        
        image_settings.file_format = 'FFMPEG'
        
        # Optimized for M4 Pro playback compatibility
        scene.render.ffmpeg.format = 'MPEG4'
        scene.render.ffmpeg.codec = 'H264'
        scene.render.ffmpeg.constant_rate_factor = 'HIGH'
        scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
        
        # Ensure path has .mp4 extension for direct video
        if not output_path.lower().endswith('.mp4'):
            output_path += '.mp4'
    else:
        # For image formats (PNG, etc)
        if hasattr(image_settings, "media_type"):
            image_settings.media_type = 'IMAGE'
            
        image_settings.file_format = file_format
        
        # For PNG sequences, ensure trailing slash
        if not output_path.endswith('/'):
            output_path += '/'
            
    scene.render.filepath = output_path

    if file_format == 'PNG':
        image_settings.color_mode = 'RGBA'
        image_settings.compression = 15




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
