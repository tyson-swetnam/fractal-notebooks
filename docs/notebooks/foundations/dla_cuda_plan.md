# Advanced CUDA Python DLA Implementation Plan

**Goal:** Implement state-of-the-art Diffusion-Limited Aggregation algorithms in CUDA Python, incorporating optimizations from markjstock.org/dla3d and paulbourke.net research to achieve million-particle scale with physically accurate off-lattice growth.

**Status:** Design phase (2025-12-21)

---

## Executive Summary

This plan extends the existing lattice-based CUDA DLA implementation (3d_dla.ipynb) to support:
1. **Off-lattice particles** with continuous coordinates for higher resolution
2. **Octree spatial acceleration** enabling O(log N) nearest-neighbor queries
3. **Sphere-hopping optimization** reducing random walk steps by 100-1000×
4. **Advanced parameter system** including bulk velocity, stickiness, rotation
5. **Scalability to 1M+ particles** through memory-efficient GPU data structures
6. **GPU-accelerated fractal analysis** with box-counting dimension calculation

**Key Innovation:** Hybrid octree-particle structure where octree leaf nodes reside in GPU shared memory, enabling parallel particle insertion with minimal synchronization overhead.

---

## 1. Core Algorithms and Data Structures

### 1.1 Off-Lattice Particle Representation

**Current limitation:** Voxel grid discretizes space to integer coordinates, limiting resolution to grid size / max_extent ratio.

**Solution:** Continuous particle coordinates with compact GPU representation.

```python
# Structure-of-Arrays (SoA) layout for coalesced memory access
@cuda.jit
class ParticleArray:
    """
    Compact particle storage optimized for GPU memory bandwidth.
    Uses SoA layout: separate arrays for each attribute.
    """
    positions_x: cuda.device_array(dtype=np.float32)  # N particles
    positions_y: cuda.device_array(dtype=np.float32)
    positions_z: cuda.device_array(dtype=np.float32)
    velocities_x: cuda.device_array(dtype=np.float32)  # For bulk velocity
    velocities_y: cuda.device_array(dtype=np.float32)
    velocities_z: cuda.device_array(dtype=np.float32)
    particle_radius: np.float32  # Single radius for all particles
    num_particles: np.int32
```

**Memory footprint:** 24 bytes per particle (6 × float32) for 1M particles = 24 MB (minimal GPU memory usage).

**Advantages:**
- Float32 precision sufficient for visualization (±1e-7 relative accuracy)
- Coalesced memory access: threads in a warp access consecutive array elements
- Supports non-uniform particle sizes via optional radius array

### 1.2 GPU Octree for Spatial Queries

**Challenge:** Naive nearest-neighbor search is O(N) per particle; unacceptable at million-particle scale.

**Solution:** Adaptive octree subdivided to leaf size ~8-16 particles, stored in GPU global memory with leaf nodes cached in shared memory during queries.

#### Octree Node Structure

```python
@cuda.jit
class OctreeNode:
    """
    GPU-friendly octree node (32 bytes, fits in cache line).
    Stores either particle indices (leaf) or child pointers (internal).
    """
    center_x: np.float32      # Node center (12 bytes)
    center_y: np.float32
    center_z: np.float32
    half_size: np.float32     # Bounding cube half-width (4 bytes)

    # Union: either child indices OR particle data
    child_start: np.int32     # Index into child node array (internal)
    particle_start: np.int32  # Index into particle list (leaf)
    particle_count: np.int32  # Number of particles in leaf

    is_leaf: np.uint8         # Boolean: 1=leaf, 0=internal
    _padding: np.uint8[3]     # Align to 32 bytes
```

**Key design decisions:**

1. **Fixed maximum depth (12-16 levels):** Prevents pathological trees, bounds stack usage
2. **Leaf size 8-16 particles:** Balance tree depth vs leaf traversal cost
3. **Breadth-first storage:** Enables level-order traversal, better cache locality
4. **No dynamic allocation:** Pre-allocate node pools, use atomic counters for allocation

#### Octree Construction Algorithm (GPU)

**Strategy:** Bottom-up construction using Morton codes (Z-order curve) for spatial sorting.

```python
@cuda.jit
def build_octree_kernel(particle_positions, morton_codes, octree_nodes,
                        num_particles, max_leaf_size=16):
    """
    Phase 1: Compute Morton codes for particles.
    Morton code interleaves x,y,z bits to preserve spatial locality.

    Example for 3D (10 bits per dimension):
    x=5 (0b0000000101), y=3 (0b0000000011), z=7 (0b0000000111)
    Morton: 0b000000000000000000000111011101
              ^z ^y ^x ^z ^y ^x ...
    """
    tid = cuda.grid(1)
    if tid >= num_particles:
        return

    x = int(particle_positions[tid, 0] * 1024) & 0x3FF  # Scale to [0, 1023]
    y = int(particle_positions[tid, 1] * 1024) & 0x3FF
    z = int(particle_positions[tid, 2] * 1024) & 0x3FF

    morton_codes[tid] = morton_encode_3d(x, y, z)

@cuda.jit(device=True)
def morton_encode_3d(x, y, z):
    """Interleave bits of x,y,z to produce Morton code."""
    code = 0
    for i in range(10):  # 10 bits per dimension = 30-bit code
        code |= ((x & (1 << i)) << (2*i)) | \
                ((y & (1 << i)) << (2*i + 1)) | \
                ((z & (1 << i)) << (2*i + 2))
    return code

# Phase 2: Sort particles by Morton code (use CUB radix sort or thrust)
# Phase 3: Build tree top-down from sorted particles
@cuda.jit
def build_octree_nodes_kernel(sorted_particles, morton_codes, octree_nodes,
                               level, nodes_at_level, max_leaf_size):
    """
    Process one tree level per kernel launch.
    Each thread handles one node, subdividing if particle count > max_leaf_size.
    """
    tid = cuda.grid(1)
    if tid >= nodes_at_level:
        return

    node = octree_nodes[level_offset + tid]

    if node.particle_count <= max_leaf_size:
        node.is_leaf = 1
        return

    # Subdivide into 8 children
    for octant in range(8):
        child_center = compute_child_center(node.center, node.half_size, octant)
        child_half_size = node.half_size * 0.5

        # Count particles in this octant (binary search on Morton codes)
        child_particle_range = find_morton_range(
            morton_codes,
            child_center,
            child_half_size
        )

        # Allocate child node
        child_idx = cuda.atomic.add(global_node_counter, 0, 1)
        octree_nodes[child_idx] = create_node(
            child_center,
            child_half_size,
            child_particle_range
        )

        # Store child pointer
        node.children[octant] = child_idx
```

**Performance notes:**
- Morton code sorting is O(N log N) but highly parallel (GPU radix sort: ~1B keys/sec)
- Tree construction is O(N) with bounded depth
- Total octree build time: ~10-50ms for 1M particles on Tesla T4

### 1.3 Accelerated Random Walk (Sphere-Hopping)

**Key insight from markjstock.org:** A random walker has equal probability of reaching any point on a sphere's surface. Therefore, instead of simulating thousands of steps, compute distance to nearest particle and "hop" that distance in a random direction.

**Algorithm:**

```python
@cuda.jit
def accelerated_random_walk_kernel(
    walker_positions,     # Current walker positions (N_walkers × 3)
    cluster_particles,    # Aggregated cluster particles
    octree_root,          # Octree for cluster
    rng_states,           # Per-thread RNG
    particle_radius,
    max_hops,
    stickiness,
    aggregated_flags      # Output: 1 if walker aggregated
):
    """
    Accelerated random walk using sphere-hopping.
    Each thread handles one walker particle.
    """
    tid = cuda.grid(1)
    if tid >= walker_positions.shape[0]:
        return

    # Walker state
    pos = cuda.local.array(3, dtype=np.float32)
    pos[0] = walker_positions[tid, 0]
    pos[1] = walker_positions[tid, 1]
    pos[2] = walker_positions[tid, 2]

    for hop in range(max_hops):
        # Find nearest cluster particle using octree
        nearest_dist = octree_nearest_neighbor(pos, octree_root, cluster_particles)

        if nearest_dist < 0:  # Octree traversal failed (should not happen)
            break

        # Check for contact (within 2 × particle_radius)
        if nearest_dist <= 2.0 * particle_radius:
            # Stickiness probability check
            if xoroshiro128p_uniform_float32(rng_states, tid) < stickiness:
                aggregated_flags[tid] = 1
                # Copy final position for aggregation
                walker_positions[tid, 0] = pos[0]
                walker_positions[tid, 1] = pos[1]
                walker_positions[tid, 2] = pos[2]
            else:
                # Non-sticky: push away slightly
                direction = cuda.local.array(3, dtype=np.float32)
                random_unit_sphere(rng_states, tid, direction)
                pos[0] += direction[0] * particle_radius * 0.5
                pos[1] += direction[1] * particle_radius * 0.5
                pos[2] += direction[2] * particle_radius * 0.5
            break

        # Sphere-hop optimization
        # Jump to surface of sphere centered at current position
        # with radius = (nearest_dist - 2*particle_radius) * safety_factor
        hop_distance = (nearest_dist - 2.0 * particle_radius) * 0.95

        if hop_distance < particle_radius:
            # Too close for hopping, use standard random walk
            hop_distance = particle_radius

        # Random direction on unit sphere
        direction = cuda.local.array(3, dtype=np.float32)
        random_unit_sphere(rng_states, tid, direction)

        pos[0] += direction[0] * hop_distance
        pos[1] += direction[1] * hop_distance
        pos[2] += direction[2] * hop_distance

        # Particle culling: if moved away 5-10 consecutive times, terminate
        # (Check if distance from cluster center increased)
        # [Implementation omitted for brevity]

    # Update walker position
    walker_positions[tid, 0] = pos[0]
    walker_positions[tid, 1] = pos[1]
    walker_positions[tid, 2] = pos[2]

@cuda.jit(device=True)
def random_unit_sphere(rng_states, tid, out_direction):
    """
    Generate uniformly distributed random direction on unit sphere.
    Uses Marsaglia (1972) method: rejection sampling in unit cube.
    """
    while True:
        x = 2.0 * xoroshiro128p_uniform_float32(rng_states, tid) - 1.0
        y = 2.0 * xoroshiro128p_uniform_float32(rng_states, tid) - 1.0
        z = 2.0 * xoroshiro128p_uniform_float32(rng_states, tid) - 1.0

        r_sq = x*x + y*y + z*z
        if r_sq > 0.0 and r_sq <= 1.0:
            r_inv = 1.0 / math.sqrt(r_sq)
            out_direction[0] = x * r_inv
            out_direction[1] = y * r_inv
            out_direction[2] = z * r_inv
            return

@cuda.jit(device=True)
def octree_nearest_neighbor(query_point, octree_root, cluster_particles):
    """
    Traverse octree to find distance to nearest cluster particle.
    Uses depth-first traversal with priority queue.

    Returns: distance to nearest particle, or -1 if no particles found.
    """
    # Stack for depth-first traversal (fixed size for GPU)
    stack = cuda.local.array((32, 2), dtype=np.int32)  # (node_idx, priority)
    stack_size = 0

    # Push root
    stack[0, 0] = 0  # Root node index
    stack[0, 1] = 0  # Priority (unused in DFS)
    stack_size = 1

    best_dist = 1e10

    while stack_size > 0:
        # Pop from stack
        stack_size -= 1
        node_idx = stack[stack_size, 0]
        node = octree_nodes[node_idx]

        # Prune: if box distance > best_dist, skip
        box_dist = point_to_box_distance(query_point, node.center, node.half_size)
        if box_dist > best_dist:
            continue

        if node.is_leaf:
            # Check all particles in leaf
            for i in range(node.particle_count):
                p_idx = node.particle_start + i
                dist = distance_3d(
                    query_point[0], query_point[1], query_point[2],
                    cluster_particles[p_idx, 0],
                    cluster_particles[p_idx, 1],
                    cluster_particles[p_idx, 2]
                )
                if dist < best_dist:
                    best_dist = dist
        else:
            # Internal node: push children sorted by distance
            # (For simplicity, push all; optimization: sort by distance)
            for octant in range(8):
                child_idx = node.children[octant]
                if child_idx >= 0:  # Valid child
                    stack[stack_size, 0] = child_idx
                    stack_size += 1

    return best_dist if best_dist < 1e10 else -1.0
```

**Performance gain:** Sphere-hopping reduces random walk steps by factor of 100-1000× when far from cluster, yielding 10-100× overall speedup.

### 1.4 Bulk Velocity and Advection

**Biological motivation:** Lichen growth can exhibit directional bias from nutrient gradients, wind, or substrate geometry.

**Implementation:** Add deterministic velocity component to random walk.

```python
@cuda.jit(device=True)
def apply_bulk_velocity(position, velocity, dt=1.0):
    """
    Add advective motion to diffusive random walk.

    Parameters:
    -----------
    position : array[3]
        Current particle position (modified in-place)
    velocity : array[3]
        Bulk velocity vector (e.g., upward growth bias)
    dt : float
        Time step (default 1.0)
    """
    position[0] += velocity[0] * dt
    position[1] += velocity[1] * dt
    position[2] += velocity[2] * dt

# Example: upward growth bias for fruticose lichen
bulk_velocity = np.array([0.0, 0.0, 0.5])  # 50% upward drift per step
```

**Rationale:** Bulk velocity breaks isotropy without destroying fractal structure; empirically, velocities up to ~50% of diffusion coefficient maintain DLA morphology.

---

## 2. CUDA Kernel Designs

### 2.1 Kernel Launch Strategy

**Pipeline architecture:** Overlap computation, memory transfer, and octree updates using CUDA streams.

```python
class DLASimulationPipeline:
    """
    Multi-stream GPU pipeline for DLA simulation.

    Stream 0: Cluster management (octree rebuild, particle compaction)
    Stream 1: Walker batch 1 (random walks)
    Stream 2: Walker batch 2 (overlaps with stream 1 processing)
    Stream 3: Data transfers (host ↔ device)
    """

    def __init__(self, num_walkers_per_batch=100000):
        self.streams = [cuda.stream() for _ in range(4)]
        self.walker_batch_size = num_walkers_per_batch

        # Allocate pinned host memory for async transfers
        self.host_aggregated = cuda.pinned_array(
            num_walkers_per_batch,
            dtype=np.int32
        )

    def run_iteration(self):
        # Stream 0: Rebuild octree if cluster grew significantly
        with self.streams[0]:
            if self.cluster_size > self.last_octree_size * 1.1:
                rebuild_octree_kernel[...](self.cluster_particles)
                self.last_octree_size = self.cluster_size

        # Stream 1: Process walker batch 1
        with self.streams[1]:
            accelerated_random_walk_kernel[...](
                self.walker_batch_1,
                self.cluster_particles,
                self.octree_root,
                ...
            )
            aggregate_particles_kernel[...](self.walker_batch_1, ...)

        # Stream 2: Process walker batch 2 (overlapped)
        with self.streams[2]:
            accelerated_random_walk_kernel[...](
                self.walker_batch_2,
                ...
            )

        # Stream 3: Transfer results to host (overlapped)
        with self.streams[3]:
            self.device_aggregated.copy_to_host(
                self.host_aggregated,
                stream=self.streams[3]
            )

        cuda.synchronize()  # Wait for all streams
```

### 2.2 Memory Optimization Strategies

**Challenge:** 1M particles × 24 bytes = 24 MB cluster, but octree and walkers require additional memory.

**Solutions:**

1. **Particle compaction:** Remove escaped walkers, compact arrays
2. **Octree pruning:** Deallocate empty subtrees
3. **Batch size tuning:** Balance parallelism vs memory (Tesla T4: 16 GB, can handle 10-20M walker batches)

```python
@cuda.jit
def compact_particles_kernel(particles_in, flags, particles_out, scan_indices):
    """
    Compact particle array by removing inactive particles.
    Uses parallel prefix sum (scan) to compute output indices.

    Phase 1: Compute scan (use CUB or Numba's scan)
    Phase 2: Scatter active particles to compacted array
    """
    tid = cuda.grid(1)
    if tid >= particles_in.shape[0]:
        return

    if flags[tid]:  # Particle is active
        out_idx = scan_indices[tid]
        particles_out[out_idx, 0] = particles_in[tid, 0]
        particles_out[out_idx, 1] = particles_in[tid, 1]
        particles_out[out_idx, 2] = particles_in[tid, 2]
```

### 2.3 Thread Block Configuration

**Tuning parameters for Tesla T4 (Turing architecture, compute capability 7.5):**

| Kernel | Threads/Block | Blocks/Grid | Occupancy | Shared Memory |
|--------|--------------|-------------|-----------|---------------|
| Random walk | 256 | (N+255)/256 | 100% | 0 KB |
| Octree build | 128 | (Nodes+127)/128 | 75% | 12 KB (scratch) |
| Nearest neighbor | 256 | (N+255)/256 | 100% | 4 KB (stack) |
| Compaction | 512 | (N+511)/512 | 50% | 0 KB |

**Rationale:**
- 256 threads/block: Sweet spot for compute-bound kernels (maximizes warp occupancy)
- 512 threads/block: For memory-bound kernels (higher memory throughput)
- 128 threads/block: When register pressure is high (octree traversal uses many registers)

**Register usage analysis:**

```bash
# Compile with ptxas info
numba --cuda-lineinfo --opt=3 dla_kernels.py
```

Target: <40 registers per thread to achieve 100% occupancy on Turing.

---

## 3. Optimization Strategies

### 3.1 Algorithmic Optimizations

#### A. Adaptive Birth Radius Scheduling

**Current approach:** Fixed birth radius offset (spawn_radius = max_radius + 5).

**Optimization:** Adaptive scheduling based on cluster density profile.

```python
def compute_adaptive_birth_radius(cluster_particles, current_max_radius):
    """
    Compute optimal birth radius by analyzing radial density profile.
    Spawn walkers just outside the "screening length" where density drops.

    Theory: DLA clusters have fractal dimension D ≈ 2.5, so density
    ρ(r) ~ r^(D-3) = r^(-0.5) for large r.
    Screening length: radius where ρ drops to 10% of peak.
    """
    # Bin particles by radial distance
    radii = np.linalg.norm(cluster_particles, axis=1)
    hist, bin_edges = np.histogram(radii, bins=50)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # Find radius where density drops below threshold
    peak_density = hist.max()
    screening_idx = np.argmax(hist < peak_density * 0.1)

    if screening_idx > 0:
        screening_radius = bin_centers[screening_idx]
        return screening_radius + 3.0  # Small offset
    else:
        return current_max_radius + 5.0  # Fallback
```

**Expected gain:** 2-3× reduction in wasted walker steps.

#### B. Particle Culling with Directional Memory

**markjstock.org insight:** If particle moves away from cluster 5-10 consecutive times, it's unlikely to aggregate soon—terminate it.

**Enhanced version:** Track net displacement vector, not just count.

```python
@cuda.jit(device=True)
def check_culling_criterion(
    current_pos,
    initial_pos,
    cluster_centroid,
    consecutive_away_moves,
    max_away_moves=7
):
    """
    Cull particle if it has moved consistently away from cluster.

    Criterion: dot(displacement, direction_to_cluster) < 0
              for consecutive_away_moves > threshold
    """
    displacement = cuda.local.array(3, dtype=np.float32)
    displacement[0] = current_pos[0] - initial_pos[0]
    displacement[1] = current_pos[1] - initial_pos[1]
    displacement[2] = current_pos[2] - initial_pos[2]

    to_cluster = cuda.local.array(3, dtype=np.float32)
    to_cluster[0] = cluster_centroid[0] - current_pos[0]
    to_cluster[1] = cluster_centroid[1] - current_pos[1]
    to_cluster[2] = cluster_centroid[2] - current_pos[2]

    dot_product = (displacement[0] * to_cluster[0] +
                   displacement[1] * to_cluster[1] +
                   displacement[2] * to_cluster[2])

    if dot_product < 0:  # Moving away
        consecutive_away_moves += 1
        if consecutive_away_moves >= max_away_moves:
            return True  # Cull this particle
    else:
        consecutive_away_moves = 0  # Reset counter

    return False  # Keep particle
```

#### C. Hierarchical Octree Updates

**Problem:** Rebuilding entire octree every iteration is wasteful when only a few particles are added.

**Solution:** Incremental octree updates for small batch additions, full rebuild every 1000-10000 particles.

```python
def incremental_octree_insert(octree, new_particles):
    """
    Insert new particles into existing octree.
    If a leaf overflows (>16 particles), subdivide it.

    Trade-off: Tree becomes less balanced over time.
    Solution: Full rebuild every 10% cluster growth.
    """
    for particle in new_particles:
        leaf_node = octree.traverse_to_leaf(particle)
        leaf_node.add_particle(particle)

        if leaf_node.particle_count > MAX_LEAF_SIZE:
            octree.subdivide_leaf(leaf_node)
```

### 3.2 GPU-Specific Optimizations

#### A. Warp-Level Primitives

**CUDA warp (32 threads) operates in lockstep—exploit this for faster reductions and scans.**

```python
from numba import cuda

@cuda.jit(device=True)
def warp_reduce_min(val):
    """
    Find minimum value across a warp (32 threads) using shuffle operations.
    No shared memory needed.

    Time complexity: O(log₂ 32) = 5 shuffle operations
    """
    mask = 0xFFFFFFFF  # All threads in warp

    for offset in [16, 8, 4, 2, 1]:
        other_val = cuda.shfl_down_sync(mask, val, offset)
        val = min(val, other_val)

    return val  # All threads in warp now hold the minimum

# Application: Find nearest particle in parallel across warp
@cuda.jit
def warp_collaborative_nearest_search(query_point, cluster_particles, output):
    """
    Each warp collaboratively searches 32 cluster particles in parallel.
    """
    tid = cuda.grid(1)
    warp_id = tid // 32
    lane_id = tid % 32

    # Each thread checks one particle
    particle_idx = warp_id * 32 + lane_id

    if particle_idx < cluster_particles.shape[0]:
        dist = distance_3d(query_point, cluster_particles[particle_idx])
    else:
        dist = 1e10  # Sentinel

    # Warp-level reduction
    min_dist = warp_reduce_min(dist)

    # Lane 0 writes result
    if lane_id == 0:
        output[warp_id] = min_dist
```

#### B. Texture Memory for Read-Only Cluster Data

**Idea:** Cluster particles are read-only during walker simulation—use texture cache for better bandwidth.

```python
from numba import cuda

# Bind particle array to texture memory (Numba doesn't directly expose textures,
# but we can use readonly arrays with @cuda.jit decorator hint)
@cuda.jit
def texture_optimized_kernel(cluster_particles, walker_positions):
    """
    Access cluster_particles through L1 cache.
    Compiler automatically uses read-only cache on Kepler+ GPUs.
    """
    tid = cuda.grid(1)

    # Read-only access pattern triggers texture cache
    for i in range(cluster_particles.shape[0]):
        dist = distance_3d(
            walker_positions[tid],
            cluster_particles[i]  # Cached read
        )
    # ... rest of kernel
```

**Performance gain:** 20-30% speedup for memory-bound kernels.

#### C. Shared Memory Tiling for Octree Leaves

**Problem:** Octree leaf traversal requires many random accesses to global memory.

**Solution:** Cache frequently accessed leaves in shared memory.

```python
@cuda.jit
def shared_memory_octree_kernel(walker_positions, octree_nodes, cluster_particles):
    """
    Use shared memory to cache hot octree leaves.
    Each thread block processes walkers in same spatial region.
    """
    # Shared memory for caching leaf particles
    shared_particles = cuda.shared.array(
        shape=(256, 3),  # 256 particles × 3 coords = 3 KB
        dtype=np.float32
    )

    tid = cuda.grid(1)
    block_tid = cuda.threadIdx.x

    # Load leaf particles into shared memory (coalesced)
    if block_tid < 256:
        shared_particles[block_tid, 0] = cluster_particles[leaf_start + block_tid, 0]
        shared_particles[block_tid, 1] = cluster_particles[leaf_start + block_tid, 1]
        shared_particles[block_tid, 2] = cluster_particles[leaf_start + block_tid, 2]

    cuda.syncthreads()  # Wait for all threads to load

    # Now all threads can access shared_particles with low latency
    for i in range(256):
        dist = distance_3d(walker_positions[tid], shared_particles[i])
        # ...
```

**Performance gain:** 3-5× speedup for leaf searches with high spatial locality.

---

## 4. Parameter System

### 4.1 Physical Parameter Structure

```python
from dataclasses import dataclass
import numpy as np

@dataclass
class DLAPhysicsParams:
    """
    Physical parameters controlling DLA morphology.
    All parameters have biological interpretations.
    """
    # Core DLA parameters
    stickiness: float = 1.0
    """
    Probability of adhesion upon contact (0.0 to 1.0).

    Effects:
    - 1.0: Classic DLA, dendritic (D ≈ 1.71 in 2D, 2.5 in 3D)
    - 0.5: Intermediate branching
    - 0.1-0.3: Dense, compact structures (Usnea-like)
    - <0.05: Approaching Eden model (D → 2.0 in 2D)

    Biology: Models nutrient availability—low nutrients = lower sticking.
    """

    particle_radius: float = 1.0
    """
    Radius of individual particles (arbitrary units).
    Sets length scale for the simulation.
    """

    diffusion_coefficient: float = 1.0
    """
    Diffusion coefficient for random walk (units: radius²/step).
    Standard Brownian motion: D = step_size² / (2 * dimension).
    """

    # Directional bias
    bulk_velocity: np.ndarray = None
    """
    Advective velocity vector (units: radius/step).

    Examples:
    - [0, 0, 0.5]: Upward growth bias (fruticose lichen)
    - [1, 0, 0]: Lateral spreading (wind-driven growth)
    - Gradient field: f(position) for spatially varying bias

    Constraint: |v| < D for maintaining fractal structure.
    """

    rotation_rate: float = 0.0
    """
    Angular velocity for cluster rotation (radians/step).

    Enables spiral/helical structures.
    Range: 0 to 0.1 rad/step (higher values break self-similarity).
    """

    # Environmental constraints
    substrate_type: str = 'none'
    """
    Boundary condition type:
    - 'none': Free growth (radial expansion)
    - 'plane': Growth on 2D substrate (z=0)
    - 'cylinder': Growth on cylindrical substrate (bark model)
    - 'sphere': Growth on spherical substrate
    """

    substrate_params: dict = None
    """
    Parameters for substrate geometry.
    Example for cylinder: {'radius': 10.0, 'axis': [0, 0, 1]}
    """

    nutrient_field: object = None
    """
    Spatially varying nutrient concentration field.

    Type: Callable[[np.ndarray], float]
        Takes position (x,y,z) and returns concentration [0,1].

    Modifies stickiness: effective_stickiness = base_stickiness * nutrient(pos).

    Example: Exponential decay from source
        lambda pos: np.exp(-np.linalg.norm(pos - source) / decay_length)
    """

    # Growth limits
    max_cluster_radius: float = 100.0
    """
    Maximum cluster radius before termination.
    Prevents unbounded growth.
    """

    target_particle_count: int = 100000
    """
    Stop condition: number of aggregated particles.
    """

    # Branch characteristics (for post-processing)
    branch_length_scale: float = None
    """
    Characteristic branch length (computed from autocorrelation).
    Set to None for automatic calculation.
    """

    branch_thickness_scale: float = None
    """
    Characteristic branch thickness.
    For rendering: particle radius × this factor.
    """

    def __post_init__(self):
        if self.bulk_velocity is None:
            self.bulk_velocity = np.zeros(3, dtype=np.float32)
        else:
            self.bulk_velocity = np.array(self.bulk_velocity, dtype=np.float32)

        if self.substrate_params is None:
            self.substrate_params = {}

        # Validate constraints
        v_mag = np.linalg.norm(self.bulk_velocity)
        if v_mag >= self.diffusion_coefficient:
            raise ValueError(
                f"Bulk velocity {v_mag} exceeds diffusion coefficient "
                f"{self.diffusion_coefficient}. Advection-dominated regime "
                f"will destroy fractal structure."
            )


@dataclass
class DLAComputeParams:
    """
    Computational parameters (do not affect physics, only performance).
    """
    max_walk_steps: int = 100000
    """Maximum random walk steps per particle before culling."""

    walker_batch_size: int = 50000
    """Number of walkers to simulate in parallel."""

    octree_max_depth: int = 14
    """Maximum octree depth (2^14 = 16384 cells per dimension)."""

    octree_leaf_size: int = 12
    """Target particles per octree leaf."""

    octree_rebuild_threshold: float = 0.15
    """Rebuild octree when cluster grows by this fraction."""

    birth_radius_margin: float = 5.0
    """Spawn walkers this many radii beyond cluster."""

    kill_radius_margin: float = 15.0
    """Terminate walkers beyond this distance from cluster."""

    culling_threshold: int = 8
    """Cull walker after this many consecutive away-moves."""

    sphere_hop_safety: float = 0.90
    """Safety factor for sphere-hopping (avoid overshooting)."""

    use_sphere_hopping: bool = True
    """Enable sphere-hopping optimization."""

    use_adaptive_birth_radius: bool = True
    """Enable adaptive birth radius scheduling."""

    use_warp_primitives: bool = True
    """Enable warp-level optimizations (requires CC >= 3.0)."""

    threads_per_block: int = 256
    """CUDA threads per block."""

    num_streams: int = 4
    """Number of CUDA streams for overlap."""
```

### 4.2 Preset Parameter Configurations

```python
# Biological morphology presets
LICHEN_PRESETS = {
    'usnea': DLAPhysicsParams(
        stickiness=0.30,
        bulk_velocity=np.array([0.0, 0.0, 0.5]),
        target_particle_count=50000,
        branch_thickness_scale=0.8,
    ),

    'cladonia': DLAPhysicsParams(
        stickiness=0.65,
        bulk_velocity=np.array([0.0, 0.0, 0.6]),
        target_particle_count=30000,
        substrate_type='plane',
        branch_thickness_scale=1.2,
    ),

    'ramalina': DLAPhysicsParams(
        stickiness=0.50,
        bulk_velocity=np.array([0.0, 0.0, 0.45]),
        target_particle_count=40000,
    ),

    'crustose_radial': DLAPhysicsParams(
        stickiness=0.75,
        bulk_velocity=np.array([0.0, 0.0, 0.0]),
        substrate_type='plane',
        target_particle_count=100000,
    ),
}

# Physics exploration presets
PHYSICS_PRESETS = {
    'classic_dla_2d': DLAPhysicsParams(
        stickiness=1.0,
        substrate_type='plane',
        target_particle_count=10000,
    ),

    'classic_dla_3d': DLAPhysicsParams(
        stickiness=1.0,
        target_particle_count=100000,
    ),

    'dielectric_breakdown': DLAPhysicsParams(
        stickiness=1.0,
        nutrient_field=lambda pos: np.linalg.norm(pos)**0.5,  # η=1.5
        target_particle_count=50000,
    ),

    'eden_model': DLAPhysicsParams(
        stickiness=0.05,
        target_particle_count=50000,
    ),
}
```

---

## 5. Implementation Phases

### Phase 1: Foundation (Week 1-2)

**Goal:** Off-lattice particles with basic random walk and aggregation.

**Deliverables:**
1. Particle data structures (SoA layout)
2. Basic random walk kernel (no sphere-hopping yet)
3. Naive nearest-neighbor search (O(N) per particle)
4. Aggregation logic with stickiness parameter
5. Visualization: export to NumPy array for Plotly 3D scatter

**Validation:**
- Reproduce 2D DLA (constrain z=0)
- Measure fractal dimension: should get D ≈ 1.71 ± 0.05 for 2D DLA
- Compare with existing voxel implementation for same parameters

**Code structure:**
```
dla_cuda_offgrid/
├── particles.py        # Particle data structures
├── kernels.py          # CUDA kernels
├── simulation.py       # Simulation loop
├── visualization.py    # Plotly/PyVista rendering
└── tests/
    └── test_2d_dla.py  # Validation against known results
```

### Phase 2: Octree Acceleration (Week 3-4)

**Goal:** Implement GPU octree for O(log N) nearest-neighbor queries.

**Deliverables:**
1. Octree data structure (breadth-first layout)
2. Morton code-based octree construction kernel
3. Octree nearest-neighbor traversal kernel
4. Octree incremental updates
5. Benchmarks: compare O(N) vs O(log N) performance

**Validation:**
- Correctness: octree NN matches brute-force NN
- Performance: 10-100× speedup for N > 10,000 particles
- Memory: octree overhead < 50% of particle data

**Metrics:**
```python
def benchmark_nearest_neighbor(cluster_size):
    # Brute force: O(N²) total, O(N) per query
    time_bruteforce = measure_kernel_time(bruteforce_nn_kernel, cluster_size)

    # Octree: O(N log N) build + O(log N) per query
    time_octree_build = measure_kernel_time(build_octree_kernel, cluster_size)
    time_octree_query = measure_kernel_time(octree_nn_kernel, cluster_size)

    speedup = time_bruteforce / (time_octree_build + time_octree_query)
    print(f"Cluster size {cluster_size}: {speedup:.1f}× speedup")
```

### Phase 3: Sphere-Hopping Optimization (Week 5)

**Goal:** Implement accelerated random walk using sphere-hopping.

**Deliverables:**
1. Sphere-hopping kernel
2. Particle culling logic
3. Adaptive birth radius scheduler
4. Performance comparison: standard walk vs sphere-hopping

**Validation:**
- Physics: sphere-hopping produces identical fractal dimension
- Performance: 10-100× reduction in walk steps
- Convergence: reaches N particles in fewer iterations

**Expected results:**
| Method | Steps/Particle | Time to 100k particles |
|--------|----------------|------------------------|
| Standard walk | ~50,000 | ~120 seconds |
| Sphere-hopping | ~500 | ~8 seconds |

### Phase 4: Advanced Parameters (Week 6-7)

**Goal:** Implement bulk velocity, rotation, substrate constraints.

**Deliverables:**
1. Bulk velocity kernel
2. Substrate constraint kernels (plane, cylinder, sphere)
3. Rotation transformation
4. Nutrient field evaluation
5. Preset library for lichen morphologies

**Validation:**
- Bulk velocity: produces expected directional growth
- Substrate: particles confined to surface ± tolerance
- Morphology: presets match biological photographs

**Demonstrations:**
```python
# Fruticose lichen with upward growth
params = LICHEN_PRESETS['usnea']
cluster = run_dla_simulation(params)
visualize_3d(cluster, colormap='Greens')

# Crustose lichen on cylindrical bark
params = DLAPhysicsParams(
    stickiness=0.7,
    substrate_type='cylinder',
    substrate_params={'radius': 20.0, 'axis': [0, 0, 1]},
    target_particle_count=100000
)
cluster = run_dla_simulation(params)
visualize_cylinder_growth(cluster, bark_texture=True)
```

### Phase 5: Fractal Analysis (Week 8)

**Goal:** GPU-accelerated fractal dimension calculation.

**Deliverables:**
1. Box-counting kernel
2. Mass-radius scaling analysis
3. Correlation dimension (two-point correlation)
4. Branch statistics (length, thickness distributions)
5. Automated morphology classification

**Implementation:**

```python
@cuda.jit
def box_counting_kernel(particle_positions, box_size, occupied_boxes):
    """
    Count occupied boxes at given scale.

    For each particle, mark its box as occupied using atomic OR.
    Then count total occupied boxes.

    Complexity: O(N) per scale
    """
    tid = cuda.grid(1)
    if tid >= particle_positions.shape[0]:
        return

    # Compute box index
    x = int(particle_positions[tid, 0] / box_size)
    y = int(particle_positions[tid, 1] / box_size)
    z = int(particle_positions[tid, 2] / box_size)

    # Flatten 3D index to 1D
    box_idx = x + y * grid_dim + z * grid_dim * grid_dim

    # Mark box as occupied (atomic OR for thread safety)
    cuda.atomic.max(occupied_boxes, box_idx, 1)

def compute_fractal_dimension_gpu(particle_positions):
    """
    Compute fractal dimension via box-counting on GPU.

    Returns:
    --------
    D : float
        Fractal dimension from log-log slope
    scales : array
        Box sizes used
    counts : array
        Number of occupied boxes at each scale
    """
    # Try box sizes from 1 to cluster_size / 8
    cluster_size = particle_positions.max(axis=0) - particle_positions.min(axis=0)
    max_box_size = cluster_size.max()

    scales = np.logspace(
        np.log10(1.0),
        np.log10(max_box_size / 8),
        num=20
    )

    counts = np.zeros(len(scales), dtype=np.int32)

    for i, box_size in enumerate(scales):
        grid_dim = int(max_box_size / box_size) + 1
        occupied = cuda.device_array(grid_dim**3, dtype=np.int32)

        threads = 256
        blocks = (len(particle_positions) + threads - 1) // threads

        box_counting_kernel[blocks, threads](
            cuda.to_device(particle_positions),
            box_size,
            occupied
        )

        counts[i] = int(occupied.copy_to_host().sum())

    # Fit log-log regression
    valid = counts > 0
    log_scales = np.log(1.0 / scales[valid])
    log_counts = np.log(counts[valid])

    D, intercept = np.polyfit(log_scales, log_counts, 1)

    return D, scales, counts
```

**Validation:**
- 2D DLA: D ≈ 1.71
- 3D DLA: D ≈ 2.50
- Eden model: D ≈ 2.00 (2D), 3.00 (3D)

### Phase 6: Visualization and Export (Week 9)

**Goal:** High-quality rendering and mesh export for 3D printing.

**Deliverables:**
1. PyVista volume rendering
2. Marching cubes mesh generation
3. STL/OBJ export
4. Animation framework (growth over time)
5. Interactive Jupyter widgets

**Visualization pipeline:**

```python
def create_lichen_mesh(particle_positions, particle_radius=1.0, resolution=64):
    """
    Convert particle cloud to smooth mesh using marching cubes.

    Steps:
    1. Create volumetric scalar field (distance to nearest particle)
    2. Run marching cubes at isosurface = particle_radius
    3. Smooth mesh (Laplacian smoothing)
    4. Compute vertex normals for lighting
    """
    import pyvista as pv
    from scipy.spatial import cKDTree

    # Build KD-tree for distance queries
    tree = cKDTree(particle_positions)

    # Create uniform grid
    bounds = particle_positions.min(axis=0), particle_positions.max(axis=0)
    grid = pv.ImageData(
        dimensions=(resolution, resolution, resolution),
        spacing=(
            (bounds[1][0] - bounds[0][0]) / resolution,
            (bounds[1][1] - bounds[0][1]) / resolution,
            (bounds[1][2] - bounds[0][2]) / resolution
        ),
        origin=bounds[0]
    )

    # Compute distance field
    points = grid.points
    distances, _ = tree.query(points)
    grid['distance'] = distances

    # Marching cubes
    mesh = grid.contour([particle_radius], method='marching_cubes')

    # Smooth
    mesh = mesh.smooth(n_iter=50, relaxation_factor=0.1)

    return mesh

# Export for 3D printing
mesh = create_lichen_mesh(cluster_positions, particle_radius=1.0)
mesh.save('fruticose_lichen.stl')

# Interactive visualization
plotter = pv.Plotter()
plotter.add_mesh(mesh, color='#4a8c4a', smooth_shading=True)
plotter.add_light(pv.Light(position=(10, 10, 10), intensity=0.8))
plotter.show()
```

### Phase 7: Scaling and Optimization (Week 10-11)

**Goal:** Achieve 1M+ particle simulations with acceptable performance.

**Deliverables:**
1. Multi-GPU support (data parallelism)
2. Memory pool allocator (reduce allocation overhead)
3. Profiling report with optimization recommendations
4. Benchmarks on various GPU architectures

**Scaling strategy:**

```python
class MultiGPUDLASimulation:
    """
    Distribute walker batches across multiple GPUs.
    Cluster state is replicated (read-only on each GPU).
    """

    def __init__(self, params, num_gpus=None):
        if num_gpus is None:
            num_gpus = cuda.gpus.count

        self.num_gpus = num_gpus
        self.devices = [cuda.gpus[i] for i in range(num_gpus)]

        # Replicate cluster on each GPU
        self.cluster_copies = [
            cuda.to_device(initial_cluster, stream=device.stream)
            for device in self.devices
        ]

    def step(self, walker_batch):
        """
        Distribute walkers across GPUs, aggregate results.
        """
        batch_size = len(walker_batch) // self.num_gpus
        results = []

        for i, device in enumerate(self.devices):
            with device:
                sub_batch = walker_batch[i*batch_size:(i+1)*batch_size]
                result = self._simulate_batch_on_gpu(
                    sub_batch,
                    self.cluster_copies[i],
                    device.stream
                )
                results.append(result)

        # Synchronize and merge
        cuda.synchronize()
        new_particles = np.concatenate([r.copy_to_host() for r in results])

        # Update all cluster copies
        for cluster_copy in self.cluster_copies:
            cluster_copy.copy_to_device(new_particles)

        return new_particles
```

**Target performance (Tesla T4):**
- 100k particles: <5 seconds
- 1M particles: <2 minutes
- 10M particles: <30 minutes (multi-GPU)

### Phase 8: Integration and Documentation (Week 12)

**Goal:** Integrate with existing notebook, create tutorials.

**Deliverables:**
1. Unified API with existing lattice-based implementation
2. Migration guide (lattice → off-lattice)
3. Tutorial notebooks for each lichen morphology
4. Gallery of generated structures
5. Performance comparison report

**Integration example:**

```python
# New unified API
from dla_cuda import DLASimulation

# Lattice-based (backward compatible)
sim_lattice = DLASimulation(
    method='lattice',
    grid_size=128,
    num_particles=25000,
    sticking_prob=0.5
)
cluster_lattice = sim_lattice.run()

# Off-lattice (new)
sim_offgrid = DLASimulation(
    method='off_lattice',
    physics_params=LICHEN_PRESETS['usnea'],
    compute_params=DLAComputeParams(
        walker_batch_size=50000,
        use_sphere_hopping=True
    )
)
cluster_offgrid = sim_offgrid.run()

# Both return same interface
cluster_offgrid.visualize_3d(colormap='Greens')
cluster_offgrid.export_mesh('lichen.stl')
print(f"Fractal dimension: {cluster_offgrid.fractal_dimension:.2f}")
```

---

## 6. Validation and Testing Strategy

### 6.1 Unit Tests

```python
import pytest
import numpy as np
from dla_cuda import (
    ParticleArray,
    build_octree,
    octree_nearest_neighbor,
    accelerated_random_walk
)

def test_octree_nearest_neighbor():
    """Verify octree NN matches brute-force NN."""
    particles = np.random.randn(1000, 3).astype(np.float32)
    octree = build_octree(particles)

    query_point = np.array([0.5, 0.5, 0.5], dtype=np.float32)

    # Brute force
    distances = np.linalg.norm(particles - query_point, axis=1)
    true_nearest_dist = distances.min()

    # Octree
    octree_nearest_dist = octree_nearest_neighbor(query_point, octree)

    assert np.isclose(octree_nearest_dist, true_nearest_dist, rtol=1e-5)

def test_fractal_dimension_2d():
    """2D DLA should have D ≈ 1.71."""
    from dla_cuda import DLASimulation, DLAPhysicsParams

    params = DLAPhysicsParams(
        stickiness=1.0,
        substrate_type='plane',
        target_particle_count=5000
    )

    sim = DLASimulation(method='off_lattice', physics_params=params)
    cluster = sim.run()

    D = cluster.fractal_dimension
    assert 1.65 < D < 1.80, f"Expected D ≈ 1.71, got {D:.2f}"

def test_sphere_hopping_physics():
    """Sphere-hopping should not change fractal dimension."""
    params = DLAPhysicsParams(stickiness=1.0, target_particle_count=10000)

    # Standard walk
    sim_standard = DLASimulation(
        method='off_lattice',
        physics_params=params,
        compute_params=DLAComputeParams(use_sphere_hopping=False)
    )
    cluster_standard = sim_standard.run()

    # Sphere-hopping
    sim_hopping = DLASimulation(
        method='off_lattice',
        physics_params=params,
        compute_params=DLAComputeParams(use_sphere_hopping=True)
    )
    cluster_hopping = sim_hopping.run()

    # Dimensions should match within statistical error
    assert abs(cluster_standard.fractal_dimension -
               cluster_hopping.fractal_dimension) < 0.1
```

### 6.2 Performance Benchmarks

```python
def benchmark_suite():
    """Compare performance across implementations and parameters."""
    import pandas as pd
    import time

    results = []

    for N in [1000, 10000, 100000, 1000000]:
        for method in ['lattice', 'off_lattice', 'off_lattice_hopping']:
            if method == 'lattice' and N > 25000:
                continue  # Lattice doesn't scale

            start = time.time()

            if method == 'lattice':
                sim = DLASimulation(method='lattice', num_particles=N)
            elif method == 'off_lattice':
                sim = DLASimulation(
                    method='off_lattice',
                    physics_params=DLAPhysicsParams(target_particle_count=N),
                    compute_params=DLAComputeParams(use_sphere_hopping=False)
                )
            else:  # off_lattice_hopping
                sim = DLASimulation(
                    method='off_lattice',
                    physics_params=DLAPhysicsParams(target_particle_count=N),
                    compute_params=DLAComputeParams(use_sphere_hopping=True)
                )

            cluster = sim.run()
            elapsed = time.time() - start

            results.append({
                'N': N,
                'method': method,
                'time_seconds': elapsed,
                'particles_per_second': N / elapsed,
                'fractal_dimension': cluster.fractal_dimension
            })

    df = pd.DataFrame(results)
    print(df)

    # Expected results (Tesla T4):
    # N=100k, lattice: ~60s, 1666 particles/sec
    # N=100k, off_lattice: ~30s, 3333 particles/sec
    # N=100k, hopping: ~5s, 20000 particles/sec
    # N=1M, hopping: ~90s, 11111 particles/sec
```

### 6.3 Biological Validation

```python
def validate_lichen_morphology(preset_name):
    """
    Compare simulated morphology against biological measurements.

    Metrics:
    - Fractal dimension
    - Branch length distribution
    - Branch angle distribution
    - Vertical extent / radial extent ratio
    """
    params = LICHEN_PRESETS[preset_name]
    sim = DLASimulation(method='off_lattice', physics_params=params)
    cluster = sim.run()

    # Compute metrics
    metrics = cluster.compute_morphology_metrics()

    # Compare against literature values
    expected = {
        'usnea': {
            'fractal_dimension': (2.3, 2.6),
            'vertical_to_radial_ratio': (1.2, 2.0),
        },
        'cladonia': {
            'fractal_dimension': (2.4, 2.7),
            'vertical_to_radial_ratio': (0.8, 1.5),
        },
        # ...
    }

    for metric, (low, high) in expected[preset_name].items():
        value = metrics[metric]
        assert low <= value <= high, \
            f"{metric} = {value:.2f} outside expected range [{low}, {high}]"

    print(f"✓ {preset_name} morphology validated")
```

---

## 7. Expected Performance Characteristics

### 7.1 Time Complexity Analysis

| Component | Complexity | Notes |
|-----------|------------|-------|
| Octree build | O(N log N) | Morton code sort dominates |
| Octree query | O(log N) | Average case, balanced tree |
| Random walk (standard) | O(S) | S = steps per particle (~10⁴-10⁵) |
| Random walk (hopping) | O(H) | H = hops per particle (~10²-10³) |
| Aggregation | O(1) | Atomic compare-and-swap |
| Overall (N particles) | O(N² log N) | Standard walk |
| Overall (hopping) | O(N log N) | Sphere-hopping dominant |

### 7.2 Memory Complexity

| Data Structure | Size (1M particles) | Notes |
|----------------|---------------------|-------|
| Particle positions | 12 MB | 3 × float32 |
| Particle velocities | 12 MB | Optional, for bulk velocity |
| Octree nodes | ~20 MB | ~500k nodes × 40 bytes |
| Walker batch (100k) | 1.2 MB | Temporary |
| **Total** | **~45 MB** | Fits comfortably in 16 GB GPU |

### 7.3 Projected Performance (Tesla T4)

| Metric | Value | Configuration |
|--------|-------|---------------|
| 100k particles | 5 seconds | Sphere-hopping, single GPU |
| 1M particles | 90 seconds | Sphere-hopping, single GPU |
| 10M particles | 25 minutes | Sphere-hopping, 4× Tesla T4 |
| Fractal dim accuracy | ±0.05 | 10k+ particles, box-counting |

---

## 8. Future Extensions

### 8.1 Anisotropic Diffusion

Model directional diffusion (e.g., along wood grain in bark colonization).

```python
@dataclass
class AnisotropicDiffusionParams:
    diffusion_tensor: np.ndarray  # 3×3 symmetric positive-definite matrix
    """
    D = [[D_xx, D_xy, D_xz],
         [D_xy, D_yy, D_yz],
         [D_xz, D_yz, D_zz]]

    Random walk step: Δx ~ N(0, 2*D*Δt)
    """
```

### 8.2 Multi-Species Competition

Simulate lichen community dynamics with multiple competing species.

```python
class MultiSpeciesDLA:
    """
    Each species has different:
    - Stickiness
    - Growth rate
    - Nutrient requirements

    Species compete for space via contact inhibition.
    """
    species_params: List[DLAPhysicsParams]
    contact_inhibition: float  # Probability of blocking competitor
```

### 8.3 Temporal Environmental Variation

Model seasonal or daily cycles (e.g., wet/dry periods).

```python
def time_varying_stickiness(t, period=100):
    """
    Stickiness varies sinusoidally with time.

    High stickiness during wet periods (rapid growth).
    Low stickiness during dry periods (slow growth).
    """
    return 0.5 + 0.3 * np.sin(2 * np.pi * t / period)
```

### 8.4 Mechanical Stress and Fragmentation

Model branch breakage under self-weight or environmental stress.

```python
def compute_stress_distribution(cluster, gravity=9.8):
    """
    Calculate stress on each particle from accumulated mass above.
    Break branches when stress exceeds tensile strength.
    """
    # Build tree of connections
    # Propagate forces from tips to base
    # Break weak connections
```

---

## 9. References and Resources

### Academic Papers

1. **Witten & Sander (1981)**: Original DLA paper
   *Phys Rev Lett* 47, 1400-1403

2. **Witten & Sander (1983)**: Extended DLA theory
   *Phys Rev B* 27, 5686-5697

3. **Meakin (1983)**: Fractal dimension analysis
   *Phys Rev A* 27, 1495

4. **Stock (2006)**: Efficient 3D DLA algorithms
   markjstock.org/dla3d/

5. **Bourke (1991-2024)**: DLA implementation notes
   paulbourke.net/fractals/dla/

### Software Libraries

- **Numba CUDA**: cuda.pydata.org
- **CuPy**: cupy.dev (NumPy-compatible GPU arrays)
- **PyVista**: pyvista.org (3D visualization)
- **scikit-image**: Marching cubes (skimage.measure.marching_cubes)

### Biological References

6. **Nash (2008)**: *Lichen Biology* (2nd ed), Cambridge
   Chapter 4: Growth and morphogenesis

7. **Desbenoit et al (2004)**: "Simulating and Modeling Lichen Growth"
   *Computer Graphics Forum* 23(3), 341-350

---

## Appendix A: Mathematical Foundations

### A.1 Harmonic Measure and Growth Probability

DLA growth probability at boundary point **r** is proportional to the local electric field:

$$P(\mathbf{r}) = \frac{1}{Z} \left|\nabla \phi(\mathbf{r})\right|$$

where $\phi$ satisfies Laplace's equation $\nabla^2 \phi = 0$ with boundary conditions:
- $\phi = 0$ on cluster surface
- $\phi \to 1$ at infinity

The normalization constant:

$$Z = \oint_{\partial \Omega} \left|\nabla \phi\right| \, dS$$

ensures $\sum_{\mathbf{r} \in \partial \Omega} P(\mathbf{r}) = 1$.

**Numerical approximation:** Random walk hitting probabilities converge to harmonic measure in the limit of infinite walkers.

### A.2 Fractal Dimension from Scaling Relations

The mass-radius relation for DLA clusters:

$$N(R) = A R^{D_f}$$

where:
- $N(R)$ = number of particles within radius $R$ from seed
- $A$ = prefactor (depends on geometry, typically $O(1)$)
- $D_f$ = fractal dimension

Taking logarithms:

$$\log N(R) = \log A + D_f \log R$$

Linear regression in log-log space yields $D_f$ as the slope.

**Box-counting method:**

$$N_{\epsilon} = B \epsilon^{-D_f}$$

where $N_{\epsilon}$ is the number of boxes of size $\epsilon$ needed to cover the cluster.

### A.3 Sphere-Hopping Derivation

**Theorem:** A Brownian walker starting at distance $r$ from a sphere of radius $R$ has uniform hitting probability on the sphere's surface.

**Proof sketch:** The hitting distribution $p(\theta, \phi)$ must satisfy Laplace's equation in spherical coordinates with rotational symmetry. The only solution is the constant distribution (uniform measure).

**Consequence:** We can skip the random walk and directly place the walker uniformly on a sphere centered at the current position with radius equal to the distance to the nearest cluster particle.

**Implementation detail:** Use Marsaglia's rejection method for uniform sampling on sphere:

```python
def random_point_on_sphere(radius):
    while True:
        x, y, z = np.random.uniform(-1, 1, 3)
        r_sq = x*x + y*y + z*z
        if 0 < r_sq <= 1:
            scale = radius / np.sqrt(r_sq)
            return np.array([x, y, z]) * scale
```

---

## Appendix B: CUDA Programming Best Practices

### B.1 Memory Access Patterns

**Coalesced access:** Threads in a warp (32 threads) access consecutive memory locations.

```python
# Good: coalesced (SoA)
x[tid]  # Thread 0 reads x[0], thread 1 reads x[1], ...

# Bad: strided (AoS)
particles[tid, 0]  # Thread 0 reads particles[0,0], thread 1 reads particles[1,0]
# Causes many separate memory transactions
```

**Solution:** Structure-of-Arrays (SoA) layout.

### B.2 Shared Memory Usage

Shared memory is 100× faster than global memory but limited (48 KB per SM on Turing).

**Use case:** Cache frequently accessed data within a thread block.

```python
@cuda.jit
def kernel_with_shared_cache():
    shared_data = cuda.shared.array(256, dtype=np.float32)

    tid = cuda.threadIdx.x

    # Cooperative load from global to shared
    shared_data[tid] = global_data[tid]
    cuda.syncthreads()  # Wait for all threads to load

    # Now all threads can access shared_data with low latency
    result = compute(shared_data)
```

### B.3 Avoiding Divergence

Threads in a warp execute in lockstep. Divergent branches cause serialization.

```python
# Bad: divergent (threads take different paths)
if tid % 2 == 0:
    result = expensive_computation_A()
else:
    result = expensive_computation_B()

# Good: predicated (all threads execute both, mask results)
result_A = expensive_computation_A()
result_B = expensive_computation_B()
result = result_A if tid % 2 == 0 else result_B
```

**Modern GPUs** (Volta+) have independent thread scheduling, but minimizing divergence is still beneficial.

### B.4 Occupancy Optimization

**Occupancy** = (active warps per SM) / (max warps per SM)

Higher occupancy ⇒ better latency hiding ⇒ higher throughput.

**Factors limiting occupancy:**
1. Registers per thread
2. Shared memory per block
3. Threads per block

**Tool:** `cuda-occupancy-calculator` (part of CUDA toolkit)

```bash
# Check occupancy for compiled kernel
cuobjdump -sass my_kernel.cubin | grep -A 20 "code for sm_75"
```

**Target:** 50-100% occupancy (100% not always necessary if kernel is compute-bound).

---

## Appendix C: Visualization Techniques

### C.1 Point Cloud Rendering (Plotly)

```python
def visualize_particles_plotly(positions, colors=None, size=2):
    import plotly.graph_objects as go

    if colors is None:
        # Color by distance from origin
        distances = np.linalg.norm(positions, axis=1)
        colors = distances / distances.max()

    fig = go.Figure(data=[go.Scatter3d(
        x=positions[:, 0],
        y=positions[:, 1],
        z=positions[:, 2],
        mode='markers',
        marker=dict(
            size=size,
            color=colors,
            colorscale='Viridis',
            opacity=0.8
        )
    )])

    fig.update_layout(
        scene=dict(
            aspectmode='data',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
        ),
        title="DLA Cluster"
    )

    fig.show()
```

### C.2 Volume Rendering (PyVista)

```python
def visualize_volume_pyvista(positions, particle_radius=1.0):
    import pyvista as pv

    # Create point cloud
    cloud = pv.PolyData(positions)

    # Add sphere glyphs
    spheres = cloud.glyph(geom=pv.Sphere(radius=particle_radius), scale=False)

    # Render
    plotter = pv.Plotter()
    plotter.add_mesh(spheres, color='lightgreen', smooth_shading=True)
    plotter.add_axes()
    plotter.show()
```

### C.3 Mesh Export for 3D Printing

```python
def export_printable_mesh(positions, filename, particle_radius=1.0, resolution=64):
    import pyvista as pv
    from scipy.spatial import cKDTree

    # Build distance field
    tree = cKDTree(positions)

    # Create grid
    bounds = positions.min(axis=0), positions.max(axis=0)
    margin = 5 * particle_radius
    grid = pv.ImageData(
        dimensions=(resolution, resolution, resolution),
        spacing=(
            (bounds[1][0] - bounds[0][0] + 2*margin) / resolution,
            (bounds[1][1] - bounds[0][1] + 2*margin) / resolution,
            (bounds[1][2] - bounds[0][2] + 2*margin) / resolution
        ),
        origin=bounds[0] - margin
    )

    # Compute distance field
    distances, _ = tree.query(grid.points)
    grid['distance'] = distances

    # Extract isosurface
    mesh = grid.contour([particle_radius])

    # Clean up
    mesh = mesh.clean()
    mesh = mesh.fill_holes(1000)
    mesh = mesh.smooth(n_iter=100)

    # Export
    mesh.save(filename)
    print(f"Exported {mesh.n_cells} triangles to {filename}")
```

---

## Conclusion

This implementation plan provides a comprehensive roadmap for building state-of-the-art CUDA-accelerated DLA simulations in Python. The phased approach ensures incremental validation while building toward the goal of million-particle scale with physically accurate morphology.

**Key innovations:**
1. Off-lattice continuous coordinates (vs existing voxel grid)
2. GPU octree with O(log N) queries (vs O(N) neighbor search)
3. Sphere-hopping random walks (100× fewer steps)
4. Rich parameter system matching biological phenomena
5. Scalable multi-GPU architecture

**Next steps:**
1. Review and approve this plan
2. Set up project structure (dla_cuda_offgrid/ directory)
3. Begin Phase 1 implementation
4. Establish continuous integration with automated testing

**Estimated timeline:** 12 weeks from approval to production-ready implementation.
