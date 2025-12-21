"""
DLA Example Renders Generator

This script generates a set of example renders showcasing different DLA presets
and configurations. Useful for documentation, gallery creation, and testing.

Usage:
    # Generate all examples (from scratch)
    blender -b -P dla_blender_setup.py -P dla_example_renders.py -- --all

    # Generate specific preset examples
    blender -b -P dla_blender_setup.py -P dla_example_renders.py -- --presets spiral tree coral

    # Generate turntable animation
    blender -b -P dla_blender_setup.py -P dla_example_renders.py -- --turntable

    # Generate growth animation
    blender -b -P dla_blender_setup.py -P dla_example_renders.py -- --growth

    # Custom output directory
    blender -b -P dla_blender_setup.py -P dla_example_renders.py -- --all --output /path/to/gallery

Author: Claude (fractal-notebooks project)
Created: 2025-12-21
Phase: 6 - Export & Integration
"""

import bpy
import sys
import os
import math
import argparse
from datetime import datetime


def parse_args():
    """Parse command line arguments after '--' separator."""
    if '--' in sys.argv:
        argv = sys.argv[sys.argv.index('--') + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser(description='DLA Example Renders Generator')

    # Output options
    parser.add_argument('--output', '-o', type=str, default='/tmp/dla_gallery',
                        help='Output directory for renders')

    # Render modes
    parser.add_argument('--all', action='store_true',
                        help='Generate all examples (presets + animations)')
    parser.add_argument('--presets', nargs='*', default=None,
                        help='Generate specific preset examples')
    parser.add_argument('--turntable', action='store_true',
                        help='Generate 360° turntable animation')
    parser.add_argument('--growth', action='store_true',
                        help='Generate growth progression animation')
    parser.add_argument('--thumbnails', action='store_true',
                        help='Generate thumbnail gallery')
    parser.add_argument('--poster', action='store_true',
                        help='Generate high-resolution poster render')

    # Quality settings
    parser.add_argument('--samples', type=int, default=128,
                        help='Render samples (default: 128)')
    parser.add_argument('--resolution', type=str, default='1920x1080',
                        help='Resolution WxH (default: 1920x1080)')
    parser.add_argument('--thumbnail-size', type=int, default=512,
                        help='Thumbnail resolution (default: 512)')
    parser.add_argument('--poster-resolution', type=str, default='4096x4096',
                        help='Poster resolution (default: 4096x4096)')

    # Simulation settings
    parser.add_argument('--frames', type=int, default=150,
                        help='Simulation frames per preset (default: 150)')
    parser.add_argument('--turntable-frames', type=int, default=120,
                        help='Turntable animation frames (default: 120)')

    # Debug
    parser.add_argument('--dry-run', action='store_true',
                        help='Print actions without rendering')

    return parser.parse_args(argv)


def setup_render(width, height, samples):
    """Configure render settings."""
    scene = bpy.context.scene
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'

    # Try GPU
    prefs = bpy.context.preferences.addons.get('cycles')
    if prefs:
        prefs = prefs.preferences
        for compute_type in ['OPTIX', 'CUDA', 'HIP', 'METAL']:
            try:
                prefs.compute_device_type = compute_type
                for device in prefs.devices:
                    device.use = True
                scene.cycles.device = 'GPU'
                break
            except:
                continue


def get_dla_object():
    """Find the DLA object."""
    obj = bpy.data.objects.get("DLA_Seed")
    if not obj:
        for obj in bpy.data.objects:
            if obj.modifiers:
                for mod in obj.modifiers:
                    if mod.type == 'NODES' and 'DLA' in str(mod.node_group.name):
                        return obj
    return obj


def apply_preset(obj, preset_name):
    """Apply a DLA preset to the object."""
    presets = {
        'classic': {
            'Socket_3': 0.02, 'Socket_5': 2.0, 'Socket_7': 0.0,
            'Socket_8': 0.0, 'Socket_9': 0.0, 'Socket_10': 0.5,
            'Socket_11': 0.0, 'Socket_14': 0.005, 'Socket_15': 0.0,
        },
        'spiral': {
            'Socket_3': 0.015, 'Socket_5': 3.0, 'Socket_7': 0.1,
            'Socket_8': 0.005, 'Socket_9': 0.003, 'Socket_10': 0.8,
            'Socket_11': 0.02, 'Socket_14': 0.01, 'Socket_15': 0.005,
        },
        'tree': {
            'Socket_3': 0.02, 'Socket_5': 2.5, 'Socket_7': 0.02,
            'Socket_8': 0.025, 'Socket_9': -0.005, 'Socket_10': 1.0,
            'Socket_11': 0.015, 'Socket_14': 0.008, 'Socket_15': 0.01,
        },
        'coral': {
            'Socket_3': 0.018, 'Socket_5': 4.0, 'Socket_7': 0.0,
            'Socket_8': 0.01, 'Socket_9': 0.008, 'Socket_10': 0.6,
            'Socket_11': 0.025, 'Socket_14': 0.005, 'Socket_15': 0.008,
        },
        'vortex': {
            'Socket_3': 0.01, 'Socket_5': 1.5, 'Socket_7': 0.2,
            'Socket_8': 0.0, 'Socket_9': -0.01, 'Socket_10': 0.3,
            'Socket_11': 0.01, 'Socket_14': 0.015, 'Socket_15': 0.002,
        },
        'turbulent': {
            'Socket_3': 0.025, 'Socket_5': 5.0, 'Socket_7': 0.05,
            'Socket_8': 0.0, 'Socket_9': 0.0, 'Socket_10': 2.0,
            'Socket_11': 0.05, 'Socket_14': 0.02, 'Socket_15': 0.01,
        },
        'dense': {
            'Socket_3': 0.015, 'Socket_5': 2.0, 'Socket_7': 0.0,
            'Socket_8': 0.0, 'Socket_9': 0.0, 'Socket_10': 0.5,
            'Socket_11': 0.01, 'Socket_14': 0.002, 'Socket_15': 0.02,
        },
        'sparse': {
            'Socket_3': 0.03, 'Socket_5': 3.0, 'Socket_7': 0.0,
            'Socket_8': 0.0, 'Socket_9': 0.0, 'Socket_10': 1.0,
            'Socket_11': 0.02, 'Socket_14': 0.03, 'Socket_15': 0.0,
        },
    }

    if preset_name not in presets:
        print(f"Unknown preset: {preset_name}")
        return False

    for mod in obj.modifiers:
        if mod.type == 'NODES':
            for socket, value in presets[preset_name].items():
                try:
                    mod[socket] = value
                except:
                    pass
            return True

    return False


def reset_simulation():
    """Reset simulation to frame 1."""
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()


def bake_to_frame(frame):
    """Bake simulation to a specific frame."""
    for f in range(1, frame + 1):
        bpy.context.scene.frame_set(f)
    bpy.context.view_layer.update()


def render_frame(output_path, dry_run=False):
    """Render current frame to file."""
    bpy.context.scene.render.filepath = output_path
    if dry_run:
        print(f"  [DRY RUN] Would render to: {output_path}")
    else:
        bpy.ops.render.render(write_still=True)
        print(f"  Rendered: {output_path}")


def generate_preset_renders(args, presets=None):
    """Generate example renders for each preset."""
    output_dir = os.path.join(args.output, 'presets')
    os.makedirs(output_dir, exist_ok=True)

    width, height = map(int, args.resolution.split('x'))
    setup_render(width, height, args.samples)

    obj = get_dla_object()
    if not obj:
        print("Error: No DLA object found")
        return

    all_presets = ['classic', 'spiral', 'tree', 'coral', 'vortex', 'turbulent', 'dense', 'sparse']

    if presets is None:
        presets = all_presets
    else:
        presets = [p for p in presets if p in all_presets]

    print(f"\nGenerating preset renders...")
    print(f"  Output: {output_dir}")
    print(f"  Presets: {', '.join(presets)}")
    print(f"  Frames per preset: {args.frames}")

    for preset_name in presets:
        print(f"\n  [{preset_name}]")

        # Reset and apply preset
        reset_simulation()
        apply_preset(obj, preset_name)

        # Bake simulation
        print(f"    Baking {args.frames} frames...")
        if not args.dry_run:
            bake_to_frame(args.frames)

        # Render
        output_path = os.path.join(output_dir, f"{preset_name}.png")
        render_frame(output_path, args.dry_run)

    print(f"\nPreset renders complete: {len(presets)} images")


def generate_thumbnails(args):
    """Generate thumbnail gallery of all presets."""
    output_dir = os.path.join(args.output, 'thumbnails')
    os.makedirs(output_dir, exist_ok=True)

    size = args.thumbnail_size
    setup_render(size, size, max(32, args.samples // 4))  # Lower samples for thumbnails

    obj = get_dla_object()
    if not obj:
        print("Error: No DLA object found")
        return

    presets = ['classic', 'spiral', 'tree', 'coral', 'vortex', 'turbulent', 'dense', 'sparse']

    print(f"\nGenerating thumbnails...")
    print(f"  Size: {size}x{size}")

    for preset_name in presets:
        reset_simulation()
        apply_preset(obj, preset_name)

        if not args.dry_run:
            bake_to_frame(100)  # Quick bake for thumbnails

        output_path = os.path.join(output_dir, f"thumb_{preset_name}.png")
        render_frame(output_path, args.dry_run)

    print(f"\nThumbnails complete: {len(presets)} images")


def generate_turntable(args):
    """Generate 360° turntable animation."""
    output_dir = os.path.join(args.output, 'turntable')
    os.makedirs(output_dir, exist_ok=True)

    width, height = map(int, args.resolution.split('x'))
    setup_render(width, height, args.samples)

    obj = get_dla_object()
    camera = bpy.data.objects.get("DLA_Camera")

    if not obj or not camera:
        print("Error: DLA object or camera not found")
        return

    print(f"\nGenerating turntable animation...")
    print(f"  Frames: {args.turntable_frames}")
    print(f"  Output: {output_dir}")

    # First, bake the simulation to a nice point
    reset_simulation()
    apply_preset(obj, 'spiral')

    print("  Baking simulation...")
    if not args.dry_run:
        bake_to_frame(150)

    # Freeze simulation at this frame
    bpy.context.scene.frame_end = 150
    bpy.context.scene.frame_set(150)

    # Create empty at origin for camera to orbit
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    pivot = bpy.context.active_object
    pivot.name = "Camera_Pivot"

    # Parent camera to pivot
    camera.parent = pivot

    # Animate pivot rotation
    pivot.rotation_euler = (0, 0, 0)
    pivot.keyframe_insert(data_path="rotation_euler", frame=1)

    pivot.rotation_euler = (0, 0, math.radians(360))
    pivot.keyframe_insert(data_path="rotation_euler", frame=args.turntable_frames)

    # Set animation range
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = args.turntable_frames

    # Render animation
    scene.render.filepath = os.path.join(output_dir, "turntable_")

    if args.dry_run:
        print(f"  [DRY RUN] Would render {args.turntable_frames} frames to: {output_dir}")
    else:
        bpy.ops.render.render(animation=True)

    # Clean up pivot
    bpy.data.objects.remove(pivot)

    print(f"\nTurntable animation complete")


def generate_growth_animation(args):
    """Generate growth progression animation."""
    output_dir = os.path.join(args.output, 'growth')
    os.makedirs(output_dir, exist_ok=True)

    width, height = map(int, args.resolution.split('x'))
    setup_render(width, height, args.samples)

    obj = get_dla_object()
    if not obj:
        print("Error: No DLA object found")
        return

    print(f"\nGenerating growth animation...")
    print(f"  Frames: {args.frames}")
    print(f"  Output: {output_dir}")

    # Reset and use spiral preset
    reset_simulation()
    apply_preset(obj, 'spiral')

    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = args.frames
    scene.render.filepath = os.path.join(output_dir, "growth_")

    if args.dry_run:
        print(f"  [DRY RUN] Would render {args.frames} frames to: {output_dir}")
    else:
        bpy.ops.render.render(animation=True)

    print(f"\nGrowth animation complete")


def generate_poster(args):
    """Generate high-resolution poster render."""
    output_dir = os.path.join(args.output, 'poster')
    os.makedirs(output_dir, exist_ok=True)

    width, height = map(int, args.poster_resolution.split('x'))
    samples = args.samples * 4  # Higher samples for poster
    setup_render(width, height, samples)

    obj = get_dla_object()
    if not obj:
        print("Error: No DLA object found")
        return

    print(f"\nGenerating poster render...")
    print(f"  Resolution: {width}x{height}")
    print(f"  Samples: {samples}")

    # Use the most visually interesting preset
    reset_simulation()
    apply_preset(obj, 'spiral')

    print("  Baking simulation (200 frames)...")
    if not args.dry_run:
        bake_to_frame(200)

    output_path = os.path.join(output_dir, "dla_poster.png")
    render_frame(output_path, args.dry_run)

    print(f"\nPoster render complete")


def generate_all(args):
    """Generate all example outputs."""
    print("=" * 60)
    print("DLA Gallery Generator")
    print("=" * 60)
    print(f"Output directory: {args.output}")
    print(f"Started: {datetime.now().isoformat()}")

    # Create output directory
    os.makedirs(args.output, exist_ok=True)

    # Generate all outputs
    generate_preset_renders(args)
    generate_thumbnails(args)
    generate_turntable(args)
    generate_growth_animation(args)
    generate_poster(args)

    print("\n" + "=" * 60)
    print("Gallery generation complete!")
    print(f"Output: {args.output}")
    print("=" * 60)


def main():
    """Main entry point."""
    args = parse_args()

    if args.all:
        generate_all(args)
    else:
        # Generate specific items
        if args.presets is not None:
            if len(args.presets) == 0:
                # --presets with no arguments means all presets
                generate_preset_renders(args)
            else:
                generate_preset_renders(args, args.presets)

        if args.thumbnails:
            generate_thumbnails(args)

        if args.turntable:
            generate_turntable(args)

        if args.growth:
            generate_growth_animation(args)

        if args.poster:
            generate_poster(args)

        # If nothing specified, show help
        if not any([args.presets is not None, args.thumbnails, args.turntable,
                    args.growth, args.poster]):
            print("DLA Example Renders Generator")
            print("=" * 40)
            print("Use --all to generate all examples, or specify individual options:")
            print("  --presets [names]  Generate preset renders")
            print("  --thumbnails       Generate thumbnail gallery")
            print("  --turntable        Generate turntable animation")
            print("  --growth           Generate growth animation")
            print("  --poster           Generate high-res poster")
            print("")
            print("Example:")
            print("  blender -b -P dla_blender_setup.py -P dla_example_renders.py -- --all")


if __name__ == "__main__":
    main()
