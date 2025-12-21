"""
DLA Gallery Render Script

Renders example images for all DLA presets to showcase different growth patterns.
Uses the actual DLA simulation from dla_blender_setup.py.

Usage:
    blender -b -P dla_gallery_render.py -- --output /tmp/dla_gallery/

Note: This script loads dla_blender_setup.py automatically - do NOT use -P with both scripts.

Author: Claude (fractal-notebooks project)
"""

import bpy
import sys
import os
import argparse
from datetime import datetime


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

# Preset-specific material colors (RGBA)
PRESET_COLORS = {
    'classic': (0.7, 0.75, 0.85, 1.0),   # Cool gray-blue
    'spiral': (0.2, 0.4, 0.9, 1.0),       # Deep blue
    'tree': (0.25, 0.65, 0.25, 1.0),      # Forest green
    'coral': (0.95, 0.35, 0.25, 1.0),     # Coral red
    'vortex': (0.6, 0.2, 0.85, 1.0),      # Purple
    'turbulent': (0.95, 0.55, 0.15, 1.0), # Orange
    'dense': (0.5, 0.5, 0.55, 1.0),       # Gray
    'sparse': (0.6, 0.85, 0.95, 1.0),     # Light cyan
}

# Global namespace for dla_blender_setup functions
dla_funcs = {}


def load_dla_setup():
    """Load dla_blender_setup.py without running main()."""
    global dla_funcs

    # Find the script path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    setup_script = os.path.join(script_dir, 'dla_blender_setup.py')

    if not os.path.exists(setup_script):
        raise FileNotFoundError(f"Cannot find dla_blender_setup.py at {setup_script}")

    print(f"Loading DLA setup from: {setup_script}")

    # Read and execute the script, but override __name__ so main() doesn't run
    with open(setup_script, 'r') as f:
        code = f.read()

    # Execute with __name__ set to something other than "__main__"
    exec(compile(code, setup_script, 'exec'), {'__name__': 'dla_blender_setup', '__file__': setup_script})

    # The functions are now in the local namespace of exec, we need to get them differently
    # Re-execute but capture the namespace
    namespace = {'__name__': 'dla_blender_setup', '__file__': setup_script}
    exec(compile(code, setup_script, 'exec'), namespace)

    # Extract the functions we need
    dla_funcs['clear_scene'] = namespace.get('clear_scene')
    dla_funcs['create_seed_geometry'] = namespace.get('create_seed_geometry')
    dla_funcs['create_dla_material'] = namespace.get('create_dla_material')
    dla_funcs['create_geometry_nodes_modifier'] = namespace.get('create_geometry_nodes_modifier')
    dla_funcs['setup_cycles_render'] = namespace.get('setup_cycles_render')
    dla_funcs['setup_camera_and_lights'] = namespace.get('setup_camera_and_lights')
    dla_funcs['setup_animation'] = namespace.get('setup_animation')
    dla_funcs['apply_preset'] = namespace.get('apply_preset')
    dla_funcs['create_flow_field_presets'] = namespace.get('create_flow_field_presets')

    # Verify all functions loaded
    missing = [k for k, v in dla_funcs.items() if v is None]
    if missing:
        raise RuntimeError(f"Failed to load functions: {missing}")

    print("DLA setup functions loaded successfully")


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


def set_material_color(obj, color):
    """Update the DLA material base color."""
    if not obj.data.materials:
        return

    mat = obj.data.materials[0]
    if not mat.use_nodes:
        return

    # Find Principled BSDF and update colors
    for node in mat.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            node.inputs['Base Color'].default_value = color
            break

    # Also find and update the emission Mix RGB node if present
    for node in mat.node_tree.nodes:
        if node.type == 'MIX_RGB' or (hasattr(node, 'bl_idname') and 'Mix' in node.bl_idname):
            # This might be the emission color mix
            if 'B' in node.inputs:
                node.inputs['B'].default_value = color


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

    print(f"  Baking simulation to frame {end_frame}...", end='', flush=True)
    for frame in range(1, end_frame + 1):
        scene.frame_set(frame)
        if frame % 50 == 0:
            print(f" {frame}", end='', flush=True)
    print(" done")


def render_preset(preset_name, output_dir, args):
    """Render a single preset using the full DLA simulation."""
    print(f"\n{'='*60}")
    print(f"Preset: {preset_name}")
    print(f"  {PRESET_DESCRIPTIONS.get(preset_name, 'N/A')}")
    print(f"{'='*60}")

    # Get functions from dla_funcs
    clear_scene = dla_funcs['clear_scene']
    create_seed_geometry = dla_funcs['create_seed_geometry']
    create_dla_material = dla_funcs['create_dla_material']
    create_geometry_nodes_modifier = dla_funcs['create_geometry_nodes_modifier']
    setup_camera_and_lights = dla_funcs['setup_camera_and_lights']
    setup_animation = dla_funcs['setup_animation']
    apply_preset = dla_funcs['apply_preset']

    # Clear and create fresh scene
    print("  Setting up scene...")
    clear_scene()

    # Create seed geometry
    seed = create_seed_geometry()

    # Create material
    material = create_dla_material()
    seed.data.materials.append(material)

    # Create geometry nodes with simulation
    create_geometry_nodes_modifier(seed)

    # Apply the preset BEFORE baking
    print(f"  Applying preset parameters...")
    apply_preset(seed, preset_name)

    # Set preset-specific color
    color = PRESET_COLORS.get(preset_name, (0.8, 0.8, 0.8, 1.0))
    set_material_color(seed, color)

    # Setup camera and lights
    setup_camera_and_lights()

    # Setup animation
    setup_animation()

    # Setup rendering with our settings
    setup_render_settings(args)

    # Bake simulation to target frame
    bake_simulation(args.frame)

    # Set to target frame for render
    scene = bpy.context.scene
    scene.frame_set(args.frame)

    # Render
    output_path = os.path.join(output_dir, f"dla_{preset_name}.png")
    scene.render.filepath = output_path

    print(f"  Rendering...", end='', flush=True)
    bpy.ops.render.render(write_still=True)
    print(f" saved to {output_path}")

    return output_path


def main():
    args = parse_args()

    print("=" * 60)
    print("DLA Gallery Renderer")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)

    # Load dla_blender_setup.py functions
    try:
        load_dla_setup()
    except Exception as e:
        print(f"\nERROR: {e}")
        return

    # Create output directory
    os.makedirs(args.output, exist_ok=True)

    # Determine which presets to render
    if args.presets:
        presets_to_render = [p.strip() for p in args.presets.split(',')]
    else:
        presets_to_render = PRESETS

    print(f"\nOutput: {args.output}")
    print(f"Frame: {args.frame}, Samples: {args.samples}")
    print(f"Presets: {', '.join(presets_to_render)}")

    rendered = []

    for i, preset in enumerate(presets_to_render):
        if preset not in PRESETS:
            print(f"Warning: Unknown preset '{preset}', skipping")
            continue

        print(f"\n[{i+1}/{len(presets_to_render)}] ", end='')

        try:
            output_path = render_preset(preset, args.output, args)
            if output_path:
                rendered.append((preset, output_path))
        except Exception as e:
            print(f"Error rendering {preset}: {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print("\n" + "=" * 60)
    print("Gallery Complete!")
    print(f"Finished: {datetime.now().isoformat()}")
    print(f"Rendered {len(rendered)}/{len(presets_to_render)} presets")
    print(f"Output: {args.output}")
    print("=" * 60)


if __name__ == "__main__":
    main()
