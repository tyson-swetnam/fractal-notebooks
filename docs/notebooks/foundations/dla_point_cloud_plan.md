# DLA Point Cloud Generation in Blender with Cycles

A comprehensive plan for implementing 3D Diffusion-Limited Aggregation using Blender's Geometry Nodes and rendering with Cycles, based on techniques from the [BlenderArtists DLA exploration thread](https://blenderartists.org/t/exploring-diffusion-limited-aggregation-in-geometry-nodes/1589322).

---

## Table of Contents

1. [Installation & Setup](#1-installation--setup)
2. [DLA Algorithm Overview](#2-dla-algorithm-overview)
3. [Geometry Nodes Implementation](#3-geometry-nodes-implementation)
4. [Flow Field Dynamics](#4-flow-field-dynamics)
5. [Performance Optimization](#5-performance-optimization)
6. [Cycles Rendering Setup](#6-cycles-rendering-setup)
7. [Integration with fractal-notebooks](#7-integration-with-fractal-notebooks)
8. [Implementation Roadmap](#8-implementation-roadmap)

---

## 1. Installation & Setup

### 1.1 Blender Installation

#### Linux (Ubuntu/Debian)
```bash
# Option A: Snap package (recommended for latest version)
sudo snap install blender --classic

# Option B: Official tarball
wget https://download.blender.org/release/Blender4.2/blender-4.2.0-linux-x64.tar.xz
tar -xf blender-4.2.0-linux-x64.tar.xz
sudo mv blender-4.2.0-linux-x64 /opt/blender
sudo ln -s /opt/blender/blender /usr/local/bin/blender

# Option C: Flatpak
flatpak install flathub org.blender.Blender
```

#### macOS
```bash
# Homebrew
brew install --cask blender

# Or download DMG from blender.org
```

#### Windows
```powershell
# Winget
winget install BlenderFoundation.Blender

# Or download MSI from blender.org
```

### 1.2 Cycles GPU Configuration

Cycles is bundled with Blender. Enable GPU rendering:

1. **Edit > Preferences > System**
2. **Cycles Render Devices**:
   - **CUDA**: NVIDIA GPUs (GTX 900+, RTX series)
   - **OptiX**: NVIDIA RTX GPUs (fastest ray tracing)
   - **HIP**: AMD GPUs (RX 5000+, RDNA architecture)
   - **oneAPI**: Intel Arc GPUs
   - **Metal**: Apple Silicon (M1/M2/M3)

3. Select your GPU device(s)
4. In scene properties: **Render Engine > Cycles**, Device > GPU Compute

### 1.3 Python API Setup (for scripting)

```bash
# Blender's bundled Python
/opt/blender/4.2/python/bin/python3 -m pip install numpy scipy

# Or use Blender as a module
pip install bpy  # Limited availability, check blender.org/download/
```

---

## 2. DLA Algorithm Overview

### 2.1 Core Algorithm Steps

```
1. INITIALIZE seed structure with random displaced points
   - Capture attributes: color, timepoint, active_flag

2. FOR each simulation frame:
   a. SPLIT particles into active (moving) and fixed (structure)
   b. DISPLACE active particles via brownian motion + flow field
   c. CHECK proximity to fixed structure
   d. IF contact: SNAP particle to structure, mark as fixed
   e. DUPLICATE/DELETE particles stochastically
   f. JOIN active + fixed geometry for next iteration

3. OUTPUT point cloud with timepoint-based coloring
```

### 2.2 Mathematical Foundation

**Brownian Motion Displacement:**
$$\vec{r}_{t+1} = \vec{r}_t + \sqrt{2D\Delta t} \cdot \vec{\xi}$$

Where:
- $D$ = diffusion coefficient
- $\Delta t$ = time step
- $\vec{\xi}$ = random unit vector (Gaussian distribution)

**Sticking Probability:**
$$P_{stick} = \begin{cases} 1 & \text{if } |\vec{r}_{particle} - \vec{r}_{structure}| < r_{contact} \\ 0 & \text{otherwise} \end{cases}$$

---

## 3. Geometry Nodes Implementation

### 3.1 Node Graph Structure

```
[Group Input]
    │
    ▼
[Distribute Points on Faces] ─── Seed geometry (sphere, plane, etc.)
    │
    ▼
[Capture Attribute] ─── Store: Random Color, Timepoint (frame), Active Flag
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SIMULATION ZONE                             │
│  ┌─────────────────┐                                            │
│  │ Separate by     │◄── Boolean: Active Flag                    │
│  │ Attribute       │                                            │
│  └────────┬────────┘                                            │
│           │                                                      │
│     ┌─────┴─────┐                                               │
│     ▼           ▼                                               │
│  [Active]   [Fixed Structure]                                   │
│     │           │                                               │
│     ▼           │                                               │
│  [Set Position] │◄── Brownian motion + Flow field              │
│     │           │                                               │
│     ▼           │                                               │
│  [Sample        │                                               │
│   Nearest]──────┘◄── Find closest structure point              │
│     │                                                           │
│     ▼                                                           │
│  [Compare        ◄── Distance < contact_radius?                │
│   Distance]                                                     │
│     │                                                           │
│     ▼                                                           │
│  [Switch]──────── Snap to structure OR continue moving         │
│     │                                                           │
│     ▼                                                           │
│  [Delete/         ◄── Stochastic particle management           │
│   Duplicate]                                                    │
│     │                                                           │
│     ▼                                                           │
│  [Join Geometry] ─── Combine active + fixed                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
[Set Material] ─── Point cloud material with timepoint coloring
    │
    ▼
[Group Output]
```

### 3.2 Key Node Configurations

#### Distribute Points on Seed
```
Node: Distribute Points on Faces
├── Density: 10000 (initial particle count)
├── Seed: Random integer
└── Selection: All faces
```

#### Brownian Motion Displacement
```
Node: Set Position (within Repeat Zone)
├── Position = Position + noise_offset
├── noise_offset = Noise Texture(Position, Scale=2.0) * step_size
└── step_size: 0.01 - 0.05 (controls diffusion rate)
```

#### Contact Detection
```
Node: Sample Nearest
├── Geometry: Fixed structure points
├── Sample Position: Active particle position
├── Output: Nearest Index, Distance

Node: Compare
├── A: Distance
├── B: contact_radius (e.g., 0.02)
├── Operation: Less Than
└── Output: Boolean (is_contacting)
```

---

## 4. Flow Field Dynamics

### 4.1 Components

The flow field combines multiple influences:

| Component | Effect | Implementation |
|-----------|--------|----------------|
| **Brownian motion** | Random walk | `Noise Texture` with high frequency |
| **Z-rotation** | Spiral growth | `Vector Rotate` around Z-axis |
| **3D noise field** | Large-scale structure | `Noise Texture` with low frequency |
| **Vertical bias** | Upward growth tendency | Add constant Z offset |
| **Radial expansion** | Outward growth | Normalize position, scale outward |

### 4.2 Flow Field Node Setup

```
[Position]
    │
    ├──► [Noise Texture] ─── Scale: 4.0, Detail: 4
    │         │
    │         ▼
    │    [Vector Math: Multiply] ◄── Factor: 0.02 (noise strength)
    │         │
    ├──► [Vector Rotate] ─── Axis: Z, Angle: 0.1 rad/frame
    │         │
    │         ▼
    │    [Vector Math: Add]
    │         │
    ├──► [Normalize] ─► [Vector Math: Scale] ◄── radial_force: 0.005
    │                        │
    │                        ▼
    │                   [Vector Math: Add]
    │                        │
    └──► [Combine XYZ] ─── X:0, Y:0, Z:0.01 (vertical bias)
              │
              ▼
         [Vector Math: Add]
              │
              ▼
         [Final Displacement Vector]
```

### 4.3 Parameters Reference

| Parameter | Range | Effect |
|-----------|-------|--------|
| `noise_scale` | 1.0 - 10.0 | Structure granularity |
| `noise_strength` | 0.01 - 0.1 | Randomness intensity |
| `rotation_rate` | 0.0 - 0.5 rad | Spiral tightness |
| `vertical_bias` | 0.0 - 0.05 | Upward growth tendency |
| `radial_force` | -0.02 - 0.02 | Expansion (+) / Contraction (-) |
| `contact_radius` | 0.01 - 0.05 | Particle sticking distance |

---

## 5. Performance Optimization

### 5.1 Known Limitations

- **VRAM Limit**: 2-4 million points before GPU memory exhaustion
- **Simulation Time**: Scales with particle count and structure complexity
- **Repeat Zone Iterations**: Each iteration adds randomness but costs compute

### 5.2 Optimization Strategies

#### Sample from Active Subset (Critical)
```
# WRONG: Sample from entire structure (slow)
Sample Nearest(all_points, active_position)

# RIGHT: Sample from active subset only (fast)
Separate(active_flag=True) → Sample Nearest(active_only, structure_position)
```

#### Stochastic Particle Management
```
Node: Delete Geometry
├── Selection: Random Value < deletion_probability (0.01)
└── Domain: Points

Node: Duplicate Elements
├── Selection: Random Value < duplication_probability (0.005)
└── Amount: 1
```

#### LOD (Level of Detail) Approach
```
Phase 1: Coarse simulation (1000 particles, large step_size)
Phase 2: Medium refinement (10000 particles, medium step_size)
Phase 3: Fine detail (100000 particles, small step_size)
```

### 5.3 Memory Management

```python
# Python script for chunked export
import bpy

def export_point_cloud_chunks(obj, chunk_size=100000):
    """Export large point clouds in chunks to avoid memory issues."""
    mesh = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
    total_points = len(mesh.vertices)

    for i in range(0, total_points, chunk_size):
        chunk = mesh.vertices[i:i+chunk_size]
        # Export chunk to PLY/OBJ/numpy
        export_chunk(chunk, f"dla_chunk_{i//chunk_size:04d}.ply")
```

---

## 6. Cycles Rendering Setup

### 6.1 Point Cloud Material

```
[Geometry: Pointcloud]
    │
    ▼
[Attribute: timepoint] ─── Named attribute from geometry nodes
    │
    ▼
[Math: Divide] ◄── total_frames (normalize to 0-1)
    │
    ▼
[Color Ramp]
├── Position 0.0: Deep Blue (#0a1628)
├── Position 0.3: Cyan (#00d4ff)
├── Position 0.6: Green (#00ff88)
├── Position 0.9: Yellow (#ffdd00)
└── Position 1.0: White (#ffffff)
    │
    ▼
[Mix Shader]
├── Shader 1: [Principled BSDF] ─── Base Color from ramp
├── Shader 2: [Emission] ─── Strength: 2.0, Color from ramp
└── Factor: emission_mask (growth tips = 1.0)
    │
    ▼
[Material Output]
```

### 6.2 Render Settings

```yaml
# Cycles Configuration
render_engine: CYCLES
device: GPU
samples: 256-1024  # Higher for final render
denoiser: OptiX / OpenImageDenoise

# Point Cloud Settings
point_size: 0.002 - 0.01  # World units
render_as: SPHERE / DISC

# Lighting
hdri: Studio or outdoor environment
ambient_occlusion: True
ao_distance: 0.1
ao_factor: 0.5

# Camera
lens: 50mm
dof: f/2.8 for bokeh effect
focus_distance: Auto to structure center
```

### 6.3 Ambient Occlusion Enhancement

```
[Ambient Occlusion]
├── Samples: 16
├── Distance: 0.1
└── Output: Color, AO factor
    │
    ▼
[Mix RGB]
├── Color 1: Base material color
├── Color 2: Dark shadow (#1a1a2e)
├── Factor: AO output (inverted)
└── Blend: Multiply
```

---

## 7. Integration with fractal-notebooks

### 7.1 Export Formats

| Format | Use Case | Size |
|--------|----------|------|
| **PLY** | Point cloud with attributes | Medium |
| **OBJ** | Mesh conversion | Large |
| **NumPy (.npy)** | Python analysis | Small |
| **Alembic (.abc)** | Animation sequences | Variable |

### 7.2 Python Export Script

```python
# dla_export.py - Run in Blender's Python console
import bpy
import numpy as np

def export_dla_to_numpy(object_name, output_path):
    """Export DLA point cloud to numpy array for analysis."""
    obj = bpy.data.objects[object_name]
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()

    # Extract positions
    positions = np.array([v.co[:] for v in mesh.vertices])

    # Extract custom attributes if available
    timepoints = np.zeros(len(mesh.vertices))
    if 'timepoint' in mesh.attributes:
        timepoints = np.array(mesh.attributes['timepoint'].data[:].foreach_get('value'))

    # Save to numpy
    np.savez(output_path,
             positions=positions,
             timepoints=timepoints,
             bounds=np.array([positions.min(axis=0), positions.max(axis=0)]))

    eval_obj.to_mesh_clear()
    print(f"Exported {len(positions)} points to {output_path}")

# Usage
export_dla_to_numpy("DLA_Structure", "/tmp/dla_export.npz")
```

### 7.3 Jupyter Notebook Visualization

```python
# dla_visualization.ipynb
import numpy as np
import plotly.graph_objects as go

# Load exported DLA data
data = np.load("dla_export.npz")
positions = data['positions']
timepoints = data['timepoints']

# Create 3D scatter plot
fig = go.Figure(data=[go.Scatter3d(
    x=positions[:, 0],
    y=positions[:, 1],
    z=positions[:, 2],
    mode='markers',
    marker=dict(
        size=1,
        color=timepoints,
        colorscale='Viridis',
        opacity=0.8
    )
)])

fig.update_layout(
    title="3D DLA Point Cloud",
    scene=dict(
        xaxis_title="X",
        yaxis_title="Y",
        zaxis_title="Z",
        aspectmode='data'
    )
)
fig.show()
```

### 7.4 Fractal Dimension Analysis

```python
# Box-counting dimension for 3D DLA
def box_counting_dimension(points, min_box=0.01, max_box=1.0, num_scales=20):
    """Estimate fractal dimension using box-counting method."""
    scales = np.logspace(np.log10(min_box), np.log10(max_box), num_scales)
    counts = []

    for scale in scales:
        # Discretize points to grid
        grid_points = np.floor(points / scale).astype(int)
        unique_boxes = len(set(map(tuple, grid_points)))
        counts.append(unique_boxes)

    # Linear regression on log-log plot
    log_scales = np.log(1/scales)
    log_counts = np.log(counts)
    slope, _ = np.polyfit(log_scales, log_counts, 1)

    return slope  # Fractal dimension

# Expected: D ≈ 2.5 for 3D DLA
dimension = box_counting_dimension(positions)
print(f"Estimated fractal dimension: {dimension:.3f}")
```

---

## 8. Implementation Roadmap

### Phase 1: Environment Setup
- [ ] Install Blender 4.2+ with Cycles
- [ ] Configure GPU rendering (CUDA/OptiX/HIP/Metal)
- [ ] Verify Python API access
- [ ] Create project folder structure

### Phase 2: Basic DLA Implementation ✅
- [x] Create seed geometry (sphere or point)
- [x] Build initialization node group (distribute + capture attributes)
- [x] Implement simulation zone with repeat
- [x] Add brownian motion displacement
- [x] Implement contact detection and snapping

### Phase 3: Flow Field Enhancement ✅
- [x] Add 3D noise texture influence
- [x] Implement Z-axis rotation for spiral patterns
- [x] Add vertical growth bias
- [x] Add radial expansion/contraction controls
- [x] Expose parameters to geometry node interface

### Phase 4: Particle Management
- [ ] Implement stochastic deletion
- [ ] Implement particle duplication
- [ ] Add particle count monitoring
- [ ] Optimize sampling performance

### Phase 5: Material & Rendering (Partial)
- [x] Create timepoint-based color ramp material
- [ ] Add emission shader for growth tips
- [ ] Configure ambient occlusion
- [x] Set up Cycles render settings
- [ ] Test GPU rendering performance

### Phase 6: Export & Integration (Partial)
- [x] Write Python export script for PLY/NumPy
- [x] Create Jupyter notebook for visualization
- [x] Implement fractal dimension analysis
- [ ] Add to fractal-notebooks documentation
- [ ] Create example renders and animations

### Phase 7: Advanced Features (Optional)
- [ ] Multi-seed growth patterns
- [ ] Animated flow fields
- [ ] Collision-aware growth
- [ ] Real-time viewport preview optimization
- [x] Headless batch rendering script

---

## References

- [BlenderArtists: Exploring DLA in Geometry Nodes](https://blenderartists.org/t/exploring-diffusion-limited-aggregation-in-geometry-nodes/1589322)
- [Blender Manual: Geometry Nodes](https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/index.html)
- [Blender Manual: Cycles Rendering](https://docs.blender.org/manual/en/latest/render/cycles/index.html)
- [Witten & Sander (1981): DLA Original Paper](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.47.1400)
- [Paul Bourke: DLA Resources](http://paulbourke.net/fractals/dla/)

---

*Plan created: 2025-12-21*
*Based on: fractal-notebooks project requirements*
