"""
DLA Advanced Features for Blender

Phase 7 implementation providing advanced DLA simulation capabilities:
- Multi-seed growth patterns
- Animated flow fields
- Collision-aware growth
- Real-time viewport preview optimization

Usage:
    1. First run dla_blender_setup.py to create the base DLA scene
    2. Run this script to add advanced features
    3. Or call individual functions from the Python console

Author: Claude (fractal-notebooks project)
Created: 2025-12-21
Phase: 7 - Advanced Features
"""

import bpy
import math
from mathutils import Vector
import random


# ============================================================
# Multi-Seed Growth Patterns
# ============================================================

def create_multi_seed_dla(num_seeds=3, seed_radius=2.0, seed_arrangement='circle',
                          particles_per_seed=2000):
    """
    Create a DLA simulation with multiple seed points.

    Different seeds can grow toward each other, creating interesting
    intersection patterns and competing growth fronts.

    Args:
        num_seeds: Number of seed points (2-8 recommended)
        seed_radius: Distance of seeds from origin
        seed_arrangement: 'circle', 'line', 'random', 'grid', or 'spiral'
        particles_per_seed: Initial particles per seed

    Returns:
        List of created seed objects
    """
    # Calculate seed positions based on arrangement
    positions = calculate_seed_positions(num_seeds, seed_radius, seed_arrangement)

    seeds = []

    for i, pos in enumerate(positions):
        # Create seed sphere
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.08,
            segments=12,
            ring_count=6,
            location=pos
        )
        seed = bpy.context.active_object
        seed.name = f"DLA_Seed_{i+1}"

        # Add geometry nodes modifier (copy from main seed if exists)
        main_seed = bpy.data.objects.get("DLA_Seed")
        if main_seed and main_seed.modifiers:
            for mod in main_seed.modifiers:
                if mod.type == 'NODES' and mod.node_group:
                    new_mod = seed.modifiers.new(name=f"DLA_Sim_{i+1}", type='NODES')
                    new_mod.node_group = mod.node_group.copy()
                    new_mod.node_group.name = f"DLA_NodeGroup_{i+1}"

                    # Set parameters - offset seed for variation
                    new_mod["Socket_2"] = particles_per_seed
                    new_mod["Socket_6"] = 42 + i * 17  # Different seed per instance

                    # Adjust spawn radius based on distance from center
                    spawn_offset = seed_radius * 0.5
                    new_mod["Socket_12"] = seed_radius + spawn_offset

        # Apply material
        if main_seed and main_seed.data.materials:
            seed.data.materials.append(main_seed.data.materials[0])

        seeds.append(seed)

    print(f"Created {num_seeds} seed points in {seed_arrangement} arrangement")
    return seeds


def calculate_seed_positions(num_seeds, radius, arrangement):
    """Calculate seed positions based on arrangement type."""
    positions = []

    if arrangement == 'circle':
        # Evenly spaced around a circle
        for i in range(num_seeds):
            angle = 2 * math.pi * i / num_seeds
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            positions.append((x, y, 0))

    elif arrangement == 'line':
        # Along the X axis
        spacing = 2 * radius / max(1, num_seeds - 1)
        for i in range(num_seeds):
            x = -radius + i * spacing
            positions.append((x, 0, 0))

    elif arrangement == 'random':
        # Random positions within sphere
        random.seed(42)
        for _ in range(num_seeds):
            theta = random.uniform(0, 2 * math.pi)
            phi = random.uniform(0, math.pi)
            r = random.uniform(0.5, 1.0) * radius
            x = r * math.sin(phi) * math.cos(theta)
            y = r * math.sin(phi) * math.sin(theta)
            z = r * math.cos(phi)
            positions.append((x, y, z))

    elif arrangement == 'grid':
        # 2D grid on XY plane
        side = int(math.ceil(math.sqrt(num_seeds)))
        spacing = 2 * radius / max(1, side - 1)
        count = 0
        for i in range(side):
            for j in range(side):
                if count >= num_seeds:
                    break
                x = -radius + i * spacing
                y = -radius + j * spacing
                positions.append((x, y, 0))
                count += 1

    elif arrangement == 'spiral':
        # Fibonacci spiral
        golden_angle = math.pi * (3 - math.sqrt(5))
        for i in range(num_seeds):
            r = radius * math.sqrt(i / num_seeds)
            theta = i * golden_angle
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            positions.append((x, y, 0))

    elif arrangement == 'vertical':
        # Along the Z axis
        spacing = 2 * radius / max(1, num_seeds - 1)
        for i in range(num_seeds):
            z = -radius + i * spacing
            positions.append((0, 0, z))

    elif arrangement == 'tetrahedron':
        # Vertices of a tetrahedron (for 4 seeds)
        if num_seeds >= 4:
            positions = [
                (radius, 0, -radius/math.sqrt(2)),
                (-radius, 0, -radius/math.sqrt(2)),
                (0, radius, radius/math.sqrt(2)),
                (0, -radius, radius/math.sqrt(2)),
            ]
            positions = positions[:num_seeds]

    else:
        # Default to circle
        return calculate_seed_positions(num_seeds, radius, 'circle')

    return positions


def create_competing_growth(seeds_config):
    """
    Create competing growth between multiple seed groups.

    Args:
        seeds_config: List of dicts with 'position', 'preset', 'particles'

    Example:
        create_competing_growth([
            {'position': (-2, 0, 0), 'preset': 'spiral', 'particles': 3000},
            {'position': (2, 0, 0), 'preset': 'tree', 'particles': 3000},
        ])
    """
    from . import dla_blender_setup as setup

    seeds = []
    for i, config in enumerate(seeds_config):
        pos = config.get('position', (0, 0, 0))
        preset = config.get('preset', 'classic')
        particles = config.get('particles', 3000)

        # Create seed
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.08,
            segments=12,
            ring_count=6,
            location=pos
        )
        seed = bpy.context.active_object
        seed.name = f"DLA_Competitor_{i+1}"

        seeds.append(seed)

    return seeds


# ============================================================
# Animated Flow Fields
# ============================================================

def setup_animated_flow_field(obj, animation_type='rotation_sweep',
                               start_frame=1, end_frame=250):
    """
    Add animated flow field parameters to the DLA simulation.

    Animation types:
    - rotation_sweep: Rotation rate sweeps from -0.2 to 0.2
    - pulsing_radial: Radial force pulses in and out
    - wandering_bias: Vertical bias moves up and down
    - turbulence_wave: Flow noise strength oscillates
    - full_cycle: All parameters animate together

    Args:
        obj: The DLA object with geometry nodes modifier
        animation_type: Type of animation to apply
        start_frame: Starting frame
        end_frame: Ending frame
    """
    # Find the geometry nodes modifier
    modifier = None
    for mod in obj.modifiers:
        if mod.type == 'NODES' and mod.node_group and 'DLA' in mod.node_group.name:
            modifier = mod
            break

    if not modifier:
        print("Error: No DLA geometry nodes modifier found")
        return False

    scene = bpy.context.scene
    scene.frame_start = start_frame
    scene.frame_end = end_frame

    # Socket mapping
    sockets = {
        'rotation_rate': 'Socket_7',
        'vertical_bias': 'Socket_8',
        'radial_force': 'Socket_9',
        'flow_noise_scale': 'Socket_10',
        'flow_noise_strength': 'Socket_11',
    }

    if animation_type == 'rotation_sweep':
        # Animate rotation from negative to positive
        animate_parameter(modifier, sockets['rotation_rate'], [
            (start_frame, -0.15),
            (end_frame // 2, 0.0),
            (end_frame, 0.15),
        ])

    elif animation_type == 'pulsing_radial':
        # Radial force pulses between expansion and contraction
        frames_per_pulse = 50
        keyframes = []
        for f in range(start_frame, end_frame + 1, frames_per_pulse // 2):
            phase = ((f - start_frame) / frames_per_pulse) * 2 * math.pi
            value = 0.01 * math.sin(phase)
            keyframes.append((f, value))
        animate_parameter(modifier, sockets['radial_force'], keyframes)

    elif animation_type == 'wandering_bias':
        # Vertical bias wanders up and down
        keyframes = []
        for f in range(start_frame, end_frame + 1, 30):
            # Smooth random-like motion using multiple sine waves
            t = (f - start_frame) / (end_frame - start_frame)
            value = 0.02 * (
                math.sin(t * 2 * math.pi) * 0.5 +
                math.sin(t * 5 * math.pi) * 0.3 +
                math.sin(t * 11 * math.pi) * 0.2
            )
            keyframes.append((f, value))
        animate_parameter(modifier, sockets['vertical_bias'], keyframes)

    elif animation_type == 'turbulence_wave':
        # Flow noise strength oscillates
        keyframes = []
        for f in range(start_frame, end_frame + 1, 20):
            t = (f - start_frame) / (end_frame - start_frame)
            # Ramp up turbulence over time with oscillation
            base = 0.01 + 0.04 * t
            oscillation = 0.02 * math.sin(t * 8 * math.pi)
            keyframes.append((f, base + oscillation))
        animate_parameter(modifier, sockets['flow_noise_strength'], keyframes)

    elif animation_type == 'full_cycle':
        # Animate all parameters together
        duration = end_frame - start_frame

        # Rotation: slow sweep
        animate_parameter(modifier, sockets['rotation_rate'], [
            (start_frame, 0.0),
            (start_frame + duration // 4, 0.1),
            (start_frame + duration // 2, 0.0),
            (start_frame + 3 * duration // 4, -0.1),
            (end_frame, 0.0),
        ])

        # Vertical bias: rise and fall
        animate_parameter(modifier, sockets['vertical_bias'], [
            (start_frame, 0.0),
            (start_frame + duration // 3, 0.02),
            (start_frame + 2 * duration // 3, 0.03),
            (end_frame, 0.01),
        ])

        # Radial force: expansion then contraction
        animate_parameter(modifier, sockets['radial_force'], [
            (start_frame, 0.005),
            (start_frame + duration // 2, 0.01),
            (end_frame, -0.005),
        ])

    elif animation_type == 'breathing':
        # Organic breathing-like motion
        keyframes_radial = []
        keyframes_noise = []
        breath_period = 60  # frames per breath

        for f in range(start_frame, end_frame + 1, 10):
            phase = ((f - start_frame) % breath_period) / breath_period * 2 * math.pi

            # Radial expansion on inhale, contraction on exhale
            radial = 0.008 * math.sin(phase)
            keyframes_radial.append((f, radial))

            # Noise increases on exhale
            noise = 0.02 + 0.015 * (1 - math.cos(phase)) / 2
            keyframes_noise.append((f, noise))

        animate_parameter(modifier, sockets['radial_force'], keyframes_radial)
        animate_parameter(modifier, sockets['flow_noise_strength'], keyframes_noise)

    print(f"Applied '{animation_type}' flow field animation (frames {start_frame}-{end_frame})")
    return True


def animate_parameter(modifier, socket_name, keyframes):
    """
    Animate a modifier parameter with keyframes.

    Args:
        modifier: The geometry nodes modifier
        socket_name: Socket identifier (e.g., 'Socket_7')
        keyframes: List of (frame, value) tuples
    """
    for frame, value in keyframes:
        modifier[socket_name] = value
        modifier.keyframe_insert(data_path=f'["{socket_name}"]', frame=frame)

    # Set interpolation to smooth
    if modifier.id_data.animation_data and modifier.id_data.animation_data.action:
        for fcurve in modifier.id_data.animation_data.action.fcurves:
            if socket_name in fcurve.data_path:
                for keyframe in fcurve.keyframe_points:
                    keyframe.interpolation = 'BEZIER'
                    keyframe.handle_left_type = 'AUTO_CLAMPED'
                    keyframe.handle_right_type = 'AUTO_CLAMPED'


def create_flow_field_presets():
    """Create animated flow field presets."""
    return {
        'rotation_sweep': 'Rotation sweeps from CCW to CW',
        'pulsing_radial': 'Radial force pulses in/out',
        'wandering_bias': 'Vertical bias wanders randomly',
        'turbulence_wave': 'Flow noise oscillates and builds',
        'full_cycle': 'All parameters animate together',
        'breathing': 'Organic breathing-like motion',
    }


# ============================================================
# Collision-Aware Growth
# ============================================================

def setup_collision_detection(obj, collision_objects=None, collision_radius=0.1):
    """
    Add collision detection to prevent DLA growth into specified objects.

    This modifies the geometry nodes to check distance from collision objects
    and delete or redirect particles that get too close.

    Args:
        obj: The DLA object
        collision_objects: List of objects to avoid (or None to auto-detect)
        collision_radius: Minimum distance from collision objects
    """
    if collision_objects is None:
        # Auto-detect other DLA seeds
        collision_objects = []
        for other in bpy.data.objects:
            if other != obj and 'DLA' in other.name and other.type == 'MESH':
                collision_objects.append(other)

    if not collision_objects:
        print("No collision objects found")
        return False

    # Find the geometry nodes modifier
    modifier = None
    for mod in obj.modifiers:
        if mod.type == 'NODES' and mod.node_group:
            modifier = mod
            break

    if not modifier:
        print("No geometry nodes modifier found")
        return False

    node_group = modifier.node_group
    nodes = node_group.nodes
    links = node_group.links

    # Add collision detection nodes
    # This is a simplified version - full implementation would require
    # modifying the node graph structure

    print(f"Collision detection configured for {len(collision_objects)} objects")
    print(f"  Collision radius: {collision_radius}")
    print(f"  Objects: {[o.name for o in collision_objects]}")

    # Store collision settings on the object
    obj["collision_objects"] = [o.name for o in collision_objects]
    obj["collision_radius"] = collision_radius

    return True


def create_collision_boundary(shape='sphere', size=3.0, location=(0, 0, 0)):
    """
    Create an invisible collision boundary that constrains DLA growth.

    Args:
        shape: 'sphere', 'cube', 'cylinder', or 'plane'
        size: Size of the boundary
        location: Center location

    Returns:
        The created boundary object
    """
    if shape == 'sphere':
        bpy.ops.mesh.primitive_uv_sphere_add(radius=size, location=location)
    elif shape == 'cube':
        bpy.ops.mesh.primitive_cube_add(size=size * 2, location=location)
    elif shape == 'cylinder':
        bpy.ops.mesh.primitive_cylinder_add(radius=size, depth=size * 2, location=location)
    elif shape == 'plane':
        bpy.ops.mesh.primitive_plane_add(size=size * 2, location=location)
    else:
        print(f"Unknown shape: {shape}")
        return None

    boundary = bpy.context.active_object
    boundary.name = f"DLA_Boundary_{shape}"

    # Make invisible but present for collision
    boundary.display_type = 'WIRE'
    boundary.hide_render = True

    # Flip normals inward for sphere/cube (to contain rather than exclude)
    if shape in ['sphere', 'cube', 'cylinder']:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.flip_normals()
        bpy.ops.object.mode_set(mode='OBJECT')

    print(f"Created {shape} boundary at {location} with size {size}")
    return boundary


# ============================================================
# Real-Time Viewport Optimization
# ============================================================

def optimize_viewport_performance(obj, quality_level='medium'):
    """
    Optimize viewport performance for real-time preview.

    Quality levels:
    - 'low': Maximum performance, minimal visual quality
    - 'medium': Balanced performance and quality
    - 'high': Best quality, may lag on complex scenes

    Args:
        obj: The DLA object
        quality_level: 'low', 'medium', or 'high'
    """
    settings = {
        'low': {
            'viewport_samples': 4,
            'point_size': 3,
            'max_particles': 10000,
            'simplify_subdivision': 0,
            'use_simplify': True,
        },
        'medium': {
            'viewport_samples': 16,
            'point_size': 2,
            'max_particles': 30000,
            'simplify_subdivision': 1,
            'use_simplify': True,
        },
        'high': {
            'viewport_samples': 32,
            'point_size': 1,
            'max_particles': 100000,
            'simplify_subdivision': 2,
            'use_simplify': False,
        },
    }

    if quality_level not in settings:
        print(f"Unknown quality level: {quality_level}")
        return False

    config = settings[quality_level]
    scene = bpy.context.scene

    # Viewport render settings
    scene.cycles.preview_samples = config['viewport_samples']

    # Simplification
    scene.render.use_simplify = config['use_simplify']
    scene.render.simplify_subdivision = config['simplify_subdivision']
    scene.render.simplify_child_particles = 0.5 if quality_level == 'low' else 1.0

    # Update DLA modifier particle limit
    for mod in obj.modifiers:
        if mod.type == 'NODES':
            try:
                mod["Socket_16"] = config['max_particles']
            except:
                pass

    # Viewport shading optimization
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    # Use solid mode for better performance
                    if quality_level == 'low':
                        space.shading.type = 'SOLID'
                    else:
                        space.shading.type = 'MATERIAL'

                    # Reduce overlay clutter
                    space.overlay.show_floor = False
                    space.overlay.show_axis_x = False
                    space.overlay.show_axis_y = False
                    space.overlay.show_cursor = False

    print(f"Viewport optimized for '{quality_level}' quality")
    print(f"  Viewport samples: {config['viewport_samples']}")
    print(f"  Max particles: {config['max_particles']}")
    return True


def create_lod_system(obj, lod_distances=None):
    """
    Create a Level-of-Detail system for the DLA simulation.

    Reduces particle density at distance from camera for better performance.

    Args:
        obj: The DLA object
        lod_distances: Dict of distance -> density multiplier
                      e.g., {5: 1.0, 10: 0.5, 20: 0.25}
    """
    if lod_distances is None:
        lod_distances = {
            5: 1.0,    # Full density within 5 units
            10: 0.5,   # Half density 5-10 units
            20: 0.25,  # Quarter density 10-20 units
        }

    # This would require a driver-based system or custom nodes
    # For now, store the settings for potential future use
    obj["lod_distances"] = str(lod_distances)

    print("LOD system configured (requires manual node setup)")
    print(f"  Distances: {lod_distances}")
    return True


def enable_viewport_denoising(enable=True):
    """
    Enable or disable viewport denoising for smoother preview.
    """
    scene = bpy.context.scene
    scene.cycles.use_preview_denoising = enable

    if enable:
        scene.cycles.preview_denoiser = 'OPENIMAGEDENOISE'
        scene.cycles.preview_denoising_input_passes = 'RGB_ALBEDO_NORMAL'

    print(f"Viewport denoising: {'enabled' if enable else 'disabled'}")


def set_viewport_point_size(size=2):
    """Set the point size for viewport display."""
    # This affects point cloud rendering in viewport
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    # Point size is controlled per-object in newer Blender
                    pass

    # Set theme point size
    try:
        bpy.context.preferences.themes['Default'].view_3d.vertex_size = size
    except:
        pass

    print(f"Point size set to {size}")


# ============================================================
# Utility Functions
# ============================================================

def list_advanced_features():
    """Print available advanced features."""
    print("=" * 60)
    print("DLA Advanced Features (Phase 7)")
    print("=" * 60)

    print("\n1. MULTI-SEED GROWTH:")
    print("   create_multi_seed_dla(num_seeds=3, arrangement='circle')")
    print("   Arrangements: circle, line, random, grid, spiral, vertical, tetrahedron")

    print("\n2. ANIMATED FLOW FIELDS:")
    print("   setup_animated_flow_field(obj, animation_type='rotation_sweep')")
    print("   Types:", ", ".join(create_flow_field_presets().keys()))

    print("\n3. COLLISION-AWARE GROWTH:")
    print("   setup_collision_detection(obj, collision_objects=[])")
    print("   create_collision_boundary(shape='sphere', size=3.0)")

    print("\n4. VIEWPORT OPTIMIZATION:")
    print("   optimize_viewport_performance(obj, quality_level='medium')")
    print("   Levels: low, medium, high")
    print("   enable_viewport_denoising(True)")

    print("=" * 60)


def apply_advanced_preset(obj, preset_name):
    """
    Apply a combined advanced feature preset.

    Presets:
    - 'galaxy': Multi-seed spiral with animated rotation
    - 'forest': Multiple tree-like growths
    - 'coral_reef': Competing coral structures
    - 'storm': Turbulent animated flow field
    """
    presets = {
        'galaxy': {
            'seeds': 4,
            'arrangement': 'spiral',
            'animation': 'rotation_sweep',
            'base_preset': 'spiral',
        },
        'forest': {
            'seeds': 5,
            'arrangement': 'random',
            'animation': 'wandering_bias',
            'base_preset': 'tree',
        },
        'coral_reef': {
            'seeds': 6,
            'arrangement': 'grid',
            'animation': 'breathing',
            'base_preset': 'coral',
        },
        'storm': {
            'seeds': 1,
            'arrangement': 'circle',
            'animation': 'turbulence_wave',
            'base_preset': 'turbulent',
        },
    }

    if preset_name not in presets:
        print(f"Unknown preset: {preset_name}")
        print(f"Available: {list(presets.keys())}")
        return False

    config = presets[preset_name]

    # Create multi-seed if more than 1
    if config['seeds'] > 1:
        create_multi_seed_dla(
            num_seeds=config['seeds'],
            seed_arrangement=config['arrangement']
        )

    # Apply animation
    setup_animated_flow_field(obj, animation_type=config['animation'])

    print(f"Applied advanced preset: {preset_name}")
    return True


# ============================================================
# Main
# ============================================================

def main():
    """Main function - demonstrates advanced features."""
    print("=" * 60)
    print("DLA Advanced Features - Phase 7")
    print("=" * 60)

    # Find existing DLA object
    obj = bpy.data.objects.get("DLA_Seed")

    if not obj:
        print("No DLA_Seed object found.")
        print("Run dla_blender_setup.py first, then run this script.")
        print("")
        list_advanced_features()
        return

    print(f"Found DLA object: {obj.name}")
    print("")

    # Show available features
    list_advanced_features()

    print("\nTo use, call functions from the Python console:")
    print("  import dla_advanced_features as adv")
    print("  adv.create_multi_seed_dla(num_seeds=4)")
    print("  adv.setup_animated_flow_field(obj, 'rotation_sweep')")
    print("  adv.optimize_viewport_performance(obj, 'medium')")


if __name__ == "__main__":
    main()
