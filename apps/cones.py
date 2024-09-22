# tree_growth_app.py

import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(page_title="Tree Growth Simulator", layout="wide")

# Function to generate a cone mesh
def cone_mesh(p0, direction, height, radius_base, sections=8):
    """
    Generate mesh data for a cone starting at point p0, pointing in 'direction'.
    """
    # Normalize direction vector
    direction = direction / np.linalg.norm(direction)
    # Calculate the top point of the cone
    p1 = p0 + direction * height

    # Create circle at base
    not_v = np.array([1, 0, 0])
    if np.allclose(direction, not_v):
        not_v = np.array([0, 1, 0])
    n1 = np.cross(direction, not_v)
    n1 /= np.linalg.norm(n1)
    n2 = np.cross(direction, n1)

    # Angles for circle points
    t = np.linspace(0, 2 * np.pi, sections, endpoint=False)
    circle_base = n1[:, None] * np.cos(t) + n2[:, None] * np.sin(t)
    circle_base *= radius_base
    base_points = p0[:, None] + circle_base

    # Combine points
    x = np.hstack((base_points[0], [p1[0]]))
    y = np.hstack((base_points[1], [p1[1]]))
    z = np.hstack((base_points[2], [p1[2]]))

    # Create faces
    faces = []
    n = sections
    apex_index = n
    for i in range(n):
        next_i = (i + 1) % n
        faces.append([i, next_i, apex_index])
    return x, y, z, faces

# Function to generate a cylinder mesh
def cylinder_mesh(p0, p1, radius, sections=8):
    """
    Generate mesh data for a cylinder between two points.
    """
    # Vector from p0 to p1
    v = p1 - p0
    # Length of the cylinder
    length = np.linalg.norm(v)
    if length == 0:
        return None
    # Unit vector in the direction of the cylinder
    v = v / length

    # Create arbitrary vectors orthogonal to v
    not_v = np.array([1, 0, 0])
    if np.allclose(v, not_v):
        not_v = np.array([0, 1, 0])
    n1 = np.cross(v, not_v)
    n1 /= np.linalg.norm(n1)
    n2 = np.cross(v, n1)

    # Create circle points
    t = np.linspace(0, 2 * np.pi, sections, endpoint=False)
    circle = n1[:, None] * np.cos(t) + n2[:, None] * np.sin(t)
    circle *= radius

    # Points at base and top
    base_points = p0[:, None] + circle
    top_points = p1[:, None] + circle

    # Combine points
    x = np.hstack((base_points[0], top_points[0]))
    y = np.hstack((base_points[1], top_points[1]))
    z = np.hstack((base_points[2], top_points[2]))

    # Create faces
    faces = []
    n = sections
    for i in range(n):
        next_i = (i + 1) % n
        faces.append([i, next_i, n + next_i])
        faces.append([i, n + next_i, n + i])
    return x, y, z, faces

# Function to grow the tree over years
def grow_tree(years, current_year, initial_height, height_increment, radius_base, radius_decrement,
              branching_years, branches_per_split, branch_angle_deg):
    """
    Simulate tree growth over the specified number of years.
    """
    tree_elements = []
    p0 = np.array([0, 0, 0])
    direction = np.array([0, 0, 1])  # Initial upward direction
    segments = []

    # Initialize the first segment
    segments.append({
        'p0': p0,
        'direction': direction,
        'height': initial_height,
        'radius': radius_base,
        'year_created': 1,
        'branch_order': 0
    })

    for year in range(1, current_year + 1):
        new_segments = []
        for seg in segments:
            # Only process segments created in this year
            if seg['year_created'] == year:
                p0 = seg['p0']
                direction = seg['direction']
                height = seg['height']
                radius = seg['radius']

                # Check if this segment should split
                if year in branching_years:
                    # Split into branches
                    for i in range(branches_per_split):
                        angle = np.deg2rad(branch_angle_deg)
                        phi = i * (2 * np.pi / branches_per_split)

                        # Calculate new direction
                        new_direction = rotate_vector(direction, angle, phi)
                        p1 = p0 + new_direction * height

                        # Add cylinder representing the branch
                        cylinder = cylinder_mesh(p0, p1, radius)
                        if cylinder:
                            x, y, z, faces = cylinder
                            tree_elements.append({
                                'x': x,
                                'y': y,
                                'z': z,
                                'faces': faces,
                                'color': 'saddlebrown'
                            })

                        # Add cone at the tip
                        cone = cone_mesh(p1, new_direction, height_increment, radius * radius_decrement)
                        if cone:
                            x, y, z, faces = cone
                            tree_elements.append({
                                'x': x,
                                'y': y,
                                'z': z,
                                'faces': faces,
                                'color': 'forestgreen'
                            })

                        # Add new segment for next year's growth
                        new_segments.append({
                            'p0': p1,
                            'direction': new_direction,
                            'height': height_increment,
                            'radius': radius * radius_decrement,
                            'year_created': year + 1,
                            'branch_order': seg['branch_order'] + 1
                        })
                else:
                    # Continue growing upward
                    p1 = p0 + direction * height

                    # Add cylinder representing the trunk
                    cylinder = cylinder_mesh(p0, p1, radius)
                    if cylinder:
                        x, y, z, faces = cylinder
                        tree_elements.append({
                            'x': x,
                            'y': y,
                            'z': z,
                            'faces': faces,
                            'color': 'saddlebrown'
                        })

                    # Add cone at the tip
                    cone = cone_mesh(p1, direction, height_increment, radius * radius_decrement)
                    if cone:
                        x, y, z, faces = cone
                        tree_elements.append({
                            'x': x,
                            'y': y,
                            'z': z,
                            'faces': faces,
                            'color': 'forestgreen'
                        })

                    # Add new segment for next year's growth
                    new_segments.append({
                        'p0': p1,
                        'direction': direction,
                        'height': height_increment,
                        'radius': radius * radius_decrement,
                        'year_created': year + 1,
                        'branch_order': seg['branch_order']
                    })
        segments.extend(new_segments)

    return tree_elements

# Function to rotate a vector by given angles
def rotate_vector(direction, angle, phi):
    """
    Rotate the direction vector by angle and phi.
    """
    # Start with the initial direction (upward)
    v = direction
    # Rotate by angle from the direction
    rotation_axis = np.cross(v, [0, 0, 1])
    if np.linalg.norm(rotation_axis) == 0:
        rotation_axis = np.array([1, 0, 0])
    else:
        rotation_axis /= np.linalg.norm(rotation_axis)

    # Apply the rotation
    v_rot = rotate_around_axis(v, rotation_axis, angle)

    # Rotate around the original direction by phi
    v_final = rotate_around_axis(v_rot, v, phi)
    return v_final

# Function to rotate a vector around an axis
def rotate_around_axis(v, axis, angle):
    """
    Rotate vector v around axis by angle using Rodrigues' rotation formula.
    """
    axis = axis / np.linalg.norm(axis)
    v_rot = v * np.cos(angle) + np.cross(axis, v) * np.sin(angle) + axis * np.dot(axis, v) * (1 - np.cos(angle))
    return v_rot

# Main function to run the Streamlit app
def tree_growth_app():
    st.title("Tree Growth Simulator")

    # Sidebar controls
    st.sidebar.header("Growth Parameters")

    current_year = st.sidebar.slider("Select Year", min_value=1, max_value=10, value=1)
    initial_height = st.sidebar.slider("Initial Height", min_value=0.5, max_value=5.0, value=1.0, step=0.1)
    height_increment = st.sidebar.slider("Height Increment per Year", min_value=0.1, max_value=2.0, value=0.5, step=0.1)
    radius_base = st.sidebar.slider("Base Radius", min_value=0.1, max_value=1.0, value=0.3, step=0.05)
    radius_decrement = st.sidebar.slider("Radius Decrement Factor", min_value=0.5, max_value=1.0, value=0.8, step=0.05)
    branches_per_split = st.sidebar.slider("Branches per Split", min_value=2, max_value=6, value=3)
    branch_angle_deg = st.sidebar.slider("Branch Angle (°)", min_value=10, max_value=80, value=45, step=5)
    branching_years = st.sidebar.multiselect("Branching Years", options=list(range(1, 11)), default=[3, 5, 7])

    # Simulate tree growth
    tree_elements = grow_tree(
        years=10,
        current_year=current_year,
        initial_height=initial_height,
        height_increment=height_increment,
        radius_base=radius_base,
        radius_decrement=radius_decrement,
        branching_years=branching_years,
        branches_per_split=branches_per_split,
        branch_angle_deg=branch_angle_deg
    )

    # Plotting
    fig = go.Figure()
    for elem in tree_elements:
        fig.add_trace(go.Mesh3d(
            x=elem['x'],
            y=elem['y'],
            z=elem['z'],
            i=[face[0] for face in elem['faces']],
            j=[face[1] for face in elem['faces']],
            k=[face[2] for face in elem['faces']],
            color=elem['color'],
            opacity=1.0,
            flatshading=True,
            lighting=dict(ambient=0.5, diffuse=0.8),
            showscale=False
        ))
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode='data'
        ),
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0)
    )

    # Display the plot
    st.plotly_chart(fig, use_container_width=True)

    # Add a documentation expander
    with st.expander("How to Use"):
        st.markdown("""
        ## Tree Growth Simulator Instructions

        This application simulates the annual growth of a tree using fractal branching patterns.

        **Controls:**

        - **Select Year:** Choose the year of growth to display (1 to 10).
        - **Initial Height:** Set the starting height of the tree in the first year.
        - **Height Increment per Year:** Determine how much the tree grows each year.
        - **Base Radius:** Set the radius of the trunk in the first year.
        - **Radius Decrement Factor:** Controls how the radius decreases with each new growth.
        - **Branches per Split:** Set the number of branches when the tree splits.
        - **Branch Angle:** Determine the angle at which branches split from the main stem.
        - **Branching Years:** Select the years when the tree will split into new branches.

        **Visualization:**

        - The tree is visualized in 3D. You can rotate, zoom, and pan the view.
        - The tree starts as a cone and grows with additional cones and cylinders representing new growth and branches.

        **Notes:**

        - Only the growth up to the selected year is displayed.
        - The branches grow fractally, with new branches potentially splitting in subsequent years.
        - Experiment with different parameters to see how they affect the tree's growth pattern.

        **Examples to Try:**

        - **No Branching:** Deselect all branching years to see a straight, unbranched tree.
        - **Annual Branching:** Select all years as branching years to create a highly branched tree.
        - **Variable Branching:** Select specific years to control when the tree branches.

        Enjoy exploring the growth patterns of the tree!
        """)

# Run the app
if __name__ == "__main__":
    tree_growth_app()
