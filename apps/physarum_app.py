"""
Physarum polycephalum Slime Mold Simulation
Interactive Streamlit app with real-time animation

Run with: streamlit run physarum_app.py
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.ndimage import uniform_filter
import time

# Page config
st.set_page_config(
    page_title="Physarum Simulation",
    page_icon="🟡",
    layout="wide"
)

# Custom colormap
physarum_cmap = LinearSegmentedColormap.from_list('physarum',
    ['#0a0a0a', '#1a1a0a', '#3d3d00', '#7a7a00', '#c7c700', '#ffff00', '#ffff80'])


def init_agents(num_agents, grid_size, spawn_mode='center'):
    """Initialize agent positions and headings."""
    center = grid_size // 2

    if spawn_mode == 'center':
        # Spawn in disk at center
        spawn_radius = grid_size * 0.1
        r = np.random.uniform(0, spawn_radius, num_agents)
        theta = np.random.uniform(0, 2 * np.pi, num_agents)
        agent_x = (center + r * np.cos(theta)).astype(np.float32)
        agent_y = (center + r * np.sin(theta)).astype(np.float32)
    elif spawn_mode == 'ring':
        # Spawn in ring
        r = grid_size * 0.3
        theta = np.random.uniform(0, 2 * np.pi, num_agents)
        agent_x = (center + r * np.cos(theta)).astype(np.float32)
        agent_y = (center + r * np.sin(theta)).astype(np.float32)
    else:  # scattered
        agent_x = np.random.uniform(20, grid_size - 20, num_agents).astype(np.float32)
        agent_y = np.random.uniform(20, grid_size - 20, num_agents).astype(np.float32)

    agent_heading = np.random.uniform(0, 2 * np.pi, num_agents).astype(np.float32)

    return agent_x, agent_y, agent_heading


def physarum_step(agent_x, agent_y, agent_heading, trail_map,
                   sensor_angle, rotation_angle, sensor_distance,
                   deposit_amount, decay_rate, grid_size):
    """Perform one simulation step."""
    num_agents = len(agent_x)
    sa = np.radians(sensor_angle)
    ra = np.radians(rotation_angle)
    sd = sensor_distance

    # Sense
    f_x = ((agent_x + sd * np.cos(agent_heading)) % grid_size).astype(np.int32)
    f_y = ((agent_y + sd * np.sin(agent_heading)) % grid_size).astype(np.int32)
    fl_x = ((agent_x + sd * np.cos(agent_heading + sa)) % grid_size).astype(np.int32)
    fl_y = ((agent_y + sd * np.sin(agent_heading + sa)) % grid_size).astype(np.int32)
    fr_x = ((agent_x + sd * np.cos(agent_heading - sa)) % grid_size).astype(np.int32)
    fr_y = ((agent_y + sd * np.sin(agent_heading - sa)) % grid_size).astype(np.int32)

    f_val = trail_map[f_y, f_x]
    fl_val = trail_map[fl_y, fl_x]
    fr_val = trail_map[fr_y, fr_x]

    # Rotate
    front_best = (f_val > fl_val) & (f_val > fr_val)
    front_worst = (f_val < fl_val) & (f_val < fr_val)
    left_better = (fl_val > fr_val) & ~front_best & ~front_worst
    right_better = (fr_val > fl_val) & ~front_best & ~front_worst
    random_turn = np.random.random(num_agents) < 0.5

    agent_heading = np.where(front_worst & random_turn, agent_heading + ra, agent_heading)
    agent_heading = np.where(front_worst & ~random_turn, agent_heading - ra, agent_heading)
    agent_heading = np.where(left_better, agent_heading + ra, agent_heading)
    agent_heading = np.where(right_better, agent_heading - ra, agent_heading)
    agent_heading = agent_heading % (2 * np.pi)

    # Move
    agent_x = (agent_x + np.cos(agent_heading)) % grid_size
    agent_y = (agent_y + np.sin(agent_heading)) % grid_size

    # Deposit
    ix = agent_x.astype(np.int32)
    iy = agent_y.astype(np.int32)
    np.add.at(trail_map, (iy, ix), deposit_amount)

    # Diffuse and decay
    trail_map[:] = uniform_filter(trail_map, size=3)
    trail_map *= (1 - decay_rate)
    trail_map[:] = np.clip(trail_map, 0, 255)

    return agent_x, agent_y, agent_heading


def add_food_sources(trail_map, food_positions, food_strength, food_radius):
    """Add chemoattractant from food sources."""
    grid_size = trail_map.shape[0]
    for fx, fy in food_positions:
        y, x = np.ogrid[-fy:grid_size-fy, -fx:grid_size-fx]
        mask = x*x + y*y <= food_radius*food_radius
        trail_map[mask] += food_strength


def main():
    st.title("🟡 Physarum polycephalum Simulation")
    st.markdown("""
    Interactive slime mold network formation based on the Jones (2010) multi-agent model.
    Agents sense chemoattractant, turn toward higher concentrations, and deposit trails.
    """)

    # Sidebar controls
    st.sidebar.header("Simulation Parameters")

    num_agents = st.sidebar.slider("Number of Agents", 1000, 50000, 10000, 1000)
    grid_size = st.sidebar.slider("Grid Size", 100, 500, 300, 50)

    st.sidebar.subheader("Agent Behavior")
    sensor_angle = st.sidebar.slider("Sensor Angle (degrees)", 10.0, 90.0, 22.5, 2.5)
    rotation_angle = st.sidebar.slider("Rotation Angle (degrees)", 10.0, 90.0, 45.0, 5.0)
    sensor_distance = st.sidebar.slider("Sensor Distance", 3, 20, 9, 1)

    st.sidebar.subheader("Trail Properties")
    deposit_amount = st.sidebar.slider("Deposit Amount", 1.0, 20.0, 5.0, 1.0)
    decay_rate = st.sidebar.slider("Decay Rate", 0.01, 0.2, 0.05, 0.01)

    st.sidebar.subheader("Spawn Mode")
    spawn_mode = st.sidebar.selectbox("Initial Distribution",
                                       ["center", "ring", "scattered"])

    st.sidebar.subheader("Food Sources")
    enable_food = st.sidebar.checkbox("Enable Food Sources", False)
    if enable_food:
        num_food = st.sidebar.slider("Number of Food Sources", 2, 8, 5)
        food_strength = st.sidebar.slider("Food Strength", 5.0, 50.0, 20.0, 5.0)

    # Animation controls
    st.sidebar.subheader("Animation")
    steps_per_frame = st.sidebar.slider("Steps per Frame", 1, 10, 3)
    frame_delay = st.sidebar.slider("Frame Delay (ms)", 10, 200, 50, 10)

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
        st.session_state.trail_map = np.zeros((grid_size, grid_size), dtype=np.float32)
        st.session_state.agent_x, st.session_state.agent_y, st.session_state.agent_heading = \
            init_agents(num_agents, grid_size, spawn_mode)
        st.session_state.step_count = 0
        st.session_state.initialized = True

        # Generate food positions
        if enable_food:
            center = grid_size // 2
            r = grid_size * 0.35
            st.session_state.food_positions = []
            for i in range(num_food):
                angle = i * 2 * np.pi / num_food - np.pi/2
                fx = int(center + r * np.cos(angle))
                fy = int(center + r * np.sin(angle))
                st.session_state.food_positions.append((fx, fy))
        else:
            st.session_state.food_positions = []

    # Display area
    plot_placeholder = st.empty()
    status_placeholder = st.empty()

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#0a0a0a')

    # Animation loop
    if st.session_state.running:
        while st.session_state.running:
            # Add food attractant
            if enable_food and st.session_state.food_positions:
                add_food_sources(st.session_state.trail_map,
                                st.session_state.food_positions,
                                food_strength, 10)

            # Simulation steps
            for _ in range(steps_per_frame):
                st.session_state.agent_x, st.session_state.agent_y, st.session_state.agent_heading = \
                    physarum_step(
                        st.session_state.agent_x,
                        st.session_state.agent_y,
                        st.session_state.agent_heading,
                        st.session_state.trail_map,
                        sensor_angle, rotation_angle, sensor_distance,
                        deposit_amount, decay_rate, grid_size
                    )
                st.session_state.step_count += 1

            # Update plot
            ax.clear()
            ax.imshow(st.session_state.trail_map, cmap=physarum_cmap,
                     interpolation='bilinear', origin='lower')

            # Draw food sources
            if enable_food and st.session_state.food_positions:
                for fx, fy in st.session_state.food_positions:
                    circle = plt.Circle((fx, fy), 8, color='red', fill=False, linewidth=2)
                    ax.add_patch(circle)

            ax.set_xlim(0, grid_size)
            ax.set_ylim(0, grid_size)
            ax.axis('off')
            ax.set_title(f'Step: {st.session_state.step_count}', color='white', fontsize=12)

            plot_placeholder.pyplot(fig)
            status_placeholder.text(f"Running... Step {st.session_state.step_count}")

            plt.clf()
            time.sleep(frame_delay / 1000.0)

            # Check for stop (rerun will reset running state if stop was clicked)
            # This is a workaround for Streamlit's execution model
    else:
        # Show current state
        ax.clear()
        ax.imshow(st.session_state.trail_map, cmap=physarum_cmap,
                 interpolation='bilinear', origin='lower')

        if enable_food and st.session_state.food_positions:
            for fx, fy in st.session_state.food_positions:
                circle = plt.Circle((fx, fy), 8, color='red', fill=False, linewidth=2)
                ax.add_patch(circle)

        ax.set_xlim(0, grid_size)
        ax.set_ylim(0, grid_size)
        ax.axis('off')
        ax.set_title(f'Step: {st.session_state.step_count}', color='white', fontsize=12)

        plot_placeholder.pyplot(fig)
        status_placeholder.text(f"Paused at step {st.session_state.step_count}. Click Start to continue.")

    plt.close(fig)

    # Instructions
    st.markdown("---")
    st.markdown("""
    ### How It Works

    Each agent follows simple rules:
    1. **Sense**: Sample chemoattractant at front, front-left, and front-right
    2. **Rotate**: Turn toward the direction with highest concentration
    3. **Move**: Step forward in the current heading direction
    4. **Deposit**: Leave chemoattractant at current position

    The trail map diffuses and decays over time, creating emergent network structures.

    ### Tips
    - Lower decay rate = more persistent trails
    - Higher sensor angle = wider field of view
    - Enable food sources to see network optimization
    """)


if __name__ == "__main__":
    main()
