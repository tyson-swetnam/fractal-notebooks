# app.py

import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Function to create a regular hexagon
def create_hexagon(center_x, center_y, size):
    angles = np.linspace(0, 2 * np.pi, 7)  # 6 sides + closing point
    x = center_x + size * np.cos(angles)
    y = center_y + size * np.sin(angles)
    return list(zip(x, y))

# Set the title of the Streamlit app
st.title("Tree Growth Rings Simulation - Linear Core Visualization")

# Sidebar for parameters
st.sidebar.header("Simulation Parameters")

# Parameters
num_years = st.sidebar.slider("Number of Years (Rings)", min_value=1, max_value=50, value=10)
growth_rate = st.sidebar.number_input("Logarithmic Growth Rate", min_value=0.1, max_value=3.0, value=1.0, step=0.1)
cells_per_ring = st.sidebar.slider("Cells per Ring (Vertical)", min_value=3, max_value=20, value=5)
cell_wall_thickness = st.sidebar.slider("Cell Wall Thickness", min_value=0.1, max_value=2.0, value=0.5, step=0.1)
hex_size = st.sidebar.slider("Hexagon Size", min_value=0.1, max_value=2.0, value=0.5, step=0.1)

# Initial position
initial_x = 0

# Calculate cumulative x positions for each ring using logarithmic growth
radii = [initial_x]
for i in range(1, num_years + 1):
    x_increment = growth_rate * np.log(1 + i)
    new_x = radii[-1] + x_increment
    radii.append(new_x)

# Define colors
early_wood_color = 'peru'         # Early wood
late_wood_color = 'saddlebrown'   # Late wood
cell_wall_color = 'black'

# Create Plotly figure
fig = go.Figure()

# Calculate vertical and horizontal spacing based on hexagon size
vertical_spacing = hex_size * np.sqrt(3)  # Height of a hexagon is size * sqrt(3)
horizontal_spacing = hex_size * 1.5       # Horizontal distance between centers

# Iterate over each year to create cells
for year in range(1, num_years + 1):
    x_start = radii[year - 1]
    x_end = radii[year]
    ring_width = x_end - x_start

    # Number of columns in each ring based on ring width
    num_columns = int(np.ceil(ring_width / horizontal_spacing)) + 1

    # Loop over rows and columns to create hexagons
    for row in range(cells_per_ring):
        for col in range(num_columns):
            # Calculate center positions
            center_x = x_start + col * horizontal_spacing
            center_y = row * vertical_spacing

            # Stagger every other row
            if row % 2 == 1:
                center_x += horizontal_spacing / 2

            # Check if hexagon center is within the ring boundaries
            if center_x - hex_size > x_end or center_x + hex_size < x_start:
                continue

            # Alternate between early wood and late wood
            if (year + row + col) % 2 == 0:
                cell_type = "Early Wood"
                fill_color = early_wood_color
                current_hex_size = hex_size
            else:
                cell_type = "Late Wood"
                fill_color = late_wood_color
                current_hex_size = hex_size * 0.8  # Smaller size for late wood

            # Create hexagon coordinates
            hex_coords = create_hexagon(center_x, center_y, current_hex_size)

            # Add hexagon to the figure
            fig.add_trace(go.Scatter(
                x=[point[0] for point in hex_coords],
                y=[point[1] for point in hex_coords],
                mode='lines',
                fill='toself',
                fillcolor=fill_color,
                line=dict(color=cell_wall_color, width=cell_wall_thickness),
                showlegend=False
            ))

# Customize layout
fig.update_layout(
    title="Linear Horizontal Core Visualization",
    xaxis=dict(
        title="Radial Axis (cm)",
        showgrid=False,
        zeroline=False,
        showticklabels=True,
        range=[0, radii[-1] + hex_size]  # Extend x-axis to show the last cells
    ),
    yaxis=dict(
        title="Transverse Axis",
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        scaleanchor="x",
        scaleratio=1
    ),
    width=1000,
    height=600,
    plot_bgcolor='lightyellow',
    margin=dict(l=50, r=50, t=50, b=50)
)

# Add legend manually
fig.add_trace(go.Scatter(
    x=[None],
    y=[None],
    mode='markers',
    marker=dict(size=10, color=early_wood_color),
    name='Early Wood'
))
fig.add_trace(go.Scatter(
    x=[None],
    y=[None],
    mode='markers',
    marker=dict(size=10, color=late_wood_color),
    name='Late Wood'
))

fig.update_layout(showlegend=True)

# Display the figure in Streamlit
st.plotly_chart(fig, use_container_width=True)

# Add explanation
st.markdown("""
### Explanation

Wood is a complex, porous structure composed of numerous cells that grow concentrically as a tree matures. This visualization represents the linear core of a tree, illustrating how growth rings form over the years. Each growth ring is composed of individual polygonal cells, resembling soap bubbles or corn kernels, divided into early wood and late wood.

- **Number of Years (Rings)**: Adjusts how many annual growth rings are displayed.
- **Logarithmic Growth Rate**: Controls the spacing between the rings based on a logarithmic scale, simulating the natural growth pattern of trees where growth rate decreases over time.
- **Cells per Ring**: Determines how many rows of cells are in each ring, representing the complexity of cellular structure.
- **Cell Wall Thickness**: Adjusts the thickness of the lines delineating each cell, simulating the physical cell walls in wood.
- **Hexagon Size**: Controls the size of each polygonal cell, affecting the overall density and appearance of the growth rings.

**Early Wood vs. Late Wood**

- **Early Wood**: Represented in lighter brown (`peru`), these larger cells form during the early growing season when conditions are favorable for rapid growth.
- **Late Wood**: Represented in darker brown (`saddlebrown`), these smaller cells form later in the growing season, providing structural strength and density to the wood.

**Axes Description**

- **Radial Axis (Horizontal)**: Represents the distance from the center (pith) of the tree outward.
- **Transverse Axis (Vertical)**: Represents the orientation perpendicular to the radial axis, providing a view into the cellular structure.

This simulation provides an interactive way to explore the cellular anatomy of wood and understand how different factors influence the growth and structure of trees.

### How to Use the App

- Adjust the parameters in the sidebar to change the visualization.
  - **Number of Years (Rings)**: Increase or decrease the number to see more or fewer growth rings.
  - **Logarithmic Growth Rate**: Modify to see how growth rate affects ring spacing.
  - **Cells per Ring**: Change the number of cell rows to see denser or sparser cellular structures.
  - **Cell Wall Thickness**: Adjust to make cell walls thicker or thinner.
  - **Hexagon Size**: Modify the size of the cells.

### Wood Anatomy Reference

This simulation is informed by the following wood anatomy concepts:

- **Cellular Structure**: Wood consists of interconnecting cells made of cellulose, hemicelluloses, and lignin. Each cell has an outer wall and an inner cavity.
- **Growth Rings**: Annual growth rings form as new cells are added concentrically around the tree's pith. Each ring typically consists of early wood and late wood.
- **Early Wood and Late Wood**: Early wood has larger cells with thinner walls, while late wood has smaller cells with thicker walls, contributing to the wood's strength and density.
- **Radial and Transverse Axes**: These principal planes help in understanding the orientation and structural properties of wood.
""")
