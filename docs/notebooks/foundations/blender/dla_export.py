"""
DLA Point Cloud Export Script for Blender

This script exports the DLA point cloud from Blender to various formats
for use in external analysis and visualization tools.

Supported formats:
- NumPy (.npz) - For Python analysis with positions, timepoints, colors
- PLY (.ply) - Standard point cloud format with attributes
- OBJ (.obj) - Mesh format (creates vertices only)
- CSV (.csv) - Simple tabular format

Usage:
    1. Run the DLA simulation in Blender
    2. Open the Scripting workspace
    3. Run this script
    4. Choose export format and path

Author: Claude (fractal-notebooks project)
Created: 2025-12-21
"""

import bpy
import os
import struct
from datetime import datetime


def get_dla_object():
    """Find the DLA object in the scene."""
    # Try to find by name
    obj = bpy.data.objects.get("DLA_Seed")
    if obj:
        return obj

    # Fallback: find any object with geometry nodes modifier
    for obj in bpy.data.objects:
        for mod in obj.modifiers:
            if mod.type == 'NODES' and mod.node_group:
                if 'DLA' in mod.node_group.name:
                    return obj

    # Last resort: use active object
    return bpy.context.active_object


def get_evaluated_mesh(obj):
    """Get the evaluated mesh with all modifiers applied."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()
    return mesh, eval_obj


def export_to_numpy(obj, output_path):
    """
    Export DLA point cloud to NumPy .npz format.

    Includes:
    - positions: (N, 3) array of point coordinates
    - timepoints: (N,) array of timepoint values
    - colors: (N,) array of color seed values
    - active: (N,) boolean array of active state
    - bounds: (2, 3) array of min/max bounds
    - metadata: dictionary with frame info
    """
    try:
        import numpy as np
    except ImportError:
        print("ERROR: NumPy not available in Blender's Python environment")
        print("Install with: /path/to/blender/python -m pip install numpy")
        return False

    mesh, eval_obj = get_evaluated_mesh(obj)

    # Extract positions
    num_verts = len(mesh.vertices)
    positions = np.zeros((num_verts, 3), dtype=np.float32)
    for i, v in enumerate(mesh.vertices):
        positions[i] = v.co[:]

    # Initialize attribute arrays
    timepoints = np.zeros(num_verts, dtype=np.float32)
    colors = np.zeros(num_verts, dtype=np.float32)
    active = np.zeros(num_verts, dtype=bool)

    # Extract named attributes if available
    if 'timepoint' in mesh.attributes:
        attr = mesh.attributes['timepoint']
        if attr.data_type == 'FLOAT':
            for i, item in enumerate(attr.data):
                timepoints[i] = item.value

    if 'color_seed' in mesh.attributes:
        attr = mesh.attributes['color_seed']
        if attr.data_type == 'FLOAT':
            for i, item in enumerate(attr.data):
                colors[i] = item.value

    if 'active' in mesh.attributes:
        attr = mesh.attributes['active']
        if attr.data_type == 'BOOLEAN':
            for i, item in enumerate(attr.data):
                active[i] = item.value

    # Calculate bounds
    bounds = np.array([
        positions.min(axis=0),
        positions.max(axis=0)
    ])

    # Metadata
    scene = bpy.context.scene
    metadata = {
        'frame': scene.frame_current,
        'total_frames': scene.frame_end,
        'object_name': obj.name,
        'export_time': datetime.now().isoformat(),
        'blender_version': bpy.app.version_string,
    }

    # Save
    np.savez(output_path,
             positions=positions,
             timepoints=timepoints,
             colors=colors,
             active=active,
             bounds=bounds,
             **metadata)

    eval_obj.to_mesh_clear()

    print(f"Exported {num_verts} points to {output_path}")
    print(f"  Bounds: {bounds[0]} to {bounds[1]}")
    return True


def export_to_ply(obj, output_path, binary=True):
    """
    Export DLA point cloud to PLY format.

    Includes vertex positions and custom attributes as properties.
    """
    mesh, eval_obj = get_evaluated_mesh(obj)

    num_verts = len(mesh.vertices)

    # Collect data
    positions = []
    timepoints = []
    colors = []

    for v in mesh.vertices:
        positions.append(v.co[:])

    # Get attributes
    has_timepoint = 'timepoint' in mesh.attributes
    has_color = 'color_seed' in mesh.attributes

    if has_timepoint:
        for item in mesh.attributes['timepoint'].data:
            timepoints.append(item.value)
    else:
        timepoints = [0.0] * num_verts

    if has_color:
        for item in mesh.attributes['color_seed'].data:
            colors.append(item.value)
    else:
        colors = [0.0] * num_verts

    # Write PLY file
    with open(output_path, 'wb' if binary else 'w') as f:
        # Header
        header = f"""ply
format {'binary_little_endian' if binary else 'ascii'} 1.0
comment DLA Point Cloud exported from Blender
comment Frame: {bpy.context.scene.frame_current}
comment Export time: {datetime.now().isoformat()}
element vertex {num_verts}
property float x
property float y
property float z
property float timepoint
property float color_seed
end_header
"""
        if binary:
            f.write(header.encode('ascii'))
        else:
            f.write(header)

        # Data
        for i in range(num_verts):
            x, y, z = positions[i]
            t = timepoints[i]
            c = colors[i]

            if binary:
                f.write(struct.pack('<fffff', x, y, z, t, c))
            else:
                f.write(f"{x} {y} {z} {t} {c}\n")

    eval_obj.to_mesh_clear()

    print(f"Exported {num_verts} points to {output_path}")
    return True


def export_to_obj(obj, output_path):
    """
    Export DLA point cloud to OBJ format (vertices only).

    Note: OBJ doesn't support custom attributes, so only positions are exported.
    """
    mesh, eval_obj = get_evaluated_mesh(obj)

    with open(output_path, 'w') as f:
        f.write(f"# DLA Point Cloud\n")
        f.write(f"# Exported from Blender\n")
        f.write(f"# Frame: {bpy.context.scene.frame_current}\n")
        f.write(f"# Vertices: {len(mesh.vertices)}\n")
        f.write(f"# Export time: {datetime.now().isoformat()}\n\n")

        for v in mesh.vertices:
            f.write(f"v {v.co.x} {v.co.y} {v.co.z}\n")

    eval_obj.to_mesh_clear()

    print(f"Exported {len(mesh.vertices)} vertices to {output_path}")
    return True


def export_to_csv(obj, output_path):
    """
    Export DLA point cloud to CSV format.

    Includes all available attributes in tabular format.
    """
    mesh, eval_obj = get_evaluated_mesh(obj)

    num_verts = len(mesh.vertices)

    # Get attributes
    has_timepoint = 'timepoint' in mesh.attributes
    has_color = 'color_seed' in mesh.attributes
    has_active = 'active' in mesh.attributes

    with open(output_path, 'w') as f:
        # Header
        headers = ['x', 'y', 'z']
        if has_timepoint:
            headers.append('timepoint')
        if has_color:
            headers.append('color_seed')
        if has_active:
            headers.append('active')

        f.write(','.join(headers) + '\n')

        # Data
        for i, v in enumerate(mesh.vertices):
            row = [str(v.co.x), str(v.co.y), str(v.co.z)]

            if has_timepoint:
                row.append(str(mesh.attributes['timepoint'].data[i].value))
            if has_color:
                row.append(str(mesh.attributes['color_seed'].data[i].value))
            if has_active:
                row.append(str(int(mesh.attributes['active'].data[i].value)))

            f.write(','.join(row) + '\n')

    eval_obj.to_mesh_clear()

    print(f"Exported {num_verts} points to {output_path}")
    return True


def export_animation_sequence(obj, output_dir, format='npz', start_frame=None, end_frame=None):
    """
    Export the entire DLA animation as a sequence of files.

    Args:
        obj: The DLA object
        output_dir: Directory to save files
        format: 'npz', 'ply', 'obj', or 'csv'
        start_frame: Starting frame (default: scene start)
        end_frame: Ending frame (default: scene end)
    """
    scene = bpy.context.scene

    if start_frame is None:
        start_frame = scene.frame_start
    if end_frame is None:
        end_frame = scene.frame_end

    # Create output directory if needed
    os.makedirs(output_dir, exist_ok=True)

    # Export functions
    exporters = {
        'npz': export_to_numpy,
        'ply': export_to_ply,
        'obj': export_to_obj,
        'csv': export_to_csv,
    }

    if format not in exporters:
        print(f"Unknown format: {format}")
        return False

    export_func = exporters[format]
    original_frame = scene.frame_current

    print(f"Exporting frames {start_frame} to {end_frame}...")

    for frame in range(start_frame, end_frame + 1):
        scene.frame_set(frame)
        filename = f"dla_frame_{frame:04d}.{format}"
        filepath = os.path.join(output_dir, filename)
        export_func(obj, filepath)

    # Restore original frame
    scene.frame_set(original_frame)

    print(f"Animation export complete: {end_frame - start_frame + 1} frames")
    return True


def export_point_cloud_chunks(obj, output_dir, chunk_size=100000, format='npz'):
    """
    Export large point clouds in chunks to avoid memory issues.

    Useful for point clouds with millions of particles.
    """
    try:
        import numpy as np
    except ImportError:
        print("ERROR: NumPy required for chunked export")
        return False

    os.makedirs(output_dir, exist_ok=True)

    mesh, eval_obj = get_evaluated_mesh(obj)
    total_points = len(mesh.vertices)

    print(f"Exporting {total_points} points in chunks of {chunk_size}...")

    num_chunks = (total_points + chunk_size - 1) // chunk_size

    for chunk_idx in range(num_chunks):
        start = chunk_idx * chunk_size
        end = min(start + chunk_size, total_points)

        # Extract chunk data
        positions = np.array([mesh.vertices[i].co[:] for i in range(start, end)])

        timepoints = np.zeros(end - start)
        if 'timepoint' in mesh.attributes:
            for i, idx in enumerate(range(start, end)):
                timepoints[i] = mesh.attributes['timepoint'].data[idx].value

        filename = f"dla_chunk_{chunk_idx:04d}.{format}"
        filepath = os.path.join(output_dir, filename)

        np.savez(filepath,
                 positions=positions,
                 timepoints=timepoints,
                 chunk_index=chunk_idx,
                 total_chunks=num_chunks,
                 total_points=total_points)

        print(f"  Chunk {chunk_idx + 1}/{num_chunks}: {end - start} points")

    eval_obj.to_mesh_clear()

    print(f"Chunked export complete: {num_chunks} chunks")
    return True


# ============================================================
# Interactive Export UI
# ============================================================

class DLA_OT_ExportPointCloud(bpy.types.Operator):
    """Export DLA Point Cloud"""
    bl_idname = "dla.export_point_cloud"
    bl_label = "Export DLA Point Cloud"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(
        name="File Path",
        description="Path to save the export",
        default="//dla_export",
        subtype='FILE_PATH'
    )

    format: bpy.props.EnumProperty(
        name="Format",
        items=[
            ('NPZ', "NumPy (.npz)", "NumPy compressed archive"),
            ('PLY', "PLY (.ply)", "Polygon File Format"),
            ('OBJ', "OBJ (.obj)", "Wavefront OBJ"),
            ('CSV', "CSV (.csv)", "Comma-separated values"),
        ],
        default='NPZ'
    )

    def execute(self, context):
        obj = get_dla_object()
        if not obj:
            self.report({'ERROR'}, "No DLA object found")
            return {'CANCELLED'}

        # Ensure proper extension
        ext = self.format.lower()
        if not self.filepath.endswith(f'.{ext}'):
            self.filepath = f"{self.filepath}.{ext}"

        # Resolve relative paths
        filepath = bpy.path.abspath(self.filepath)

        # Export based on format
        if self.format == 'NPZ':
            success = export_to_numpy(obj, filepath)
        elif self.format == 'PLY':
            success = export_to_ply(obj, filepath)
        elif self.format == 'OBJ':
            success = export_to_obj(obj, filepath)
        elif self.format == 'CSV':
            success = export_to_csv(obj, filepath)
        else:
            success = False

        if success:
            self.report({'INFO'}, f"Exported to {filepath}")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Export failed")
            return {'CANCELLED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def register():
    """Register export operator."""
    bpy.utils.register_class(DLA_OT_ExportPointCloud)


def unregister():
    """Unregister export operator."""
    bpy.utils.unregister_class(DLA_OT_ExportPointCloud)


# ============================================================
# Quick Export Functions (for scripting)
# ============================================================

def quick_export(format='npz', output_path=None):
    """
    Quick export function for scripting.

    Args:
        format: 'npz', 'ply', 'obj', or 'csv'
        output_path: Output file path (default: /tmp/dla_export.<format>)

    Returns:
        True if successful, False otherwise
    """
    obj = get_dla_object()
    if not obj:
        print("ERROR: No DLA object found in scene")
        return False

    if output_path is None:
        output_path = f"/tmp/dla_export.{format}"

    exporters = {
        'npz': export_to_numpy,
        'ply': export_to_ply,
        'obj': export_to_obj,
        'csv': export_to_csv,
    }

    if format not in exporters:
        print(f"Unknown format: {format}")
        return False

    return exporters[format](obj, output_path)


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    # When run directly, do a quick export to /tmp
    print("=" * 60)
    print("DLA Point Cloud Export")
    print("=" * 60)

    obj = get_dla_object()
    if obj:
        print(f"Found DLA object: {obj.name}")

        # Export to all formats
        quick_export('npz', '/tmp/dla_export.npz')
        quick_export('ply', '/tmp/dla_export.ply')
        quick_export('csv', '/tmp/dla_export.csv')

        print("")
        print("Exports saved to /tmp/")
    else:
        print("No DLA object found. Run dla_blender_setup.py first.")

    print("=" * 60)
