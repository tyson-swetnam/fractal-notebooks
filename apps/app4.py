# app.py

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

def simulate_tree_growth(
    num_years,
    initial_rays,
    max_angular_spacing,
    initial_radius,
    radial_growth_per_year,
    early_late_ratio,
    early_cell_radial_size,
    late_cell_radial_size
):
    """
    Simulate the growth of tree cambium over a number of years with rays of cells.

    Parameters:
        num_years (int): Number of years to simulate.
        initial_rays (int): Initial number of rays (vertical cell alignments).
        max_angular_spacing (float): Maximum allowable angular spacing between rays (in radians).
        initial_radius (float): Initial radius of the pith (in micrometers).
        radial_growth_per_year (float): Radial growth per year (in micrometers).
        early_late_ratio (float): Proportion of early wood in each ring (0 to 1).
        early_cell_radial_size (float): Radial size of early wood cells (micrometers).
        late_cell_radial_size (float): Radial size of late wood cells (micrometers).

    Returns:
        cells (list): List of dictionaries containing cell information.
    """
    cells = []
    center = np.array([0, 0])  # Center of the tree (pith)
    current_radius = initial_radius
    current_rays = initial_rays

    for year in range(1, num_years + 1):
        # Calculate the inner and outer radii of this year's ring
        inner_radius = current_radius
        outer_radius = inner_radius + radial_growth_per_year

        # Determine the circumference at the outer radius
        circumference = 2 * np.pi * outer_radius

        # Calculate angular spacing between rays
        angular_spacing = 2 * np.pi / current_rays

        # If angular spacing exceeds max, split rays
        while angular_spacing > max_angular_spacing:
            current_rays *= 2  # Double the number of rays
            angular_spacing = 2 * np.pi / current_rays

        # Generate angles for rays
        ray_angles = np.linspace(0, 2 * np.pi, current_rays, endpoint=False)

        # For each ray, generate cells along the radial direction
        for angle in ray_angles:
            # Determine the radial positions of early wood cells
            early_wood_thickness = radial_growth_per_year * early_late_ratio
            late_wood_thickness = radial_growth_per_year * (1 - early_late_ratio)

            # Number of early wood cells in this ray
            num_early_cells = max(1, int(early_wood_thickness / early_cell_radial_size))
            # Number of late wood cells in this ray
            num_late_cells = max(1, int(late_wood_thickness / late_cell_radial_size))

            # Radial positions for early wood cells
            early_cell_edges = np.linspace(
                inner_radius,
                inner_radius + early_wood_thickness,
                num_early_cells + 1
            )

            # Radial positions for late wood cells
            late_cell_edges = np.linspace(
                inner_radius + early_wood_thickness,
                outer_radius,
                num_late_cells + 1
            )

            # Create early wood cells
            for i in range(num_early_cells):
                cell_inner_radius = early_cell_edges[i]
                cell_outer_radius = early_cell_edges[i + 1]
                cell = {
                    'Year': year,
                    'cell_type': 'Early Wood',
                    'inner_radius': cell_inner_radius,
                    'outer_radius': cell_outer_radius,
                    'start_angle': angle,
                    'end_angle': angle + angular_spacing,
                }
                cells.append(cell)

            # Create late wood cells
            for i in range(num_late_cells):
                cell_inner_radius = late_cell_edges[i]
                cell_outer_radius = late_cell_edges[i + 1]
                cell = {
                    'Year': year,
                    'cell_type': 'Late Wood',
                    'inner_radius': cell_inner_radius,
                    'outer_radius': cell_outer_radius,
                    'start_angle': angle,
                    'end_angle': angle + angular_spacing,
                }
                cells.append(cell)

        # Update the current radius for the next year
        current_radius = outer_radius

    return cells

def create_cell_polygons(cells):
    """
    Create polygon coordinates for each cell.

    Parameters:
        cells (list): List of cell dictionaries.

    Returns:
        cells (list): Updated list of cell dictionaries with polygon coordinates.
    """
    for cell in cells:
        # Create the polygon for the cell as a wedge between two radii and two angles
        inner_radius = cell['inner_radius']
        outer_radius = cell['outer_radius']
        start_angle = cell['start_angle']
        end_angle = cell['end_angle']

        # Ensure the angles are within 0 to 2*pi
        start_angle = start_angle % (2 * np.pi)
        end_angle = end_angle % (2 * np.pi)

        # Create points for the polygon
        angles = np.array([start_angle, end_angle, end_angle, start_angle, start_angle])
        radii = np.array([inner_radius, inner_radius, outer_radius, outer_radius, inner_radius])

        x_coords = radii * np.cos(angles)
        y_coords = radii * np.sin(angles)

        cell['polygon_x'] = x_coords
        cell['polygon_y'] = y_coords

    return cells

def main():
    # Set the title of the Streamlit app
    st.title("Tree Cambium Growth Simulation with Rays and Cell Rows")

    # Sidebar for parameters
    st.sidebar.header("Simulation Parameters")

    num_years = st.sidebar.number_input("Number of Years", min_value=1, max_value=50, value=5, step=1)
    initial_radius = st.sidebar.number_input("Initial Pith Radius (micrometers)", min_value=1.0, max_value=100.0, value=10.0, step=1.0)
    radial_growth_per_year = st.sidebar.number_input("Radial Growth per Year (micrometers)", min_value=1.0, max_value=100.0, value=20.0, step=1.0)
    initial_rays = st.sidebar.number_input("Initial Number of Rays", min_value=4, max_value=64, value=8, step=1)
    max_angular_spacing = st.sidebar.number_input("Max Angular Spacing Between Rays (degrees)", min_value=5.0, max_value=90.0, value=30.0, step=5.0)
    early_late_ratio = st.sidebar.slider("Proportion of Early Wood", min_value=0.1, max_value=0.9, value=0.6, step=0.1)
    early_cell_radial_size = st.sidebar.number_input("Early Wood Cell Radial Size (micrometers)", min_value=1.0, max_value=50.0, value=10.0, step=0.5)
    late_cell_radial_size = st.sidebar.number_input("Late Wood Cell Radial Size (micrometers)", min_value=1.0, max_value=50.0, value=5.0, step=0.5)

    # Convert max angular spacing to radians
    max_angular_spacing_rad = np.deg2rad(max_angular_spacing)

    # Simulate tree growth
    cells = simulate_tree_growth(
        num_years,
        initial_rays,
        max_angular_spacing_rad,
        initial_radius,
        radial_growth_per_year,
        early_late_ratio,
        early_cell_radial_size,
        late_cell_radial_size
    )

    # Create cell polygons
    cells = create_cell_polygons(cells)

    # Convert cells to DataFrame for easier handling
    df_cells = pd.DataFrame(cells)

    # Display the data
    st.subheader("Cell Data (First 5 Rows)")
    st.write(df_cells.head())

    # Create Plotly figure
    fig = go.Figure()

    # Define colors for early wood and late wood
    color_mapping = {'Early Wood': 'sandybrown', 'Late Wood': 'saddlebrown'}

    # Plot cells
    for _, cell in df_cells.iterrows():
        fig.add_trace(go.Scatter(
            x=cell['polygon_x'],
            y=cell['polygon_y'],
            mode='lines',
            fill='toself',
            fillcolor=color_mapping[cell['cell_type']],
            line=dict(color='black', width=0.5),
            name=f"Year {cell['Year']} - {cell['cell_type']}",
            hoverinfo='skip'
        ))

    # Customize layout
    fig.update_layout(
        title="Tree Cambium Growth Simulation with Rays and Cell Rows",
        xaxis_title="X Position (micrometers)",
        yaxis_title="Y Position (micrometers)",
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        height=800,
        width=800,
        showlegend=False,
        hovermode="closest",
        xaxis_scaleanchor="y",
        xaxis_scaleratio=1,
    )

    # Show the Plotly figure in Streamlit
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
