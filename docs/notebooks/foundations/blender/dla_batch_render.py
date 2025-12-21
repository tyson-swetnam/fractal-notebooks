"""
DLA Batch Rendering Script for Blender

This script enables headless (command-line) rendering of DLA simulations.
Useful for automation, batch processing, and remote rendering.

Usage:
    # Single frame render
    blender -b -P dla_batch_render.py -- --frame 100 --output /tmp/dla_frame.png

    # Animation render
    blender -b -P dla_batch_render.py -- --animation --start 1 --end 250 --output /tmp/dla_anim/

    # With custom settings
    blender -b -P dla_batch_render.py -- --samples 512 --resolution 1920x1080 --output /tmp/render.png

    # Load existing .blend file
    blender -b existing_scene.blend -P dla_batch_render.py -- --render

Author: Claude (fractal-notebooks project)
Created: 2025-12-21
"""

import bpy
import sys
import os
import argparse
from datetime import datetime


def parse_args():
    """Parse command line arguments after '--' separator."""
    # Find arguments after '--'
    if '--' in sys.argv:
        argv = sys.argv[sys.argv.index('--') + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser(description='DLA Batch Renderer')

    # Render mode
    parser.add_argument('--render', action='store_true',
                        help='Render single frame (current frame)')
    parser.add_argument('--animation', action='store_true',
                        help='Render animation sequence')
    parser.add_argument('--frame', type=int, default=None,
                        help='Single frame to render')
    parser.add_argument('--start', type=int, default=None,
                        help='Start frame for animation')
    parser.add_argument('--end', type=int, default=None,
                        help='End frame for animation')

    # Output
    parser.add_argument('--output', '-o', type=str, default='/tmp/dla_render',
                        help='Output path (file or directory)')
    parser.add_argument('--format', type=str, default='PNG',
                        choices=['PNG', 'JPEG', 'TIFF', 'EXR', 'BMP'],
                        help='Output format')

    # Quality settings
    parser.add_argument('--samples', type=int, default=128,
                        help='Render samples')
    parser.add_argument('--resolution', type=str, default='1920x1080',
                        help='Resolution WxH')
    parser.add_argument('--denoiser', type=str, default='OPENIMAGEDENOISE',
                        choices=['OPENIMAGEDENOISE', 'OPTIX', 'NONE'],
                        help='Denoiser to use')

    # DLA parameters
    parser.add_argument('--particles', type=int, default=5000,
                        help='Initial particle count')
    parser.add_argument('--step-size', type=float, default=0.02,
                        help='Brownian motion step size')
    parser.add_argument('--contact-radius', type=float, default=0.03,
                        help='Contact radius for particle sticking')
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed for simulation')

    # Export options
    parser.add_argument('--export', type=str, default=None,
                        help='Export point cloud after simulation (npz, ply, csv)')
    parser.add_argument('--export-path', type=str, default='/tmp/dla_export',
                        help='Path for exported data')

    # Scene setup
    parser.add_argument('--setup', action='store_true',
                        help='Create DLA scene from scratch')

    return parser.parse_args(argv)


def setup_render_settings(args):
    """Configure render settings based on arguments."""
    scene = bpy.context.scene

    # Parse resolution
    width, height = map(int, args.resolution.split('x'))
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100

    # Cycles settings
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = args.samples
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.01

    # Denoiser
    if args.denoiser == 'NONE':
        scene.cycles.use_denoising = False
    else:
        scene.cycles.use_denoising = True
        scene.cycles.denoiser = args.denoiser

    # Try to use GPU
    prefs = bpy.context.preferences.addons.get('cycles')
    if prefs:
        prefs = prefs.preferences
        # Try different GPU backends
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
        else:
            scene.cycles.device = 'CPU'
            print("Falling back to CPU rendering")

    # Output settings
    scene.render.image_settings.file_format = args.format

    # Set output path
    output = args.output
    if not output.endswith(('/', '\\')):
        if args.animation:
            output = output + '/'
    scene.render.filepath = output

    print(f"Render settings:")
    print(f"  Resolution: {width}x{height}")
    print(f"  Samples: {args.samples}")
    print(f"  Denoiser: {args.denoiser}")
    print(f"  Output: {output}")


def setup_dla_scene(args):
    """Set up DLA scene from scratch."""
    print("Setting up DLA scene...")

    # Import the setup module
    import importlib.util
    script_dir = os.path.dirname(os.path.abspath(__file__))
    setup_path = os.path.join(script_dir, 'dla_blender_setup.py')

    if os.path.exists(setup_path):
        spec = importlib.util.spec_from_file_location("dla_setup", setup_path)
        dla_setup = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(dla_setup)

        # Run main setup
        dla_setup.main()

        # Override parameters if specified
        obj = bpy.data.objects.get("DLA_Seed")
        if obj:
            for mod in obj.modifiers:
                if mod.type == 'NODES':
                    mod["Socket_2"] = args.particles
                    mod["Socket_3"] = args.step_size
                    mod["Socket_4"] = args.contact_radius
                    mod["Socket_6"] = args.seed
                    print(f"DLA parameters set:")
                    print(f"  Particles: {args.particles}")
                    print(f"  Step size: {args.step_size}")
                    print(f"  Contact radius: {args.contact_radius}")
                    print(f"  Seed: {args.seed}")
    else:
        print(f"Warning: dla_blender_setup.py not found at {setup_path}")
        print("Creating minimal DLA scene...")

        # Clear scene
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

        # Create simple sphere
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(0, 0, 0))


def bake_simulation(end_frame):
    """Bake the simulation by advancing through all frames."""
    print(f"Baking simulation to frame {end_frame}...")

    scene = bpy.context.scene
    start = scene.frame_start

    for frame in range(start, end_frame + 1):
        scene.frame_set(frame)
        if frame % 10 == 0:
            print(f"  Frame {frame}/{end_frame}")

    print("Simulation bake complete")


def export_point_cloud(args):
    """Export the current point cloud."""
    print(f"Exporting point cloud to {args.export_path}.{args.export}...")

    # Import export module
    import importlib.util
    script_dir = os.path.dirname(os.path.abspath(__file__))
    export_path = os.path.join(script_dir, 'dla_export.py')

    if os.path.exists(export_path):
        spec = importlib.util.spec_from_file_location("dla_export", export_path)
        dla_export = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(dla_export)

        # Export
        output_file = f"{args.export_path}.{args.export}"
        dla_export.quick_export(args.export, output_file)
    else:
        print(f"Warning: dla_export.py not found at {export_path}")


def render_single_frame(frame=None):
    """Render a single frame."""
    scene = bpy.context.scene

    if frame is not None:
        scene.frame_set(frame)

    print(f"Rendering frame {scene.frame_current}...")
    bpy.ops.render.render(write_still=True)
    print(f"Frame rendered to: {scene.render.filepath}")


def render_animation(start=None, end=None):
    """Render animation sequence."""
    scene = bpy.context.scene

    if start is not None:
        scene.frame_start = start
    if end is not None:
        scene.frame_end = end

    print(f"Rendering animation: frames {scene.frame_start} to {scene.frame_end}")
    print(f"Output: {scene.render.filepath}")

    bpy.ops.render.render(animation=True)

    print("Animation render complete")


def main():
    """Main entry point for batch rendering."""
    print("=" * 60)
    print("DLA Batch Renderer")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)

    args = parse_args()

    # Set up scene if requested
    if args.setup:
        setup_dla_scene(args)

    # Configure render settings
    setup_render_settings(args)

    # Determine render mode
    if args.animation:
        start = args.start or bpy.context.scene.frame_start
        end = args.end or bpy.context.scene.frame_end

        # Bake simulation first
        bake_simulation(end)

        # Export if requested
        if args.export:
            export_point_cloud(args)

        # Render animation
        render_animation(start, end)

    elif args.frame is not None:
        # Bake up to requested frame
        bake_simulation(args.frame)

        # Export if requested
        if args.export:
            export_point_cloud(args)

        # Render single frame
        render_single_frame(args.frame)

    elif args.render:
        # Export if requested
        if args.export:
            export_point_cloud(args)

        # Render current frame
        render_single_frame()

    else:
        print("No render action specified.")
        print("Use --render for single frame, --animation for sequence, or --frame N for specific frame")
        print("Use --help for more options")

    print("=" * 60)
    print(f"Completed: {datetime.now().isoformat()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
