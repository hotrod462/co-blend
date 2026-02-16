"""
Finding the One — Character Creation.
Factory functions that create each shape and its material.
"""
import bpy
import math
import random

from scripts.utils.materials import create_emission_material, assign_material
from scripts.animations.finding_the_one.config import (
    PARENT_TRI_LEG, PARENT_FILL_GRAY, PARENT_EMISSION,
    SEEKER_SIZE, SEEKER_FILL_GRAY, SEEKER_EMISSION,
    RIGHT_TRI_LEG, RIGHT_TRI_FILL_GRAY, RIGHT_TRI_EMISSION,
    ISO_TRI_BASE, ISO_TRI_HEIGHT, ISO_TRI_FILL_GRAY, ISO_TRI_EMISSION,
    ONE_SIZE, ONE_FILL_GRAY, ONE_EMISSION,
    BG_TRI_SIZE, BG_TRI_FILL_GRAY_MIN, BG_TRI_FILL_GRAY_MAX,
    BG_TRI_EMISSION, BG_TRI_COUNT, BG_TRI_EXCLUSION_Y,
    WORLD_PATH_LENGTH,
)


def _create_right_angle_tri(name, leg_size, location=(0, 0, 0)):
    import bmesh
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bm = bmesh.new()
    half = leg_size / 2
    v1 = bm.verts.new((-half, -half, 0))
    v2 = bm.verts.new((half, -half, 0))
    v3 = bm.verts.new((-half, half, 0))
    bm.faces.new([v1, v2, v3])
    bm.to_mesh(mesh)
    bm.free()
    obj.location = location
    return obj


def _create_isosceles_tri(name, base, height, location=(0, 0, 0)):
    import bmesh
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bm = bmesh.new()
    half_base = base / 2
    v1 = bm.verts.new((-half_base, -height / 3, 0))
    v2 = bm.verts.new((half_base, -height / 3, 0))
    v3 = bm.verts.new((0, 2 * height / 3, 0))
    bm.faces.new([v1, v2, v3])
    bm.to_mesh(mesh)
    bm.free()
    obj.location = location
    return obj


def _create_equilateral_tri(name, size, location=(0, 0, 0)):
    import bmesh
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bm = bmesh.new()
    half = size / 2
    h = size * math.sqrt(3) / 2
    v1 = bm.verts.new((-half, -h / 3, 0))
    v2 = bm.verts.new((half, -h / 3, 0))
    v3 = bm.verts.new((0, 2 * h / 3, 0))
    bm.faces.new([v1, v2, v3])
    bm.to_mesh(mesh)
    bm.free()
    obj.location = location
    return obj


def create_parent_triangles():
    results = []
    for idx, name in enumerate(["ParentTriA", "ParentTriB"]):
        g = PARENT_FILL_GRAY
        mat = create_emission_material(f"{name}Mat", color=(g, g, g, 1), strength=PARENT_EMISSION)
        obj = _create_right_angle_tri(name, PARENT_TRI_LEG, location=(-50, 0, 0))
        assign_material(obj, mat)
        results.append((obj, mat))
    return results


def create_seeker():
    g = SEEKER_FILL_GRAY
    mat = create_emission_material("SeekerMat", color=(g, g, g, 1), strength=SEEKER_EMISSION)
    bpy.ops.mesh.primitive_plane_add(size=SEEKER_SIZE, location=(-50, 0, 0))
    obj = bpy.context.active_object
    obj.name = "Seeker"
    assign_material(obj, mat)
    return obj, mat


def create_right_angle_triangle():
    g = RIGHT_TRI_FILL_GRAY
    mat = create_emission_material("RightTriMat", color=(g, g, g, 1), strength=RIGHT_TRI_EMISSION)
    obj = _create_right_angle_tri("RightAngleTri", RIGHT_TRI_LEG, location=(-50, 0, 0))
    assign_material(obj, mat)
    return obj, mat


def create_isosceles_triangle():
    g = ISO_TRI_FILL_GRAY
    mat = create_emission_material("IsoTriMat", color=(g, g, g, 1), strength=ISO_TRI_EMISSION)
    obj = _create_isosceles_tri("IsoscelesTri", ISO_TRI_BASE, ISO_TRI_HEIGHT, location=(-50, 0, 0))
    assign_material(obj, mat)
    return obj, mat


def create_the_one():
    g = ONE_FILL_GRAY
    mat = create_emission_material("TheOneMat", color=(g, g, g, 1), strength=ONE_EMISSION)
    bpy.ops.mesh.primitive_plane_add(size=ONE_SIZE, location=(-50, 0, 0))
    obj = bpy.context.active_object
    obj.name = "TheOne"
    assign_material(obj, mat)
    return obj, mat


def create_background_triangles(count=BG_TRI_COUNT, seed=42):
    """All equilateral, same size, excluded from protagonist's Y path."""
    random.seed(seed)
    triangles = []

    for i in range(count):
        world_x = random.uniform(-5, WORLD_PATH_LENGTH + 5)
        # Exclude the central Y band where protagonist travels
        if random.random() < 0.5:
            world_y = random.uniform(-4.5, -BG_TRI_EXCLUSION_Y)
        else:
            world_y = random.uniform(BG_TRI_EXCLUSION_Y, 4.5)
        gray = random.uniform(BG_TRI_FILL_GRAY_MIN, BG_TRI_FILL_GRAY_MAX)
        name = f"BgTri_{i:03d}"
        mat = create_emission_material(f"{name}Mat", color=(gray, gray, gray, 1), strength=BG_TRI_EMISSION)
        obj = _create_equilateral_tri(name, BG_TRI_SIZE, location=(world_x, world_y, -0.01))
        assign_material(obj, mat)
        obj.rotation_euler[2] = random.uniform(0, 2 * math.pi)
        triangles.append((obj, mat, world_x, world_y))

    return triangles
