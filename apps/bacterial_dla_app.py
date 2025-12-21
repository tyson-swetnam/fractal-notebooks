"""
Bacterial DLA (Diffusion-Limited Aggregation) Simulation
Interactive Streamlit app with real-time animation

Based on Fujikawa & Matsushita (1989) - fractal bacterial colonies with D ≈ 1.71

Run with: streamlit run bacterial_dla_app.py
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import time

# Page config
st.set_page_config(
    page_title="Bacterial DLA",
    page_icon="🌿",
    layout="wide"
)

# Custom colormap
dla_cmap = LinearSegmentedColormap.from_list('dla',
    ['#0a0a0a', '#1a4a1a', '#2d7d2d', '#4db34d', '#7ddb7d', '#b3ffb3'])


class DLASimulation:
    """Batch-processed DLA simulation for real-time visualization."""

    def __init__(self, grid_size, batch_size=500):
        self.grid_size = grid_size
        self.batch_size = batch_size
        self.grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
        self.center = grid_size // 2

        # Seed at center
        self.grid[self.center, self.center] = 1
        self.particles_added = 1
        self.max_radius = 1

        # Neighbor offsets
        self.neighbors = np.array([[0, 1], [0, -1], [1, 0], [-1, 0]], dtype=np.int32)

        # Initialize walkers
        self._spawn_walkers()

    def _spawn_walkers(self):
        """Spawn batch of walkers on circle around colony."""
        birth_r = self.max_radius + 5
        angles = np.random.uniform(0, 2 * np.pi, self.batch_size)
        self.walker_x = (self.center + birth_r * np.cos(angles)).astype(np.int32)
        self.walker_y = (self.center + birth_r * np.sin(angles)).astype(np.int32)
        self.active = np.ones(self.batch_size, dtype=bool)

    def step(self, sticking_prob=1.0, steps_per_call=100):
        """Perform simulation steps, return number of particles added."""
        added = 0
        kill_r_sq = (self.max_radius + 50) ** 2

        for _ in range(steps_per_call):
            if not np.any(self.active):
                self._spawn_walkers()

            # Random walk for all active walkers
            move_idx = np.random.randint(0, 4, self.batch_size)
            dx = self.neighbors[move_idx, 0]
            dy = self.neighbors[move_idx, 1]

            self.walker_x = np.where(self.active, self.walker_x + dx, self.walker_x)
            self.walker_y = np.where(self.active, self.walker_y + dy, self.walker_y)

            # Check kill radius
            dist_sq = (self.walker_x - self.center)**2 + (self.walker_y - self.center)**2
            escaped = dist_sq > kill_r_sq

            # Check bounds
            out_of_bounds = ((self.walker_x < 1) | (self.walker_x >= self.grid_size - 1) |
                            (self.walker_y < 1) | (self.walker_y >= self.grid_size - 1))

            # Deactivate escaped/OOB walkers
            self.active = self.active & ~escaped & ~out_of_bounds

            if not np.any(self.active):
                continue

            # Check for neighbors
            has_neighbor = np.zeros(self.batch_size, dtype=bool)
            for nx, ny in self.neighbors:
                check_x = np.clip(self.walker_x + nx, 0, self.grid_size - 1)
                check_y = np.clip(self.walker_y + ny, 0, self.grid_size - 1)
                has_neighbor |= (self.grid[check_x, check_y] > 0)

            # Sticking check
            will_stick = self.active & has_neighbor & (np.random.random(self.batch_size) < sticking_prob)

            # Add sticking particles
            stick_indices = np.where(will_stick)[0]
            for idx in stick_indices:
                px, py = self.walker_x[idx], self.walker_y[idx]
                if self.grid[px, py] == 0:
                    self.grid[px, py] = 1
                    self.particles_added += 1
                    added += 1
                    r = int(np.sqrt((px - self.center)**2 + (py - self.center)**2))
                    self.max_radius = max(self.max_radius, r + 1)

            # Deactivate stuck walkers
            self.active = self.active & ~will_stick

            # Respawn inactive walkers
            inactive = ~self.active
            n_inactive = np.sum(inactive)
            if n_inactive > 0:
                birth_r = self.max_radius + 5
                angles = np.random.uniform(0, 2 * np.pi, n_inactive)
                self.walker_x[inactive] = (self.center + birth_r * np.cos(angles)).astype(np.int32)
                self.walker_y[inactive] = (self.center + birth_r * np.sin(angles)).astype(np.int32)
                self.active[inactive] = True

        return added


def box_counting_dimension(binary_image, min_box_size=2, max_box_size=None):
    """Estimate fractal dimension using box-counting method."""
    if max_box_size is None:
        max_box_size = min(binary_image.shape) // 8

    box_sizes = []
    size = min_box_size
    while size <= max_box_size:
        box_sizes.append(size)
        size *= 2
    box_sizes = np.array(box_sizes)

    counts = []
    for box_size in box_sizes:
        n_boxes = 0
        for i in range(0, binary_image.shape[0], box_size):
            for j in range(0, binary_image.shape[1], box_size):
                box = binary_image[i:i+box_size, j:j+box_size]
                if box.sum() > 0:
                    n_boxes += 1
        counts.append(n_boxes)

    counts = np.array(counts)
    if len(counts) < 2 or np.any(counts == 0):
        return 1.71  # Default

    log_sizes = np.log(1.0 / box_sizes)
    log_counts = np.log(counts)
    coeffs = np.polyfit(log_sizes, log_counts, 1)

    return coeffs[0]


def main():
    st.title("🌿 Bacterial DLA Simulation")
    st.markdown("""
    Diffusion-Limited Aggregation model of bacterial colony growth.
    Based on Fujikawa & Matsushita (1989) - *Bacillus subtilis* colonies exhibit fractal dimension D ≈ 1.71.
    """)

    # Sidebar controls
    st.sidebar.header("Simulation Parameters")

    grid_size = st.sidebar.slider("Grid Size", 201, 601, 401, 100)
    batch_size = st.sidebar.slider("Walker Batch Size", 100, 2000, 500, 100)

    st.sidebar.subheader("Sticking Probability")
    sticking_prob = st.sidebar.slider(
        "p_stick",
        0.01, 1.0, 1.0, 0.01,
        help="1.0 = Pure DLA (D≈1.71), lower = denser colonies"
    )

    st.sidebar.subheader("Animation Speed")
    steps_per_frame = st.sidebar.slider("Steps per Frame", 10, 200, 50, 10)
    frame_delay = st.sidebar.slider("Frame Delay (ms)", 10, 200, 50, 10)

    # Presets
    st.sidebar.subheader("Morphology Presets")
    preset = st.sidebar.selectbox("Load Preset", [
        "Custom",
        "Pure DLA (D≈1.71)",
        "Dense Branching (D≈1.8)",
        "Transitional (D≈1.9)",
        "Eden-like (D≈2.0)"
    ])

    if preset == "Pure DLA (D≈1.71)":
        sticking_prob = 1.0
    elif preset == "Dense Branching (D≈1.8)":
        sticking_prob = 0.3
    elif preset == "Transitional (D≈1.9)":
        sticking_prob = 0.1
    elif preset == "Eden-like (D≈2.0)":
        sticking_prob = 0.03

    # Control buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        start_btn = st.button("▶️ Start", use_container_width=True)
    with col2:
        stop_btn = st.button("⏹️ Stop", use_container_width=True)
    with col3:
        reset_btn = st.button("🔄 Reset", use_container_width=True)

    # Initialize session state
    if 'running' not in st.session_state:
        st.session_state.running = False
    if 'dla_sim' not in st.session_state:
        st.session_state.dla_sim = None

    if start_btn:
        st.session_state.running = True
    if stop_btn:
        st.session_state.running = False
    if reset_btn:
        st.session_state.dla_sim = None
        st.session_state.running = False

    # Initialize simulation
    if st.session_state.dla_sim is None or reset_btn:
        st.session_state.dla_sim = DLASimulation(grid_size, batch_size)

    sim = st.session_state.dla_sim

    # Display area
    col_plot, col_stats = st.columns([2, 1])

    with col_plot:
        plot_placeholder = st.empty()

    with col_stats:
        st.subheader("Colony Statistics")
        particles_metric = st.empty()
        radius_metric = st.empty()
        dimension_metric = st.empty()
        rate_metric = st.empty()

    status_placeholder = st.empty()

    # Animation loop
    if st.session_state.running:
        last_time = time.time()
        last_particles = sim.particles_added

        while st.session_state.running:
            # Simulation steps
            added = sim.step(sticking_prob, steps_per_frame)

            # Calculate rate
            current_time = time.time()
            dt = current_time - last_time
            if dt > 0:
                rate = (sim.particles_added - last_particles) / dt
            else:
                rate = 0
            last_time = current_time
            last_particles = sim.particles_added

            # Update plot
            fig, ax = plt.subplots(figsize=(8, 8))
            fig.patch.set_facecolor('#0a0a0a')
            ax.set_facecolor('#0a0a0a')
            ax.imshow(sim.grid, cmap=dla_cmap, interpolation='nearest')
            ax.axis('off')
            ax.set_title(f'Particles: {sim.particles_added}', color='white', fontsize=14)
            plot_placeholder.pyplot(fig)
            plt.close(fig)

            # Update stats
            particles_metric.metric("Total Particles", f"{sim.particles_added:,}")
            radius_metric.metric("Colony Radius", f"{sim.max_radius}")

            # Compute fractal dimension periodically
            if sim.particles_added > 100 and sim.particles_added % 500 < steps_per_frame:
                D = box_counting_dimension(sim.grid)
                dimension_metric.metric("Fractal Dimension", f"{D:.3f}")

            rate_metric.metric("Growth Rate", f"{rate:.0f} particles/s")

            status_placeholder.text(f"Running... {sim.particles_added:,} particles")

            time.sleep(frame_delay / 1000.0)
    else:
        # Show current state
        fig, ax = plt.subplots(figsize=(8, 8))
        fig.patch.set_facecolor('#0a0a0a')
        ax.set_facecolor('#0a0a0a')
        ax.imshow(sim.grid, cmap=dla_cmap, interpolation='nearest')
        ax.axis('off')
        ax.set_title(f'Particles: {sim.particles_added}', color='white', fontsize=14)
        plot_placeholder.pyplot(fig)
        plt.close(fig)

        # Stats
        particles_metric.metric("Total Particles", f"{sim.particles_added:,}")
        radius_metric.metric("Colony Radius", f"{sim.max_radius}")

        if sim.particles_added > 100:
            D = box_counting_dimension(sim.grid)
            dimension_metric.metric("Fractal Dimension", f"{D:.3f}")

        rate_metric.metric("Growth Rate", "—")

        status_placeholder.text(f"Paused. {sim.particles_added:,} particles. Click Start to continue.")

    # Information
    st.markdown("---")

    col_info1, col_info2 = st.columns(2)

    with col_info1:
        st.markdown("""
        ### The DLA Algorithm

        1. **Seed**: Start with a single particle at the center
        2. **Spawn**: Release random walkers from a circle around the colony
        3. **Walk**: Each walker performs a random walk
        4. **Stick**: When a walker touches the colony, it sticks with probability p
        5. **Repeat**: Continue until desired colony size

        ### Sticking Probability Effects

        | p_stick | Morphology | Fractal D |
        |---------|------------|-----------|
        | 1.0 | Pure DLA (dendritic) | ~1.71 |
        | 0.3 | Dense branching | ~1.8 |
        | 0.1 | Transitional | ~1.9 |
        | 0.03 | Eden-like (compact) | ~2.0 |
        """)

    with col_info2:
        st.markdown("""
        ### Physical Interpretation

        The sticking probability models **nutrient availability**:

        - **High p (≈1)**: Low nutrients → particles stick immediately at tips
          → dendritic, fractal growth (DLA regime)

        - **Low p (≈0.01)**: High nutrients → particles can penetrate
          → compact, Eden-like growth

        ### Screening Effect

        Interior branches stop growing because protruding tips
        "screen" them from incoming particles. This is exactly
        what happens in nutrient-limited bacterial colonies!

        ### Reference
        Fujikawa, H. & Matsushita, M. (1989).
        *J. Phys. Soc. Japan*, 58, 3875-3878.
        """)


if __name__ == "__main__":
    main()
