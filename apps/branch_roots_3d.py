import streamlit as st
import numpy as np
import plotly.graph_objects as go

def cylinder_mesh(p0, p1, radius_base, radius_top, sections=8):
    """
    Generate mesh data for a tapered cylinder (frustum) between two points.
    """
    v = np.array(p1) - np.array(p0)
    length = np.linalg.norm(v)
    if length == 0:
        return None
    v = v / length

    not_v = np.array([1, 0, 0])
    if np.allclose(v, not_v):
        not_v = np.array([0, 1, 0])
    n1 = np.cross(v, not_v)
    n1 /= np.linalg.norm(n1)
    n2 = np.cross(v, n1)

    t = np.linspace(0, 2 * np.pi, sections, endpoint=False)
    circle_base = n1[:, None] * np.cos(t)[None, :] + n2[:, None] * np.sin(t)[None, :]
    circle_top = circle_base.copy()

    circle_base *= radius_base
    circle_top *= radius_top

    base_points = p0[:, None] + circle_base
    top_points = p1[:, None] + circle_top

    x = np.hstack([base_points[0], top_points[0]])
    y = np.hstack([base_points[1], top_points[1]])
    z = np.hstack([base_points[2], top_points[2]])

    faces = []
    n = sections
    for i in range(n):
        next_i = (i + 1) % n
        faces.append([i, next_i, n + next_i])
        faces.append([i, n + next_i, n + i])
    return x, y, z, faces

def rotate_vector(v, k, theta):
    v_rot = v * np.cos(theta) + np.cross(k, v) * np.sin(theta) + k * np.dot(k, v) * (1 - np.cos(theta))
    return v_rot

def grow_tree(p0, direction, length, radius_base, taper_ratio, levels, angle, length_reduction,
              branches_per_level, tree_elements, is_root=False):
    if levels == 0 or radius_base < 0.01 or length < 0.01:
        return

    p1 = p0 + direction * length
    if is_root and p1[2] > 0:
        p1[2] = 0

    radius_top = radius_base * taper_ratio
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

    N = branches_per_level
    if N > 0:
        radius_base_child = radius_top / np.sqrt(N)
    else:
        radius_base_child = 0

    length_child = length * length_reduction

    for _ in range(N):
        if is_root:
            min_theta = np.pi / 2
            max_theta = np.pi / 2 + angle
            theta = min_theta + np.random.rand() * (max_theta - min_theta)
        else:
            min_theta = 0
            max_theta = angle
            theta = min_theta + np.random.rand() * (max_theta - min_theta)

        theta += (np.random.rand() - 0.5) * np.deg2rad(10)
        phi = np.random.rand() * 2 * np.pi

        if is_root:
            theta = np.clip(theta, np.pi / 2, np.pi)
        else:
            theta = np.clip(theta, 0, np.pi / 2)

        new_direction = np.array([
            np.sin(theta) * np.cos(phi),
            np.sin(theta) * np.sin(phi),
            np.cos(theta)
        ])

        rotation_axis = np.cross([0, 0, 1], direction)
        rotation_angle = np.arccos(np.clip(np.dot(direction, [0, 0, 1]), -1.0, 1.0))
        if np.linalg.norm(rotation_axis) > 1e-6:
            rotation_axis /= np.linalg.norm(rotation_axis)
            new_direction = rotate_vector(new_direction, rotation_axis, rotation_angle)

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
    st.sidebar.header("Crown Parameters")
    crown_levels = st.sidebar.slider('Crown Levels', min_value=1, max_value=8, value=5, step=1)
    crown_length = st.sidebar.slider('Crown Length', min_value=1.0, max_value=15.0, value=7.0, step=0.5)
    crown_radius = st.sidebar.slider('Crown Radius', min_value=0.1, max_value=1.5, value=0.5, step=0.1)
    crown_taper_ratio = st.sidebar.slider('Crown Taper', min_value=0.5, max_value=1.0, value=0.7, step=0.05)
    crown_angle_deg = st.sidebar.slider('Crown Angle', min_value=10, max_value=80, value=30, step=5)
    crown_length_reduction = st.sidebar.slider('Crown Length Red.', min_value=0.5, max_value=1.0, value=0.7, step=0.05)
    crown_branches_per_level = st.sidebar.slider('Crown Branches', min_value=0, max_value=8, value=3, step=1)

    st.sidebar.header("Root Parameters")
    root_levels = st.sidebar.slider('Root Levels', min_value=1, max_value=8, value=4, step=1)
    root_length = st.sidebar.slider('Root Length', min_value=1.0, max_value=15.0, value=5.0, step=0.5)
    root_radius = st.sidebar.slider('Root Radius', min_value=0.1, max_value=1.5, value=0.4, step=0.1)
    root_taper_ratio = st.sidebar.slider('Root Taper', min_value=0.5, max_value=1.0, value=0.7, step=0.05)
    root_angle_deg = st.sidebar.slider('Root Angle', min_value=-80, max_value=80, value=45, step=5)
    root_length_reduction = st.sidebar.slider('Root Length Red.', min_value=0.5, max_value=1.0, value=0.8, step=0.05)
    root_branches_per_level = st.sidebar.slider('Root Branches', min_value=0, max_value=8, value=2, step=1)

    crown_angle_rad = np.deg2rad(crown_angle_deg)
    root_angle_rad = np.deg2rad(root_angle_deg)

    tree_elements = []
    p0 = np.array([0, 0, 0])
    direction = np.array([0, 0, 1])
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

    direction_root = np.array([0, 0, -1])
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

def show_documentation():
    st.markdown("""
    ## 3D Tree Visualization Documentation
    This app generates a 3D visualization of a tree with customizable parameters for the crown and roots.
    
    ### Crown Parameters:
    - **Crown Levels**: The number of hierarchical levels in the crown structure (branches).
    - **Crown Length**: The length of the crown (main trunk and branches) in the visualization.
    - **Crown Radius**: The base radius of the crown, which tapers as the branches grow.
    - **Crown Taper**: Controls how much the branches taper from the base to the tip.
    - **Crown Angle**: The maximum angle for branches in the crown to spread outwards.
    - **Crown Length Reduction**: A factor controlling how much the length of branches reduces as they grow.
    - **Crown Branches**: Number of branches generated per hierarchical level.

    ### Root Parameters:
    - **Root Levels**: The number of hierarchical levels in the root structure.
    - **Root Length**: The length of the roots in the visualization.
    - **Root Radius**: The base radius of the roots, tapering as they grow.
    - **Root Taper**: Controls how much the roots taper from the base to the tip.
    - **Root Angle**: The maximum angle for roots to spread outwards.
    - **Root Length Reduction**: A factor controlling the reduction in root length at each level.
    - **Root Branches**: Number of branches generated per level in the root structure.

    ### Plotly Visualization:
    The tree and its roots are visualized using a 3D Plotly mesh, where each branch and root is modeled as a tapered cylinder.
    
    ### Interaction:
    Use the sidebar controls to adjust the parameters and generate different tree shapes dynamically. The 3D plot is interactive, allowing you to rotate, zoom, and explore the tree from different angles.

    ### About the Code:
    - **cylinder_mesh()**: Generates the 3D mesh for a tapered cylinder (frustum) between two points.
    - **grow_tree()**: Recursively grows the tree by adding branches and roots based on the given parameters.
    - **rotate_vector()**: Rotates a vector using Rodrigues' rotation formula for realistic branch spreading.
    """)
    
# Main function to run the app
if __name__ == "__main__":
    st.subheader("Interactive 3D Tree Visualization")

    tabs = st.tabs(["Visualization", "Documentation"])
    
    with tabs[0]:
        plot_tree()
    
    with tabs[1]:
        show_documentation()
