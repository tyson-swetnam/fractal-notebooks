# 3D Tree and Root Visualization

Interactive three-dimensional visualization of branching networks, demonstrating the self-affine geometry of vascular plant architectures.

---

## Overview

This application generates 3D branching structures that model:

- **Tree canopy architecture**: Above-ground branching from trunk to twigs
- **Root systems**: Below-ground foraging networks
- **Vascular networks**: Internal transport systems

The visualization demonstrates how self-affine scaling creates space-filling structures that optimize resource transport.

---

## Mathematical Model

### WBE Branching Ratios

The West-Brown-Enquist model predicts specific scaling relationships for branching networks:

**Radial scaling** (area-preserving):
\[
\xi = \frac{r_{k+1}}{r_k} = n^{-1/2}
\]

**Longitudinal scaling** (space-filling):
\[
\gamma = \frac{l_{k+1}}{l_k} = n^{-1/3}
\]

where \( n \) is the branching ratio (number of daughter branches per parent).

### Self-Affinity

Since \( \xi \neq \gamma \), the branching network is **self-affine**, not self-similar. Branches become relatively more slender as the network subdivides:

\[
\frac{l/r \text{ at level } k+1}{l/r \text{ at level } k} = \frac{\gamma}{\xi} = n^{1/6}
\]

---

## Features

### Tree Generation

| Parameter | Description | Default |
|-----------|-------------|---------|
| Branching ratio | Children per parent | 2 |
| Length ratio | \( \gamma \) | 0.7 |
| Width ratio | \( \xi \) | 0.6 |
| Iterations | Branching levels | 8 |
| Angle spread | Branch angle variation | 30° |

### Root Generation

Root systems can use different parameters reflecting:
- Higher branching ratios (more fine roots)
- Different length/width ratios
- Gravitropism (downward bias)

### Visualization Controls

- **Rotate**: Click and drag to rotate the view
- **Zoom**: Scroll wheel to zoom in/out
- **Pan**: Right-click drag to pan
- **Reset**: Double-click to reset view

---

## Biological Applications

### Canopy Architecture

Tree crowns exhibit characteristic scaling:

| Species Type | Branching Ratio | Typical \( D_M \) |
|--------------|-----------------|-------------------|
| Broadleaf deciduous | 2-3 | 1.4-1.6 |
| Conifer | 3-5 | 1.5-1.7 |
| Palm | 1 (unbranched) | ~1.0 |

### Root Systems

Root architecture varies with soil conditions:

| Root Type | Description | Fractal Dimension |
|-----------|-------------|-------------------|
| Taproot | Single dominant root | Lower \( D \) |
| Fibrous | Highly branched | Higher \( D \) |
| Adventitious | Surface roots | Variable |

### Crown Shyness

In dense forests, neighboring crowns maintain gaps, creating a Voronoi-like tessellation of the canopy. The 3D visualization can demonstrate this by:
- Generating multiple trees
- Applying collision detection
- Showing the resulting canopy structure

---

## Technical Implementation

### Rendering

The visualization uses Three.js for WebGL-based 3D rendering:

```javascript
// Simplified branch generation
function generateBranch(parent, level, maxLevel, params) {
    if (level > maxLevel) return;

    const length = parent.length * params.gamma;
    const radius = parent.radius * params.xi;

    for (let i = 0; i < params.branchingRatio; i++) {
        const angle = (2 * Math.PI * i) / params.branchingRatio;
        const child = createCylinder(length, radius, parent.end, angle);

        scene.add(child);
        generateBranch(child, level + 1, maxLevel, params);
    }
}
```

### Performance Optimization

- **Level of Detail (LOD)**: Reduce detail for distant branches
- **Instanced rendering**: Batch similar geometry
- **Culling**: Skip branches outside view frustum

---

## Analysis Tools

### Fractal Dimension Calculation

The application can compute the fractal dimension of generated structures using:

1. **Box-counting**: 3D voxelization and counting
2. **Mass dimension**: Scaling of total branch volume
3. **Surface dimension**: Scaling of total surface area

### Export Options

- **OBJ format**: 3D mesh for external rendering
- **Point cloud**: XYZ coordinates of branch endpoints
- **CSV**: Tabular data of branch properties

---

## Examples

### Example 1: Symmetric Binary Tree

Parameters:
- Branching ratio: 2
- Length ratio: 0.7
- Width ratio: 0.7 (self-similar)
- Iterations: 10

Result: \( D \approx 2.0 \) (self-similar, fills a plane)

### Example 2: Self-Affine Tree

Parameters:
- Branching ratio: 2
- Length ratio: 0.7 (\( \gamma = n^{-1/3} \))
- Width ratio: 0.5 (\( \xi = n^{-1/2} \))
- Iterations: 10

Result: \( D_M \approx 1.5 \) (matches MST prediction)

### Example 3: Dense Root System

Parameters:
- Branching ratio: 4
- Length ratio: 0.6
- Width ratio: 0.4
- Iterations: 6
- Downward bias: 0.8

Result: Space-filling root network for nutrient foraging

---

## Further Reading

- West, G. B., Brown, J. H., & Enquist, B. J. (1999). A general model for the structure and allometry of plant vascular systems. *Nature*, 400(6745), 664-667.

- Bentley, L. P., et al. (2013). An empirical assessment of tree branching networks and implications for plant allometric scaling models. *Ecology Letters*, 16(8), 1069-1078.

- Smith, D. D., et al. (2014). Deviation from symmetrically self-similar branching in trees predicts altered hydraulics, mechanics, light interception and metabolic scaling. *New Phytologist*, 201(1), 217-229.
