# Blender DLA Point Cloud Tools

3D Diffusion-Limited Aggregation (DLA) simulation using Blender's Geometry Nodes and Cycles rendering.

## Features

- **Phase 2**: Basic DLA simulation with brownian motion and contact detection
- **Phase 3**: Flow field dynamics for artistic growth patterns

## Files

| File | Description |
|------|-------------|
| `dla_blender_setup.py` | Main setup script - creates DLA geometry nodes simulation with flow field |
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

### 2. Apply Flow Field Presets

After running the setup script, apply artistic presets in Blender's Python console:

```python
# Apply a preset
apply_preset(bpy.data.objects['DLA_Seed'], 'spiral')

# Available presets:
# - classic: Pure brownian motion DLA
# - spiral: Galaxy-like spiral growth
# - tree: Upward-growing tree structure
# - coral: Coral-like radial branching
# - vortex: Strong spiraling vortex
# - turbulent: Chaotic flow field
```

### 3. Headless Rendering

```bash
# Render single frame
blender -b -P dla_blender_setup.py -P dla_batch_render.py -- --frame 100 --output /tmp/dla.png

# Render animation
blender -b -P dla_blender_setup.py -P dla_batch_render.py -- \
    --animation --start 1 --end 250 --output /tmp/dla_frames/
```

### 4. Export and Analyze

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

### Basic Parameters (Phase 2)

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Initial Particles | 5000 | 100-50000 | Starting particle count on seed |
| Step Size | 0.02 | 0.01-0.1 | Brownian motion magnitude |
| Contact Radius | 0.03 | 0.01-0.05 | Distance for particle sticking |
| Noise Scale | 2.0 | 1.0-10.0 | Spatial frequency of brownian motion |
| Seed | 42 | any int | Random seed for reproducibility |

### Flow Field Parameters (Phase 3)

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Rotation Rate | 0.05 | 0.0-0.5 | Z-axis spiral (radians/frame) |
| Vertical Bias | 0.01 | 0.0-0.05 | Upward growth tendency |
| Radial Force | 0.005 | -0.02-0.02 | Expansion (+) / Contraction (-) |
| Flow Noise Scale | 0.5 | 0.1-5.0 | Large-scale structure frequency |
| Flow Noise Strength | 0.03 | 0.0-0.1 | Large-scale displacement magnitude |
| Spawn Radius | 2.0 | 0.5-5.0 | Distance where new particles appear |
| Spawn Rate | 100 | 10-500 | New particles per frame |

### Flow Field Components

The flow field combines 5 components:

```
Final Displacement = Brownian + Flow Noise + Rotation + Vertical + Radial
```

1. **Brownian Motion**: High-frequency noise for random walk (Step Size × Noise Scale)
2. **Flow Noise**: Low-frequency noise for large-scale structure (Flow Noise Strength × Flow Noise Scale)
3. **Z-Axis Rotation**: Spiral pattern around vertical axis (Rotation Rate)
4. **Vertical Bias**: Constant upward drift (Vertical Bias)
5. **Radial Force**: Expansion or contraction from center (Radial Force)

## Presets

| Preset | Description | Key Settings |
|--------|-------------|--------------|
| `classic` | Traditional DLA | No flow field, pure brownian |
| `spiral` | Galaxy-like | High rotation, slight expansion |
| `tree` | Tree growth | Strong vertical bias, contraction |
| `coral` | Coral branching | Radial expansion, moderate noise |
| `vortex` | Tight spiral | Very high rotation, contraction |
| `turbulent` | Chaotic | High noise strength, low rotation |

## Flow Field Visual Guide

```
                    Vertical Bias ↑
                         │
                         │
        ←─── Radial Force (negative = inward)
                         │
                         ▼
    Rotation Rate ───→ ○ ←─── Radial Force (positive = outward)
         (spiral)        │
                         │
              Flow Noise (structure)
              Brownian (randomness)
```

## Requirements

- Blender 4.2+ with Cycles
- GPU recommended (CUDA, OptiX, HIP, or Metal)
- Python 3.10+ (for analysis notebook)
- NumPy, Plotly, Matplotlib, SciPy (for visualization)

## Expected Results

- Fractal dimension D ≈ 2.5 for 3D DLA
- Branching dendritic structure growing from seed
- Timepoint coloring shows growth progression
- Flow field creates artistic patterns (spirals, trees, corals)

## Troubleshooting

### Simulation runs slowly
- Reduce `Initial Particles` and `Spawn Rate`
- Increase `Contact Radius` for faster aggregation

### Structure looks too random
- Reduce `Step Size` and `Noise Scale`
- Increase `Flow Noise Strength` for more structure

### Structure doesn't grow upward
- Increase `Vertical Bias` (try 0.02-0.03)
- Set `Radial Force` to negative for inward pull

### Spiral is too tight/loose
- Adjust `Rotation Rate` (0.1 = moderate, 0.2 = tight)
- Combine with `Radial Force` to control arm spacing
