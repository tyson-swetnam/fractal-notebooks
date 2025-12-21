# Blender DLA Point Cloud Generator

3D Diffusion-Limited Aggregation (DLA) simulation using Blender's Geometry Nodes and Cycles rendering.

## Overview

This tool provides a complete DLA simulation environment in Blender, featuring:

- **Real-time simulation** via Geometry Nodes
- **Artistic flow fields** for spiral, tree, coral, and vortex patterns
- **Particle management** with stochastic deletion and duplication
- **Publication-quality rendering** with Cycles GPU acceleration
- **Export tools** for Python analysis (NumPy, PLY, CSV formats)

![DLA Concept](https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/DLA_Cluster.JPG/220px-DLA_Cluster.JPG)

## Requirements

- **Blender 4.2+** with Cycles
- **GPU** recommended (CUDA, OptiX, HIP, or Metal)
- **Python 3.10+** (for analysis notebooks)

## Quick Start

### 1. Install Blender

=== "Linux"
    ```bash
    # Snap (recommended)
    sudo snap install blender --classic

    # Or official tarball
    wget https://download.blender.org/release/Blender4.2/blender-4.2.0-linux-x64.tar.xz
    tar -xf blender-4.2.0-linux-x64.tar.xz
    ```

=== "macOS"
    ```bash
    brew install --cask blender
    ```

=== "Windows"
    ```powershell
    winget install BlenderFoundation.Blender
    ```

### 2. Run the Setup Script

1. Open Blender
2. Go to **Scripting** workspace
3. Open `docs/notebooks/foundations/blender/dla_blender_setup.py`
4. Run the script (Alt+P)
5. Press **Space** to play the animation

### 3. Apply a Preset

In Blender's Python console:

```python
# Apply artistic preset
apply_preset(bpy.data.objects['DLA_Seed'], 'spiral')

# Available presets:
# classic, spiral, tree, coral, vortex, turbulent, dense, sparse
```

## Parameters

### Basic DLA (Phase 2)

| Parameter | Default | Description |
|-----------|---------|-------------|
| Initial Particles | 5000 | Starting particle count |
| Step Size | 0.02 | Brownian motion magnitude |
| Contact Radius | 0.03 | Sticking distance |
| Noise Scale | 2.0 | Spatial frequency of motion |

### Flow Field (Phase 3)

| Parameter | Default | Description |
|-----------|---------|-------------|
| Rotation Rate | 0.05 | Z-axis spiral (rad/frame) |
| Vertical Bias | 0.01 | Upward growth tendency |
| Radial Force | 0.005 | Expansion (+) / Contraction (-) |
| Flow Noise Scale | 0.5 | Large-scale structure frequency |
| Flow Noise Strength | 0.03 | Flow displacement magnitude |

### Particle Management (Phase 4)

| Parameter | Default | Description |
|-----------|---------|-------------|
| Deletion Probability | 0.01 | % particles deleted per frame |
| Duplication Probability | 0.005 | % particles duplicated per frame |
| Max Active Particles | 50000 | Memory limit for active particles |
| Boundary Radius | 5.0 | Delete particles beyond this distance |

### Material Settings (Phase 5)

| Parameter | Default | Description |
|-----------|---------|-------------|
| tip_threshold | 0.85 | Timepoint threshold for emission glow |
| emission_strength | 2.0 | Growth tip glow intensity |
| ao_distance | 0.1 | Ambient occlusion range |
| ao_factor | 0.5 | AO shadow strength |

## Presets

| Preset | Description | Key Settings |
|--------|-------------|--------------|
| `classic` | Traditional DLA | No flow field, pure brownian |
| `spiral` | Galaxy-like | High rotation, slight expansion |
| `tree` | Tree growth | Strong vertical bias, high duplication |
| `coral` | Coral branching | Radial expansion, moderate noise |
| `vortex` | Tight spiral | Very high rotation, contraction |
| `turbulent` | Chaotic | High noise strength |
| `dense` | Thick growth | Low deletion, high duplication |
| `sparse` | Thin branches | High deletion |

## Rendering

### GPU Configuration

1. **Edit > Preferences > System**
2. **Cycles Render Devices**: Select CUDA/OptiX/HIP/Metal
3. In scene: **Render Engine > Cycles**, Device > GPU Compute

### Material Features

The DLA material includes:

- **Timepoint coloring**: Deep blue → Cyan → Green → Yellow → White
- **Growth tip emission**: Recently added particles glow
- **Ambient occlusion**: Depth-enhancing shadows

### Performance Testing

```python
# Test render speeds at various sample counts
test_gpu_performance()

# Benchmark simulation speed
benchmark_simulation(frames=50)
```

## Export Formats

Export point clouds for external analysis:

| Format | Extension | Description |
|--------|-----------|-------------|
| NumPy | `.npz` | Python analysis with all attributes |
| PLY | `.ply` | Standard point cloud format |
| OBJ | `.obj` | Mesh format (vertices only) |
| CSV | `.csv` | Tabular format |

### Quick Export

```python
# Export current frame
quick_export('npz', '/tmp/dla_export.npz')
quick_export('ply', '/tmp/dla_export.ply')

# Export animation sequence
export_animation_sequence(obj, '/tmp/dla_anim/', format='npz')
```

## Analysis Notebook

The included Jupyter notebook (`dla_visualization.ipynb`) provides:

- **Interactive 3D visualization** with Plotly
- **Fractal dimension analysis** using box-counting
- **Growth pattern analysis** over time
- **Cross-section views** (XY, XZ, YZ planes)

### Fractal Dimension

Expected result for 3D DLA: **D ≈ 2.5**

```python
dimension, scales, counts, r_squared = box_counting_dimension(positions)
print(f"Fractal dimension: {dimension:.3f}")
```

## Batch Rendering

Render animations from the command line:

```bash
# Single frame
blender -b -P dla_blender_setup.py -P dla_batch_render.py -- \
    --frame 100 --output /tmp/dla_frame.png

# Animation
blender -b -P dla_blender_setup.py -P dla_batch_render.py -- \
    --animation --start 1 --end 250 --output /tmp/dla_frames/
```

## File Reference

| File | Description |
|------|-------------|
| `dla_blender_setup.py` | Main setup script (Geometry Nodes + Material) |
| `dla_export.py` | Export to NumPy/PLY/OBJ/CSV |
| `dla_batch_render.py` | Headless batch rendering |
| `dla_visualization.ipynb` | Analysis and visualization notebook |

## Performance Tips

| GPU VRAM | Max Active Particles | Spawn Rate |
|----------|---------------------|------------|
| 4GB | 20,000 | 50 |
| 8GB | 50,000 | 100 |
| 12GB+ | 100,000 | 200 |

### Optimization

1. **Reduce Spawn Rate** if simulation lags
2. **Increase Deletion Probability** to keep particle count stable
3. **Decrease Boundary Radius** to remove wandering particles

## References

- [BlenderArtists: Exploring DLA in Geometry Nodes](https://blenderartists.org/t/exploring-diffusion-limited-aggregation-in-geometry-nodes/1589322)
- [Blender Manual: Geometry Nodes](https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/index.html)
- [Blender Manual: Cycles Rendering](https://docs.blender.org/manual/en/latest/render/cycles/index.html)
- [Paul Bourke: DLA Resources](http://paulbourke.net/fractals/dla/)
- [Witten & Sander (1981): DLA Original Paper](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.47.1400)
