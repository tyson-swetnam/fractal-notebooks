# Blender DLA Point Cloud Tools

3D Diffusion-Limited Aggregation (DLA) simulation using Blender's Geometry Nodes and Cycles rendering.

## Features

- **Phase 2**: Basic DLA simulation with brownian motion and contact detection
- **Phase 3**: Flow field dynamics for artistic growth patterns
- **Phase 4**: Particle management with stochastic deletion, duplication, and memory limits
- **Phase 5**: Material & rendering with growth tip emission, ambient occlusion, GPU performance testing

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

### 2. Apply Presets

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
# - dense: High duplication for thick growth
# - sparse: High deletion for thin branches
```

### 3. Monitor Particles

```python
# Check current particle statistics
print_particle_stats(bpy.data.objects['DLA_Seed'])
# Output: Frame 100: Total=15234, Active=2341, Fixed=12893
```

### 4. Headless Rendering

```bash
# Render single frame
blender -b -P dla_blender_setup.py -P dla_batch_render.py -- --frame 100 --output /tmp/dla.png

# Render animation
blender -b -P dla_blender_setup.py -P dla_batch_render.py -- \
    --animation --start 1 --end 250 --output /tmp/dla_frames/
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

### Particle Management Parameters (Phase 4)

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Deletion Probability | 0.01 | 0.0-0.1 | % of particles deleted per frame |
| Duplication Probability | 0.005 | 0.0-0.05 | % of particles duplicated per frame |
| Max Active Particles | 50000 | 1000-500000 | Memory limit (stops spawning when reached) |
| Boundary Radius | 5.0 | 1.0-20.0 | Delete particles beyond this distance |

## Particle Management System

Phase 4 introduces intelligent particle lifecycle management:

```
┌─────────────────────────────────────────────────────────────┐
│                    SIMULATION FRAME                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. COUNT active particles                                   │
│     └── If count < Max Active → spawn new particles         │
│     └── If count >= Max Active → skip spawning              │
│                                                              │
│  2. MOVE particles via flow field                            │
│                                                              │
│  3. DELETE particles if:                                     │
│     └── random() < Deletion Probability                     │
│     └── distance from origin > Boundary Radius              │
│                                                              │
│  4. DUPLICATE particles if:                                  │
│     └── random() < Duplication Probability                  │
│                                                              │
│  5. CHECK contact with structure                             │
│     └── If contact → particle becomes fixed                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Deletion vs Duplication Trade-offs

| Scenario | Deletion | Duplication | Effect |
|----------|----------|-------------|--------|
| Dense growth | Low (0.002) | High (0.02) | Thick, filled structure |
| Sparse branching | High (0.03) | Low (0.0) | Thin, wispy branches |
| Balanced | Medium (0.01) | Medium (0.005) | Natural DLA pattern |
| Memory constrained | High (0.02) | Low (0.002) | Keeps particle count low |

## Presets

| Preset | Description | Key Settings |
|--------|-------------|--------------|
| `classic` | Traditional DLA | No flow field, pure brownian |
| `spiral` | Galaxy-like | High rotation, slight expansion |
| `tree` | Tree growth | Strong vertical bias, high duplication |
| `coral` | Coral branching | Radial expansion, moderate noise |
| `vortex` | Tight spiral | Very high rotation, contraction |
| `turbulent` | Chaotic | High noise strength, low rotation |
| `dense` | Thick growth | Low deletion, high duplication |
| `sparse` | Thin branches | High deletion, no duplication |

## Material & Rendering (Phase 5)

### Growth Tip Emission

Recently added particles (timepoint > 85% of max) glow with emission shading:

```python
# Default settings
create_dla_material(
    max_frames=250,        # Simulation length
    tip_threshold=0.85,    # Particles above this normalized timepoint emit
    emission_strength=2.0, # Glow intensity
    ao_distance=0.1,       # Ambient occlusion range
    ao_factor=0.5          # AO shadow strength
)

# More visible tips (higher threshold, stronger glow)
create_dla_material(tip_threshold=0.9, emission_strength=4.0)

# Subtle effect
create_dla_material(tip_threshold=0.95, emission_strength=1.0)
```

### Ambient Occlusion

Built-in AO enhances depth perception by darkening crevices and contact points.

### GPU Performance Testing

After setting up the scene, test render performance:

```python
# Test render speeds at various sample counts (16, 32, 64, 128, 256)
test_gpu_performance()

# Test with custom sample counts
test_gpu_performance(sample_counts=[32, 64, 128, 512])

# Benchmark simulation speed (not rendering)
benchmark_simulation(frames=50)
```

Output includes:
- GPU device information
- Render time per sample count
- Samples per second efficiency
- Estimated animation render time
- Performance log saved to `/tmp/dla_perf_test/`

## Performance Optimization

### Memory Management

The simulation automatically prevents memory exhaustion:

1. **Max Active Particles**: Stops spawning when limit is reached
2. **Boundary Radius**: Deletes escaped particles
3. **Stochastic Deletion**: Continuously removes excess particles

### Recommended Settings by Hardware

| GPU VRAM | Max Active Particles | Spawn Rate |
|----------|---------------------|------------|
| 4GB | 20,000 | 50 |
| 8GB | 50,000 | 100 |
| 12GB+ | 100,000 | 200 |

### Optimization Tips

1. **Reduce Spawn Rate** if simulation lags
2. **Increase Deletion Probability** to keep particle count stable
3. **Decrease Boundary Radius** to remove wandering particles faster
4. **Use lower Contact Radius** for faster aggregation

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
- Reduce `Spawn Rate` and `Max Active Particles`
- Increase `Deletion Probability`
- Increase `Contact Radius` for faster aggregation

### Memory errors / crashes
- Lower `Max Active Particles` (try 20000)
- Increase `Deletion Probability` to 0.02+
- Reduce `Boundary Radius` to 3.0

### Structure looks too random
- Reduce `Step Size` and `Noise Scale`
- Increase `Flow Noise Strength` for more structure

### Structure doesn't grow
- Check `Deletion Probability` isn't too high
- Verify `Boundary Radius` isn't too small
- Increase `Spawn Rate`

### Particles escaping to infinity
- Reduce `Boundary Radius`
- Increase `Radial Force` (negative for inward pull)
- Increase `Deletion Probability`
