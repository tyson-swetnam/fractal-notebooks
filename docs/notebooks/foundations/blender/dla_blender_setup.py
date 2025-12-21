"""
DLA Point Cloud Generator for Blender with Geometry Nodes

This script creates a complete Diffusion-Limited Aggregation (DLA) simulation
using Blender's Geometry Nodes and prepares it for Cycles rendering.

Usage:
    1. Open Blender 4.2+
    2. Open the Scripting workspace
    3. Load and run this script
    4. Press Play in the timeline to run the simulation

Based on techniques from the BlenderArtists DLA exploration thread.

Author: Claude (fractal-notebooks project)
Created: 2025-12-21
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
    """Create and configure the Geometry Nodes modifier for DLA simulation."""
    # Add geometry nodes modifier
    modifier = obj.modifiers.new(name="DLA_Simulation", type='NODES')

    # Create new node group
    node_group = bpy.data.node_groups.new(name="DLA_NodeGroup", type='GeometryNodeTree')
    modifier.node_group = node_group

    nodes = node_group.nodes
    links = node_group.links

    # Create interface (inputs/outputs)
    node_group.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    node_group.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

    # Add parameter inputs
    node_group.interface.new_socket(name="Initial Particles", in_out='INPUT', socket_type='NodeSocketInt')
    node_group.interface.new_socket(name="Step Size", in_out='INPUT', socket_type='NodeSocketFloat')
    node_group.interface.new_socket(name="Contact Radius", in_out='INPUT', socket_type='NodeSocketFloat')
    node_group.interface.new_socket(name="Noise Scale", in_out='INPUT', socket_type='NodeSocketFloat')
    node_group.interface.new_socket(name="Seed", in_out='INPUT', socket_type='NodeSocketInt')

    # Set default values
    modifier["Socket_2"] = 5000      # Initial Particles
    modifier["Socket_3"] = 0.02      # Step Size
    modifier["Socket_4"] = 0.03      # Contact Radius
    modifier["Socket_5"] = 2.0       # Noise Scale
    modifier["Socket_6"] = 42        # Seed

    # Create nodes
    group_input = nodes.new('NodeGroupInput')
    group_input.location = (-1600, 0)

    group_output = nodes.new('NodeGroupOutput')
    group_output.location = (1200, 0)

    # ========== INITIALIZATION SECTION ==========

    # Distribute points on the seed mesh
    distribute = nodes.new('GeometryNodeDistributePointsOnFaces')
    distribute.location = (-1200, 100)
    distribute.distribute_method = 'RANDOM'

    # Merge by distance to create initial structure
    merge_init = nodes.new('GeometryNodeMergeByDistance')
    merge_init.location = (-1000, 100)
    merge_init.inputs['Distance'].default_value = 0.01

    # Capture initial attributes
    # Random color attribute
    random_val = nodes.new('FunctionNodeRandomValue')
    random_val.location = (-1200, -150)
    random_val.data_type = 'FLOAT'

    # Store attribute: color
    store_color = nodes.new('GeometryNodeStoreNamedAttribute')
    store_color.location = (-800, 100)
    store_color.data_type = 'FLOAT'
    store_color.domain = 'POINT'
    store_color.inputs['Name'].default_value = "color_seed"

    # Frame counter for timepoint
    scene_time = nodes.new('GeometryNodeInputSceneTime')
    scene_time.location = (-1200, -300)

    # Store attribute: timepoint
    store_timepoint = nodes.new('GeometryNodeStoreNamedAttribute')
    store_timepoint.location = (-600, 100)
    store_timepoint.data_type = 'FLOAT'
    store_timepoint.domain = 'POINT'
    store_timepoint.inputs['Name'].default_value = "timepoint"

    # Store attribute: active flag (0 = fixed structure, 1 = moving particle)
    store_active = nodes.new('GeometryNodeStoreNamedAttribute')
    store_active.location = (-400, 100)
    store_active.data_type = 'BOOLEAN'
    store_active.domain = 'POINT'
    store_active.inputs['Name'].default_value = "active"

    # Create boolean true for initial particles (they start as structure)
    bool_false = nodes.new('FunctionNodeInputBool')
    bool_false.location = (-600, -100)
    bool_false.boolean = False  # Initial seed is fixed structure

    # ========== SIMULATION ZONE ==========

    # Simulation input/output
    sim_input = nodes.new('GeometryNodeSimulationInput')
    sim_input.location = (-200, 0)

    sim_output = nodes.new('GeometryNodeSimulationOutput')
    sim_output.location = (1000, 0)

    # Link simulation zones
    sim_output.pair_with_input(sim_input)

    # ========== INSIDE SIMULATION ZONE ==========

    # Separate active from fixed particles
    named_attr_active = nodes.new('GeometryNodeInputNamedAttribute')
    named_attr_active.location = (0, -200)
    named_attr_active.data_type = 'BOOLEAN'
    named_attr_active.inputs['Name'].default_value = "active"

    separate = nodes.new('GeometryNodeSeparateGeometry')
    separate.location = (200, 0)
    separate.domain = 'POINT'

    # ========== ACTIVE PARTICLE PROCESSING ==========

    # Get position for displacement
    position = nodes.new('GeometryNodeInputPosition')
    position.location = (200, -400)

    # Noise texture for brownian motion
    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (400, -300)
    noise.noise_dimensions = '3D'

    # Multiply noise by step size
    noise_multiply = nodes.new('ShaderNodeVectorMath')
    noise_multiply.location = (600, -300)
    noise_multiply.operation = 'MULTIPLY'

    # Add some randomness per frame
    frame_random = nodes.new('FunctionNodeRandomValue')
    frame_random.location = (400, -500)
    frame_random.data_type = 'FLOAT_VECTOR'

    # Combine displacement
    add_displacement = nodes.new('ShaderNodeVectorMath')
    add_displacement.location = (600, -450)
    add_displacement.operation = 'ADD'

    # Scale combined displacement
    scale_displacement = nodes.new('ShaderNodeVectorMath')
    scale_displacement.location = (800, -400)
    scale_displacement.operation = 'SCALE'
    scale_displacement.inputs['Scale'].default_value = 0.02

    # Add to position
    new_position = nodes.new('ShaderNodeVectorMath')
    new_position.location = (600, -150)
    new_position.operation = 'ADD'

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
    compare.inputs['B'].default_value = 0.03  # Contact radius

    # Update active attribute based on contact
    store_active_update = nodes.new('GeometryNodeStoreNamedAttribute')
    store_active_update.location = (1000, 0)
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
    and_gate.location = (950, 100)
    and_gate.operation = 'AND'

    # ========== SPAWN NEW PARTICLES ==========

    # Points node for spawning new particles
    spawn_points = nodes.new('GeometryNodePoints')
    spawn_points.location = (200, -600)
    spawn_points.inputs['Count'].default_value = 100  # Spawn rate per frame

    # Set random position for new particles (on a sphere shell)
    random_pos = nodes.new('FunctionNodeRandomValue')
    random_pos.location = (350, -650)
    random_pos.data_type = 'FLOAT_VECTOR'
    random_pos.inputs['Min'].default_value = (-1, -1, -1)
    random_pos.inputs['Max'].default_value = (1, 1, 1)

    # Normalize to sphere
    normalize = nodes.new('ShaderNodeVectorMath')
    normalize.location = (500, -650)
    normalize.operation = 'NORMALIZE'

    # Scale to spawn radius
    scale_spawn = nodes.new('ShaderNodeVectorMath')
    scale_spawn.location = (650, -650)
    scale_spawn.operation = 'SCALE'
    scale_spawn.inputs['Scale'].default_value = 2.0  # Spawn radius

    # Set position for spawned particles
    set_spawn_pos = nodes.new('GeometryNodeSetPosition')
    set_spawn_pos.location = (800, -600)

    # Store active=True for spawned particles
    store_spawn_active = nodes.new('GeometryNodeStoreNamedAttribute')
    store_spawn_active.location = (950, -600)
    store_spawn_active.data_type = 'BOOLEAN'
    store_spawn_active.domain = 'POINT'
    store_spawn_active.inputs['Name'].default_value = "active"

    bool_true = nodes.new('FunctionNodeInputBool')
    bool_true.location = (800, -750)
    bool_true.boolean = True

    # Store timepoint for spawned
    store_spawn_time = nodes.new('GeometryNodeStoreNamedAttribute')
    store_spawn_time.location = (1100, -600)
    store_spawn_time.data_type = 'FLOAT'
    store_spawn_time.domain = 'POINT'
    store_spawn_time.inputs['Name'].default_value = "timepoint"

    # ========== JOIN GEOMETRY ==========

    # Join all geometry: fixed + updated active + newly spawned
    join = nodes.new('GeometryNodeJoinGeometry')
    join.location = (1200, 0)

    # Update timepoint for particles that just became fixed
    # (we'll use a simpler approach - just keep the timepoint from spawn)

    # ========== LINKING SECTION ==========

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

    # Simulation zone internal connections
    links.new(sim_input.outputs['Geometry'], separate.inputs['Geometry'])
    links.new(named_attr_active.outputs['Attribute'], separate.inputs['Selection'])

    # Active particle displacement
    links.new(separate.outputs['Selection'], set_position.inputs['Geometry'])
    links.new(position.outputs['Position'], noise.inputs['Vector'])
    links.new(group_input.outputs['Noise Scale'], noise.inputs['Scale'])
    links.new(noise.outputs['Color'], noise_multiply.inputs[0])
    links.new(group_input.outputs['Step Size'], noise_multiply.inputs['Scale'])
    links.new(position.outputs['Position'], new_position.inputs[0])
    links.new(noise_multiply.outputs['Vector'], new_position.inputs[1])
    links.new(new_position.outputs['Vector'], set_position.inputs['Position'])

    # Contact detection
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

    # Spawn new particles
    links.new(random_pos.outputs['Value'], normalize.inputs[0])
    links.new(normalize.outputs['Vector'], scale_spawn.inputs[0])
    links.new(spawn_points.outputs['Geometry'], set_spawn_pos.inputs['Geometry'])
    links.new(scale_spawn.outputs['Vector'], set_spawn_pos.inputs['Position'])
    links.new(set_spawn_pos.outputs['Geometry'], store_spawn_active.inputs['Geometry'])
    links.new(bool_true.outputs['Boolean'], store_spawn_active.inputs['Value'])
    links.new(store_spawn_active.outputs['Geometry'], store_spawn_time.inputs['Geometry'])
    links.new(scene_time.outputs['Frame'], store_spawn_time.inputs['Value'])

    # Join all geometry
    links.new(separate.outputs['Inverted'], join.inputs['Geometry'])  # Fixed structure
    links.new(store_active_update.outputs['Geometry'], join.inputs['Geometry'])  # Updated active
    links.new(store_spawn_time.outputs['Geometry'], join.inputs['Geometry'])  # New spawned

    # Simulation output
    links.new(join.outputs['Geometry'], sim_output.inputs['Geometry'])

    # Final output
    links.new(sim_output.outputs['Geometry'], group_output.inputs['Geometry'])

    return modifier


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
    """Main function to set up the complete DLA scene."""
    print("=" * 60)
    print("DLA Point Cloud Generator for Blender")
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

    # Create geometry nodes
    print("Setting up Geometry Nodes for DLA simulation...")
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
    print("Parameters:")
    print("  - Initial Particles: Starting point density")
    print("  - Step Size: Brownian motion magnitude")
    print("  - Contact Radius: Distance for particle sticking")
    print("  - Noise Scale: Spatial frequency of displacement")
    print("  - Seed: Random seed for reproducibility")
    print("=" * 60)


if __name__ == "__main__":
    main()
