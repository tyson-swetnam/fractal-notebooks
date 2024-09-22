import streamlit as st
import numpy as np
import plotly.graph_objects as go

def cylinder_mesh(p0, p1, radius_base, radius_top, sections=8):
    """
    Generate mesh data for a tapered cylinder (frustum) between two points.
    """
    # Vector from p0 to p1
    v = np.array(p1) - np.array(p0)
    # Length of the cylinder
    length = np.linalg.norm(v)
    if length == 0:
        return None
    # Unit vector in direction of the cylinder
    v = v / length

    # Create arbitrary vectors orthogonal to v
    not_v = np.array([1, 0, 0])
    if np.allclose(v, not_v):
        not_v = np.array([0, 1, 0])
    n1 = np.cross(v, not_v)
    n1 /= np.linalg.norm(n1)
    n2 = np.cross(v, n1)

    # Create circle points in the plane orthogonal to v
    t = np.linspace(0, 2 * np.pi, sections, endpoint=False)
    circle_base = n1[:, None] * np.cos(t)[None, :] + n2[:, None] * np.sin(t)[None, :]
    circle_top = circle_base.copy()

    # Scale circles by radii
    circle_base *= radius_base
    circle_top *= radius_top

    # Points at base and top
    base_points = p0[:, None] + circle_base
    top_points = p1[:, None] + circle_top

    # Combine points
    x = np.hstack([base_points[0], top_points[0]])
    y = np.hstack([base_points[1], top_points[1]])
    z = np.hstack([base_points[2], top_points[2]])

    # Create faces
    faces = []
    n = sections
    for i in range(n):
        next_i = (i + 1) % n
        faces.append([i, next_i, n + next_i])
        faces.append([i, n + next_i, n + i])
    return x, y, z, faces

def rotate_vector(v, k, theta):
    """
    Rotate vector v around axis k by angle theta using Rodrigues' rotation formula.
    """
    v_rot = v * np.cos(theta) + np.cross(k, v) * np.sin(theta) + k * np.dot(k, v) * (1 - np.cos(theta))
    return v_rot

def grow_tree(p0, direction, length, radius_base, taper_ratio, levels, angle, length_reduction,
              branches_per_level, tree_elements, is_root=False):
    """
    Recursively grow the tree from point p0 in a given direction.
    """
    if levels == 0 or radius_base < 0.01 or length < 0.01:
        return

    # Calculate end point of the current branch
    p1 = p0 + direction * length

    # Ensure roots do not grow above ground level
    if is_root and p1[2] > 0:
        p1[2] = 0

    # Calculate top radius using consistent tapering
    radius_top = radius_base * taper_ratio

    # Add the cylinder representing the trunk or branch
    cylinder = cylinder_mesh(p0, p1, radius_base, radius_top)
    if cylinder:
        x, y, z, faces = cylinder
        tree_elements.append({
            'x': x,
            'y': y,
            'z': z,
            'faces': faces,
            'color': 'saddlebrown' if not is_root else 'sienna'
        })

    # Calculate base radius of child branches
    N = branches_per_level
    if N > 0:
        radius_base_child = radius_top / np.sqrt(N)
    else:
        radius_base_child = 0

    # Length of child branches
    length_child = length * length_reduction

    # Generate branches at this level
    for _ in range(N):
        # Random rotation for natural appearance
        if is_root:
            # For roots, theta ranges from π/2 to π (90° to 180°), pointing downward
            min_theta = np.pi / 2
            max_theta = np.pi / 2 + angle
            theta = min_theta + np.random.rand() * (max_theta - min_theta)
        else:
            # For crown, theta ranges from 0 to angle (pointing upward)
            min_theta = 0
            max_theta = angle
            theta = min_theta + np.random.rand() * (max_theta - min_theta)

        # Add small random variation
        theta += (np.random.rand() - 0.5) * np.deg2rad(10)
        phi = np.random.rand() * 2 * np.pi

        # Ensure theta is within valid range
        if is_root:
            theta = np.clip(theta, np.pi / 2, np.pi)
        else:
            theta = np.clip(theta, 0, np.pi / 2)

        # Spherical to Cartesian coordinates
        new_direction = np.array([
            np.sin(theta) * np.cos(phi),
            np.sin(theta) * np.sin(phi),
            np.cos(theta)
        ])

        # Rotate new_direction to align with the parent branch direction
        rotation_axis = np.cross([0, 0, 1], direction)
        rotation_angle = np.arccos(np.clip(np.dot(direction, [0, 0, 1]), -1.0, 1.0))
        if np.linalg.norm(rotation_axis) > 1e-6:
            rotation_axis /= np.linalg.norm(rotation_axis)
            new_direction = rotate_vector(new_direction, rotation_axis, rotation_angle)

        # Recursive call to grow the branch
        grow_tree(
            p1,
            new_direction,
            length_child,
            radius_base_child,
            taper_ratio,
            levels - 1,
            angle,
            length_reduction,
            branches_per_level,
            tree_elements,
            is_root=is_root
        )

def plot_tree():
    # Sidebar sliders for crown parameters
    st.sidebar.header("Crown Parameters")
    crown_levels = st.sidebar.slider('Crown Levels', min_value=1, max_value=8, value=5, step=1)
    crown_length = st.sidebar.slider('Crown Length', min_value=1.0, max_value=15.0, value=7.0, step=0.5)
    crown_radius = st.sidebar.slider('Crown Radius', min_value=0.1, max_value=1.5, value=0.5, step=0.1)
    crown_taper_ratio = st.sidebar.slider('Crown Taper', min_value=0.5, max_value=1.0, value=0.7, step=0.05)
    crown_angle_deg = st.sidebar.slider('Crown Angle', min_value=10, max_value=80, value=30, step=5)
    crown_length_reduction = st.sidebar.slider('Crown Length Red.', min_value=0.5, max_value=1.0, value=0.7, step=0.05)
    crown_branches_per_level = st.sidebar.slider('Crown Branches', min_value=0, max_value=8, value=3, step=1)

    # Sidebar sliders for root parameters
    st.sidebar.header("Root Parameters")
    root_levels = st.sidebar.slider('Root Levels', min_value=1, max_value=8, value=4, step=1)
    root_length = st.sidebar.slider('Root Length', min_value=1.0, max_value=15.0, value=5.0, step=0.5)
    root_radius = st.sidebar.slider('Root Radius', min_value=0.1, max_value=1.5, value=0.4, step=0.1)
    root_taper_ratio = st.sidebar.slider('Root Taper', min_value=0.5, max_value=1.0, value=0.7, step=0.05)
    root_angle_deg = st.sidebar.slider('Root Angle', min_value=-80, max_value=80, value=45, step=5)
    root_length_reduction = st.sidebar.slider('Root Length Red.', min_value=0.5, max_value=1.0, value=0.8, step=0.05)
    root_branches_per_level = st.sidebar.slider('Root Branches', min_value=0, max_value=8, value=2, step=1)

    # Convert angles from degrees to radians
    crown_angle_rad = np.deg2rad(crown_angle_deg)
    root_angle_rad = np.deg2rad(root_angle_deg)

    tree_elements = []
    # Start with the main trunk (above ground)
    p0 = np.array([0, 0, 0])
    direction = np.array([0, 0, 1])  # Grow upwards
    grow_tree(
        p0,
        direction,
        crown_length,
        crown_radius,
        crown_taper_ratio,
        crown_levels,
        crown_angle_rad,
        crown_length_reduction,
        crown_branches_per_level,
        tree_elements,
        is_root=False
    )

    # Now grow the roots (below ground)
    direction_root = np.array([0, 0, -1])  # Grow downwards
    grow_tree(
        p0,
        direction_root,
        root_length,
        root_radius,
        root_taper_ratio,
        root_levels,
        root_angle_rad,
        root_length_reduction,
        root_branches_per_level,
        tree_elements,
        is_root=True
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
            flatshading=True,
            lighting=dict(ambient=0.5, diffuse=0.8, roughness=0.9),
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
    st.plotly_chart(fig, use_container_width=True)

# Run the app
if __name__ == "__main__":
    st.title("Interactive 3D Tree Visualization")
    plot_tree()
