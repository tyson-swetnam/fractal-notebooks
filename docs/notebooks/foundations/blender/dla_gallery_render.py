"""
DLA Gallery Render Script

Renders example images for all DLA presets to showcase different growth patterns.

Usage:
    blender -b -P dla_blender_setup.py -P dla_gallery_render.py -- --output /tmp/dla_gallery/

Author: Claude (fractal-notebooks project)
"""

import bpy
import sys
import os
import argparse
from datetime import datetime


# Import functions from dla_blender_setup (already loaded via -P)
# These are available in the global namespace after running dla_blender_setup.py


PRESETS = ['classic', 'spiral', 'tree', 'coral', 'vortex', 'turbulent', 'dense', 'sparse']

PRESET_DESCRIPTIONS = {
    'classic': 'Classic DLA with pure Brownian motion',
    'spiral': 'Spiral galaxy-like growth pattern',
    'tree': 'Upward-growing tree-like structure',
    'coral': 'Coral-like branching with radial expansion',
    'vortex': 'Strong spiraling vortex pattern',
    'turbulent': 'Chaotic turbulent flow field',
    'dense': 'Dense growth with high duplication',
    'sparse': 'Sparse branching with high deletion',
}


def parse_args():
    """Parse command line arguments."""
    if '--' in sys.argv:
        argv = sys.argv[sys.argv.index('--') + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser(description='DLA Gallery Renderer')
    parser.add_argument('--output', '-o', type=str, default='/tmp/dla_gallery',
                        help='Output directory for gallery images')
    parser.add_argument('--frame', type=int, default=150,
                        help='Frame to render (simulation progress)')
    parser.add_argument('--samples', type=int, default=128,
                        help='Render samples')
    parser.add_argument('--resolution', type=str, default='1920x1080',
                        help='Resolution WxH')
    parser.add_argument('--presets', type=str, default=None,
                        help='Comma-separated list of presets to render (default: all)')

    return parser.parse_args(argv)


def get_preset_params(preset_name):
    """Get parameter dictionary for a preset."""
    presets = {
        'classic': {
            'Step Size': 0.02,
            'Rotation Rate': 0.0,
            'Vertical Bias': 0.0,
            'Radial Force': 0.0,
            'Flow Scale': 0.0,
            'Flow Strength': 0.0,
        },
        'spiral': {
            'Step Size': 0.015,
            'Rotation Rate': 0.05,
            'Vertical Bias': 0.002,
            'Radial Force': -0.001,
            'Flow Scale': 2.0,
            'Flow Strength': 0.01,
        },
        'tree': {
            'Step Size': 0.02,
            'Rotation Rate': 0.01,
            'Vertical Bias': 0.015,
            'Radial Force': 0.0,
            'Flow Scale': 3.0,
            'Flow Strength': 0.005,
        },
        'coral': {
            'Step Size': 0.018,
            'Rotation Rate': 0.02,
            'Vertical Bias': 0.005,
            'Radial Force': 0.005,
            'Flow Scale': 1.5,
            'Flow Strength': 0.015,
        },
        'vortex': {
            'Step Size': 0.01,
            'Rotation Rate': 0.15,
            'Vertical Bias': 0.0,
            'Radial Force': -0.01,
            'Flow Scale': 1.0,
            'Flow Strength': 0.02,
        },
        'turbulent': {
            'Step Size': 0.025,
            'Rotation Rate': 0.03,
            'Vertical Bias': 0.0,
            'Radial Force': 0.0,
            'Flow Scale': 0.5,
            'Flow Strength': 0.04,
        },
        'dense': {
            'Step Size': 0.015,
            'Rotation Rate': 0.02,
            'Vertical Bias': 0.003,
            'Radial Force': -0.002,
            'Flow Scale': 2.0,
            'Flow Strength': 0.01,
        },
        'sparse': {
            'Step Size': 0.03,
            'Rotation Rate': 0.01,
            'Vertical Bias': 0.01,
            'Radial Force': 0.003,
            'Flow Scale': 4.0,
            'Flow Strength': 0.008,
        },
    }
    return presets.get(preset_name, presets['classic'])


def apply_preset_to_modifier(obj, preset_name):
    """Apply preset parameters to the DLA geometry nodes modifier."""
    params = get_preset_params(preset_name)

    # Find the geometry nodes modifier
    modifier = None
    for mod in obj.modifiers:
        if mod.type == 'NODES' and mod.node_group:
            modifier = mod
            break

    if not modifier:
        print(f"Warning: No geometry nodes modifier found on {obj.name}")
        return False

    # Apply parameters
    for param_name, value in params.items():
        # Find the input socket by name
        for item in modifier.node_group.interface.items_tree:
            if item.item_type == 'SOCKET' and item.in_out == 'INPUT':
                if item.name == param_name:
                    try:
                        modifier[item.identifier] = value
                        print(f"  Set {param_name} = {value}")
                    except Exception as e:
                        print(f"  Warning: Could not set {param_name}: {e}")

    return True


def setup_render_settings(args):
    """Configure render settings."""
    scene = bpy.context.scene

    # Resolution
    width, height = map(int, args.resolution.split('x'))
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100

    # Cycles settings
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = args.samples
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.01

    # Denoising - check availability
    scene.cycles.use_denoising = False
    denoiser_prop = scene.cycles.bl_rna.properties.get('denoiser')
    if denoiser_prop and denoiser_prop.enum_items:
        available = [item.identifier for item in denoiser_prop.enum_items]
        if available:
            scene.cycles.use_denoising = True
            scene.cycles.denoiser = available[0]

    # Try GPU
    prefs = bpy.context.preferences.addons.get('cycles')
    if prefs:
        prefs = prefs.preferences
        for compute_type in ['OPTIX', 'CUDA', 'HIP', 'METAL', 'ONEAPI']:
            try:
                prefs.compute_device_type = compute_type
                for device in prefs.devices:
                    device.use = True
                scene.cycles.device = 'GPU'
                print(f"Using GPU rendering with {compute_type}")
                break
            except:
                continue

    # Output format
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '8'


def bake_simulation(end_frame):
    """Bake simulation up to target frame."""
    scene = bpy.context.scene

    # Bake by stepping through frames
    print(f"Baking simulation to frame {end_frame}...")
    for frame in range(1, end_frame + 1):
        scene.frame_set(frame)
        if frame % 25 == 0:
            print(f"  Frame {frame}/{end_frame}")

    print("Simulation bake complete")


def render_preset(preset_name, output_dir, args):
    """Render a single preset."""
    print(f"\n{'='*60}")
    print(f"Rendering preset: {preset_name}")
    print(f"Description: {PRESET_DESCRIPTIONS.get(preset_name, 'N/A')}")
    print(f"{'='*60}")

    # Clear scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Import and run the setup script's main function
    # Since dla_blender_setup.py was loaded with -P, its functions are in globals
    # We need to recreate the scene for each preset

    # Create basic scene elements manually
    scene = bpy.context.scene

    # Create seed point cloud
    mesh = bpy.data.meshes.new("DLA_Seed_Mesh")
    import mathutils
    mesh.from_pydata([(0, 0, 0)], [], [])
    mesh.update()

    seed = bpy.data.objects.new("DLA_Seed", mesh)
    bpy.context.collection.objects.link(seed)

    # Convert to point cloud
    bpy.context.view_layer.objects.active = seed
    seed.select_set(True)

    # Add geometry nodes modifier
    modifier = seed.modifiers.new(name="DLA_Simulation", type='NODES')

    # Create new node group
    node_group = bpy.data.node_groups.new('DLA_Geometry_Nodes', 'GeometryNodeTree')

    # Create interface sockets
    node_group.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    node_group.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')

    # Add parameter inputs
    params = [
        ('Initial Particles', 'NodeSocketInt', 5000),
        ('Step Size', 'NodeSocketFloat', 0.02),
        ('Contact Radius', 'NodeSocketFloat', 0.03),
        ('Rotation Rate', 'NodeSocketFloat', 0.0),
        ('Vertical Bias', 'NodeSocketFloat', 0.0),
        ('Radial Force', 'NodeSocketFloat', 0.0),
        ('Flow Scale', 'NodeSocketFloat', 2.0),
        ('Flow Strength', 'NodeSocketFloat', 0.01),
    ]

    for name, socket_type, default in params:
        socket = node_group.interface.new_socket(name, in_out='INPUT', socket_type=socket_type)
        socket.default_value = default

    # Create nodes
    nodes = node_group.nodes
    links = node_group.links

    # Group input/output
    group_input = nodes.new('NodeGroupInput')
    group_input.location = (-800, 0)
    group_output = nodes.new('NodeGroupOutput')
    group_output.location = (800, 0)

    # Mesh to Points
    mesh_to_points = nodes.new('GeometryNodeMeshToPoints')
    mesh_to_points.location = (-600, 0)

    # Points node for particle distribution
    distribute = nodes.new('GeometryNodeDistributePointsOnFaces')
    distribute.location = (-400, 0)
    distribute.distribute_method = 'RANDOM'

    # Create an icosphere for better distribution
    ico = nodes.new('GeometryNodeMeshIcoSphere')
    ico.location = (-600, 200)
    ico.inputs['Radius'].default_value = 0.5
    ico.inputs['Subdivisions'].default_value = 3

    # Simulation zone
    sim_output = nodes.new('GeometryNodeSimulationOutput')
    sim_output.location = (400, 0)
    sim_input = nodes.new('GeometryNodeSimulationInput')
    sim_input.location = (-200, 0)
    sim_input.pair_with_output(sim_output)

    # Set Point Radius for visualization
    set_radius = nodes.new('GeometryNodeSetPointRadius')
    set_radius.location = (600, 0)
    set_radius.inputs['Radius'].default_value = 0.015

    # Join geometry (ico + input)
    join = nodes.new('GeometryNodeJoinGeometry')
    join.location = (0, 0)

    # Connect nodes
    links.new(ico.outputs['Mesh'], distribute.inputs['Mesh'])
    links.new(group_input.outputs['Initial Particles'], distribute.inputs['Density'])
    links.new(distribute.outputs['Points'], join.inputs['Geometry'])
    links.new(group_input.outputs['Geometry'], mesh_to_points.inputs['Mesh'])
    links.new(mesh_to_points.outputs['Points'], join.inputs['Geometry'])
    links.new(join.outputs['Geometry'], sim_input.inputs['Geometry'])
    links.new(sim_input.outputs['Geometry'], sim_output.inputs['Geometry'])
    links.new(sim_output.outputs['Geometry'], set_radius.inputs['Points'])
    links.new(set_radius.outputs['Points'], group_output.inputs['Geometry'])

    # Assign node group to modifier
    modifier.node_group = node_group

    # Apply preset parameters
    print(f"Applying preset parameters for {preset_name}...")
    preset_params = get_preset_params(preset_name)
    for param_name, value in preset_params.items():
        for item in node_group.interface.items_tree:
            if item.item_type == 'SOCKET' and item.in_out == 'INPUT':
                if item.name == param_name:
                    try:
                        modifier[item.identifier] = value
                        print(f"  {param_name} = {value}")
                    except:
                        pass

    # Create material
    mat = bpy.data.materials.new(name="DLA_Material")
    mat.use_nodes = True
    mat_nodes = mat.node_tree.nodes
    mat_links = mat.node_tree.links

    # Clear default nodes
    mat_nodes.clear()

    # Create material nodes
    output = mat_nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)

    principled = mat_nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)

    # Set color based on preset
    preset_colors = {
        'classic': (0.8, 0.8, 0.9, 1.0),
        'spiral': (0.2, 0.5, 0.9, 1.0),
        'tree': (0.3, 0.7, 0.3, 1.0),
        'coral': (0.9, 0.4, 0.3, 1.0),
        'vortex': (0.6, 0.2, 0.8, 1.0),
        'turbulent': (0.9, 0.6, 0.2, 1.0),
        'dense': (0.4, 0.4, 0.5, 1.0),
        'sparse': (0.7, 0.9, 0.95, 1.0),
    }
    color = preset_colors.get(preset_name, (0.8, 0.8, 0.8, 1.0))
    principled.inputs['Base Color'].default_value = color
    principled.inputs['Metallic'].default_value = 0.3
    principled.inputs['Roughness'].default_value = 0.4

    mat_links.new(principled.outputs['BSDF'], output.inputs['Surface'])

    # Assign material
    seed.data.materials.append(mat)

    # Setup camera
    cam_data = bpy.data.cameras.new("Camera")
    cam = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(cam)
    scene.camera = cam
    cam.location = (3, -3, 2)
    cam.rotation_euler = (1.1, 0, 0.8)

    # Setup lights
    light_data = bpy.data.lights.new("Key_Light", type='AREA')
    light_data.energy = 500
    light_data.size = 3
    key_light = bpy.data.objects.new("Key_Light", light_data)
    bpy.context.collection.objects.link(key_light)
    key_light.location = (3, -2, 4)
    key_light.rotation_euler = (0.5, 0.3, 0)

    fill_data = bpy.data.lights.new("Fill_Light", type='AREA')
    fill_data.energy = 200
    fill_data.size = 2
    fill_light = bpy.data.objects.new("Fill_Light", fill_data)
    bpy.context.collection.objects.link(fill_light)
    fill_light.location = (-2, -3, 2)

    # Set world background
    world = bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = (0.02, 0.02, 0.03, 1.0)

    # Configure animation
    scene.frame_start = 1
    scene.frame_end = 250

    # Setup render settings
    setup_render_settings(args)

    # Bake simulation
    bake_simulation(args.frame)

    # Set to target frame
    scene.frame_set(args.frame)

    # Render
    output_path = os.path.join(output_dir, f"dla_{preset_name}.png")
    scene.render.filepath = output_path

    print(f"Rendering to {output_path}...")
    bpy.ops.render.render(write_still=True)
    print(f"Saved: {output_path}")

    return output_path


def main():
    args = parse_args()

    # Create output directory
    os.makedirs(args.output, exist_ok=True)

    # Determine which presets to render
    if args.presets:
        presets_to_render = [p.strip() for p in args.presets.split(',')]
    else:
        presets_to_render = PRESETS

    print("=" * 60)
    print("DLA Gallery Renderer")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Output directory: {args.output}")
    print(f"Frame: {args.frame}")
    print(f"Presets: {', '.join(presets_to_render)}")
    print("=" * 60)

    rendered = []

    for preset in presets_to_render:
        if preset not in PRESETS:
            print(f"Warning: Unknown preset '{preset}', skipping")
            continue

        try:
            output_path = render_preset(preset, args.output, args)
            rendered.append((preset, output_path))
        except Exception as e:
            print(f"Error rendering {preset}: {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print("\n" + "=" * 60)
    print("Gallery Render Complete!")
    print(f"Finished: {datetime.now().isoformat()}")
    print(f"Rendered {len(rendered)} presets:")
    for preset, path in rendered:
        print(f"  - {preset}: {path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
