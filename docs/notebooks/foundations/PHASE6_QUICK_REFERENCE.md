# Phase 6 Quick Reference Guide

Quick reference for visualization and export functions added in Phase 6.

---

## Color Schemes

### Compute Colors
```python
colors = compute_color_values(cluster, mode='radial')
# modes: 'radial', 'order', 'height', 'branch_depth'
```

### Lichen Colorscale
```python
colorscale = get_lichen_colorscale()
# Natural green/grey gradient
```

---

## 3D Visualization

### PyVista (High Quality)
```python
visualize_volume_pyvista(
    cluster,
    particle_radius=1.0,
    color_mode='radial',
    title='My DLA Cluster',
    show=True
)
```

### Plotly (Fallback)
```python
visualize_volume_plotly(
    cluster,
    color_mode='radial',
    title='My DLA Cluster',
    point_size=3,
    opacity=0.8
)
```

---

## Mesh Generation

### Create Mesh
```python
mesh = create_lichen_mesh(
    cluster,
    particle_radius=1.0,    # Isosurface threshold
    resolution=64,          # Grid size (64³)
    smooth_iterations=50    # Smoothing passes
)
```

### Export for 3D Printing
```python
# Single format
export_printable_mesh(mesh, 'lichen.stl', format='stl')

# Multiple formats
for fmt in ['stl', 'obj', 'ply']:
    export_printable_mesh(mesh, f'lichen.{fmt}', format=fmt)
```

---

## Animation

### Create Growth Animation
```python
# 1. Collect snapshots during simulation
snapshots = []
for i in range(iterations):
    # ... simulation step ...
    if i % 10 == 0:
        snapshots.append(copy.deepcopy(cluster))

# 2. Generate animation
create_growth_animation(
    snapshots,
    output_file='growth.gif',  # or 'growth.mp4'
    fps=10,
    duration_per_frame=0.1
)
```

---

## Interactive Widgets

### Launch Widget
```python
create_interactive_dla_widget()
# Sliders for stickiness, bulk velocity, particle count
# Dropdown for color mode
# "Run Simulation" button
```

---

## Gallery

### Multi-Panel Comparison
```python
create_morphology_gallery(
    {
        'Usnea': cluster_usnea,
        'Cladonia': cluster_cladonia,
        'Ramalina': cluster_ramalina,
        'Crustose': cluster_crustose
    },
    color_mode='radial',
    title='Lichen Morphology Gallery'
)
```

---

## Complete Workflow Example

```python
# 1. Run simulation (from Phase 4)
params = DLAPhysicsParams(
    stickiness=0.5,
    bulk_velocity=np.array([0.0, 0.0, 0.4]),
    target_particle_count=10000
)
sim = OffGridDLASimulationHopping(...)
cluster = sim.run()

# 2. Visualize
if PYVISTA_AVAILABLE:
    visualize_volume_pyvista(cluster, color_mode='radial')
else:
    visualize_volume_plotly(cluster, color_mode='radial')

# 3. Generate mesh
mesh = create_lichen_mesh(cluster, resolution=80)

# 4. Export for 3D printing
export_printable_mesh(mesh, 'my_lichen.stl')

# 5. Create comparison gallery
create_morphology_gallery({
    'Test 1': cluster,
    # ... more clusters ...
})
```

---

## Dependency Check

```python
# Check what's available
print(f"PyVista:   {'✓' if PYVISTA_AVAILABLE else '✗'}")
print(f"imageio:   {'✓' if IMAGEIO_AVAILABLE else '✗'}")
print(f"ipywidgets: {'✓' if WIDGETS_AVAILABLE else '✗'}")
```

### Install Missing Dependencies
```bash
pip install pyvista imageio ipywidgets
jupyter nbextension enable --py widgetsnbextension
```

---

## Tips and Tricks

### High-Quality Mesh
```python
# Increase resolution and particle radius for smoother surfaces
mesh = create_lichen_mesh(
    cluster,
    particle_radius=1.5,  # Larger = smoother
    resolution=100,       # Higher = more detail
    smooth_iterations=100 # More = smoother
)
```

### Fast Preview
```python
# Low resolution for quick preview
mesh_preview = create_lichen_mesh(cluster, resolution=32, smooth_iterations=10)
```

### Color by Growth Order
```python
# Show temporal structure
visualize_volume_plotly(cluster, color_mode='order')
```

### Gallery with Custom Layout
```python
# Create custom figure with more control
fig = create_morphology_gallery(clusters_dict)
fig.update_layout(height=1200, width=1600)
fig.write_image('figure.png', width=3200, height=2400)  # High-res export
```

---

## Troubleshooting

### PyVista not showing plot
```python
# Try different backend
import pyvista as pv
pv.set_jupyter_backend('static')  # or 'ipyvtklink', 'panel'
```

### Widget not interactive
```bash
# Enable extension
jupyter nbextension enable --py widgetsnbextension
# Then restart kernel
```

### Mesh has holes
```python
# Increase fill_holes size
export_printable_mesh(mesh, 'lichen.stl', fill_holes=True)
# Or manually in mesh software (MeshLab, Blender)
```

### Animation too slow
```python
# Reduce particles or frames
create_growth_animation(
    snapshots[::2],  # Use every other frame
    fps=15           # Higher FPS = shorter video
)
```

---

## Performance Guidelines

| Task | Particles | Resolution | Time |
|------|-----------|-----------|------|
| Plotly viz | 50k | - | ~1s |
| PyVista viz | 50k | - | ~2s |
| Mesh gen | 10k | 64³ | ~3s |
| Mesh gen | 50k | 100³ | ~25s |
| STL export | - | - | <1s |
| Animation | 5k × 20 frames | - | ~30s |

---

## File Locations

**Notebook:** `/home/jovyan/fractal-notebooks/docs/notebooks/foundations/dla_cuda_offgrid.ipynb`

**Plan:** `/home/jovyan/fractal-notebooks/docs/notebooks/foundations/dla_cuda_plan.md`

**Summary:** `/home/jovyan/fractal-notebooks/docs/notebooks/foundations/PHASE6_IMPLEMENTATION_SUMMARY.md`

**This Guide:** `/home/jovyan/fractal-notebooks/docs/notebooks/foundations/PHASE6_QUICK_REFERENCE.md`

---

**Last Updated:** 2025-12-21
