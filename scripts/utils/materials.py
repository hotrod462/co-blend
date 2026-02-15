"""
Material and shader creation helpers.
"""
import bpy


def create_principled_material(
    name="Material",
    color=(0.8, 0.2, 0.2, 1.0),
    metallic=0.0,
    roughness=0.5,
    emission_color=None,
    emission_strength=0.0,
):
    """
    Create a Principled BSDF material with common properties.
    Returns the material.
    """
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    principled = nodes.get("Principled BSDF")
    if principled is None:
        principled = nodes.new(type='ShaderNodeBsdfPrincipled')

    principled.inputs["Base Color"].default_value = color
    principled.inputs["Metallic"].default_value = metallic
    principled.inputs["Roughness"].default_value = roughness

    if emission_color:
        principled.inputs["Emission Color"].default_value = emission_color
        principled.inputs["Emission Strength"].default_value = emission_strength

    return mat


def create_glass_material(name="Glass", color=(0.9, 0.95, 1.0, 1.0), ior=1.45, roughness=0.0):
    """Create a glass-like material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    principled = nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = color
    principled.inputs["Roughness"].default_value = roughness
    principled.inputs["IOR"].default_value = ior
    principled.inputs["Transmission Weight"].default_value = 1.0

    return mat


def create_emission_material(name="Emission", color=(1.0, 0.5, 0.2, 1.0), strength=5.0):
    """Create a pure emission (glowing) material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Remove default nodes
    for node in nodes:
        nodes.remove(node)

    # Create emission + output
    emission = nodes.new(type='ShaderNodeEmission')
    emission.inputs["Color"].default_value = color
    emission.inputs["Strength"].default_value = strength

    output = nodes.new(type='ShaderNodeOutputMaterial')
    links.new(emission.outputs["Emission"], output.inputs["Surface"])

    return mat


def assign_material(obj, material):
    """Assign a material to an object."""
    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)
