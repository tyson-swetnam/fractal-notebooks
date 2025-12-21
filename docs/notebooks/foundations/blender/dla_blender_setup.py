"""
DLA Point Cloud Generator for Blender with Geometry Nodes

This script creates a complete Diffusion-Limited Aggregation (DLA) simulation
using Blender's Geometry Nodes and prepares it for Cycles rendering.

Features:
- Phase 2: Basic DLA simulation with brownian motion and contact detection
- Phase 3: Flow field dynamics with spiral rotation, vertical bias, radial forces

Usage:
    1. Open Blender 4.2+
    2. Open the Scripting workspace
    3. Load and run this script
    4. Press Play in the timeline to run the simulation

Based on techniques from the BlenderArtists DLA exploration thread.

Author: Claude (fractal-notebooks project)
Created: 2025-12-21
Updated: 2025-12-21 (Phase 3: Flow Field Enhancement)
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


def create_dla_material():
    """Create a material for the DLA point cloud with timepoint-based coloring."""
    mat = bpy.data.materials.new(name="DLA_Material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear default nodes
    nodes.clear()

    # Create nodes
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)

    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (300, 0)

    color_ramp = nodes.new('ShaderNodeValToRGB')
    color_ramp.location = (0, 0)
    color_ramp.color_ramp.interpolation = 'LINEAR'

    # Set up color ramp: deep blue -> cyan -> green -> yellow -> white
    ramp = color_ramp.color_ramp
    ramp.elements[0].position = 0.0
    ramp.elements[0].color = (0.04, 0.09, 0.16, 1.0)  # Deep blue

    ramp.elements[1].position = 1.0
    ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)  # White

    # Add intermediate colors
    elem = ramp.elements.new(0.3)
    elem.color = (0.0, 0.83, 1.0, 1.0)  # Cyan

    elem = ramp.elements.new(0.6)
    elem.color = (0.0, 1.0, 0.53, 1.0)  # Green

    elem = ramp.elements.new(0.9)
    elem.color = (1.0, 0.87, 0.0, 1.0)  # Yellow

    # Attribute node to read timepoint
    attr = nodes.new('ShaderNodeAttribute')
    attr.location = (-400, 0)
    attr.attribute_name = "timepoint"
    attr.attribute_type = 'INSTANCER'

    # Divide by max frames to normalize
    divide = nodes.new('ShaderNodeMath')
    divide.location = (-200, 0)
    divide.operation = 'DIVIDE'
    divide.inputs[1].default_value = 250.0  # Max frames

    # Link nodes
    links.new(attr.outputs['Fac'], divide.inputs[0])
    links.new(divide.outputs['Value'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])

    # Set some emission for the material
    principled.inputs['Emission Strength'].default_value = 0.1

    return mat


def create_geometry_nodes_modifier(obj):
    """
    Create and configure the Geometry Nodes modifier for DLA simulation.

    Includes Phase 3 Flow Field Enhancement:
    - 3D noise texture for large-scale structure
    - Z-axis rotation for spiral patterns
    - Vertical growth bias
    - Radial expansion/contraction controls
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

    # Create nodes
    group_input = nodes.new('NodeGroupInput')
    group_input.location = (-2000, 0)

    group_output = nodes.new('NodeGroupOutput')
    group_output.location = (1600, 0)

    # ========== INITIALIZATION SECTION ==========

    # Distribute points on the seed mesh
    distribute = nodes.new('GeometryNodeDistributePointsOnFaces')
    distribute.location = (-1600, 100)
    distribute.distribute_method = 'RANDOM'

    # Merge by distance to create initial structure
    merge_init = nodes.new('GeometryNodeMergeByDistance')
    merge_init.location = (-1400, 100)
    merge_init.inputs['Distance'].default_value = 0.01

    # Capture initial attributes
    # Random color attribute
    random_val = nodes.new('FunctionNodeRandomValue')
    random_val.location = (-1600, -150)
    random_val.data_type = 'FLOAT'

    # Store attribute: color
    store_color = nodes.new('GeometryNodeStoreNamedAttribute')
    store_color.location = (-1200, 100)
    store_color.data_type = 'FLOAT'
    store_color.domain = 'POINT'
    store_color.inputs['Name'].default_value = "color_seed"

    # Frame counter for timepoint
    scene_time = nodes.new('GeometryNodeInputSceneTime')
    scene_time.location = (-1600, -300)

    # Store attribute: timepoint
    store_timepoint = nodes.new('GeometryNodeStoreNamedAttribute')
    store_timepoint.location = (-1000, 100)
    store_timepoint.data_type = 'FLOAT'
    store_timepoint.domain = 'POINT'
    store_timepoint.inputs['Name'].default_value = "timepoint"

    # Store attribute: active flag (0 = fixed structure, 1 = moving particle)
    store_active = nodes.new('GeometryNodeStoreNamedAttribute')
    store_active.location = (-800, 100)
    store_active.data_type = 'BOOLEAN'
    store_active.domain = 'POINT'
    store_active.inputs['Name'].default_value = "active"

    # Create boolean false for initial particles (they start as structure)
    bool_false = nodes.new('FunctionNodeInputBool')
    bool_false.location = (-1000, -100)
    bool_false.boolean = False  # Initial seed is fixed structure

    # ========== SIMULATION ZONE ==========

    # Simulation input/output
    sim_input = nodes.new('GeometryNodeSimulationInput')
    sim_input.location = (-600, 0)

    sim_output = nodes.new('GeometryNodeSimulationOutput')
    sim_output.location = (1400, 0)

    # Link simulation zones
    sim_output.pair_with_input(sim_input)

    # ========== INSIDE SIMULATION ZONE ==========

    # Separate active from fixed particles
    named_attr_active = nodes.new('GeometryNodeInputNamedAttribute')
    named_attr_active.location = (-400, -200)
    named_attr_active.data_type = 'BOOLEAN'
    named_attr_active.inputs['Name'].default_value = "active"

    separate = nodes.new('GeometryNodeSeparateGeometry')
    separate.location = (-200, 0)
    separate.domain = 'POINT'

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
    vertical_bias_vec = nodes.new('FunctionNodeCombineXYZ')
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
    store_active_update.location = (1100, 0)
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
    join.location = (1300, 0)

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

    # --- Contact Detection Links ---
    links.new(separate.outputs['Inverted'], sample_nearest.inputs['Geometry'])
    links.new(set_position.outputs['Geometry'], sample_nearest.inputs['Sample Position'])

    links.new(separate.outputs['Inverted'], sample_index.inputs['Geometry'])
    links.new(sample_nearest.outputs['Index'], sample_index.inputs['Index'])
    links.new(position2.outputs['Position'], sample_index.inputs['Value'])

    links.new(set_position.outputs['Geometry'], distance.inputs[0])
    links.new(sample_index.outputs['Value'], distance.inputs[1])

    links.new(distance.outputs['Value'], compare.inputs['A'])
    links.new(group_input.outputs['Contact Radius'], compare.inputs['B'])

    # Update active flag
    links.new(compare.outputs['Result'], not_gate.inputs[0])
    links.new(named_attr_active2.outputs['Attribute'], and_gate.inputs[0])
    links.new(not_gate.outputs['Boolean'], and_gate.inputs[1])

    links.new(set_position.outputs['Geometry'], store_active_update.inputs['Geometry'])
    links.new(and_gate.outputs['Boolean'], store_active_update.inputs['Value'])

    # --- Spawn Links ---
    links.new(group_input.outputs['Spawn Rate'], spawn_points.inputs['Count'])
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
    }

    print(f"Applying preset: {preset_name}")
    print(f"  {preset['description']}")

    for param, socket in socket_map.items():
        if param in preset:
            modifier[socket] = preset[param]
            print(f"  {param}: {preset[param]}")

    return True


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
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'

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


def main():
    """Main function to set up the complete DLA scene with flow field."""
    print("=" * 60)
    print("DLA Point Cloud Generator for Blender")
    print("With Flow Field Enhancement (Phase 3)")
    print("=" * 60)

    # Clear existing scene
    print("Clearing scene...")
    clear_scene()

    # Create seed geometry
    print("Creating seed geometry...")
    seed = create_seed_geometry()

    # Create material
    print("Creating DLA material...")
    material = create_dla_material()
    seed.data.materials.append(material)

    # Create geometry nodes with flow field
    print("Setting up Geometry Nodes with Flow Field...")
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
    print("Basic Parameters:")
    print("  - Initial Particles: Starting point density")
    print("  - Step Size: Brownian motion magnitude")
    print("  - Contact Radius: Distance for particle sticking")
    print("  - Noise Scale: Spatial frequency of brownian motion")
    print("")
    print("Flow Field Parameters (Phase 3):")
    print("  - Rotation Rate: Z-axis spiral (rad/frame)")
    print("  - Vertical Bias: Upward growth tendency")
    print("  - Radial Force: Expansion (+) / Contraction (-)")
    print("  - Flow Noise Scale: Large-scale structure frequency")
    print("  - Flow Noise Strength: Large-scale displacement magnitude")
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
