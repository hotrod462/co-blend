"""
Tests for scripts/utils/materials.py — material creation helpers.
"""
import bpy
from tests.run_tests import test, assert_eq, assert_true, assert_near, assert_gt

from scripts.utils.scene import reset_scene
from scripts.utils.materials import (
    create_principled_material,
    create_glass_material,
    create_emission_material,
    assign_material,
)


# ──────────────────────────────────────────────
# create_principled_material
# ──────────────────────────────────────────────

@test
def test_principled_material_basic():
    """create_principled_material should create a material with correct name and color."""
    reset_scene()
    color = (0.5, 0.3, 0.1, 1.0)
    mat = create_principled_material(name="TestMat", color=color)

    assert_eq(mat.name, "TestMat")
    assert_true(mat.use_nodes, "Material should use nodes")

    principled = mat.node_tree.nodes.get("Principled BSDF")
    assert_true(principled is not None, "Should have Principled BSDF node")

    for i in range(4):
        assert_near(principled.inputs["Base Color"].default_value[i], color[i],
                    tolerance=0.01, msg=f"Color channel {i}")


@test
def test_principled_material_metallic_roughness():
    """create_principled_material should set metallic and roughness."""
    reset_scene()
    mat = create_principled_material(metallic=0.8, roughness=0.2)

    principled = mat.node_tree.nodes.get("Principled BSDF")
    assert_near(principled.inputs["Metallic"].default_value, 0.8)
    assert_near(principled.inputs["Roughness"].default_value, 0.2)


@test
def test_principled_material_emission():
    """create_principled_material should set emission color and strength."""
    reset_scene()
    emission_color = (1.0, 0.5, 0.0, 1.0)
    mat = create_principled_material(
        emission_color=emission_color,
        emission_strength=3.0,
    )

    principled = mat.node_tree.nodes.get("Principled BSDF")
    for i in range(4):
        assert_near(principled.inputs["Emission Color"].default_value[i],
                    emission_color[i], tolerance=0.01)
    assert_near(principled.inputs["Emission Strength"].default_value, 3.0)


@test
def test_principled_material_no_emission_by_default():
    """Without emission args, emission strength should stay at default (0)."""
    reset_scene()
    mat = create_principled_material(name="NoEmission")

    principled = mat.node_tree.nodes.get("Principled BSDF")
    assert_near(principled.inputs["Emission Strength"].default_value, 0.0)


# ──────────────────────────────────────────────
# create_glass_material
# ──────────────────────────────────────────────

@test
def test_glass_material():
    """create_glass_material should create a transmissive material."""
    reset_scene()
    mat = create_glass_material(name="GlassMat", ior=1.5, roughness=0.1)

    principled = mat.node_tree.nodes.get("Principled BSDF")
    assert_true(principled is not None)
    assert_near(principled.inputs["IOR"].default_value, 1.5)
    assert_near(principled.inputs["Roughness"].default_value, 0.1)
    assert_near(principled.inputs["Transmission Weight"].default_value, 1.0)


# ──────────────────────────────────────────────
# create_emission_material
# ──────────────────────────────────────────────

@test
def test_emission_material():
    """create_emission_material should create a pure emission shader."""
    reset_scene()
    color = (0.0, 1.0, 0.5, 1.0)
    mat = create_emission_material(name="GlowMat", color=color, strength=10.0)

    assert_eq(mat.name, "GlowMat")
    assert_true(mat.use_nodes)

    # Should have an Emission node
    emission_nodes = [n for n in mat.node_tree.nodes if n.type == 'EMISSION']
    assert_eq(len(emission_nodes), 1, "Should have exactly one Emission node")

    emission = emission_nodes[0]
    for i in range(4):
        assert_near(emission.inputs["Color"].default_value[i], color[i], tolerance=0.01)
    assert_near(emission.inputs["Strength"].default_value, 10.0)


@test
def test_emission_material_has_output():
    """create_emission_material should connect emission to material output."""
    reset_scene()
    mat = create_emission_material()

    output_nodes = [n for n in mat.node_tree.nodes if n.type == 'OUTPUT_MATERIAL']
    assert_eq(len(output_nodes), 1, "Should have exactly one Output node")

    # Check that surface input is connected
    output = output_nodes[0]
    assert_true(output.inputs["Surface"].is_linked, "Surface should be linked")


# ──────────────────────────────────────────────
# assign_material
# ──────────────────────────────────────────────

@test
def test_assign_material_to_empty_slots():
    """assign_material should add material to an object with no material slots."""
    reset_scene()
    bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.active_object
    mat = create_principled_material(name="CubeMat")

    assert_eq(len(cube.data.materials), 0, "Cube should start with no materials")

    assign_material(cube, mat)
    assert_eq(len(cube.data.materials), 1, "Cube should have 1 material")
    assert_eq(cube.data.materials[0].name, "CubeMat")


@test
def test_assign_material_replaces_existing():
    """assign_material should replace the first material slot."""
    reset_scene()
    bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.active_object

    mat1 = create_principled_material(name="OldMat")
    mat2 = create_principled_material(name="NewMat")

    assign_material(cube, mat1)
    assert_eq(cube.data.materials[0].name, "OldMat")

    assign_material(cube, mat2)
    assert_eq(cube.data.materials[0].name, "NewMat")
    assert_eq(len(cube.data.materials), 1, "Should still be 1 slot")
