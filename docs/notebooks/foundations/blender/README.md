# Blender DLA Point Cloud Tools

3D Diffusion-Limited Aggregation (DLA) simulation using Blender's Geometry Nodes and Cycles rendering.

## Files

| File | Description |
|------|-------------|
| `dla_blender_setup.py` | Main setup script - creates DLA geometry nodes simulation |
| `dla_export.py` | Export point clouds to NumPy, PLY, OBJ, CSV formats |
| `dla_batch_render.py` | Headless batch rendering for automation |
| `dla_visualization.ipynb` | Jupyter notebook for analysis and visualization |

## Quick Start

### 1. Interactive Setup (Blender GUI)

```bash
# Open Blender
blender

# In Blender:
# 1. Go to Scripting workspace
# 2. Open dla_blender_setup.py
# 3. Run the script (Alt+P)
# 4. Press Space to play animation
```

### 2. Headless Rendering

```bash
# Render single frame
blender -b -P dla_blender_setup.py -P dla_batch_render.py -- --frame 100 --output /tmp/dla.png

# Render animation
blender -b -P dla_blender_setup.py -P dla_batch_render.py -- \
    --animation --start 1 --end 250 --output /tmp/dla_frames/
```

### 3. Export and Analyze

```python
# In Blender Python console (after running simulation):
exec(open('dla_export.py').read())
quick_export('npz', '/tmp/dla_export.npz')
```

```python
# In Jupyter (dla_visualization.ipynb):
dla_data = load_dla_data('/tmp/dla_export.npz')
fig = visualize_dla_3d(dla_data['positions'], dla_data['timepoints'])
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Initial Particles | 5000 | Starting particle count on seed |
| Step Size | 0.02 | Brownian motion magnitude |
| Contact Radius | 0.03 | Distance for particle sticking |
| Noise Scale | 2.0 | Spatial frequency of displacement |
| Seed | 42 | Random seed for reproducibility |

## Requirements

- Blender 4.2+ with Cycles
- GPU recommended (CUDA, OptiX, HIP, or Metal)
- Python 3.10+ (for analysis notebook)
- NumPy, Plotly, Matplotlib, SciPy (for visualization)

## Expected Results

- Fractal dimension D ≈ 2.5 for 3D DLA
- Branching dendritic structure growing from seed
- Timepoint coloring shows growth progression
