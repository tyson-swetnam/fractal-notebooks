# Simulating Lichen Growth: DLA and L-System Mathematics

**Diffusion-Limited Aggregation and Lindenmayer systems provide complementary mathematical frameworks for simulating the distinctive growth patterns of lichens.** DLA captures the edge-preferential, nutrient-diffusion-limited growth of crustose and foliose forms, while L-systems elegantly model the recursive branching structures of fruticose lichens. This technical report synthesizes the mathematical foundations, algorithmic implementations across dimensions, and Python implementation strategies necessary for building realistic lichen growth simulations.

The biological appropriateness of these models stems from lichen physiology: lacking vascular tissue, lichens depend entirely on diffusion for nutrient transport, making DLA's harmonic measure weighting biologically accurate. Meanwhile, fruticose lichens exhibit self-similar branching at multiple scales—precisely what L-systems formalize through parallel string rewriting. The seminal computational work by Desbenoit, Galin, and Akkouche (2004) demonstrated that "Open DLA" constrained by environmental parameters produces visually convincing lichen morphologies.

---

## Lichen morphology dictates modeling approach

Lichens are symbiotic organisms combining a mycobiont (fungus, typically Ascomycetes) with a photobiont (green algae or cyanobacteria). Their growth forms determine which mathematical model applies best:

**Crustose lichens** (approximately 75% of species) grow as thin crusts tightly adhered to substrate, expanding radially from the center at **0.1–2.0 mm/year**. Growth occurs at the margin through a pseudo-meristem, with the peripheral 4–7 mm ring supplying nutrients to the advancing edge. This edge-limited growth pattern directly corresponds to DLA's harmonic measure weighting.

**Foliose lichens** form loose, leaf-like structures with distinct upper and lower surfaces, attached by rhizines. Their four-layer architecture (upper cortex → algal layer → medulla → lower cortex) supports lobed expansion at **0.5–4 mm/year**. The directional lobe formation can be modeled through biased DLA or Eden model variants.

**Fruticose lichens** grow as three-dimensional shrubby or filamentous structures attached at a single holdfast. With growth rates of **1–20 mm/year** concentrated at branch tips, they exhibit recursive branching that L-systems capture naturally. In *Usnea* species, side-branches emerge at obtuse angles (~90°) from main branches, providing concrete parameters for L-system rules.

**Rugose** describes surface texture (wrinkled, folded) rather than a distinct growth form—this texture can be added to any base model through fractal noise functions.

The biological basis for DLA appropriateness was quantified by Royal Society research showing lichen growth follows directly from CO₂ diffusion in surrounding air. When small, the entire thallus contributes to growth; when large, carbon dioxide is disproportionately fixed at edges where diffusive flux is strongest. Maximum growth velocity of approximately **26 mm/year** can be predicted from diffusion constants and thallus geometry.

---

## Mathematical foundations of Diffusion-Limited Aggregation

DLA, introduced by Witten and Sander in 1981, describes aggregation through Brownian motion with fractal dimension **D ≈ 1.71** in 2D and **D ≈ 2.5** in 3D. The mathematical structure connects random walks to potential theory through the Laplace equation.

### Core algorithm definition

The basic DLA process:
1. Place a seed particle at the origin
2. Release a walker from distance R_birth (birth radius)
3. Walker performs random walk until either:
   - Adjacent to cluster → attach with probability p_stick
   - Beyond R_kill (kill radius) → terminate and restart
4. Update R_birth, R_kill as cluster grows; repeat

The **mass-radius scaling relation** N(R) ∝ R^D defines the fractal dimension, measurable through box-counting:

$$D = \lim_{\epsilon \to 0} \frac{\log N(\epsilon)}{\log(1/\epsilon)}$$

### Connection to Laplacian growth

DLA's deep structure emerges from its connection to harmonic measure. The concentration field u(x) of diffusing particles satisfies Laplace's equation ∇²u = 0 with boundary conditions u = 0 on the cluster surface and u → 1 at infinity. Growth probability at any boundary point is proportional to the local electric field:

$$P_{\text{growth}} \propto |\nabla u|^\eta$$

For DLA, η = 1. This is the **Mullins-Sekerka instability**: protruding tips experience higher field gradients and grow faster, producing dendritic branching. The **Dielectric Breakdown Model** (Niemeyer, Pietronero, Wiesmann 1984) generalizes this with variable η:
- η = 0: Eden model (compact clusters, D = 2)
- η = 1: Standard DLA (D ≈ 1.71)
- η > 1: More extreme branching (D < 1.71)
- η → ∞: Needle-like growth (D → 1)

### Random walk theory

The underlying stochastic process follows the diffusion equation for probability density P(x,t):

$$\frac{\partial P}{\partial t} = D \nabla^2 P$$

For discrete random walks with step size Δx and time step Δt, the diffusion coefficient D = (Δx)²/2Δt. The mean square displacement grows linearly with time: ⟨x²(t)⟩ = 2Dt. In the Langevin formulation:

$$\frac{dx}{dt} = \sqrt{2D}\xi(t)$$

where ξ(t) is Gaussian white noise with ⟨ξ(t)ξ(t')⟩ = δ(t - t').

### Key parameters affecting morphology

| Parameter | Effect | Value Range |
|-----------|--------|-------------|
| Sticking probability (p_stick) | Cluster density | 0.01 (compact) to 1.0 (dendritic) |
| Birth radius offset | Efficiency | 5–10 particle radii |
| Kill radius factor | Memory/speed tradeoff | 2–3 × birth radius |
| Neighborhood connectivity | Lattice effects | 4-neighbor vs 8-neighbor (2D) |

When p_stick < 1, particles can bounce and penetrate deeper into fjords, producing denser structures. The empirical relationship D(p_stick) ≈ 1.54 + 0.17 log₁₀(p_stick) shows how reducing stickiness increases fractal dimension toward the Euclidean value of 2.

---

## L-system mathematics for branching structures

L-systems (Lindenmayer systems), introduced in 1968 for modeling filamentous algae, are parallel rewriting systems that naturally capture the recursive self-similarity of branching organisms. Unlike sequential Chomsky grammars, L-systems apply production rules **simultaneously** to all symbols—reflecting parallel cell division.

### Formal definition

A deterministic context-free L-system (D0L) is the ordered triple G = ⟨V, ω, P⟩ where:
- **V** = alphabet (set of symbols)
- **ω ∈ V⁺** = axiom (initial string)
- **P ⊂ V × V*** = production rules

Production rule notation: a → χ (predecessor a yields successor string χ). For any symbol without explicit production, the identity rule a → a applies. Derivation proceeds by simultaneous replacement:

$$\omega = \mu_0 \Rightarrow \mu_1 \Rightarrow \mu_2 \Rightarrow \cdots \Rightarrow \mu_n$$

The classic algae example (Lindenmayer's original) with V = {A, B}, ω = A, and rules A → AB, B → A produces strings whose lengths follow the Fibonacci sequence.

### Classification and extensions

**Context-sensitive systems** allow productions to depend on neighboring symbols:
- 1L-system: checks one neighbor (left or right)
- 2L-system: checks both neighbors
- Notation: a_L < a > a_R → χ (symbol a with left context a_L and right context a_R)

**Stochastic L-systems** (S0L) assign probabilities to productions:
G_π = ⟨V, ω, P, π⟩ where π: P → (0,1] satisfies ∑π(p) = 1 for all productions sharing a predecessor. This generates natural specimen-to-specimen variation.

**Parametric L-systems** couple symbols with continuous parameters:
```
A(x, y) : condition → successor
```
Example: `A(age) : age > 5 → Flower` enables age-dependent development.

### Bracketed L-systems and turtle graphics

Brackets delimit branches using a stack-based turtle interpreter:
- `[` = push current state (position, orientation) onto stack
- `]` = pop state from stack

The turtle state in 2D is (x, y, α); in 3D it's (x, y, z, H⃗, L⃗, U⃗) where H⃗, L⃗, U⃗ are heading, left, and up orientation vectors.

| Symbol | 2D Command | 3D Command |
|--------|------------|------------|
| F | Move forward, draw | Move forward, draw |
| + | Turn left by δ | Yaw left (rotate around U⃗) |
| - | Turn right by δ | Yaw right |
| & | — | Pitch down (rotate around L⃗) |
| ^ | — | Pitch up |
| \\ | — | Roll left (rotate around H⃗) |
| / | — | Roll right |

### Example grammar for fruticose lichen

```
Axiom: A(1)
Rules:
  A(n) : n < maxOrder → F(segLen)[+(θ)A(n+1)][-(θ)A(n+1)]
  A(n) : n >= maxOrder → F(tipLen)
  F(len) → F(len * growthFactor)
```

With maxOrder = 5, θ = 25°, growthFactor = 1.1, this produces branching structures resembling *Usnea* morphology.

---

## Algorithms for 1D growth modeling

One-dimensional DLA and the Eden model provide foundations for understanding time-series growth and linear expansion along substrates.

### 1D DLA algorithm

```python
def dla_1d(num_particles, lattice_size):
    lattice = np.zeros(lattice_size, dtype=int)
    center = lattice_size // 2
    lattice[center] = 1
    max_extent = 0
    
    for _ in range(num_particles):
        # Spawn beyond current extent
        pos = center + (max_extent + 5) * np.random.choice([-1, 1])
        
        while True:
            pos += np.random.choice([-1, 1])  # Random walk
            
            if abs(pos - center) > max_extent + 50:  # Kill condition
                break
            
            if 0 < pos < lattice_size - 1:
                if lattice[pos - 1] or lattice[pos + 1]:  # Neighbor check
                    lattice[pos] = 1
                    max_extent = max(max_extent, abs(pos - center))
                    break
    
    return lattice
```

### Eden model for compact growth

The Eden model produces compact clusters with fractal surfaces—appropriate for dense lichen colonization:

```python
def eden_model_2d(num_cells, grid_size):
    grid = np.zeros((grid_size, grid_size), dtype=int)
    center = grid_size // 2
    grid[center, center] = 1
    boundary = [(center, center)]
    
    for _ in range(num_cells):
        cell = random.choice(boundary)
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            new_pos = (cell[0] + dx, cell[1] + dy)
            if 0 <= new_pos[0] < grid_size and 0 <= new_pos[1] < grid_size:
                if grid[new_pos] == 0:
                    grid[new_pos] = 1
                    boundary.append(new_pos)
                    break
        
        # Remove fully surrounded cells
        if all(grid[cell[0]+dx, cell[1]+dy] for dx, dy in directions 
               if 0 <= cell[0]+dx < grid_size and 0 <= cell[1]+dy < grid_size):
            boundary.remove(cell)
    
    return grid
```

---

## Two-dimensional DLA for crustose and foliose patterns

The classical 2D Witten-Sander model produces the characteristic dendritic patterns seen in radiating lichen growth.

### On-lattice implementation

```python
import numpy as np
from random import choice, random
from math import sin, cos, sqrt, pi

def dla_2d(num_particles, L=200):
    size = 2 * L + 1
    lattice = np.zeros((size, size), dtype=np.uint8)
    lattice[L, L] = 255  # Seed at center
    
    nn_steps = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    birth_offset, kill_offset = 5, 50
    max_radius = 0
    
    for _ in range(num_particles):
        # Spawn on circle
        angle = random() * 2 * pi
        birth_r = max_radius + birth_offset
        pos = [int(sin(angle) * birth_r), int(cos(angle) * birth_r)]
        
        while True:
            move = choice(nn_steps)
            pos[0] += move[0]
            pos[1] += move[1]
            
            dist_sq = pos[0]**2 + pos[1]**2
            kill_r = max_radius + kill_offset
            
            if dist_sq > kill_r**2:
                break  # Kill wandering particle
            
            # Check for occupied neighbor
            lpos = (pos[0] + L, pos[1] + L)
            for step in nn_steps:
                if lattice[lpos[0] + step[0], lpos[1] + step[1]]:
                    lattice[lpos] = 255
                    r = sqrt(dist_sq)
                    max_radius = max(max_radius, int(r))
                    break
            else:
                continue
            break
    
    return lattice
```

### Off-lattice implementation with continuous positions

Off-lattice DLA produces smoother, more isotropic clusters without lattice artifacts:

```python
def dla_2d_off_lattice(num_particles, particle_radius=1.0):
    from scipy.spatial import KDTree
    
    particles = [np.array([0.0, 0.0])]
    max_radius = particle_radius
    
    for _ in range(num_particles):
        spawn_r = max_radius + 5 * particle_radius
        angle = random.uniform(0, 2 * np.pi)
        walker = np.array([spawn_r * np.cos(angle), spawn_r * np.sin(angle)])
        
        tree = KDTree(particles)
        
        while True:
            # Random walk step
            step_angle = random.uniform(0, 2 * np.pi)
            walker += particle_radius * np.array([np.cos(step_angle), 
                                                   np.sin(step_angle)])
            
            dist, idx = tree.query(walker)
            
            if dist <= 2 * particle_radius:  # Contact
                particles.append(walker.copy())
                max_radius = max(max_radius, np.linalg.norm(walker))
                break
            
            if np.linalg.norm(walker) > 3 * spawn_r:  # Kill
                break
    
    return np.array(particles)
```

### Boundary conditions for biological realism

**Circular/radial growth** (standard): Appropriate for isolated thalli expanding from a colonization point.

**Substrate-edge growth**: Seeds along an edge simulate lichen colonizing rock cracks or bark margins:

```python
def substrate_edge_dla(num_particles, width, height):
    grid = np.zeros((height, width), dtype=int)
    # Seed along bottom edge
    for x in range(0, width, 10):
        grid[0, x] = 1
    # Particles spawn from top, stick when reaching colonized region
```

**Periodic boundaries**: For simulating continuous substrates without edge effects, wrap coordinates modulo grid dimensions.

---

## Three-dimensional algorithms for fruticose and rugose forms

3D DLA enables modeling of thallus thickness, rugose surface textures, and the full morphology of fruticose lichens.

### Voxel-based 3D DLA

```python
def dla_3d_voxel(num_particles, L=100):
    size = 2 * L + 1
    lattice = np.zeros((size, size, size), dtype=np.uint8)
    lattice[L, L, L] = 1
    
    nn_steps_6 = [(1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)]
    max_radius = 0
    
    for _ in range(num_particles):
        birth_r = max_radius + 5
        pos = random_point_on_sphere(birth_r)  # Uniform spherical sampling
        
        while True:
            move = random.choice(nn_steps_6)
            pos = [pos[i] + move[i] for i in range(3)]
            
            dist = sqrt(sum(p**2 for p in pos))
            if dist > max_radius + 50:
                break
            
            lpos = tuple(p + L for p in pos)
            for step in nn_steps_6:
                neighbor = tuple(lpos[i] + step[i] for i in range(3))
                if lattice[neighbor]:
                    lattice[lpos] = 1
                    max_radius = max(max_radius, int(dist))
                    break
            else:
                continue
            break
    
    return lattice

def random_point_on_sphere(radius):
    """Uniform random point on sphere using rejection or trigonometric method"""
    theta = random.uniform(0, 2 * np.pi)
    phi = np.arccos(2 * random.random() - 1)
    return [int(radius * np.sin(phi) * np.cos(theta)),
            int(radius * np.sin(phi) * np.sin(theta)),
            int(radius * np.cos(phi))]
```

### Computational optimization with octrees

Naive 3D DLA scales as O(N²) per particle; octree-based nearest-neighbor queries reduce this to O(N log N):

```python
class OctreeNode:
    def __init__(self, center, half_size, max_particles=8):
        self.center = np.array(center)
        self.half_size = half_size
        self.particles = []
        self.children = None
        self.max_particles = max_particles
    
    def insert(self, particle):
        if self.children is None:
            self.particles.append(particle)
            if len(self.particles) > self.max_particles:
                self._subdivide()
        else:
            octant = self._get_octant(particle)
            self.children[octant].insert(particle)
    
    def _subdivide(self):
        hs = self.half_size / 2
        self.children = []
        for i in range(8):
            offset = np.array([
                hs if i & 1 else -hs,
                hs if i & 2 else -hs,
                hs if i & 4 else -hs
            ])
            self.children.append(OctreeNode(self.center + offset, hs))
        
        for p in self.particles:
            self.children[self._get_octant(p)].insert(p)
        self.particles = []
```

For practical implementations, `scipy.spatial.cKDTree` provides highly optimized nearest-neighbor queries.

### Diameter-scaled L-systems for *Cladonia rangiferina* morphology

Reindeer lichen (*Cladonia rangiferina*) exhibits characteristic **diameter scaling**: primary podetia are thickest at the base (2-4 mm), with each dichotomous or trichotomous branching producing progressively thinner segments down to terminal tips of ~0.3 mm. This follows **Murray's Law** (or the pipe model), where the sum of cross-sectional areas is approximately conserved across branching:

$d_{\text{parent}}^n = \sum_{i} d_{\text{child}_i}^n$

For dichotomous branching with exponent n ≈ 2-3 (Murray's Law uses n=3 for vascular systems; lichens often closer to n=2):

$d_{\text{child}} = d_{\text{parent}} / 2^{1/n}$

#### Parametric L-system with width scaling

```python
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class BranchSegment:
    """3D branch segment with position, orientation, and diameter"""
    start: np.ndarray
    end: np.ndarray
    start_width: float
    end_width: float
    order: int  # Branching order (0 = main stem)

def cladonia_lsystem(
    iterations: int = 5,
    base_length: float = 10.0,
    base_width: float = 2.0,
    length_ratio: float = 0.7,        # Each generation shorter
    width_ratio: float = 0.65,        # Murray's law scaling (~1/2^(1/2.5))
    branch_angle: float = 25.0,       # Degrees from parent axis
    taper_ratio: float = 0.85,        # Within-segment taper
    branching_type: str = 'dichotomous',  # or 'trichotomous'
    stochastic: bool = True,
    angle_variance: float = 10.0,     # Random angle variation
    length_variance: float = 0.15     # Random length variation
) -> List[BranchSegment]:
    """
    Generate Cladonia rangiferina-like branching with diameter scaling.
    
    Parameters:
    -----------
    iterations : int
        Number of branching generations
    base_length : float
        Length of primary podetium segment (mm)
    base_width : float
        Diameter at base of primary podetium (mm)
    length_ratio : float
        Length multiplier per generation (0.6-0.8 typical)
    width_ratio : float
        Width multiplier per generation (Murray's law: ~0.63-0.71)
    branch_angle : float
        Angle between child branches and parent axis
    taper_ratio : float
        End width / start width within single segment
    branching_type : str
        'dichotomous' (2-way) or 'trichotomous' (3-way)
    stochastic : bool
        Add random variation to angles and lengths
    """
    
    segments = []
    
    # Stack entries: (position, heading, up_vector, length, width, order)
    initial_heading = np.array([0.0, 0.0, 1.0])  # Growing upward
    initial_up = np.array([0.0, 1.0, 0.0])
    stack = [(np.array([0.0, 0.0, 0.0]), initial_heading, initial_up, 
              base_length, base_width, 0)]
    
    while stack:
        pos, heading, up, length, width, order = stack.pop()
        
        if order > iterations:
            continue
        
        # Apply stochastic variation
        if stochastic and order > 0:
            length *= (1 + np.random.uniform(-length_variance, length_variance))
            
        # Create this segment with taper
        end_pos = pos + heading * length
        end_width = width * taper_ratio
        
        segments.append(BranchSegment(
            start=pos.copy(),
            end=end_pos.copy(),
            start_width=width,
            end_width=end_width,
            order=order
        ))
        
        # Terminal condition
        if order >= iterations:
            continue
        
        # Calculate child parameters
        child_length = length * length_ratio
        child_width = end_width * width_ratio  # Scale from tapered end
        
        # Generate branch directions
        right = np.cross(heading, up)
        right = right / np.linalg.norm(right)
        
        if branching_type == 'dichotomous':
            angles = [branch_angle, -branch_angle]
            rotation_axes = [right, right]
        else:  # trichotomous
            angles = [branch_angle, -branch_angle, branch_angle]
            # Third branch rotates around heading first
            rotation_axes = [right, right, up]
        
        for i, (angle, axis) in enumerate(zip(angles, rotation_axes)):
            if stochastic:
                angle += np.random.uniform(-angle_variance, angle_variance)
            
            # Rotate heading around axis
            child_heading = rotate_vector(heading, axis, np.radians(angle))
            child_heading = child_heading / np.linalg.norm(child_heading)
            
            # Update up vector to stay perpendicular
            child_up = np.cross(child_heading, right)
            child_up = child_up / np.linalg.norm(child_up)
            
            stack.append((end_pos.copy(), child_heading, child_up,
                         child_length, child_width, order + 1))
    
    return segments

def rotate_vector(v: np.ndarray, axis: np.ndarray, theta: float) -> np.ndarray:
    """Rotate vector v around axis by angle theta (Rodrigues' formula)"""
    axis = axis / np.linalg.norm(axis)
    return (v * np.cos(theta) + 
            np.cross(axis, v) * np.sin(theta) + 
            axis * np.dot(axis, v) * (1 - np.cos(theta)))
```

#### Rendering tapered cylindrical branches

```python
def render_cladonia_pyvista(segments: List[BranchSegment], 
                            resolution: int = 12) -> 'pyvista.PolyData':
    """Render branch segments as tapered cylinders using PyVista"""
    import pyvista as pv
    
    meshes = []
    
    # Color by branch order (lighter = higher order)
    cmap_values = []
    
    for seg in segments:
        # Create tapered cylinder (frustum)
        direction = seg.end - seg.start
        height = np.linalg.norm(direction)
        center = (seg.start + seg.end) / 2
        
        cylinder = pv.CylinderStructured(
            center=center,
            direction=direction,
            radius=[seg.start_width/2, seg.end_width/2],
            height=height,
            theta_resolution=resolution,
            z_resolution=2
        )
        
        meshes.append(cylinder)
        cmap_values.append(seg.order)
    
    # Combine all meshes
    combined = meshes[0]
    for mesh in meshes[1:]:
        combined = combined.merge(mesh)
    
    return combined

def render_cladonia_matplotlib(segments: List[BranchSegment], 
                                elev: float = 20, 
                                azim: float = 45):
    """Simple 3D visualization with matplotlib"""
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Color gradient: darker at base, lighter at tips
    max_order = max(seg.order for seg in segments)
    colors = plt.cm.YlGn(np.linspace(0.3, 0.9, max_order + 1))
    
    for seg in segments:
        xs = [seg.start[0], seg.end[0]]
        ys = [seg.start[1], seg.end[1]]
        zs = [seg.start[2], seg.end[2]]
        
        # Line width proportional to branch diameter
        lw = seg.start_width * 2  # Scale for visibility
        
        ax.plot(xs, ys, zs, 
                color=colors[seg.order], 
                linewidth=lw,
                solid_capstyle='round')
    
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')
    ax.view_init(elev=elev, azim=azim)
    ax.set_title('Cladonia rangiferina L-system Model')
    
    # Equal aspect ratio
    max_range = max(
        max(seg.end[i] for seg in segments) - min(seg.start[i] for seg in segments)
        for i in range(3)
    )
    for setter, idx in [(ax.set_xlim, 0), (ax.set_ylim, 1), (ax.set_zlim, 2)]:
        mid = (max(seg.end[idx] for seg in segments) + 
               min(seg.start[idx] for seg in segments)) / 2
        setter([mid - max_range/2, mid + max_range/2])
    
    plt.tight_layout()
    return fig, ax
```

#### Biological parameter ranges for *Cladonia* species

| Parameter | C. rangiferina | C. stellaris | C. arbuscula | Description |
|-----------|----------------|--------------|--------------|-------------|
| `base_width` | 2.0-4.0 mm | 1.5-3.0 mm | 1.0-2.5 mm | Primary podetium diameter |
| `width_ratio` | 0.63-0.71 | 0.60-0.68 | 0.65-0.72 | Murray's law exponent n≈2.3-2.8 |
| `length_ratio` | 0.65-0.75 | 0.70-0.80 | 0.60-0.70 | Segment length scaling |
| `branch_angle` | 20-35° | 25-40° | 15-30° | Dichotomy angle |
| `taper_ratio` | 0.80-0.90 | 0.85-0.92 | 0.82-0.88 | Within-segment taper |
| `iterations` | 4-6 | 5-7 | 4-5 | Branching generations |
| `branching_type` | dichotomous | di/trichotomous | dichotomous | Branching pattern |

#### Deriving width_ratio from Murray's Law exponent

```python
def murray_width_ratio(n_children: int = 2, murray_exponent: float = 2.5) -> float:
    """
    Calculate width ratio from Murray's Law.
    
    Murray's Law: d_parent^n = sum(d_child^n)
    For equal children: d_child = d_parent / n_children^(1/n)
    
    Parameters:
    -----------
    n_children : int
        Number of child branches (2 for dichotomous, 3 for trichotomous)
    murray_exponent : float
        Exponent n in Murray's Law (2 for area-preserving, 3 for volume flow)
        Lichens typically: 2.0-2.8
    
    Returns:
    --------
    float
        Width ratio (child_diameter / parent_diameter)
    """
    return 1.0 / (n_children ** (1.0 / murray_exponent))

# Examples:
# Dichotomous, n=2.0 (area-preserving): ratio = 0.707
# Dichotomous, n=2.5: ratio = 0.659
# Dichotomous, n=3.0 (Murray's original): ratio = 0.630
# Trichotomous, n=2.5: ratio = 0.552
```

### Combining DLA with L-systems for fruticose morphology

The most realistic fruticose simulations use L-systems for the branching skeleton and DLA for surface detail:

```python
def fruticose_hybrid(l_iterations=4, dla_particles_per_segment=100):
    # Step 1: Generate L-system skeleton
    axiom = "F"
    rules = {"F": "F[+F][-F]F"}
    angle = 25  # degrees
    
    l_string = axiom
    for _ in range(l_iterations):
        l_string = "".join(rules.get(c, c) for c in l_string)
    
    # Step 2: Interpret as 3D branch segments
    segments = interpret_turtle_3d(l_string, angle)
    
    # Step 3: Apply constrained DLA around each segment
    all_particles = []
    for start, end in segments:
        segment_particles = dla_along_cylinder(
            start, end, 
            radius=0.1, 
            num_particles=dla_particles_per_segment
        )
        all_particles.extend(segment_particles)
    
    return segments, all_particles

def interpret_turtle_3d(l_string, angle):
    segments = []
    pos = np.array([0.0, 0.0, 0.0])
    heading = np.array([0.0, 1.0, 0.0])
    stack = []
    segment_length = 1.0
    
    for char in l_string:
        if char == 'F':
            new_pos = pos + heading * segment_length
            segments.append((pos.copy(), new_pos.copy()))
            pos = new_pos
        elif char == '+':
            heading = rotate_y(heading, np.radians(angle))
        elif char == '-':
            heading = rotate_y(heading, np.radians(-angle))
        elif char == '[':
            stack.append((pos.copy(), heading.copy()))
        elif char == ']':
            pos, heading = stack.pop()
    
    return segments
```

### Surface roughness (rugose) through fractal noise

Add microscale texture using Perlin noise or fractal Brownian motion:

```python
def add_rugose_texture(surface_grid, roughness=0.3, octaves=4):
    from noise import pnoise3
    
    textured = surface_grid.astype(float)
    
    for i, j, k in np.ndindex(surface_grid.shape):
        if surface_grid[i, j, k] > 0:
            noise_val = 0
            amplitude = roughness
            frequency = 0.1
            
            for _ in range(octaves):
                noise_val += amplitude * pnoise3(i * frequency, 
                                                  j * frequency, 
                                                  k * frequency)
                amplitude *= 0.5
                frequency *= 2
            
            textured[i, j, k] += noise_val
    
    return textured
```

---

## Hybrid and alternative modeling approaches

Beyond pure DLA and L-systems, several hybrid and alternative methods offer additional capabilities.

### Reaction-diffusion systems

Turing patterns from reaction-diffusion provide an alternative for surface patterning. The **Gray-Scott model** is particularly versatile:

$$\frac{\partial u}{\partial t} = D_u \nabla^2 u - uv^2 + f(1-u)$$
$$\frac{\partial v}{\partial t} = D_v \nabla^2 v + uv^2 - (f+k)v$$

Parameters f (feed rate) and k (kill rate) control pattern morphology—spots, stripes, spirals, or coral-like structures. This complements DLA for generating photobiont distribution patterns within thalli.

### Open DLA with environmental constraints

Desbenoit et al.'s (2004) **Open DLA** model incorporates environmental sensitivity through aggregation probability:

$$P(p) = E(p) \times A(p)$$

where the **aggregation function** A(p) = α + (1-α) × exp(-σ(n(p)-τ)²) depends on local neighbor density n(p), and the **environment function** E(p) combines light I(p), moisture W(p), and substrate properties. This produces biologically realistic colonization patterns.

### Multi-scale modeling

For comprehensive lichen simulation:
1. **Macro scale**: L-system or DLA for thallus morphology
2. **Meso scale**: Reaction-diffusion for internal structure
3. **Micro scale**: Cellular automata for hyphal tip growth

The VirtualLeaf framework and similar approaches combine individual cell behavior with continuous fields for nutrient/hormone diffusion.

---

## Implementation considerations for Python and Jupyter

### Recommended library stack

| Category | Libraries | Purpose |
|----------|-----------|---------|
| Core computation | NumPy, SciPy | Arrays, sparse matrices, spatial queries |
| JIT compilation | Numba | 10-100× speedup for inner loops |
| 2D visualization | matplotlib | Static plots, animations |
| 3D visualization | PyVista, Mayavi, Open3D | Volume rendering, mesh display |
| GPU acceleration | CuPy, PyTorch | Large-scale simulations |
| Noise generation | noise, opensimplex | Rugose textures |
| Mesh processing | trimesh, PyMesh | 3D output formats |
| L-systems | L-Py (OpenAlea) | Full L-system framework |

### Numba acceleration example

```python
from numba import njit

@njit
def dla_step_numba(lattice, pos, nn_steps, L):
    """JIT-compiled neighbor check and walk step"""
    for _ in range(1000):  # Max steps per particle
        move_idx = np.random.randint(0, len(nn_steps))
        pos[0] += nn_steps[move_idx, 0]
        pos[1] += nn_steps[move_idx, 1]
        
        lpos_x, lpos_y = pos[0] + L, pos[1] + L
        for step in nn_steps:
            if lattice[lpos_x + step[0], lpos_y + step[1]]:
                lattice[lpos_x, lpos_y] = 1
                return True
    return False
```

### Visualization strategy

**2D**: Use `matplotlib.animation.FuncAnimation` for growth animations, `imshow` for final clusters.

**3D voxels**: PyVista's `add_volume` or Mayavi's `contour3d` for volumetric rendering.

**3D point clouds**: Open3D for particle-based visualizations with customizable rendering.

**Export formats**: STL/OBJ meshes via trimesh for 3D printing or external rendering.

---

---

## Snowflake Yeast L-System Model

Snowflake yeast (*Saccharomyces cerevisiae* with ACE2 knockout) represent a fundamentally different growth paradigm from lichens—they form through **incomplete cytokinesis** where daughter cells remain permanently attached to mother cells via chitinous bud scars. This creates fractal-like branched tree structures that serve as a powerful model system for studying the evolution of multicellularity.

### Biological parameters from Ratcliff lab research

| Parameter | Ancestral | Evolved (Macroscopic) | Description |
|-----------|-----------|----------------------|-------------|
| Cell aspect ratio | ~1.2 | ~2.7 | Length/width of ellipsoidal cells |
| Cluster size | ~100 cells | ~20,000× larger | Selection for settling drives size increase |
| Material toughness | Gelatin-like | Wood-like (10,000× tougher) | Entanglement enables mechanical strength |
| Branching topology | Tree (fixed) | Tree with entanglement | Cells cannot reposition after division |
| Budding polar angle | Variable | Variable | Angle from mother's long axis |
| Budding azimuthal angle | Random | Random | Rotation around polar axis |

### L-system formalism for cell division

Unlike lichen L-systems where symbols represent branch segments, snowflake yeast L-systems treat **each symbol as a cell** with associated parameters for position, orientation, size, and age.

```python
import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import random

@dataclass
class YeastCell:
    """Represents a single yeast cell in the snowflake cluster"""
    position: np.ndarray           # 3D center position
    orientation: np.ndarray        # Long axis direction (unit vector)
    major_axis: float              # Length along orientation
    minor_axis: float              # Width perpendicular to orientation
    age: int = 0                   # Division cycles since birth
    generation: int = 0            # Distance from founder cell
    bud_sites_used: int = 0        # Number of daughters produced
    max_buds: int = 5              # Maximum daughter cells
    parent_id: Optional[int] = None
    cell_id: int = 0
    
    @property
    def aspect_ratio(self) -> float:
        return self.major_axis / self.minor_axis
    
    def can_divide(self) -> bool:
        """Check if cell can produce another daughter"""
        return self.bud_sites_used < self.max_buds

@dataclass
class SnowflakeYeastParams:
    """Parameters controlling snowflake yeast morphology"""
    # Cell geometry
    initial_major_axis: float = 5.0      # μm, ancestral ~5μm
    initial_minor_axis: float = 4.2      # μm, gives aspect ratio ~1.2
    aspect_ratio_evolution: float = 1.0  # Multiplier (1.0=ancestral, 2.25=evolved)
    
    # Budding geometry  
    bud_polar_angle_mean: float = 45.0   # Degrees from mother's long axis
    bud_polar_angle_std: float = 15.0    # Stochastic variation
    bud_size_ratio: float = 0.6          # Daughter size relative to mother at birth
    
    # Growth dynamics
    growth_rate: float = 1.05            # Size increase per division cycle
    max_divisions_per_cell: int = 5      # Bud site limitation
    division_probability: float = 0.7    # Per-cycle division probability
    
    # Cluster properties
    max_generations: int = 8             # Tree depth
    max_cells: int = 500                 # Computational limit
    
    # Physical constraints
    enable_collision_detection: bool = True
    repulsion_strength: float = 0.1      # Soft collision response


class SnowflakeYeastLSystem:
    """
    L-system simulation of snowflake yeast cluster growth.
    
    Growth rule (informal):
        Mother(age, gen) → Mother(age+1, gen) + [Daughter(0, gen+1)] 
                           (with probability p, if buds available)
    
    The bracket notation indicates spatial branching - the daughter
    is positioned at a bud site on the mother's surface.
    """
    
    def __init__(self, params: SnowflakeYeastParams = None):
        self.params = params or SnowflakeYeastParams()
        self.cells: List[YeastCell] = []
        self.next_id = 0
        self._initialize_founder()
    
    def _initialize_founder(self):
        """Create the founding cell at origin"""
        # Apply aspect ratio evolution to initial cell shape
        major = self.params.initial_major_axis
        minor = self.params.initial_minor_axis / self.params.aspect_ratio_evolution
        
        founder = YeastCell(
            position=np.array([0.0, 0.0, 0.0]),
            orientation=np.array([0.0, 0.0, 1.0]),  # Pointing up
            major_axis=major,
            minor_axis=minor,
            generation=0,
            cell_id=self.next_id
        )
        self.cells.append(founder)
        self.next_id += 1
    
    def _get_bud_position_and_orientation(self, mother: YeastCell) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate daughter cell position and orientation based on budding geometry.
        
        Budding occurs at a polar angle from the mother's long axis,
        with random azimuthal rotation around that axis.
        """
        # Polar angle (from mother's long axis)
        polar_angle = np.radians(
            self.params.bud_polar_angle_mean + 
            np.random.normal(0, self.params.bud_polar_angle_std)
        )
        polar_angle = np.clip(polar_angle, np.radians(20), np.radians(80))
        
        # Random azimuthal angle (rotation around mother's axis)
        azimuthal_angle = np.random.uniform(0, 2 * np.pi)
        
        # Build local coordinate frame for mother
        mother_axis = mother.orientation / np.linalg.norm(mother.orientation)
        
        # Find perpendicular vectors
        if abs(mother_axis[0]) < 0.9:
            perp1 = np.cross(mother_axis, np.array([1, 0, 0]))
        else:
            perp1 = np.cross(mother_axis, np.array([0, 1, 0]))
        perp1 = perp1 / np.linalg.norm(perp1)
        perp2 = np.cross(mother_axis, perp1)
        
        # Bud direction in mother's frame
        bud_direction = (
            np.cos(polar_angle) * mother_axis +
            np.sin(polar_angle) * np.cos(azimuthal_angle) * perp1 +
            np.sin(polar_angle) * np.sin(azimuthal_angle) * perp2
        )
        bud_direction = bud_direction / np.linalg.norm(bud_direction)
        
        # Position daughter at mother's surface along bud direction
        # Account for ellipsoidal shape
        surface_dist = self._ellipsoid_radius(mother, bud_direction)
        daughter_radius = mother.minor_axis * self.params.bud_size_ratio / 2
        
        bud_position = mother.position + bud_direction * (surface_dist + daughter_radius)
        
        # Daughter orientation: slight deviation from bud direction
        orientation_noise = np.random.normal(0, 0.1, 3)
        daughter_orientation = bud_direction + orientation_noise
        daughter_orientation = daughter_orientation / np.linalg.norm(daughter_orientation)
        
        return bud_position, daughter_orientation
    
    def _ellipsoid_radius(self, cell: YeastCell, direction: np.ndarray) -> float:
        """Calculate distance from cell center to surface along given direction"""
        # Project direction onto cell's principal axes
        cos_theta = abs(np.dot(direction, cell.orientation))
        sin_theta = np.sqrt(1 - cos_theta**2)
        
        # Ellipsoid parametric radius
        a = cell.major_axis / 2  # Semi-major
        b = cell.minor_axis / 2  # Semi-minor
        
        # r = ab / sqrt((b*cos)^2 + (a*sin)^2)
        r = (a * b) / np.sqrt((b * cos_theta)**2 + (a * sin_theta)**2)
        return r
    
    def _check_collision(self, new_cell: YeastCell) -> bool:
        """Check if new cell overlaps with existing cells (except parent)"""
        if not self.params.enable_collision_detection:
            return False
            
        for cell in self.cells:
            if cell.cell_id == new_cell.parent_id:
                continue
            
            dist = np.linalg.norm(new_cell.position - cell.position)
            min_dist = (cell.minor_axis + new_cell.minor_axis) / 2 * 0.8
            
            if dist < min_dist:
                return True
        return False
    
    def step(self) -> int:
        """
        Execute one division cycle (L-system rewriting step).
        Returns number of new cells created.
        """
        if len(self.cells) >= self.params.max_cells:
            return 0
        
        new_cells = []
        
        for cell in self.cells:
            # Age all cells
            cell.age += 1
            
            # Growth: cells increase in size slightly
            cell.major_axis *= self.params.growth_rate
            cell.minor_axis *= self.params.growth_rate
            
            # Division check
            if not cell.can_divide():
                continue
            if cell.generation >= self.params.max_generations:
                continue
            if random.random() > self.params.division_probability:
                continue
            if len(self.cells) + len(new_cells) >= self.params.max_cells:
                break
            
            # Create daughter cell
            bud_pos, bud_orient = self._get_bud_position_and_orientation(cell)
            
            daughter = YeastCell(
                position=bud_pos,
                orientation=bud_orient,
                major_axis=cell.major_axis * self.params.bud_size_ratio,
                minor_axis=cell.minor_axis * self.params.bud_size_ratio,
                generation=cell.generation + 1,
                parent_id=cell.cell_id,
                cell_id=self.next_id
            )
            
            # Collision check
            if not self._check_collision(daughter):
                new_cells.append(daughter)
                cell.bud_sites_used += 1
                self.next_id += 1
        
        self.cells.extend(new_cells)
        return len(new_cells)
    
    def grow(self, cycles: int = 10) -> 'SnowflakeYeastLSystem':
        """Run multiple division cycles"""
        for _ in range(cycles):
            added = self.step()
            if added == 0 and len(self.cells) > 1:
                break  # No more growth possible
        return self
    
    def get_cell_positions(self) -> np.ndarray:
        """Return Nx3 array of cell centers"""
        return np.array([c.position for c in self.cells])
    
    def get_cell_sizes(self) -> np.ndarray:
        """Return Nx2 array of (major_axis, minor_axis)"""
        return np.array([[c.major_axis, c.minor_axis] for c in self.cells])
    
    def get_connectivity(self) -> List[Tuple[int, int]]:
        """Return list of (parent_id, child_id) edges for tree visualization"""
        edges = []
        for cell in self.cells:
            if cell.parent_id is not None:
                edges.append((cell.parent_id, cell.cell_id))
        return edges
    
    def get_generations(self) -> np.ndarray:
        """Return array of generation numbers for coloring"""
        return np.array([c.generation for c in self.cells])
```

### Visualization with matplotlib and PyVista

```python
def visualize_snowflake_matplotlib(model: SnowflakeYeastLSystem,
                                    elev: float = 20,
                                    azim: float = 45,
                                    figsize: Tuple[int, int] = (12, 10)):
    """
    3D visualization of snowflake yeast cluster using matplotlib.
    Cells rendered as ellipsoids via wireframe approximation.
    """
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection='3d')
    
    # Color by generation
    generations = model.get_generations()
    max_gen = max(generations) if len(generations) > 0 else 1
    colors = plt.cm.viridis(generations / max_gen)
    
    # Draw cells as points with size proportional to cell volume
    positions = model.get_cell_positions()
    sizes = model.get_cell_sizes()
    
    # Point size ~ cell volume
    volumes = sizes[:, 0] * sizes[:, 1]**2  # Prolate ellipsoid approximation
    point_sizes = volumes / volumes.max() * 200
    
    ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2],
               c=colors, s=point_sizes, alpha=0.7, edgecolors='black', linewidth=0.5)
    
    # Draw connectivity tree
    edges = model.get_connectivity()
    for parent_id, child_id in edges:
        parent = next(c for c in model.cells if c.cell_id == parent_id)
        child = next(c for c in model.cells if c.cell_id == child_id)
        
        xs = [parent.position[0], child.position[0]]
        ys = [parent.position[1], child.position[1]]
        zs = [parent.position[2], child.position[2]]
        
        ax.plot(xs, ys, zs, 'k-', linewidth=0.5, alpha=0.3)
    
    ax.set_xlabel('X (μm)')
    ax.set_ylabel('Y (μm)')
    ax.set_zlabel('Z (μm)')
    ax.set_title(f'Snowflake Yeast Cluster ({len(model.cells)} cells)')
    ax.view_init(elev=elev, azim=azim)
    
    # Equal aspect ratio
    max_range = np.max([
        positions[:, i].max() - positions[:, i].min()
        for i in range(3)
    ]) / 2
    mid = positions.mean(axis=0)
    ax.set_xlim(mid[0] - max_range, mid[0] + max_range)
    ax.set_ylim(mid[1] - max_range, mid[1] + max_range)
    ax.set_zlim(mid[2] - max_range, mid[2] + max_range)
    
    plt.tight_layout()
    return fig, ax


def visualize_snowflake_pyvista(model: SnowflakeYeastLSystem,
                                 resolution: int = 16) -> 'pyvista.PolyData':
    """
    High-quality 3D rendering using PyVista with true ellipsoid geometry.
    """
    import pyvista as pv
    
    meshes = []
    generations = model.get_generations()
    max_gen = max(generations) if len(generations) > 0 else 1
    
    for cell in model.cells:
        # Create ellipsoid for each cell
        sphere = pv.Sphere(radius=1.0, 
                          center=(0, 0, 0),
                          theta_resolution=resolution,
                          phi_resolution=resolution)
        
        # Scale to ellipsoid dimensions
        sphere.points[:, 2] *= cell.major_axis / 2  # Z is major axis initially
        sphere.points[:, 0] *= cell.minor_axis / 2
        sphere.points[:, 1] *= cell.minor_axis / 2
        
        # Rotate to match cell orientation
        # Calculate rotation from [0,0,1] to cell.orientation
        z_axis = np.array([0, 0, 1])
        target = cell.orientation / np.linalg.norm(cell.orientation)
        
        if not np.allclose(z_axis, target):
            rotation_axis = np.cross(z_axis, target)
            rotation_axis = rotation_axis / (np.linalg.norm(rotation_axis) + 1e-10)
            angle = np.arccos(np.clip(np.dot(z_axis, target), -1, 1))
            
            # Rodrigues rotation
            sphere.rotate_vector(rotation_axis * np.degrees(angle), 
                                point=(0, 0, 0), inplace=True)
        
        # Translate to position
        sphere.translate(cell.position, inplace=True)
        
        # Add generation as scalar data for coloring
        sphere['generation'] = np.full(sphere.n_points, cell.generation)
        
        meshes.append(sphere)
    
    # Combine all cell meshes
    combined = meshes[0]
    for mesh in meshes[1:]:
        combined = combined.merge(mesh)
    
    return combined


def create_snowflake_animation(params: SnowflakeYeastParams,
                                max_cycles: int = 15,
                                save_path: str = 'snowflake_growth.gif'):
    """
    Create animated GIF of snowflake yeast growth.
    """
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation, PillowWriter
    
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Storage for animation frames
    frames_data = []
    
    # Run simulation and store snapshots
    model = SnowflakeYeastLSystem(params)
    for cycle in range(max_cycles):
        positions = model.get_cell_positions().copy()
        sizes = model.get_cell_sizes().copy()
        generations = model.get_generations().copy()
        frames_data.append((positions, sizes, generations, len(model.cells)))
        model.step()
    
    def update(frame):
        ax.clear()
        positions, sizes, generations, n_cells = frames_data[frame]
        
        if len(positions) == 0:
            return
        
        max_gen = max(generations) if len(generations) > 0 else 1
        colors = plt.cm.viridis(generations / max(max_gen, 1))
        volumes = sizes[:, 0] * sizes[:, 1]**2
        point_sizes = volumes / (volumes.max() + 1e-10) * 200
        
        ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2],
                   c=colors, s=point_sizes, alpha=0.7)
        
        ax.set_xlabel('X (μm)')
        ax.set_ylabel('Y (μm)')
        ax.set_zlabel('Z (μm)')
        ax.set_title(f'Cycle {frame}: {n_cells} cells')
        
        # Fixed axis limits for stable animation
        ax.set_xlim(-50, 50)
        ax.set_ylim(-50, 50)
        ax.set_zlim(-50, 50)
    
    anim = FuncAnimation(fig, update, frames=len(frames_data), interval=500)
    anim.save(save_path, writer=PillowWriter(fps=2))
    plt.close()
    
    return save_path
```

### Simulating evolved macroscopic morphology

The Ratcliff lab observed that over ~3,000 generations, snowflake yeast evolved:
1. **Elongated cells** (aspect ratio 1.2 → 2.7)
2. **Entanglement** where branches grow around each other
3. **Dramatically increased toughness** (10,000×)

```python
def compare_ancestral_vs_evolved():
    """
    Compare ancestral vs evolved macroscopic snowflake yeast morphology.
    """
    # Ancestral parameters (week 1 of Ratcliff experiments)
    ancestral_params = SnowflakeYeastParams(
        initial_major_axis=5.0,
        initial_minor_axis=4.2,          # Aspect ratio ~1.2
        aspect_ratio_evolution=1.0,
        bud_polar_angle_mean=45.0,
        max_generations=6,
        max_cells=300,
        division_probability=0.8
    )
    
    # Evolved parameters (after 600+ transfers, ~3000 generations)
    evolved_params = SnowflakeYeastParams(
        initial_major_axis=5.0,
        initial_minor_axis=1.85,          # Aspect ratio ~2.7
        aspect_ratio_evolution=2.25,      # 2.7/1.2
        bud_polar_angle_mean=50.0,        # Slightly different budding
        max_generations=10,               # Can grow larger
        max_cells=1000,
        division_probability=0.85,
        enable_collision_detection=True   # Enables entanglement effects
    )
    
    # Run both simulations
    ancestral = SnowflakeYeastLSystem(ancestral_params).grow(cycles=20)
    evolved = SnowflakeYeastLSystem(evolved_params).grow(cycles=25)
    
    return ancestral, evolved


# Entanglement model extension
class EntangledSnowflakeYeast(SnowflakeYeastLSystem):
    """
    Extended model that allows branch entanglement.
    When collision is detected, instead of rejecting the cell,
    it can be repositioned to wrap around existing structure.
    """
    
    def __init__(self, params: SnowflakeYeastParams):
        super().__init__(params)
        self.entanglement_factor = 0.3  # Probability of entangling vs rejecting
    
    def _resolve_collision(self, new_cell: YeastCell) -> Optional[YeastCell]:
        """
        Attempt to resolve collision by repositioning cell.
        Simulates the entanglement behavior of evolved macroscopic yeast.
        """
        if random.random() > self.entanglement_factor:
            return None  # Reject cell
        
        # Find nearby cells
        nearby = []
        for cell in self.cells:
            if cell.cell_id == new_cell.parent_id:
                continue
            dist = np.linalg.norm(new_cell.position - cell.position)
            if dist < cell.major_axis * 2:
                nearby.append(cell)
        
        if not nearby:
            return new_cell
        
        # Try to reposition around nearby cells
        for attempt in range(10):
            # Random perturbation
            offset = np.random.normal(0, new_cell.minor_axis * 0.5, 3)
            test_pos = new_cell.position + offset
            
            # Check if this position is valid
            valid = True
            for cell in self.cells:
                if cell.cell_id == new_cell.parent_id:
                    continue
                dist = np.linalg.norm(test_pos - cell.position)
                min_dist = (cell.minor_axis + new_cell.minor_axis) / 2 * 0.9
                if dist < min_dist:
                    valid = False
                    break
            
            if valid:
                new_cell.position = test_pos
                return new_cell
        
        return None  # Could not find valid position
```

### Quantitative analysis functions

```python
def analyze_snowflake_cluster(model: SnowflakeYeastLSystem) -> dict:
    """
    Compute morphological metrics for snowflake yeast cluster.
    Matches metrics used in Ratcliff lab publications.
    """
    positions = model.get_cell_positions()
    sizes = model.get_cell_sizes()
    generations = model.get_generations()
    
    if len(positions) < 2:
        return {}
    
    # Cluster radius (from centroid to furthest cell)
    centroid = positions.mean(axis=0)
    distances = np.linalg.norm(positions - centroid, axis=1)
    
    # Radius of gyration
    Rg = np.sqrt(np.mean(distances**2))
    
    # Fractal dimension estimate (box counting approximation)
    # Using mass-radius relation: N(r) ~ r^D
    r_bins = np.linspace(distances.min(), distances.max(), 20)
    N_within = [np.sum(distances <= r) for r in r_bins]
    
    # Fit log-log slope
    valid = (np.array(N_within) > 0) & (r_bins > 0)
    if np.sum(valid) > 3:
        log_r = np.log(r_bins[valid])
        log_N = np.log(np.array(N_within)[valid])
        D_fractal = np.polyfit(log_r, log_N, 1)[0]
    else:
        D_fractal = np.nan
    
    # Average aspect ratio
    aspect_ratios = sizes[:, 0] / sizes[:, 1]
    
    # Tree statistics
    max_gen = generations.max()
    cells_per_gen = [np.sum(generations == g) for g in range(max_gen + 1)]
    
    # Branching ratio (average children per parent)
    edges = model.get_connectivity()
    parent_counts = {}
    for parent_id, _ in edges:
        parent_counts[parent_id] = parent_counts.get(parent_id, 0) + 1
    avg_branching = np.mean(list(parent_counts.values())) if parent_counts else 1.0
    
    return {
        'n_cells': len(model.cells),
        'cluster_radius': distances.max(),
        'radius_of_gyration': Rg,
        'fractal_dimension': D_fractal,
        'mean_aspect_ratio': aspect_ratios.mean(),
        'std_aspect_ratio': aspect_ratios.std(),
        'max_generation': max_gen,
        'cells_per_generation': cells_per_gen,
        'avg_branching_ratio': avg_branching,
        'compactness': len(model.cells) / (4/3 * np.pi * Rg**3)  # Cells per unit volume
    }
```

---

---

## DLA Patterns in Bacteria, Slime Molds, and Fungi

The mathematical framework of Diffusion-Limited Aggregation extends far beyond lichens to explain fractal growth patterns across the microbial kingdom. Research from the Kolter laboratory at Harvard (documented in the Quanta Magazine article "The Beautiful Intelligence of Bacteria and Other Microbes") and foundational work by Fujikawa, Matsushita, and Ben-Jacob demonstrate that DLA is a universal growth mechanism when nutrient diffusion limits colony expansion.

### Bacterial Colony DLA: The Fujikawa-Matsushita Discovery

The seminal 1989 paper by Fujikawa and Matsushita established that *Bacillus subtilis* colonies grown on nutrient-poor agar plates exhibit **fractal dimension D = 1.716 ± 0.008**—in remarkable agreement with the theoretical DLA value of 1.71. This discovery proved that living systems can spontaneously generate DLA patterns through the same physics governing electrochemical deposition.

**Key experimental conditions for DLA-like bacterial growth:**

| Parameter | DLA-like Pattern | Eden-like (Compact) Pattern |
|-----------|------------------|----------------------------|
| Nutrient concentration | Low (0.1-1 g/L peptone) | High (>5 g/L peptone) |
| Agar concentration | High (hard surface) | Low (soft surface) |
| Colony morphology | Fractal branching, D ≈ 1.7 | Round, compact, D ≈ 2.0 |
| Growth mechanism | Diffusion-limited | Reaction-limited |

**Screening effect**: Interior branches stop growing despite open neighborhood—exactly as predicted by DLA theory, where protruding tips screen inner regions from nutrient flux.

### The Ben-Jacob Morphology Diagram

Eshel Ben-Jacob and colleagues developed a comprehensive **morphology phase diagram** for bacterial colony patterns, mapping colony form as a function of nutrient concentration (Cn) and agar hardness (Ca):

| Region | Cn | Ca | Pattern | Model Analogy |
|--------|----|----|---------|---------------|
| A | Low | High | DLA-like fractal | Diffusion-Limited Aggregation |
| B | High | High | Compact with fractal boundary | Eden model |
| C | Medium | Medium | Concentric rings | Reaction-diffusion |
| D | High | Low | Homogeneous disk | Uniform growth |
| E | Low | Medium | Dense Branching Morphology (DBM) | Modified DLA |

**Key papers:**
- Ben-Jacob, E. et al. (1994). "Generic modeling of cooperative growth patterns in bacterial colonies." *Nature*, 368, 46-49.
- Ben-Jacob, E. (1993/1997). "From snowflake formation to growth of bacterial colonies." *Contemporary Physics*, Parts I & II.

### Dendritic Swarming in *Bacillus subtilis*

The dendritic swarming patterns shown in the Quanta article arise from a combination of DLA-like nutrient limitation and active bacterial motility:

```python
def bacterial_swarming_model(grid_size=500, 
                              nutrient_initial=1.0,
                              diffusion_rate=0.1,
                              consumption_rate=0.05,
                              motility=0.3,
                              surfactant_production=0.1):
    """
    Hybrid DLA + active motility model for bacterial swarming.
    
    Based on Kawasaki et al. (1997) reaction-diffusion model.
    """
    import numpy as np
    from scipy.ndimage import laplace
    
    # Initialize fields
    bacteria = np.zeros((grid_size, grid_size))
    nutrients = np.ones((grid_size, grid_size)) * nutrient_initial
    surfactant = np.zeros((grid_size, grid_size))
    
    # Seed colony at center
    center = grid_size // 2
    bacteria[center-2:center+2, center-2:center+2] = 1.0
    
    dt = 0.1
    
    for step in range(10000):
        # Nutrient diffusion (Laplacian)
        nutrient_diffusion = diffusion_rate * laplace(nutrients)
        
        # Nutrient consumption by bacteria
        consumption = consumption_rate * bacteria * nutrients
        
        # Bacterial growth (proportional to local nutrients)
        growth = bacteria * nutrients * (1 - bacteria)  # Logistic
        
        # Bacterial motility (biased random walk + surfactant-mediated)
        # Cells move up nutrient gradients (chemotaxis)
        grad_n_x = np.gradient(nutrients, axis=1)
        grad_n_y = np.gradient(nutrients, axis=0)
        
        # Surfactant enables swarming on hard agar
        effective_motility = motility * (1 + surfactant)
        
        # Update fields
        nutrients += dt * (nutrient_diffusion - consumption)
        nutrients = np.clip(nutrients, 0, nutrient_initial)
        
        bacteria += dt * growth
        
        # Surfactant production by bacteria at colony edge
        edge_bacteria = bacteria * (1 - bacteria)  # Peaks at intermediate density
        surfactant += dt * (surfactant_production * edge_bacteria - 0.01 * surfactant)
        
        # Add stochastic noise for branching instability
        if step % 100 == 0:
            noise = np.random.normal(0, 0.01, bacteria.shape)
            bacteria += noise * (bacteria > 0.1) * (bacteria < 0.9)
            bacteria = np.clip(bacteria, 0, 1)
    
    return bacteria, nutrients, surfactant
```

### *Physarum polycephalum* Network Formation

The slime mold *Physarum polycephalum* demonstrates a different but related pattern formation mechanism: **adaptive network optimization** rather than pure DLA. However, fractal dimension analysis shows network complexity typically converges to D ≈ 1.5-2.0 depending on environmental conditions.

**Key characteristics:**
- Single giant cell with cytoplasmic streaming
- Forms transport networks resembling proximity graphs (Steiner trees, relative neighborhood graphs)
- Uses chemotaxis for foraging, leaving chemical trails as "externalized memory"
- Network tubes exhibit peristaltic pumping for nutrient transport

**Seminal papers:**
- Nakagaki, T. et al. (2000). "Maze-solving by an amoeboid organism." *Nature*, 407, 470.
- Tero, A. et al. (2010). "Rules for biologically inspired adaptive network design." *Science*, 327, 439-442.
- Alim, K. et al. (2013). "Random network peristalsis in Physarum polycephalum organizes fluid flows across an individual." *PNAS*, 110, 13306-13311.

```python
def physarum_agent_model(num_agents=5000, 
                          grid_size=200,
                          sensor_angle=45,
                          rotation_angle=45,
                          sensor_distance=9,
                          deposit_amount=5,
                          decay_rate=0.1):
    """
    Multi-agent model approximating Physarum network formation.
    
    Based on Jones (2010) "Characteristics of pattern formation 
    and evolution in approximations of Physarum transport networks."
    """
    import numpy as np
    
    # Agent state: position (x, y) and heading angle
    agents = np.zeros((num_agents, 3))
    agents[:, 0] = np.random.uniform(grid_size*0.4, grid_size*0.6, num_agents)  # x
    agents[:, 1] = np.random.uniform(grid_size*0.4, grid_size*0.6, num_agents)  # y
    agents[:, 2] = np.random.uniform(0, 2*np.pi, num_agents)  # heading
    
    # Chemoattractant trail map
    trail_map = np.zeros((grid_size, grid_size))
    
    sa_rad = np.radians(sensor_angle)
    ra_rad = np.radians(rotation_angle)
    
    for step in range(1000):
        for i in range(num_agents):
            x, y, heading = agents[i]
            
            # Sense chemoattractant at three positions
            # Front
            fx = int(x + sensor_distance * np.cos(heading)) % grid_size
            fy = int(y + sensor_distance * np.sin(heading)) % grid_size
            f_sense = trail_map[fy, fx]
            
            # Front-left
            fl_x = int(x + sensor_distance * np.cos(heading + sa_rad)) % grid_size
            fl_y = int(y + sensor_distance * np.sin(heading + sa_rad)) % grid_size
            fl_sense = trail_map[fl_y, fl_x]
            
            # Front-right
            fr_x = int(x + sensor_distance * np.cos(heading - sa_rad)) % grid_size
            fr_y = int(y + sensor_distance * np.sin(heading - sa_rad)) % grid_size
            fr_sense = trail_map[fr_y, fr_x]
            
            # Rotation decision
            if f_sense > fl_sense and f_sense > fr_sense:
                pass  # Continue straight
            elif f_sense < fl_sense and f_sense < fr_sense:
                # Random turn
                if np.random.random() < 0.5:
                    heading += ra_rad
                else:
                    heading -= ra_rad
            elif fl_sense < fr_sense:
                heading -= ra_rad  # Turn right
            elif fr_sense < fl_sense:
                heading += ra_rad  # Turn left
            
            # Move forward
            x = (x + np.cos(heading)) % grid_size
            y = (y + np.sin(heading)) % grid_size
            
            # Deposit chemoattractant
            trail_map[int(y), int(x)] += deposit_amount
            
            agents[i] = [x, y, heading]
        
        # Diffuse and decay trail
        from scipy.ndimage import uniform_filter
        trail_map = uniform_filter(trail_map, size=3)
        trail_map *= (1 - decay_rate)
    
    return trail_map, agents
```

### Spiral Migration in *Bacillus mycoides*

The spiral colony patterns of *Bacillus mycoides* shown in the Quanta article arise from **chiral growth**—cells grow in long filaments that curl either clockwise or counterclockwise based on genetic factors. This represents a departure from pure DLA, incorporating handedness as an inherited trait.

**Key paper:**
- Di Franco, C. et al. (2002). "Colony shape as a genetic trait in the pattern-forming *Bacillus mycoides*." *BMC Microbiology*, 2, 33.

### Fungal Mycelium Networks

Fungal mycelium exhibits DLA-like branching during hyphal tip growth, with fractal dimensions typically in the range D ≈ 1.5-1.9 depending on species and nutrient conditions. The growth mechanism combines:

1. **Apical dominance**: New branches form behind the extending tip
2. **Negative autotropism**: Hyphae avoid their own trails
3. **Nutrient tropism**: Growth biased toward nutrient sources

This produces networks intermediate between pure DLA (dendritic) and space-filling (compact), optimized for resource extraction from heterogeneous substrates.

### Unified Morphology Classification

| Organism | Growth Form | Fractal Dimension | Primary Mechanism |
|----------|-------------|-------------------|-------------------|
| *B. subtilis* (low nutrient) | Dendritic | 1.71 ± 0.01 | Pure DLA |
| *B. subtilis* (high nutrient) | Compact | ~2.0 | Eden model |
| *B. subtilis* (swarming) | Dense branching | 1.7-1.9 | DLA + motility |
| *B. mycoides* | Spiral | 1.8-1.9 | Chiral DLA |
| *Physarum polycephalum* | Reticulated network | 1.5-2.0 | Adaptive optimization |
| Crustose lichen | Radial/dendritic | 1.6-1.8 | DLA + photobiont |
| Fruticose lichen | 3D branching | 2.3-2.6 | L-system + DLA |
| Fungal mycelium | Branching network | 1.5-1.9 | Tip-growth DLA |

---

## Key academic references

### Foundational DLA papers
- Witten, T.A. & Sander, L.M. (1981). "Diffusion-Limited Aggregation, a Kinetic Critical Phenomenon." *Physical Review Letters*, 47, 1400–1403.
- Witten, T.A. & Sander, L.M. (1983). "Diffusion-Limited Aggregation." *Physical Review B*, 27, 5686–5697.
- Niemeyer, L., Pietronero, L., & Wiesmann, H.J. (1984). "Fractal Dimension of Dielectric Breakdown." *Physical Review Letters*, 52, 1033–1036.

### Bacterial colony DLA and pattern formation
- Fujikawa, H. & Matsushita, M. (1989). "Fractal Growth of Bacillus subtilis on Agar Plates." *Journal of the Physical Society of Japan*, 58, 3875–3878.
- Matsuyama, T. & Matsushita, M. (1993). "Fractal morphogenesis by a bacterial cell population." *Critical Reviews in Microbiology*, 19(2), 117–135.
- Ben-Jacob, E. et al. (1994). "Generic modeling of cooperative growth patterns in bacterial colonies." *Nature*, 368, 46–49.
- Ben-Jacob, E. (1993). "From snowflake formation to growth of bacterial colonies Part I." *Contemporary Physics*, 34(5), 247–273.
- Ben-Jacob, E. (1997). "From snowflake formation to growth of bacterial colonies Part II." *Contemporary Physics*, 38(3), 205–241.
- Kawasaki, K. et al. (1997). "Modeling spatio-temporal patterns created by Bacillus subtilis." *Journal of Theoretical Biology*, 188, 177–185.
- Julkowska, D. et al. (2004). "Branched swarming patterns on a synthetic medium formed by wild-type Bacillus subtilis strain 3610." *Microbiology*, 150, 1839–1849.
- Di Franco, C. et al. (2002). "Colony shape as a genetic trait in the pattern-forming Bacillus mycoides." *BMC Microbiology*, 2, 33.

### Physarum polycephalum and slime mold networks
- Nakagaki, T. et al. (2000). "Maze-solving by an amoeboid organism." *Nature*, 407, 470.
- Tero, A. et al. (2010). "Rules for biologically inspired adaptive network design." *Science*, 327, 439–442.
- Jones, J. (2010). "Characteristics of pattern formation and evolution in approximations of Physarum transport networks." *Artificial Life*, 16(2), 127–153.
- Alim, K. et al. (2013). "Random network peristalsis in Physarum polycephalum organizes fluid flows across an individual." *PNAS*, 110, 13306–13311.
- Adamatzky, A. (2010). *Physarum Machines: Computers from Slime Mould*. World Scientific.

### L-systems and algorithmic botany
- Lindenmayer, A. (1968). "Mathematical Models for Cellular Interaction in Development." *Journal of Theoretical Biology*, 18, 280–315.
- Prusinkiewicz, P. & Lindenmayer, A. (1990). *The Algorithmic Beauty of Plants*. Springer-Verlag. (Free at algorithmicbotany.org)
- Prusinkiewicz, P., Cieslak, M., Ferraro, P., & Hanan, J. (2018). "Modeling Plant Development with L-Systems." In *Mathematical Modelling in Plant Biology*, Springer.

### Lichen-specific computational models
- Desbenoit, B., Galin, E., & Akkouche, S. (2004). "Simulating and Modeling Lichen Growth." *Computer Graphics Forum*, 23(3), 341–350.
- Sumner, R.W. (2001). "Pattern Formation in Lichen." Ph.D. thesis, MIT.

### Hybrid approaches
- Fernández, S. et al. (2018). "Hybrid L-Systems–Diffusion Limited Aggregation Schemes." *Physica A: Statistical Mechanics and its Applications*.
- Merks, R.M. et al. (2004). "Polyp Oriented Modelling of Coral Growth." *Journal of Theoretical Biology*, 228(4), 559–576.

---

## Conclusion

The mathematical frameworks of DLA and L-systems provide rigorous, complementary approaches to lichen growth simulation. **DLA's connection to harmonic measure and Laplacian growth directly models the diffusion-limited nutrient transport** governing crustose and foliose expansion, while **L-systems' parallel rewriting formalism captures the developmental logic** of fruticose branching. The hybrid approach—L-system skeleton with DLA surface detail—produces the most realistic 3D morphologies.

For Jupyter implementation, the key insight is **dimensional separation**: 1D models for time-series analysis, 2D for crustose/foliose colony patterns, and 3D for fruticose structures and rugose textures. The Desbenoit et al. Open DLA framework, with its environmental constraint functions, provides the most complete existing template for biologically realistic simulation. Future extensions could incorporate reaction-diffusion for internal photobiont patterning and agent-based models for competitive lichen community dynamics.

The provided pseudocode and algorithms are designed for direct translation to Python, with NumPy for array operations, SciPy for spatial queries, Numba for performance-critical loops, and PyVista or Mayavi for 3D visualization.