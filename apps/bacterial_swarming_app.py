"""
Bacterial Swarming Reaction-Diffusion Simulation
Interactive Streamlit app with real-time animation

Based on Kawasaki et al. (1997) model for Bacillus subtilis colony patterns.

Run with: streamlit run bacterial_swarming_app.py
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.ndimage import laplace
import time

# Page config
st.set_page_config(
    page_title="Bacterial Swarming",
    page_icon="🦠",
    layout="wide"
)

# Custom colormaps
bacteria_cmap = LinearSegmentedColormap.from_list('bacteria',
    ['#0a0a0a', '#1a3d1a', '#2d6b2d', '#3d9b3d', '#4ddb4d', '#7dff7d'])
nutrient_cmap = LinearSegmentedColormap.from_list('nutrient',
    ['#0a0a0a', '#0a1a3d', '#1a3d6b', '#2d6b9b', '#3d9bdb', '#7ddbff'])


def init_simulation(grid_size, seed_radius=5):
    """Initialize bacterial and nutrient fields."""
    bacteria = np.zeros((grid_size, grid_size), dtype=np.float32)
    nutrients = np.ones((grid_size, grid_size), dtype=np.float32)

    # Seed colony at center
    center = grid_size // 2
    y, x = np.ogrid[-center:grid_size-center, -center:grid_size-center]
    mask = x*x + y*y <= seed_radius*seed_radius
    bacteria[mask] = 0.8

    return bacteria, nutrients


def simulation_step(bacteria, nutrients, diffusion_rate, consumption_rate,
                    growth_rate, bacteria_motility, noise_amplitude, dt=0.5):
    """Perform one simulation step."""
    # Nutrient diffusion (Laplacian)
    nutrient_lap = laplace(nutrients)

    # Nutrient consumption by bacteria
    consumption = consumption_rate * bacteria * nutrients

    # Bacterial growth (logistic, nutrient-dependent)
    growth = growth_rate * bacteria * nutrients * (1 - bacteria)

    # Bacterial diffusion (motility)
    bacteria_lap = laplace(bacteria)

    # Update fields
    nutrients += dt * (diffusion_rate * nutrient_lap - consumption)
    nutrients = np.clip(nutrients, 0, 1)

    bacteria += dt * (growth + bacteria_motility * bacteria_lap)

    # Add stochastic noise for branching instability
    noise = np.random.normal(0, noise_amplitude, bacteria.shape)
    edge_mask = (bacteria > 0.05) & (bacteria < 0.8)
    bacteria += noise * edge_mask
    bacteria = np.clip(bacteria, 0, 1)

    return bacteria, nutrients


def main():
    st.title("🦠 Bacterial Swarming Simulation")
    st.markdown("""
    Reaction-diffusion model of bacterial colony growth based on Kawasaki et al. (1997).
    Watch dendritic branching patterns emerge from nutrient-limited growth!
    """)

    # Sidebar controls
    st.sidebar.header("Simulation Parameters")

    grid_size = st.sidebar.slider("Grid Size", 100, 500, 300, 50)

    st.sidebar.subheader("Nutrient Dynamics")
    diffusion_rate = st.sidebar.slider("Nutrient Diffusion", 0.05, 0.5, 0.2, 0.05)
    consumption_rate = st.sidebar.slider("Consumption Rate", 0.02, 0.2, 0.08, 0.02)

    st.sidebar.subheader("Bacterial Growth")
    growth_rate = st.sidebar.slider("Growth Rate", 0.05, 0.3, 0.15, 0.02)
    bacteria_motility = st.sidebar.slider("Bacterial Motility", 0.001, 0.05, 0.01, 0.002)

    st.sidebar.subheader("Branching Instability")
    noise_amplitude = st.sidebar.slider("Noise Amplitude", 0.0, 0.1, 0.02, 0.005)

    st.sidebar.subheader("Animation")
    steps_per_frame = st.sidebar.slider("Steps per Frame", 1, 20, 5)
    frame_delay = st.sidebar.slider("Frame Delay (ms)", 10, 200, 50, 10)

    # Presets
    st.sidebar.subheader("Presets")
    preset = st.sidebar.selectbox("Load Preset", [
        "Custom",
        "Dense Branching",
        "Fine Dendrites",
        "Compact Colony",
        "Sparse Network"
    ])

    if preset == "Dense Branching":
        diffusion_rate, consumption_rate = 0.15, 0.06
        growth_rate, bacteria_motility = 0.12, 0.015
        noise_amplitude = 0.025
    elif preset == "Fine Dendrites":
        diffusion_rate, consumption_rate = 0.25, 0.1
        growth_rate, bacteria_motility = 0.18, 0.008
        noise_amplitude = 0.03
    elif preset == "Compact Colony":
        diffusion_rate, consumption_rate = 0.1, 0.04
        growth_rate, bacteria_motility = 0.2, 0.025
        noise_amplitude = 0.01
    elif preset == "Sparse Network":
        diffusion_rate, consumption_rate = 0.3, 0.12
        growth_rate, bacteria_motility = 0.1, 0.005
        noise_amplitude = 0.04

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
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False

    if start_btn:
        st.session_state.running = True
    if stop_btn:
        st.session_state.running = False
    if reset_btn:
        st.session_state.initialized = False
        st.session_state.running = False

    # Initialize simulation
    if not st.session_state.initialized or reset_btn:
        st.session_state.bacteria, st.session_state.nutrients = init_simulation(grid_size)
        st.session_state.step_count = 0
        st.session_state.grid_size = grid_size
        st.session_state.initialized = True

    # Check if grid size changed
    if st.session_state.grid_size != grid_size:
        st.session_state.bacteria, st.session_state.nutrients = init_simulation(grid_size)
        st.session_state.step_count = 0
        st.session_state.grid_size = grid_size

    # Display area - two columns for bacteria and nutrients
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Bacterial Density")
        bacteria_placeholder = st.empty()

    with col_right:
        st.subheader("Nutrient Concentration")
        nutrient_placeholder = st.empty()

    status_placeholder = st.empty()

    # Stats display
    stats_col1, stats_col2, stats_col3 = st.columns(3)

    # Animation loop
    if st.session_state.running:
        while st.session_state.running:
            # Simulation steps
            for _ in range(steps_per_frame):
                st.session_state.bacteria, st.session_state.nutrients = simulation_step(
                    st.session_state.bacteria,
                    st.session_state.nutrients,
                    diffusion_rate, consumption_rate,
                    growth_rate, bacteria_motility,
                    noise_amplitude
                )
                st.session_state.step_count += 1

            # Update bacteria plot
            fig1, ax1 = plt.subplots(figsize=(6, 6))
            fig1.patch.set_facecolor('#0a0a0a')
            ax1.set_facecolor('#0a0a0a')
            ax1.imshow(st.session_state.bacteria, cmap=bacteria_cmap,
                      interpolation='bilinear', vmin=0, vmax=1)
            ax1.axis('off')
            ax1.set_title(f'Step: {st.session_state.step_count}', color='white')
            bacteria_placeholder.pyplot(fig1)
            plt.close(fig1)

            # Update nutrient plot
            fig2, ax2 = plt.subplots(figsize=(6, 6))
            fig2.patch.set_facecolor('#0a0a0a')
            ax2.set_facecolor('#0a0a0a')
            ax2.imshow(st.session_state.nutrients, cmap=nutrient_cmap,
                      interpolation='bilinear', vmin=0, vmax=1)
            ax2.axis('off')
            nutrient_placeholder.pyplot(fig2)
            plt.close(fig2)

            # Update stats
            total_bacteria = st.session_state.bacteria.sum()
            total_nutrients = st.session_state.nutrients.sum()
            colony_radius = np.sqrt(np.sum(st.session_state.bacteria > 0.1) / np.pi)

            with stats_col1:
                st.metric("Total Bacterial Mass", f"{total_bacteria:.1f}")
            with stats_col2:
                st.metric("Remaining Nutrients", f"{total_nutrients:.1f}")
            with stats_col3:
                st.metric("Colony Radius (approx)", f"{colony_radius:.1f}")

            status_placeholder.text(f"Running... Step {st.session_state.step_count}")

            time.sleep(frame_delay / 1000.0)
    else:
        # Show current state
        fig1, ax1 = plt.subplots(figsize=(6, 6))
        fig1.patch.set_facecolor('#0a0a0a')
        ax1.set_facecolor('#0a0a0a')
        ax1.imshow(st.session_state.bacteria, cmap=bacteria_cmap,
                  interpolation='bilinear', vmin=0, vmax=1)
        ax1.axis('off')
        ax1.set_title(f'Step: {st.session_state.step_count}', color='white')
        bacteria_placeholder.pyplot(fig1)
        plt.close(fig1)

        fig2, ax2 = plt.subplots(figsize=(6, 6))
        fig2.patch.set_facecolor('#0a0a0a')
        ax2.set_facecolor('#0a0a0a')
        ax2.imshow(st.session_state.nutrients, cmap=nutrient_cmap,
                  interpolation='bilinear', vmin=0, vmax=1)
        ax2.axis('off')
        nutrient_placeholder.pyplot(fig2)
        plt.close(fig2)

        # Stats
        total_bacteria = st.session_state.bacteria.sum()
        total_nutrients = st.session_state.nutrients.sum()
        colony_radius = np.sqrt(np.sum(st.session_state.bacteria > 0.1) / np.pi)

        with stats_col1:
            st.metric("Total Bacterial Mass", f"{total_bacteria:.1f}")
        with stats_col2:
            st.metric("Remaining Nutrients", f"{total_nutrients:.1f}")
        with stats_col3:
            st.metric("Colony Radius (approx)", f"{colony_radius:.1f}")

        status_placeholder.text(f"Paused at step {st.session_state.step_count}. Click Start to continue.")

    # Instructions
    st.markdown("---")
    st.markdown("""
    ### The Model

    This simulation models bacterial colony growth using reaction-diffusion equations:

    **Nutrients**: Diffuse through the medium and are consumed by bacteria
    ```
    ∂N/∂t = D∇²N - cBN
    ```

    **Bacteria**: Grow proportionally to nutrient availability (logistic growth)
    ```
    ∂B/∂t = rBN(1-B) + μ∇²B + noise
    ```

    ### Morphology Regimes

    | Pattern | Conditions |
    |---------|------------|
    | **Dense Branching** | Medium diffusion, moderate growth |
    | **Fine Dendrites** | High diffusion, high consumption |
    | **Compact Colony** | Low diffusion, high motility |
    | **DLA-like** | Very high diffusion, low motility |

    ### References
    - Kawasaki, K. et al. (1997). J. Theor. Biol. 188, 177-185
    - Ben-Jacob, E. et al. (1994). Nature 368, 46-49
    """)


if __name__ == "__main__":
    main()
