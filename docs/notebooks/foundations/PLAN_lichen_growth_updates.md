# Plan: Non-Spherical Lichen Morphology Updates for dla_cuda_offgrid.ipynb

## Problem Analysis

The current lichen morphology examples in `dla_cuda_offgrid.ipynb` all produce **spherically-expanding** DLA clusters despite having different biological labels (Usnea, Cladonia, Ramalina, Crustose). This occurs because:

1. **Spherical birth radius**: All particles spawn on a spherical shell around the cluster origin
2. **Single-point seed**: Growth originates from a single seed at the origin
3. **Spherical kill radius**: Particles are killed when they exceed a spherical distance threshold

The `bulk_velocity` parameter adds directional bias but doesn't fundamentally change the spherical expansion pattern. The `substrate_type='plane'` constraint only prevents particles from penetrating z<0 after they've already been spawned.

## Required Changes (from lichen_dla_claude.md)

### 1. Planar Growth for Foliose/Crustose Morphologies

**Goal**: 2D radial expansion on a substrate surface

**Implementation**:
- **Hemispherical birth**: Spawn particles only from the upper hemisphere (z > 0)
- **Line/edge seeding**: Multiple seed particles along the z=0 plane
- **Planar kill boundary**: Kill particles that travel too far laterally instead of radially

```python
birth_geometry: str = 'sphere'  # 'sphere' | 'hemisphere' | 'plane' | 'cylinder'
seed_geometry: str = 'point'    # 'point' | 'line' | 'disk' | 'ring'
```

### 2. Vertical Upward Growth for Fruticose Morphologies

**Goal**: Tree-like or columnar upward growth (like Cladonia podetia or Usnea filaments)

**Implementation**:
- **Disk/ring birth plane**: Spawn particles from a horizontal disk above the cluster
- **Line seed**: Vertical line seed or single point at substrate
- **Cylindrical or hemispherical birth**: Particles enter from above, not from all directions
- **Height-biased spawning**: Concentrate new particle spawning above current cluster max height

```python
# For vertical growth
birth_geometry = 'hemisphere_above'  # only spawn from z > cluster_max_z
seed_geometry = 'point'              # single base point
bulk_velocity = [0, 0, 0.5]          # upward bias
```

### 3. New DLAPhysicsParams Fields

Add to the existing `DLAPhysicsParams` dataclass:

```python
@dataclass
class DLAPhysicsParams:
    # ... existing fields ...

    # New birth geometry fields
    birth_geometry: str = 'sphere'
    """Geometry for spawning new particles:
    - 'sphere': Classic spherical birth shell (default)
    - 'hemisphere_upper': Upper hemisphere only (z > center)
    - 'hemisphere_lower': Lower hemisphere only
    - 'disk_above': Horizontal disk above cluster
    - 'cylinder': Cylindrical shell around z-axis
    - 'plane_above': Infinite plane above cluster
    """

    seed_geometry: str = 'point'
    """Initial seed configuration:
    - 'point': Single particle at origin (default)
    - 'line_x': Line of particles along x-axis at z=0
    - 'line_z': Vertical line along z-axis
    - 'disk': Disk of particles in z=0 plane
    - 'ring': Ring of particles at radius R in z=0 plane
    """

    seed_params: Dict = field(default_factory=dict)
    """Parameters for seed geometry:
    - For 'line_*': {'length': 10.0, 'spacing': 2.0}
    - For 'disk': {'radius': 10.0, 'count': 20}
    - For 'ring': {'radius': 10.0, 'count': 12}
    """

    birth_height_tracking: bool = False
    """If True, birth disk/plane follows cluster's max height.
    Creates columnar upward growth by spawning above current growth front.
    """
```

## Updated Lichen Presets

### Crustose Radial (Truly Planar)

```python
'crustose_radial': DLAPhysicsParams(
    stickiness=0.75,
    bulk_velocity=np.array([0.0, 0.0, 0.0]),  # No vertical bias
    substrate_type='plane',
    substrate_params={'z_level': 0.0},
    birth_geometry='hemisphere_upper',  # Only spawn from above
    seed_geometry='disk',               # Start with disk of seeds
    seed_params={'radius': 5.0, 'count': 20},
)
```

### Foliose (Lobed Planar)

```python
'foliose': DLAPhysicsParams(
    stickiness=0.55,
    bulk_velocity=np.array([0.0, 0.0, 0.05]),  # Slight vertical for thickness
    substrate_type='plane',
    substrate_params={'z_level': 0.0},
    birth_geometry='hemisphere_upper',
    seed_geometry='ring',               # Ring creates radial lobes
    seed_params={'radius': 8.0, 'count': 8},
)
```

### Cladonia Podetia (Vertical Columnar)

```python
'cladonia_podetia': DLAPhysicsParams(
    stickiness=0.65,
    bulk_velocity=np.array([0.0, 0.0, 0.6]),
    substrate_type='plane',
    substrate_params={'z_level': 0.0},
    birth_geometry='disk_above',        # Spawn from disk above growth front
    birth_height_tracking=True,         # Track cluster max height
    seed_geometry='point',              # Single base point
)
```

### Usnea (Hanging/Vertical Filaments)

```python
'usnea_filament': DLAPhysicsParams(
    stickiness=0.30,
    bulk_velocity=np.array([0.0, 0.0, 0.5]),
    substrate_type='none',              # Free growth
    birth_geometry='cylinder',          # Cylindrical spawning around z-axis
    birth_height_tracking=True,
    seed_geometry='line_z',             # Vertical line seed
    seed_params={'length': 5.0, 'spacing': 1.0},
)
```

### Ramalina (Branching Strap-like)

```python
'ramalina': DLAPhysicsParams(
    stickiness=0.50,
    bulk_velocity=np.array([0.0, 0.0, 0.45]),
    substrate_type='none',
    birth_geometry='hemisphere_upper',
    seed_geometry='point',
)
```

## Implementation Tasks

### Phase A: Core Birth Geometry Changes

1. **Add birth geometry fields to DLAPhysicsParams** (Cell ~63)
   - Add `birth_geometry`, `seed_geometry`, `seed_params`, `birth_height_tracking`
   - Update docstrings with biological interpretations

2. **Create seed initialization function** (new helper function)
   - `initialize_seeds(geometry, params) -> np.ndarray`
   - Support point, line_x, line_z, disk, ring geometries

3. **Create birth position sampling function** (new CUDA device function)
   - `sample_birth_position(geometry, birth_radius, cluster_max_z, rng)`
   - Support sphere, hemisphere_upper, disk_above, cylinder geometries

4. **Update `sphere_hopping_walk_advanced` kernel** (Cell ~69)
   - Pass birth_geometry and related params to kernel
   - Modify birth position calculation based on geometry

5. **Update `AdvancedDLASimulation` class** (Cell ~70)
   - Initialize seeds based on seed_geometry
   - Track cluster max_z for height-tracking birth
   - Pass birth geometry params to kernel

### Phase B: Updated Presets and Demos

6. **Update LICHEN_PRESETS dictionary** (Cell ~67)
   - Replace existing presets with corrected versions
   - Add new morphology types (foliose, cladonia_podetia)

7. **Update demonstration cells** (Cells 72-85)
   - Show side-by-side comparison of old (spherical) vs new geometries
   - Demonstrate truly planar crustose growth
   - Demonstrate vertical columnar Cladonia growth
   - Add annotations explaining the geometric differences

### Phase C: Validation and Visualization

8. **Add morphology validation**
   - Compute z-extent / xy-extent ratio (should be << 1 for crustose)
   - Compute cluster aspect ratio
   - Verify fruticose shows z-extent / xy-extent > 1

9. **Add side-by-side comparison figure**
   - Show spherical vs planar birth for crustose
   - Show spherical vs vertical for fruticose
   - Use consistent scales for fair comparison

## Expected Results

| Morphology | Current (Spherical) | After Update |
|------------|---------------------|--------------|
| Crustose Radial | Spherical blob | Flat circular disk, z-extent ≈ particle_radius |
| Foliose | Spherical blob | Thin lobed structure, z-extent ≈ 5-10 particles |
| Cladonia Podetia | Spherical with slight vertical stretch | Columnar/tree-like, z-extent >> xy-extent |
| Usnea | Spherical with vertical stretch | Filamentous vertical, narrow diameter |
| Ramalina | Spherical with vertical stretch | Branching with upward bias |

## File Changes Summary

**Modified cells in dla_cuda_offgrid.ipynb:**
- Cell 63: DLAPhysicsParams dataclass (add 4 new fields)
- Cell 65: Device functions (add birth geometry sampling)
- Cell 67: LICHEN_PRESETS (update all presets)
- Cell 69: sphere_hopping_walk_advanced kernel (add birth geometry)
- Cell 70: AdvancedDLASimulation class (add seed init, height tracking)
- Cells 72-85: Demo cells (show corrected morphologies)
- Cell 85: Comparison figure (update to show geometric differences)

**New cells to add:**
- Helper functions for seed initialization
- Validation cells showing z-extent/xy-extent ratios
- Before/after comparison visualization
