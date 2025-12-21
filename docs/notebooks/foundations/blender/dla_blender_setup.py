"""
DLA Point Cloud Generator for Blender with Geometry Nodes

This script creates a complete Diffusion-Limited Aggregation (DLA) simulation
using Blender's Geometry Nodes and prepares it for Cycles rendering.

Features:
- Phase 2: Basic DLA simulation with brownian motion and contact detection
- Phase 3: Flow field dynamics with spiral rotation, vertical bias, radial forces
- Phase 4: Particle management with stochastic deletion, duplication, and count limits
- Phase 5: Material & rendering with growth tip emission, ambient occlusion, GPU perf testing

Usage:
    1. Open Blender 4.2+
    2. Open the Scripting workspace
    3. Load and run this script
    4. Press Play in the timeline to run the simulation

GPU Performance Testing:
    After running main(), use these functions:
    - test_gpu_performance()     # Test render times at various sample counts
    - benchmark_simulation(50)   # Benchmark simulation speed

Based on techniques from the BlenderArtists DLA exploration thread.

Author: Claude (fractal-notebooks project)
Created: 2025-12-21
Updated: 2025-12-21 (Phase 5: Material & Rendering)
"""

import bpy
import math
from mathutils import Vector


def clear_scene():
    """Remove all objects, meshes, and materials from the scene."""
    # Delete all objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    # Clean up orphaned data
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)
    for node_group in bpy.data.node_groups:
        bpy.data.node_groups.remove(node_group)


def create_seed_geometry():
    """Create the seed geometry for DLA growth - a small sphere at origin."""
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.1,
        segments=16,
        ring_count=8,
        location=(0, 0, 0)
    )
    seed = bpy.context.active_object
    seed.name = "DLA_Seed"
    return seed


def create_dla_material(max_frames=250, tip_threshold=0.85, emission_strength=2.0,
                        ao_distance=0.1, ao_factor=0.5):
    """
    Create a material for the DLA point cloud with timepoint-based coloring,
    emission for growth tips, and ambient occlusion.

    Phase 5 Material Features:
    - Timepoint-based color ramp (deep blue -> cyan -> green -> yellow -> white)
    - Emission shader for growth tips (particles with timepoint > threshold glow)
    - Ambient occlusion for depth perception and shadowing

    Args:
        max_frames: Maximum simulation frames for normalizing timepoint
        tip_threshold: Normalized timepoint threshold for emission (0-1)
        emission_strength: Intensity of growth tip emission
        ao_distance: Ambient occlusion sampling distance
        ao_factor: Strength of ambient occlusion darkening
    """
    mat = bpy.data.materials.new(name="DLA_Material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear default nodes
    nodes.clear()

    # ========== OUTPUT ==========
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (1200, 0)

    # ========== TIMEPOINT PROCESSING ==========
    # Attribute node to read timepoint
    attr = nodes.new('ShaderNodeAttribute')
    attr.location = (-800, 0)
    attr.attribute_name = "timepoint"
    attr.attribute_type = 'INSTANCER'
    attr.label = "Timepoint Attribute"

    # Divide by max frames to normalize (0-1)
    divide = nodes.new('ShaderNodeMath')
    divide.location = (-600, 0)
    divide.operation = 'DIVIDE'
    divide.inputs[1].default_value = float(max_frames)
    divide.label = "Normalize Timepoint"

    # ========== BASE COLOR RAMP ==========
    color_ramp = nodes.new('ShaderNodeValToRGB')
    color_ramp.location = (-400, 0)
    color_ramp.color_ramp.interpolation = 'LINEAR'
    color_ramp.label = "Age Color Ramp"

    # Set up color ramp: deep blue -> cyan -> green -> yellow -> white
    ramp = color_ramp.color_ramp
    ramp.elements[0].position = 0.0
    ramp.elements[0].color = (0.04, 0.09, 0.16, 1.0)  # Deep blue #0a1728

    ramp.elements[1].position = 1.0
    ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)  # White

    # Add intermediate colors
    elem = ramp.elements.new(0.3)
    elem.color = (0.0, 0.83, 1.0, 1.0)  # Cyan #00d4ff

    elem = ramp.elements.new(0.6)
    elem.color = (0.0, 1.0, 0.53, 1.0)  # Green #00ff88

    elem = ramp.elements.new(0.9)
    elem.color = (1.0, 0.87, 0.0, 1.0)  # Yellow #ffdd00

    # ========== AMBIENT OCCLUSION ==========
    ao_node = nodes.new('ShaderNodeAmbientOcclusion')
    ao_node.location = (-400, -250)
    ao_node.samples = 16
    ao_node.inside = False
    ao_node.only_local = False
    ao_node.inputs['Distance'].default_value = ao_distance
    ao_node.label = "Ambient Occlusion"

    # Mix base color with AO darkening
    ao_mix = nodes.new('ShaderNodeMixRGB')
    ao_mix.location = (-150, 0)
    ao_mix.blend_type = 'MULTIPLY'
    ao_mix.inputs['Fac'].default_value = ao_factor
    ao_mix.label = "Apply AO Darkening"

    # AO shadow color (dark blue-gray)
    ao_shadow = nodes.new('ShaderNodeRGB')
    ao_shadow.location = (-400, -400)
    ao_shadow.outputs['Color'].default_value = (0.1, 0.1, 0.18, 1.0)
    ao_shadow.label = "AO Shadow Color"

    # Mix shader color based on AO
    ao_color_mix = nodes.new('ShaderNodeMixRGB')
    ao_color_mix.location = (-150, -250)
    ao_color_mix.blend_type = 'MIX'
    ao_color_mix.label = "AO Color Blend"

    # ========== GROWTH TIP EMISSION ==========
    # Compare timepoint to threshold - growth tips are recent particles
    tip_compare = nodes.new('ShaderNodeMath')
    tip_compare.location = (-400, 200)
    tip_compare.operation = 'GREATER_THAN'
    tip_compare.inputs[1].default_value = tip_threshold
    tip_compare.label = "Is Growth Tip?"

    # Smooth the tip transition
    tip_smooth = nodes.new('ShaderNodeMath')
    tip_smooth.location = (-200, 200)
    tip_smooth.operation = 'SMOOTH_MIN'
    tip_smooth.inputs[1].default_value = 0.0
    tip_smooth.inputs[2].default_value = 0.1  # Smoothing distance
    tip_smooth.label = "Smooth Tip Transition"

    # Calculate emission mask: how much above threshold (0 to ~0.15)
    tip_subtract = nodes.new('ShaderNodeMath')
    tip_subtract.location = (-400, 350)
    tip_subtract.operation = 'SUBTRACT'
    tip_subtract.inputs[1].default_value = tip_threshold
    tip_subtract.label = "Above Threshold"

    # Clamp negative values to 0
    tip_clamp = nodes.new('ShaderNodeClamp')
    tip_clamp.location = (-200, 350)
    tip_clamp.inputs['Min'].default_value = 0.0
    tip_clamp.inputs['Max'].default_value = 1.0
    tip_clamp.label = "Clamp Emission"

    # Scale emission factor (map 0-0.15 to 0-1 for stronger effect)
    tip_scale = nodes.new('ShaderNodeMath')
    tip_scale.location = (0, 350)
    tip_scale.operation = 'MULTIPLY'
    tip_scale.inputs[1].default_value = 6.67  # 1.0 / (1.0 - tip_threshold)
    tip_scale.label = "Scale Emission Factor"

    # Emission color ramp (tip glow: yellow -> orange -> white)
    emission_ramp = nodes.new('ShaderNodeValToRGB')
    emission_ramp.location = (0, 200)
    emission_ramp.color_ramp.interpolation = 'LINEAR'
    emission_ramp.label = "Emission Color"

    em_ramp = emission_ramp.color_ramp
    em_ramp.elements[0].position = 0.0
    em_ramp.elements[0].color = (1.0, 0.7, 0.0, 1.0)  # Yellow-orange

    em_ramp.elements[1].position = 1.0
    em_ramp.elements[1].color = (1.0, 1.0, 0.9, 1.0)  # Near-white

    # Add hot orange at midpoint
    em_elem = em_ramp.elements.new(0.5)
    em_elem.color = (1.0, 0.5, 0.1, 1.0)  # Hot orange

    # Emission shader
    emission = nodes.new('ShaderNodeEmission')
    emission.location = (200, 200)
    emission.inputs['Strength'].default_value = emission_strength
    emission.label = "Tip Emission"

    # ========== BASE SHADERS ==========
    # Principled BSDF for non-emitting parts
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (200, 0)
    principled.inputs['Roughness'].default_value = 0.5
    principled.inputs['Metallic'].default_value = 0.0
    principled.inputs['IOR'].default_value = 1.45
    principled.label = "Base BSDF"

    # ========== MIX SHADERS ==========
    # Mix between base BSDF and emission based on tip factor
    mix_shader = nodes.new('ShaderNodeMixShader')
    mix_shader.location = (600, 0)
    mix_shader.label = "Base/Emission Mix"

    # Add shader to combine (additive blending for emission)
    add_shader = nodes.new('ShaderNodeAddShader')
    add_shader.location = (800, 100)
    add_shader.label = "Add Emission Glow"

    # Secondary principled for additive base
    principled2 = nodes.new('ShaderNodeBsdfPrincipled')
    principled2.location = (600, -200)
    principled2.inputs['Roughness'].default_value = 0.5
    principled2.label = "Additive Base"

    # Final mix for emission intensity control
    final_mix = nodes.new('ShaderNodeMixShader')
    final_mix.location = (1000, 0)
    final_mix.label = "Final Shader"

    # ========== LINKING ==========
    # Timepoint processing
    links.new(attr.outputs['Fac'], divide.inputs[0])
    links.new(divide.outputs['Value'], color_ramp.inputs['Fac'])

    # Ambient Occlusion
    links.new(color_ramp.outputs['Color'], ao_node.inputs['Color'])
    links.new(color_ramp.outputs['Color'], ao_color_mix.inputs['Color1'])
    links.new(ao_shadow.outputs['Color'], ao_color_mix.inputs['Color2'])
    links.new(ao_node.outputs['AO'], ao_color_mix.inputs['Fac'])

    # Growth tip emission calculation
    links.new(divide.outputs['Value'], tip_compare.inputs[0])
    links.new(divide.outputs['Value'], tip_subtract.inputs[0])
    links.new(tip_subtract.outputs['Value'], tip_clamp.inputs['Value'])
    links.new(tip_clamp.outputs['Result'], tip_scale.inputs[0])
    links.new(tip_clamp.outputs['Result'], emission_ramp.inputs['Fac'])

    # Emission shader
    links.new(emission_ramp.outputs['Color'], emission.inputs['Color'])

    # Base BSDF with AO-modified color
    links.new(ao_color_mix.outputs['Color'], principled.inputs['Base Color'])
    links.new(ao_color_mix.outputs['Color'], principled2.inputs['Base Color'])

    # Emission color to principled emission input (subtle base emission)
    links.new(emission_ramp.outputs['Color'], principled.inputs['Emission Color'])
    links.new(tip_scale.outputs['Value'], principled.inputs['Emission Strength'])

    # Mix shaders: base BSDF mixed with emission based on tip factor
    links.new(tip_scale.outputs['Value'], mix_shader.inputs['Fac'])
    links.new(principled.outputs['BSDF'], mix_shader.inputs[1])
    links.new(emission.outputs['Emission'], mix_shader.inputs[2])

    # Output
    links.new(mix_shader.outputs['Shader'], output.inputs['Surface'])

    return mat


def create_geometry_nodes_modifier(obj):
    """
    Create and configure the Geometry Nodes modifier for DLA simulation.

    Includes:
    - Phase 2: Basic DLA with brownian motion and contact detection
    - Phase 3: Flow field enhancement with rotation, vertical bias, radial force
    - Phase 4: Particle management with deletion, duplication, and limits
    """
    # Add geometry nodes modifier
    modifier = obj.modifiers.new(name="DLA_Simulation", type='NODES')

    # Create new node group
    node_group = bpy.data.node_groups.new(name="DLA_NodeGroup", type='GeometryNodeTree')
    modifier.node_group = node_group

    nodes = node_group.nodes
    links = node_group.links

    # ========== INTERFACE SETUP ==========
    # Create interface (inputs/outputs)
    node_group.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    node_group.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

    # Basic DLA parameters (Phase 2)
    node_group.interface.new_socket(name="Initial Particles", in_out='INPUT', socket_type='NodeSocketInt')
    node_group.interface.new_socket(name="Step Size", in_out='INPUT', socket_type='NodeSocketFloat')
    node_group.interface.new_socket(name="Contact Radius", in_out='INPUT', socket_type='NodeSocketFloat')
    node_group.interface.new_socket(name="Noise Scale", in_out='INPUT', socket_type='NodeSocketFloat')
    node_group.interface.new_socket(name="Seed", in_out='INPUT', socket_type='NodeSocketInt')

    # Flow Field parameters (Phase 3)
    node_group.interface.new_socket(name="Rotation Rate", in_out='INPUT', socket_type='NodeSocketFloat')
    node_group.interface.new_socket(name="Vertical Bias", in_out='INPUT', socket_type='NodeSocketFloat')
    node_group.interface.new_socket(name="Radial Force", in_out='INPUT', socket_type='NodeSocketFloat')
    node_group.interface.new_socket(name="Flow Noise Scale", in_out='INPUT', socket_type='NodeSocketFloat')
    node_group.interface.new_socket(name="Flow Noise Strength", in_out='INPUT', socket_type='NodeSocketFloat')
    node_group.interface.new_socket(name="Spawn Radius", in_out='INPUT', socket_type='NodeSocketFloat')
    node_group.interface.new_socket(name="Spawn Rate", in_out='INPUT', socket_type='NodeSocketInt')

    # Particle Management parameters (Phase 4)
    node_group.interface.new_socket(name="Deletion Probability", in_out='INPUT', socket_type='NodeSocketFloat')
    node_group.interface.new_socket(name="Duplication Probability", in_out='INPUT', socket_type='NodeSocketFloat')
    node_group.interface.new_socket(name="Max Active Particles", in_out='INPUT', socket_type='NodeSocketInt')
    node_group.interface.new_socket(name="Boundary Radius", in_out='INPUT', socket_type='NodeSocketFloat')

    # Set default values - indexed by socket order
    # Socket_2 = Initial Particles, Socket_3 = Step Size, etc.
    modifier["Socket_2"] = 5000       # Initial Particles
    modifier["Socket_3"] = 0.02       # Step Size
    modifier["Socket_4"] = 0.03       # Contact Radius
    modifier["Socket_5"] = 2.0        # Noise Scale
    modifier["Socket_6"] = 42         # Seed
    modifier["Socket_7"] = 0.05       # Rotation Rate (radians per frame)
    modifier["Socket_8"] = 0.01       # Vertical Bias
    modifier["Socket_9"] = 0.005      # Radial Force (positive = expand, negative = contract)
    modifier["Socket_10"] = 0.5       # Flow Noise Scale (large-scale)
    modifier["Socket_11"] = 0.03      # Flow Noise Strength
    modifier["Socket_12"] = 2.0       # Spawn Radius
    modifier["Socket_13"] = 100       # Spawn Rate
    # Phase 4 parameters
    modifier["Socket_14"] = 0.01      # Deletion Probability (1% per frame)
    modifier["Socket_15"] = 0.005     # Duplication Probability (0.5% per frame)
    modifier["Socket_16"] = 50000     # Max Active Particles
    modifier["Socket_17"] = 5.0       # Boundary Radius (delete particles beyond this)

    # Create nodes
    group_input = nodes.new('NodeGroupInput')
    group_input.location = (-2200, 0)

    group_output = nodes.new('NodeGroupOutput')
    group_output.location = (2000, 0)

    # ========== INITIALIZATION SECTION ==========

    # Distribute points on the seed mesh
    distribute = nodes.new('GeometryNodeDistributePointsOnFaces')
    distribute.location = (-1800, 100)
    distribute.distribute_method = 'RANDOM'

    # Merge by distance to create initial structure
    merge_init = nodes.new('GeometryNodeMergeByDistance')
    merge_init.location = (-1600, 100)
    merge_init.inputs['Distance'].default_value = 0.01

    # Capture initial attributes
    # Random color attribute
    random_val = nodes.new('FunctionNodeRandomValue')
    random_val.location = (-1800, -150)
    random_val.data_type = 'FLOAT'

    # Store attribute: color
    store_color = nodes.new('GeometryNodeStoreNamedAttribute')
    store_color.location = (-1400, 100)
    store_color.data_type = 'FLOAT'
    store_color.domain = 'POINT'
    store_color.inputs['Name'].default_value = "color_seed"

    # Frame counter for timepoint
    scene_time = nodes.new('GeometryNodeInputSceneTime')
    scene_time.location = (-1800, -300)

    # Store attribute: timepoint
    store_timepoint = nodes.new('GeometryNodeStoreNamedAttribute')
    store_timepoint.location = (-1200, 100)
    store_timepoint.data_type = 'FLOAT'
    store_timepoint.domain = 'POINT'
    store_timepoint.inputs['Name'].default_value = "timepoint"

    # Store attribute: active flag (0 = fixed structure, 1 = moving particle)
    store_active = nodes.new('GeometryNodeStoreNamedAttribute')
    store_active.location = (-1000, 100)
    store_active.data_type = 'BOOLEAN'
    store_active.domain = 'POINT'
    store_active.inputs['Name'].default_value = "active"

    # Create boolean false for initial particles (they start as structure)
    bool_false = nodes.new('FunctionNodeInputBool')
    bool_false.location = (-1200, -100)
    bool_false.boolean = False  # Initial seed is fixed structure

    # ========== SIMULATION ZONE ==========

    # Simulation input/output
    sim_input = nodes.new('GeometryNodeSimulationInput')
    sim_input.location = (-800, 0)

    sim_output = nodes.new('GeometryNodeSimulationOutput')
    sim_output.location = (1800, 0)

    # Link simulation zones (Blender 4.0+: use pair_with_output on input node)
    sim_input.pair_with_output(sim_output)

    # ========== INSIDE SIMULATION ZONE ==========

    # Separate active from fixed particles
    named_attr_active = nodes.new('GeometryNodeInputNamedAttribute')
    named_attr_active.location = (-600, -200)
    named_attr_active.data_type = 'BOOLEAN'
    named_attr_active.inputs['Name'].default_value = "active"

    separate = nodes.new('GeometryNodeSeparateGeometry')
    separate.location = (-400, 0)
    separate.domain = 'POINT'

    # ========== PHASE 4: PARTICLE COUNT MONITORING ==========
    # Count active particles and compare to max

    # Domain Size node to count active particles
    domain_size_active = nodes.new('GeometryNodeAttributeDomainSize')
    domain_size_active.location = (-200, 400)
    domain_size_active.component = 'POINTCLOUD'

    # Compare count to max
    compare_count = nodes.new('FunctionNodeCompare')
    compare_count.location = (0, 400)
    compare_count.data_type = 'INT'
    compare_count.operation = 'LESS_THAN'
    compare_count.label = "Below Max?"

    # ========== FLOW FIELD COMPUTATION (Phase 3) ==========
    # Build the combined flow field displacement vector

    # Get position for all calculations
    position = nodes.new('GeometryNodeInputPosition')
    position.location = (-200, -500)

    # --- Component 1: Brownian Motion (Noise Texture) ---
    noise_brownian = nodes.new('ShaderNodeTexNoise')
    noise_brownian.location = (0, -400)
    noise_brownian.noise_dimensions = '3D'
    noise_brownian.label = "Brownian Noise"

    # Scale brownian noise by step size
    brownian_scale = nodes.new('ShaderNodeVectorMath')
    brownian_scale.location = (200, -400)
    brownian_scale.operation = 'SCALE'
    brownian_scale.label = "Scale Brownian"

    # --- Component 2: Large-Scale Flow Noise (Phase 3) ---
    noise_flow = nodes.new('ShaderNodeTexNoise')
    noise_flow.location = (0, -600)
    noise_flow.noise_dimensions = '3D'
    noise_flow.label = "Flow Field Noise"

    # Subtract 0.5 to center noise around 0 (-0.5 to 0.5)
    flow_center = nodes.new('ShaderNodeVectorMath')
    flow_center.location = (200, -600)
    flow_center.operation = 'SUBTRACT'
    flow_center.inputs[1].default_value = (0.5, 0.5, 0.5)
    flow_center.label = "Center Flow"

    # Scale flow noise by strength
    flow_scale = nodes.new('ShaderNodeVectorMath')
    flow_scale.location = (400, -600)
    flow_scale.operation = 'SCALE'
    flow_scale.label = "Scale Flow"

    # --- Component 3: Z-Axis Rotation (Phase 3) ---
    # Vector Rotate around Z axis
    vector_rotate = nodes.new('ShaderNodeVectorRotate')
    vector_rotate.location = (0, -800)
    vector_rotate.rotation_type = 'AXIS_ANGLE'
    vector_rotate.label = "Spiral Rotation"

    # Z axis vector
    z_axis = nodes.new('FunctionNodeInputVector')
    z_axis.location = (-200, -900)
    z_axis.vector = (0, 0, 1)

    # Subtract original position to get rotation displacement
    rotation_diff = nodes.new('ShaderNodeVectorMath')
    rotation_diff.location = (200, -800)
    rotation_diff.operation = 'SUBTRACT'
    rotation_diff.label = "Rotation Displacement"

    # --- Component 4: Vertical Bias (Phase 3) ---
    vertical_bias_vec = nodes.new('ShaderNodeCombineXYZ')
    vertical_bias_vec.location = (0, -1000)
    vertical_bias_vec.inputs['X'].default_value = 0.0
    vertical_bias_vec.inputs['Y'].default_value = 0.0
    vertical_bias_vec.label = "Vertical Bias"

    # --- Component 5: Radial Force (Phase 3) ---
    # Normalize position to get direction from center
    radial_normalize = nodes.new('ShaderNodeVectorMath')
    radial_normalize.location = (0, -1200)
    radial_normalize.operation = 'NORMALIZE'
    radial_normalize.label = "Radial Direction"

    # Scale by radial force parameter
    radial_scale = nodes.new('ShaderNodeVectorMath')
    radial_scale.location = (200, -1200)
    radial_scale.operation = 'SCALE'
    radial_scale.label = "Radial Force"

    # ========== COMBINE ALL FLOW FIELD COMPONENTS ==========

    # Add brownian + flow noise
    add_flow1 = nodes.new('ShaderNodeVectorMath')
    add_flow1.location = (600, -450)
    add_flow1.operation = 'ADD'
    add_flow1.label = "Brownian + Flow"

    # Add rotation displacement
    add_flow2 = nodes.new('ShaderNodeVectorMath')
    add_flow2.location = (800, -500)
    add_flow2.operation = 'ADD'
    add_flow2.label = "+ Rotation"

    # Add vertical bias
    add_flow3 = nodes.new('ShaderNodeVectorMath')
    add_flow3.location = (1000, -550)
    add_flow3.operation = 'ADD'
    add_flow3.label = "+ Vertical"

    # Add radial force (final combined displacement)
    add_flow_final = nodes.new('ShaderNodeVectorMath')
    add_flow_final.location = (1200, -600)
    add_flow_final.operation = 'ADD'
    add_flow_final.label = "Final Flow Field"

    # ========== APPLY DISPLACEMENT ==========

    # Add displacement to current position
    new_position = nodes.new('ShaderNodeVectorMath')
    new_position.location = (600, -150)
    new_position.operation = 'ADD'
    new_position.label = "New Position"

    # Set new position
    set_position = nodes.new('GeometryNodeSetPosition')
    set_position.location = (800, 0)

    # ========== PHASE 4: STOCHASTIC DELETION ==========
    # Delete some active particles randomly to prevent memory overflow

    # Random value for deletion decision
    random_delete = nodes.new('FunctionNodeRandomValue')
    random_delete.location = (900, -200)
    random_delete.data_type = 'FLOAT'
    random_delete.inputs['Min'].default_value = 0.0
    random_delete.inputs['Max'].default_value = 1.0

    # Compare random value to deletion probability
    compare_delete = nodes.new('FunctionNodeCompare')
    compare_delete.location = (1100, -200)
    compare_delete.data_type = 'FLOAT'
    compare_delete.operation = 'GREATER_THAN'
    compare_delete.label = "Keep Particle?"

    # ========== PHASE 4: BOUNDARY DELETION ==========
    # Delete particles that go too far from center

    # Get position for boundary check
    position_boundary = nodes.new('GeometryNodeInputPosition')
    position_boundary.location = (900, -350)

    # Calculate distance from origin (length of position vector)
    distance_from_origin = nodes.new('ShaderNodeVectorMath')
    distance_from_origin.location = (1100, -350)
    distance_from_origin.operation = 'LENGTH'
    distance_from_origin.label = "Distance from Center"

    # Compare distance to boundary radius
    compare_boundary = nodes.new('FunctionNodeCompare')
    compare_boundary.location = (1300, -350)
    compare_boundary.data_type = 'FLOAT'
    compare_boundary.operation = 'LESS_THAN'
    compare_boundary.label = "Within Boundary?"

    # Combine deletion conditions: keep if (random > delete_prob) AND (within boundary)
    and_keep = nodes.new('FunctionNodeBooleanMath')
    and_keep.location = (1400, -250)
    and_keep.operation = 'AND'
    and_keep.label = "Keep Conditions"

    # Delete geometry based on combined selection
    delete_particles = nodes.new('GeometryNodeDeleteGeometry')
    delete_particles.location = (1000, 0)
    delete_particles.domain = 'POINT'
    delete_particles.mode = 'ALL'

    # NOT gate to invert selection (delete where keep=False)
    not_keep = nodes.new('FunctionNodeBooleanMath')
    not_keep.location = (1500, -250)
    not_keep.operation = 'NOT'
    not_keep.label = "Delete Selection"

    # ========== PHASE 4: PARTICLE DUPLICATION ==========
    # Duplicate some particles to create denser growth at branch tips

    # Random value for duplication decision
    random_duplicate = nodes.new('FunctionNodeRandomValue')
    random_duplicate.location = (1100, -500)
    random_duplicate.data_type = 'FLOAT'
    random_duplicate.inputs['Min'].default_value = 0.0
    random_duplicate.inputs['Max'].default_value = 1.0

    # Compare random value to duplication probability
    compare_duplicate = nodes.new('FunctionNodeCompare')
    compare_duplicate.location = (1300, -500)
    compare_duplicate.data_type = 'FLOAT'
    compare_duplicate.operation = 'LESS_THAN'
    compare_duplicate.label = "Duplicate?"

    # Duplicate Elements node
    duplicate = nodes.new('GeometryNodeDuplicateElements')
    duplicate.location = (1200, 0)
    duplicate.domain = 'POINT'

    # Convert boolean to integer for amount (1 if duplicate, 0 if not)
    bool_to_int = nodes.new('FunctionNodeBooleanMath')
    bool_to_int.location = (1450, -500)
    bool_to_int.operation = 'AND'  # Will use this as passthrough

    # Switch for duplication amount: 0 or 1
    switch_amount = nodes.new('GeometryNodeSwitch')
    switch_amount.location = (1500, -450)
    switch_amount.input_type = 'INT'
    switch_amount.inputs['False'].default_value = 0
    switch_amount.inputs['True'].default_value = 1

    # ========== CONTACT DETECTION ==========

    # Sample nearest from fixed structure
    sample_nearest = nodes.new('GeometryNodeSampleNearest')
    sample_nearest.location = (400, 200)
    sample_nearest.domain = 'POINT'

    # Evaluate at nearest
    sample_index = nodes.new('GeometryNodeSampleIndex')
    sample_index.location = (550, 200)
    sample_index.data_type = 'FLOAT_VECTOR'
    sample_index.domain = 'POINT'

    # Position for sampling
    position2 = nodes.new('GeometryNodeInputPosition')
    position2.location = (350, 350)

    # Distance calculation
    distance = nodes.new('ShaderNodeVectorMath')
    distance.location = (700, 200)
    distance.operation = 'DISTANCE'

    # Compare distance
    compare = nodes.new('FunctionNodeCompare')
    compare.location = (850, 200)
    compare.data_type = 'FLOAT'
    compare.operation = 'LESS_THAN'

    # Update active attribute based on contact
    store_active_update = nodes.new('GeometryNodeStoreNamedAttribute')
    store_active_update.location = (1400, 0)
    store_active_update.data_type = 'BOOLEAN'
    store_active_update.domain = 'POINT'
    store_active_update.inputs['Name'].default_value = "active"

    # Not gate for inverting (if contact, set active=False)
    not_gate = nodes.new('FunctionNodeBooleanMath')
    not_gate.location = (850, 100)
    not_gate.operation = 'NOT'

    # Get current active attribute
    named_attr_active2 = nodes.new('GeometryNodeInputNamedAttribute')
    named_attr_active2.location = (700, 100)
    named_attr_active2.data_type = 'BOOLEAN'
    named_attr_active2.inputs['Name'].default_value = "active"

    # AND gate: active AND NOT(contact) = still active
    and_gate = nodes.new('FunctionNodeBooleanMath')
    and_gate.location = (1000, 100)
    and_gate.operation = 'AND'

    # ========== SPAWN NEW PARTICLES ==========

    # Points node for spawning new particles
    spawn_points = nodes.new('GeometryNodePoints')
    spawn_points.location = (0, -1400)

    # PHASE 4: Conditional spawn based on particle count
    # Switch spawn count: 0 if at max, spawn_rate if below
    switch_spawn = nodes.new('GeometryNodeSwitch')
    switch_spawn.location = (200, 400)
    switch_spawn.input_type = 'INT'
    switch_spawn.inputs['False'].default_value = 0  # Don't spawn if at max

    # Set random position for new particles (on a sphere shell)
    random_pos = nodes.new('FunctionNodeRandomValue')
    random_pos.location = (200, -1450)
    random_pos.data_type = 'FLOAT_VECTOR'
    random_pos.inputs['Min'].default_value = (-1, -1, -1)
    random_pos.inputs['Max'].default_value = (1, 1, 1)

    # Normalize to sphere
    normalize = nodes.new('ShaderNodeVectorMath')
    normalize.location = (400, -1450)
    normalize.operation = 'NORMALIZE'

    # Scale to spawn radius
    scale_spawn = nodes.new('ShaderNodeVectorMath')
    scale_spawn.location = (600, -1450)
    scale_spawn.operation = 'SCALE'

    # Set position for spawned particles
    set_spawn_pos = nodes.new('GeometryNodeSetPosition')
    set_spawn_pos.location = (800, -1400)

    # Store active=True for spawned particles
    store_spawn_active = nodes.new('GeometryNodeStoreNamedAttribute')
    store_spawn_active.location = (1000, -1400)
    store_spawn_active.data_type = 'BOOLEAN'
    store_spawn_active.domain = 'POINT'
    store_spawn_active.inputs['Name'].default_value = "active"

    bool_true = nodes.new('FunctionNodeInputBool')
    bool_true.location = (850, -1550)
    bool_true.boolean = True

    # Store timepoint for spawned
    store_spawn_time = nodes.new('GeometryNodeStoreNamedAttribute')
    store_spawn_time.location = (1200, -1400)
    store_spawn_time.data_type = 'FLOAT'
    store_spawn_time.domain = 'POINT'
    store_spawn_time.inputs['Name'].default_value = "timepoint"

    # ========== JOIN GEOMETRY ==========

    # Join all geometry: fixed + updated active + newly spawned
    join = nodes.new('GeometryNodeJoinGeometry')
    join.location = (1600, 0)

    # ========== LINKING SECTION ==========

    # --- Initialization Links ---
    # Input -> Distribute
    links.new(group_input.outputs['Geometry'], distribute.inputs['Mesh'])
    links.new(group_input.outputs['Initial Particles'], distribute.inputs['Density'])
    links.new(group_input.outputs['Seed'], distribute.inputs['Seed'])

    # Distribute -> Merge -> Store attributes
    links.new(distribute.outputs['Points'], merge_init.inputs['Geometry'])
    links.new(merge_init.outputs['Geometry'], store_color.inputs['Geometry'])
    links.new(random_val.outputs['Value'], store_color.inputs['Value'])

    links.new(store_color.outputs['Geometry'], store_timepoint.inputs['Geometry'])
    links.new(scene_time.outputs['Frame'], store_timepoint.inputs['Value'])

    links.new(store_timepoint.outputs['Geometry'], store_active.inputs['Geometry'])
    links.new(bool_false.outputs['Boolean'], store_active.inputs['Value'])

    # Initial geometry -> Simulation
    links.new(store_active.outputs['Geometry'], sim_input.inputs['Geometry'])

    # --- Simulation Zone Internal ---
    # Separate active from fixed
    links.new(sim_input.outputs['Geometry'], separate.inputs['Geometry'])
    links.new(named_attr_active.outputs['Attribute'], separate.inputs['Selection'])

    # --- Phase 4: Particle Count Monitoring ---
    links.new(separate.outputs['Selection'], domain_size_active.inputs['Geometry'])
    links.new(domain_size_active.outputs['Point Count'], compare_count.inputs['A'])
    links.new(group_input.outputs['Max Active Particles'], compare_count.inputs['B'])

    # Conditional spawn based on count
    links.new(compare_count.outputs['Result'], switch_spawn.inputs['Switch'])
    links.new(group_input.outputs['Spawn Rate'], switch_spawn.inputs['True'])
    links.new(switch_spawn.outputs['Output'], spawn_points.inputs['Count'])

    # --- Flow Field Component Links (Phase 3) ---

    # Component 1: Brownian Motion
    links.new(position.outputs['Position'], noise_brownian.inputs['Vector'])
    links.new(group_input.outputs['Noise Scale'], noise_brownian.inputs['Scale'])
    links.new(noise_brownian.outputs['Color'], brownian_scale.inputs[0])
    links.new(group_input.outputs['Step Size'], brownian_scale.inputs['Scale'])

    # Component 2: Large-Scale Flow Noise
    links.new(position.outputs['Position'], noise_flow.inputs['Vector'])
    links.new(group_input.outputs['Flow Noise Scale'], noise_flow.inputs['Scale'])
    links.new(noise_flow.outputs['Color'], flow_center.inputs[0])
    links.new(flow_center.outputs['Vector'], flow_scale.inputs[0])
    links.new(group_input.outputs['Flow Noise Strength'], flow_scale.inputs['Scale'])

    # Component 3: Z-Axis Rotation
    links.new(position.outputs['Position'], vector_rotate.inputs['Vector'])
    links.new(z_axis.outputs['Vector'], vector_rotate.inputs['Axis'])
    links.new(group_input.outputs['Rotation Rate'], vector_rotate.inputs['Angle'])
    links.new(vector_rotate.outputs['Vector'], rotation_diff.inputs[0])
    links.new(position.outputs['Position'], rotation_diff.inputs[1])

    # Component 4: Vertical Bias
    links.new(group_input.outputs['Vertical Bias'], vertical_bias_vec.inputs['Z'])

    # Component 5: Radial Force
    links.new(position.outputs['Position'], radial_normalize.inputs[0])
    links.new(radial_normalize.outputs['Vector'], radial_scale.inputs[0])
    links.new(group_input.outputs['Radial Force'], radial_scale.inputs['Scale'])

    # Combine all flow field components
    links.new(brownian_scale.outputs['Vector'], add_flow1.inputs[0])
    links.new(flow_scale.outputs['Vector'], add_flow1.inputs[1])
    links.new(add_flow1.outputs['Vector'], add_flow2.inputs[0])
    links.new(rotation_diff.outputs['Vector'], add_flow2.inputs[1])
    links.new(add_flow2.outputs['Vector'], add_flow3.inputs[0])
    links.new(vertical_bias_vec.outputs['Vector'], add_flow3.inputs[1])
    links.new(add_flow3.outputs['Vector'], add_flow_final.inputs[0])
    links.new(radial_scale.outputs['Vector'], add_flow_final.inputs[1])

    # Apply combined displacement
    links.new(separate.outputs['Selection'], set_position.inputs['Geometry'])
    links.new(position.outputs['Position'], new_position.inputs[0])
    links.new(add_flow_final.outputs['Vector'], new_position.inputs[1])
    links.new(new_position.outputs['Vector'], set_position.inputs['Position'])

    # --- Phase 4: Stochastic Deletion Links ---
    links.new(random_delete.outputs['Value'], compare_delete.inputs['A'])
    links.new(group_input.outputs['Deletion Probability'], compare_delete.inputs['B'])

    # Boundary deletion
    links.new(position_boundary.outputs['Position'], distance_from_origin.inputs[0])
    links.new(distance_from_origin.outputs['Value'], compare_boundary.inputs['A'])
    links.new(group_input.outputs['Boundary Radius'], compare_boundary.inputs['B'])

    # Combine keep conditions
    links.new(compare_delete.outputs['Result'], and_keep.inputs[0])
    links.new(compare_boundary.outputs['Result'], and_keep.inputs[1])

    # Invert for delete selection
    links.new(and_keep.outputs['Boolean'], not_keep.inputs[0])

    # Apply deletion to positioned geometry
    links.new(set_position.outputs['Geometry'], delete_particles.inputs['Geometry'])
    links.new(not_keep.outputs['Boolean'], delete_particles.inputs['Selection'])

    # --- Phase 4: Duplication Links ---
    links.new(random_duplicate.outputs['Value'], compare_duplicate.inputs['A'])
    links.new(group_input.outputs['Duplication Probability'], compare_duplicate.inputs['B'])
    links.new(compare_duplicate.outputs['Result'], switch_amount.inputs['Switch'])
    links.new(delete_particles.outputs['Geometry'], duplicate.inputs['Geometry'])
    links.new(switch_amount.outputs['Output'], duplicate.inputs['Amount'])

    # --- Contact Detection Links ---
    links.new(separate.outputs['Inverted'], sample_nearest.inputs['Geometry'])
    links.new(duplicate.outputs['Geometry'], sample_nearest.inputs['Sample Position'])

    links.new(separate.outputs['Inverted'], sample_index.inputs['Geometry'])
    links.new(sample_nearest.outputs['Index'], sample_index.inputs['Index'])
    links.new(position2.outputs['Position'], sample_index.inputs['Value'])

    links.new(duplicate.outputs['Geometry'], distance.inputs[0])
    links.new(sample_index.outputs['Value'], distance.inputs[1])

    links.new(distance.outputs['Value'], compare.inputs['A'])
    links.new(group_input.outputs['Contact Radius'], compare.inputs['B'])

    # Update active flag
    links.new(compare.outputs['Result'], not_gate.inputs[0])
    links.new(named_attr_active2.outputs['Attribute'], and_gate.inputs[0])
    links.new(not_gate.outputs['Boolean'], and_gate.inputs[1])

    links.new(duplicate.outputs['Geometry'], store_active_update.inputs['Geometry'])
    links.new(and_gate.outputs['Boolean'], store_active_update.inputs['Value'])

    # --- Spawn Links ---
    links.new(random_pos.outputs['Value'], normalize.inputs[0])
    links.new(normalize.outputs['Vector'], scale_spawn.inputs[0])
    links.new(group_input.outputs['Spawn Radius'], scale_spawn.inputs['Scale'])
    links.new(spawn_points.outputs['Geometry'], set_spawn_pos.inputs['Geometry'])
    links.new(scale_spawn.outputs['Vector'], set_spawn_pos.inputs['Position'])
    links.new(set_spawn_pos.outputs['Geometry'], store_spawn_active.inputs['Geometry'])
    links.new(bool_true.outputs['Boolean'], store_spawn_active.inputs['Value'])
    links.new(store_spawn_active.outputs['Geometry'], store_spawn_time.inputs['Geometry'])
    links.new(scene_time.outputs['Frame'], store_spawn_time.inputs['Value'])

    # --- Join and Output ---
    links.new(separate.outputs['Inverted'], join.inputs['Geometry'])  # Fixed structure
    links.new(store_active_update.outputs['Geometry'], join.inputs['Geometry'])  # Updated active
    links.new(store_spawn_time.outputs['Geometry'], join.inputs['Geometry'])  # New spawned

    # Simulation output
    links.new(join.outputs['Geometry'], sim_output.inputs['Geometry'])

    # Final output
    links.new(sim_output.outputs['Geometry'], group_output.inputs['Geometry'])

    return modifier


def create_flow_field_presets():
    """
    Create preset configurations for different DLA growth patterns.

    Returns a dictionary of presets that can be applied to the modifier.
    """
    presets = {
        'classic': {
            'description': 'Classic DLA with pure brownian motion',
            'Step Size': 0.02,
            'Noise Scale': 2.0,
            'Rotation Rate': 0.0,
            'Vertical Bias': 0.0,
            'Radial Force': 0.0,
            'Flow Noise Scale': 0.5,
            'Flow Noise Strength': 0.0,
            'Deletion Probability': 0.005,
            'Duplication Probability': 0.0,
        },
        'spiral': {
            'description': 'Spiral galaxy-like growth pattern',
            'Step Size': 0.015,
            'Noise Scale': 3.0,
            'Rotation Rate': 0.1,
            'Vertical Bias': 0.005,
            'Radial Force': 0.003,
            'Flow Noise Scale': 0.8,
            'Flow Noise Strength': 0.02,
            'Deletion Probability': 0.01,
            'Duplication Probability': 0.005,
        },
        'tree': {
            'description': 'Upward-growing tree-like structure',
            'Step Size': 0.02,
            'Noise Scale': 2.5,
            'Rotation Rate': 0.02,
            'Vertical Bias': 0.025,
            'Radial Force': -0.005,
            'Flow Noise Scale': 1.0,
            'Flow Noise Strength': 0.015,
            'Deletion Probability': 0.008,
            'Duplication Probability': 0.01,  # More duplication for branching
        },
        'coral': {
            'description': 'Coral-like branching with radial expansion',
            'Step Size': 0.018,
            'Noise Scale': 4.0,
            'Rotation Rate': 0.0,
            'Vertical Bias': 0.01,
            'Radial Force': 0.008,
            'Flow Noise Scale': 0.6,
            'Flow Noise Strength': 0.025,
            'Deletion Probability': 0.005,
            'Duplication Probability': 0.008,
        },
        'vortex': {
            'description': 'Strong spiraling vortex pattern',
            'Step Size': 0.01,
            'Noise Scale': 1.5,
            'Rotation Rate': 0.2,
            'Vertical Bias': 0.0,
            'Radial Force': -0.01,
            'Flow Noise Scale': 0.3,
            'Flow Noise Strength': 0.01,
            'Deletion Probability': 0.015,
            'Duplication Probability': 0.002,
        },
        'turbulent': {
            'description': 'Chaotic turbulent flow field',
            'Step Size': 0.025,
            'Noise Scale': 5.0,
            'Rotation Rate': 0.05,
            'Vertical Bias': 0.0,
            'Radial Force': 0.0,
            'Flow Noise Scale': 2.0,
            'Flow Noise Strength': 0.05,
            'Deletion Probability': 0.02,
            'Duplication Probability': 0.01,
        },
        'dense': {
            'description': 'Dense growth with high duplication',
            'Step Size': 0.015,
            'Noise Scale': 2.0,
            'Rotation Rate': 0.0,
            'Vertical Bias': 0.0,
            'Radial Force': 0.0,
            'Flow Noise Scale': 0.5,
            'Flow Noise Strength': 0.01,
            'Deletion Probability': 0.002,
            'Duplication Probability': 0.02,  # High duplication
        },
        'sparse': {
            'description': 'Sparse branching with high deletion',
            'Step Size': 0.03,
            'Noise Scale': 3.0,
            'Rotation Rate': 0.0,
            'Vertical Bias': 0.0,
            'Radial Force': 0.0,
            'Flow Noise Scale': 1.0,
            'Flow Noise Strength': 0.02,
            'Deletion Probability': 0.03,  # High deletion
            'Duplication Probability': 0.0,
        },
    }
    return presets


def apply_preset(obj, preset_name):
    """
    Apply a flow field preset to the DLA object.

    Args:
        obj: The DLA object with geometry nodes modifier
        preset_name: Name of the preset to apply
    """
    presets = create_flow_field_presets()

    if preset_name not in presets:
        print(f"Unknown preset: {preset_name}")
        print(f"Available presets: {list(presets.keys())}")
        return False

    preset = presets[preset_name]

    # Find the modifier
    modifier = None
    for mod in obj.modifiers:
        if mod.type == 'NODES' and mod.node_group and 'DLA' in mod.node_group.name:
            modifier = mod
            break

    if not modifier:
        print("No DLA geometry nodes modifier found")
        return False

    # Socket mapping (based on interface order)
    socket_map = {
        'Step Size': 'Socket_3',
        'Noise Scale': 'Socket_5',
        'Rotation Rate': 'Socket_7',
        'Vertical Bias': 'Socket_8',
        'Radial Force': 'Socket_9',
        'Flow Noise Scale': 'Socket_10',
        'Flow Noise Strength': 'Socket_11',
        'Deletion Probability': 'Socket_14',
        'Duplication Probability': 'Socket_15',
    }

    print(f"Applying preset: {preset_name}")
    print(f"  {preset['description']}")

    for param, socket in socket_map.items():
        if param in preset:
            modifier[socket] = preset[param]
            print(f"  {param}: {preset[param]}")

    return True


def get_particle_stats(obj):
    """
    Get current particle statistics from the DLA object.

    Returns dict with total, active, and fixed particle counts.
    """
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)

    try:
        mesh = eval_obj.to_mesh()
        total = len(mesh.vertices)

        active_count = 0
        fixed_count = 0

        if 'active' in mesh.attributes:
            for item in mesh.attributes['active'].data:
                if item.value:
                    active_count += 1
                else:
                    fixed_count += 1
        else:
            fixed_count = total

        eval_obj.to_mesh_clear()

        return {
            'total': total,
            'active': active_count,
            'fixed': fixed_count,
            'frame': bpy.context.scene.frame_current,
        }
    except Exception as e:
        return {'error': str(e)}


def print_particle_stats(obj):
    """Print current particle statistics."""
    stats = get_particle_stats(obj)
    if 'error' in stats:
        print(f"Error getting stats: {stats['error']}")
    else:
        print(f"Frame {stats['frame']}: Total={stats['total']}, "
              f"Active={stats['active']}, Fixed={stats['fixed']}")


def setup_cycles_render():
    """Configure Cycles render settings for high-quality point cloud rendering."""
    scene = bpy.context.scene

    # Set render engine to Cycles
    scene.render.engine = 'CYCLES'

    # GPU settings
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'CUDA'  # or 'OPTIX', 'HIP', 'METAL'

    # Enable all GPU devices
    for device in prefs.devices:
        device.use = True

    # Scene settings
    scene.cycles.device = 'GPU'
    scene.cycles.samples = 128
    # Set denoising if available (varies by Blender build)
    denoiser_prop = scene.cycles.bl_rna.properties.get('denoiser')
    if denoiser_prop and denoiser_prop.enum_items:
        available = [item.identifier for item in denoiser_prop.enum_items]
        if 'OPENIMAGEDENOISE' in available:
            scene.cycles.use_denoising = True
            scene.cycles.denoiser = 'OPENIMAGEDENOISE'
        elif available:
            scene.cycles.use_denoising = True
            scene.cycles.denoiser = available[0]
        else:
            scene.cycles.use_denoising = False
    else:
        scene.cycles.use_denoising = False

    # Performance
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.01

    # Point cloud rendering
    scene.cycles.use_motion_blur = False

    print("Cycles render settings configured for GPU rendering")


def setup_camera_and_lights():
    """Create camera and lighting setup for DLA visualization."""
    # Camera
    bpy.ops.object.camera_add(location=(5, -5, 4))
    camera = bpy.context.active_object
    camera.name = "DLA_Camera"
    camera.data.lens = 50

    # Point camera at origin
    constraint = camera.constraints.new('TRACK_TO')
    constraint.target = bpy.data.objects.get("DLA_Seed")
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'

    bpy.context.scene.camera = camera

    # Key light (sun)
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.name = "Key_Light"
    sun.data.energy = 3.0

    # Fill light (area)
    bpy.ops.object.light_add(type='AREA', location=(-5, -5, 5))
    fill = bpy.context.active_object
    fill.name = "Fill_Light"
    fill.data.energy = 100.0
    fill.data.size = 5.0

    # Add world HDRI-like ambient
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True

    bg_node = world.node_tree.nodes.get('Background')
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.05, 0.05, 0.1, 1.0)
        bg_node.inputs['Strength'].default_value = 0.5


def setup_animation():
    """Configure animation settings for DLA simulation."""
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 250
    scene.frame_current = 1

    # Set playback to show simulation
    scene.render.fps = 24


def test_gpu_performance(output_dir="/tmp/dla_perf_test", sample_counts=None):
    """
    Test GPU rendering performance with various sample counts.

    Phase 5: GPU Performance Testing

    Measures render times and estimates optimal settings for the DLA scene.
    Outputs timing data and renders test images at different quality levels.

    Args:
        output_dir: Directory to save test renders and performance log
        sample_counts: List of sample counts to test (default: [16, 32, 64, 128, 256])

    Returns:
        dict: Performance results with timings and recommendations
    """
    import os
    import time

    if sample_counts is None:
        sample_counts = [16, 32, 64, 128, 256]

    scene = bpy.context.scene

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    results = {
        'tests': [],
        'gpu_info': {},
        'scene_info': {},
    }

    # ========== Gather GPU Info ==========
    prefs = bpy.context.preferences.addons['cycles'].preferences

    # Get compute device type
    results['gpu_info']['compute_type'] = prefs.compute_device_type

    # Get active devices
    active_devices = []
    for device in prefs.devices:
        if device.use:
            active_devices.append({
                'name': device.name,
                'type': device.type,
            })
    results['gpu_info']['active_devices'] = active_devices

    # ========== Gather Scene Info ==========
    # Get particle count
    dla_obj = bpy.data.objects.get("DLA_Seed")
    if dla_obj:
        stats = get_particle_stats(dla_obj)
        results['scene_info']['particle_count'] = stats.get('total', 'unknown')
        results['scene_info']['active_particles'] = stats.get('active', 'unknown')
        results['scene_info']['fixed_particles'] = stats.get('fixed', 'unknown')

    results['scene_info']['resolution'] = (scene.render.resolution_x,
                                            scene.render.resolution_y)
    results['scene_info']['frame'] = scene.frame_current

    print("=" * 60)
    print("DLA GPU Performance Test")
    print("=" * 60)
    print(f"Compute Device: {results['gpu_info']['compute_type']}")
    print(f"Active GPUs: {len(active_devices)}")
    for dev in active_devices:
        print(f"  - {dev['name']} ({dev['type']})")
    print(f"Resolution: {results['scene_info']['resolution']}")
    print(f"Particles: {results['scene_info'].get('particle_count', 'unknown')}")
    print("")

    # ========== Run Performance Tests ==========
    # Store original settings
    original_samples = scene.cycles.samples
    original_filepath = scene.render.filepath

    print("Running render tests...")
    print("-" * 40)

    for samples in sample_counts:
        scene.cycles.samples = samples
        scene.render.filepath = os.path.join(output_dir, f"test_{samples}spp.png")

        print(f"Testing {samples} samples...", end=" ", flush=True)

        # Time the render
        start_time = time.time()
        bpy.ops.render.render(write_still=True)
        elapsed = time.time() - start_time

        result = {
            'samples': samples,
            'time_seconds': round(elapsed, 2),
            'samples_per_second': round(samples / elapsed, 1),
            'output_file': scene.render.filepath,
        }
        results['tests'].append(result)

        print(f"{elapsed:.2f}s ({result['samples_per_second']} spp/s)")

    # Restore original settings
    scene.cycles.samples = original_samples
    scene.render.filepath = original_filepath

    # ========== Analysis ==========
    print("-" * 40)
    print("Performance Analysis:")

    # Find optimal quality/speed tradeoff
    if len(results['tests']) >= 2:
        # Calculate efficiency (samples per second)
        best_efficiency = max(results['tests'], key=lambda x: x['samples_per_second'])
        results['recommendation'] = {
            'optimal_samples': best_efficiency['samples'],
            'reason': 'Highest samples per second',
        }

        # Estimate time for full animation
        frames = scene.frame_end - scene.frame_start + 1
        for test in results['tests']:
            test['estimated_animation_time'] = round(test['time_seconds'] * frames, 1)
            test['estimated_animation_time_formatted'] = format_time(
                test['time_seconds'] * frames
            )

        print(f"  Best efficiency: {best_efficiency['samples']} samples "
              f"({best_efficiency['samples_per_second']} spp/s)")

        # Find quality sweet spot (64-128 samples typically)
        quality_tests = [t for t in results['tests'] if 64 <= t['samples'] <= 128]
        if quality_tests:
            quality_pick = min(quality_tests, key=lambda x: x['time_seconds'])
            print(f"  Quality/speed balance: {quality_pick['samples']} samples "
                  f"({quality_pick['time_seconds']}s per frame)")
            print(f"    Full animation ({frames} frames): "
                  f"{quality_pick['estimated_animation_time_formatted']}")

    # ========== Save Results ==========
    log_path = os.path.join(output_dir, "performance_log.txt")
    with open(log_path, 'w') as f:
        f.write("DLA GPU Performance Test Results\n")
        f.write("=" * 50 + "\n\n")

        f.write("GPU Configuration:\n")
        f.write(f"  Compute Type: {results['gpu_info']['compute_type']}\n")
        for dev in results['gpu_info']['active_devices']:
            f.write(f"  Device: {dev['name']} ({dev['type']})\n")
        f.write("\n")

        f.write("Scene Info:\n")
        f.write(f"  Resolution: {results['scene_info']['resolution']}\n")
        f.write(f"  Particles: {results['scene_info'].get('particle_count', 'N/A')}\n")
        f.write(f"  Frame: {results['scene_info']['frame']}\n")
        f.write("\n")

        f.write("Render Tests:\n")
        f.write("-" * 50 + "\n")
        f.write(f"{'Samples':<10} {'Time (s)':<12} {'SPP/s':<10} {'Anim Est.':<15}\n")
        f.write("-" * 50 + "\n")
        for test in results['tests']:
            f.write(f"{test['samples']:<10} {test['time_seconds']:<12} "
                    f"{test['samples_per_second']:<10} "
                    f"{test.get('estimated_animation_time_formatted', 'N/A'):<15}\n")
        f.write("\n")

        if 'recommendation' in results:
            f.write(f"Recommendation: {results['recommendation']['optimal_samples']} samples\n")
            f.write(f"Reason: {results['recommendation']['reason']}\n")

    print("")
    print(f"Results saved to: {log_path}")
    print("=" * 60)

    return results


def format_time(seconds):
    """Format seconds into human-readable time string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def benchmark_simulation(frames=50):
    """
    Benchmark the DLA simulation performance.

    Measures how long it takes to compute simulation frames (not rendering).

    Args:
        frames: Number of frames to simulate

    Returns:
        dict: Benchmark results
    """
    import time

    scene = bpy.context.scene
    dla_obj = bpy.data.objects.get("DLA_Seed")

    if not dla_obj:
        print("Error: DLA_Seed object not found")
        return None

    print("=" * 60)
    print("DLA Simulation Benchmark")
    print("=" * 60)

    # Store original frame
    original_frame = scene.frame_current
    scene.frame_current = 1

    # Force evaluation
    bpy.context.view_layer.update()

    results = {
        'frames': [],
        'total_time': 0,
        'particles_over_time': [],
    }

    print(f"Simulating {frames} frames...")

    start_total = time.time()

    for frame in range(1, frames + 1):
        frame_start = time.time()

        scene.frame_current = frame
        bpy.context.view_layer.update()

        frame_time = time.time() - frame_start

        # Get particle stats
        stats = get_particle_stats(dla_obj)

        results['frames'].append({
            'frame': frame,
            'time': round(frame_time, 3),
            'particles': stats.get('total', 0),
            'active': stats.get('active', 0),
            'fixed': stats.get('fixed', 0),
        })

        if frame % 10 == 0 or frame == frames:
            print(f"  Frame {frame}: {frame_time:.3f}s, "
                  f"{stats.get('total', '?')} particles")

    results['total_time'] = round(time.time() - start_total, 2)
    results['avg_frame_time'] = round(results['total_time'] / frames, 3)

    # Restore frame
    scene.frame_current = original_frame

    print("-" * 40)
    print(f"Total time: {results['total_time']}s")
    print(f"Average per frame: {results['avg_frame_time']}s")
    print(f"Estimated for 250 frames: {format_time(results['avg_frame_time'] * 250)}")
    print("=" * 60)

    return results


def main():
    """Main function to set up the complete DLA scene with all features."""
    print("=" * 60)
    print("DLA Point Cloud Generator for Blender")
    print("Phases 2-5: Flow Field + Particles + Material & Rendering")
    print("=" * 60)

    # Clear existing scene
    print("Clearing scene...")
    clear_scene()

    # Create seed geometry
    print("Creating seed geometry...")
    seed = create_seed_geometry()

    # Create material with Phase 5 features (emission, AO)
    print("Creating DLA material (with emission + AO)...")
    material = create_dla_material()
    seed.data.materials.append(material)

    # Create geometry nodes with flow field and particle management
    print("Setting up Geometry Nodes...")
    create_geometry_nodes_modifier(seed)

    # Setup rendering
    print("Configuring Cycles render settings...")
    setup_cycles_render()

    # Setup camera and lights
    print("Setting up camera and lighting...")
    setup_camera_and_lights()

    # Setup animation
    print("Configuring animation...")
    setup_animation()

    print("=" * 60)
    print("DLA scene setup complete!")
    print("")
    print("To run the simulation:")
    print("  1. Press SPACE to play the animation")
    print("  2. The DLA structure will grow over 250 frames")
    print("  3. Adjust parameters in the Modifier panel")
    print("")
    print("Basic Parameters (Phase 2):")
    print("  - Initial Particles: Starting point density")
    print("  - Step Size: Brownian motion magnitude")
    print("  - Contact Radius: Distance for particle sticking")
    print("")
    print("Flow Field Parameters (Phase 3):")
    print("  - Rotation Rate: Z-axis spiral (rad/frame)")
    print("  - Vertical Bias: Upward growth tendency")
    print("  - Radial Force: Expansion (+) / Contraction (-)")
    print("")
    print("Particle Management (Phase 4):")
    print("  - Deletion Probability: % particles deleted per frame")
    print("  - Duplication Probability: % particles duplicated per frame")
    print("  - Max Active Particles: Memory limit for active particles")
    print("  - Boundary Radius: Delete particles beyond this distance")
    print("")
    print("Material & Rendering (Phase 5):")
    print("  - Growth tip emission: Recent particles (>85% timepoint) glow")
    print("  - Ambient occlusion: Depth shading for visual depth")
    print("  - Modify in Shader Editor or recreate with:")
    print("    create_dla_material(tip_threshold=0.9, emission_strength=3.0)")
    print("")
    print("GPU Performance Testing (Phase 5):")
    print("  test_gpu_performance()      # Render speed at various sample counts")
    print("  benchmark_simulation(50)    # Simulation speed benchmark")
    print("")
    print("Monitor particles: print_particle_stats(bpy.data.objects['DLA_Seed'])")
    print("")
    print("Available Presets:")
    presets = create_flow_field_presets()
    for name, preset in presets.items():
        print(f"  - {name}: {preset['description']}")
    print("")
    print("To apply a preset:")
    print("  apply_preset(bpy.data.objects['DLA_Seed'], 'spiral')")
    print("=" * 60)


if __name__ == "__main__":
    main()
