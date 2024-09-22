# app.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.spatial import Voronoi
from shapely.geometry import Polygon, box

def load_growth_data(uploaded_file):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        # Sample data
        data = {
            'Year': [1, 2, 3, 4, 5],
            'TotalRingLength': [1000, 950, 900, 850, 800],
            'EarlyWoodLength': [600, 570, 540, 510, 480],
            'LateWoodLength': [400, 380, 360, 340, 320],
            'MaxCellWallThickness': [5, 4.8, 4.6, 4.4, 4.2],
            'MinCellWallThickness': [4, 3.9, 3.8, 3.7, 3.6],
        }
        df = pd.DataFrame(data)
    return df

def voronoi_finite_polygons_2d(vor, bounding_box):
    """
    Reconstruct infinite Voronoi regions in a 2D diagram to finite regions clipped to a bounding box.
    Returns a list of (point_index, clipped_polygon_coords).
    """
    if vor.points.shape[1] != 2:
        raise ValueError("Requires 2D input")

    new_regions = []
    new_vertices = vor.vertices.tolist()
    center = vor.points.mean(axis=0)

    # Map from ridge points to ridge vertices
    all_ridges = {}
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges.setdefault(p1, []).append((p2, v1, v2))
        all_ridges.setdefault(p2, []).append((p1, v1, v2))

    # Bounding box polygon
    bbox_polygon = box(*bounding_box)

    for p1, region_index in enumerate(vor.point_region):
        vertices = vor.regions[region_index]

        if -1 not in vertices:
            # Finite region
            region_points = [vor.vertices[i] for i in vertices]
            poly = Polygon(region_points)
            # Clip the polygon to the bounding box
            clipped_polygon = poly.intersection(bbox_polygon)
            if clipped_polygon.is_empty or not clipped_polygon.exterior:
                continue
            new_regions.append((p1, np.array(clipped_polygon.exterior.coords)))
            continue

        # Reconstruct a non-finite region
        ridges = all_ridges[p1]
        new_region = [v for v in vertices if v >= 0]

        for p2, v1, v2 in ridges:
            if v2 < 0:
                v1, v2 = v2, v1
            if v1 >= 0 and v2 >= 0:
                continue  # Both vertices are finite
            # Compute the missing endpoint
            t = vor.points[p2] - vor.points[p1]  # Tangent
            t /= np.linalg.norm(t)
            n = np.array([-t[1], t[0]])  # Normal

            midpoint = vor.points[[p1, p2]].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n)) * n
            far_point = vor.vertices[v2] + direction * 1e6  # A large number to extend to infinity

            new_vertices.append(far_point.tolist())
            new_region.append(len(new_vertices) - 1)

        # Sort the region's vertices
        vs = np.array([new_vertices[v] for v in new_region])
        c = vs.mean(axis=0)
        angles = np.arctan2(vs[:,1] - c[1], vs[:,0] - c[0])
        new_region = [v for _, v in sorted(zip(angles, new_region))]

        # Build the polygon
        region_points = [new_vertices[v] for v in new_region]
        poly = Polygon(region_points)
        # Clip the polygon to the bounding box
        clipped_polygon = poly.intersection(bbox_polygon)
        if clipped_polygon.is_empty or not clipped_polygon.exterior:
            continue
        new_regions.append((p1, np.array(clipped_polygon.exterior.coords)))

    return new_regions

# Set the title of the Streamlit app
st.title("Tree Growth Rings Simulation - Linear Core Visualization with Aligned Cells")

# Sidebar for parameters
st.sidebar.header("Simulation Parameters")

uploaded_file = st.sidebar.file_uploader("Upload growth_rate CSV file", type="csv")

# Load growth data
df_growth = load_growth_data(uploaded_file)

# Display the data
st.subheader("Growth Data")
st.write(df_growth)

cell_size = st.sidebar.number_input("Cell Size (micrometers)", min_value=1.0, max_value=100.0, value=20.0, step=1.0)
total_height = st.sidebar.number_input("Total Height (micrometers)", min_value=100.0, max_value=5000.0, value=1000.0, step=100.0)

# Initialize the starting x position
x_positions = [0]  # Starting at the pith (x=0)

# Prepare ring data
rings = []

for index, row in df_growth.iterrows():
    year = row['Year']
    total_length = row['TotalRingLength']
    early_length = row['EarlyWoodLength']
    late_length = row['LateWoodLength']
    max_thickness = row['MaxCellWallThickness']
    min_thickness = row['MinCellWallThickness']

    # Start and end positions
    x_start = x_positions[-1]
    x_end = x_start + total_length

    # Early wood and late wood positions
    early_end = x_start + early_length
    late_end = x_end  # Since early_length + late_length = total_length

    ring_data = {
        'Year': year,
        'x_start': x_start,
        'x_end': x_end,
        'early_end': early_end,
        'late_end': late_end,
        'max_thickness': max_thickness,
        'min_thickness': min_thickness,
    }
    rings.append(ring_data)

    # Update x_positions
    x_positions.append(x_end)

# Initialize cells list
cells = []

y_min = 0
y_max = total_height  # Total height of the visualization

# Define global y_values for consistent horizontal alignment
y_values = np.arange(y_min + cell_size / 2, y_max, cell_size)

# Generate x_values for the entire core to ensure columns are mostly aligned
x_max = x_positions[-1]
x_values_global = np.arange(0 + cell_size / 2, x_max, cell_size)

for ring in rings:
    # Get x_values within the ring
    x_values_ring = x_values_global[(x_values_global >= ring['x_start']) & (x_values_global < ring['x_end'])]

    # Early wood cells
    x_values_early = x_values_ring[(x_values_ring >= ring['x_start']) & (x_values_ring < ring['early_end'])]

    # Late wood cells
    x_values_late = x_values_ring[(x_values_ring >= ring['early_end']) & (x_values_ring < ring['x_end'])]

    # Generate grid points for early wood
    xv_early, yv_early = np.meshgrid(x_values_early, y_values)
    early_points = np.vstack([xv_early.ravel(), yv_early.ravel()]).T

    for point in early_points:
        cell = {
            'x': point[0],
            'y': point[1],
            'cell_type': 'Early Wood',
            'max_thickness': ring['max_thickness'],
            'min_thickness': ring['min_thickness'],
            'Year': ring['Year'],
        }
        cells.append(cell)

    # Generate grid points for late wood
    if len(x_values_late) > 0:
        xv_late, yv_late = np.meshgrid(x_values_late, y_values)
        late_points = np.vstack([xv_late.ravel(), yv_late.ravel()]).T

        for point in late_points:
            cell = {
                'x': point[0],
                'y': point[1],
                'cell_type': 'Late Wood',
                'max_thickness': ring['max_thickness'],
                'min_thickness': ring['min_thickness'],
                'Year': ring['Year'],
            }
            cells.append(cell)

# Assign cell wall thicknesses
for cell in cells:
    min_thickness = cell['min_thickness']
    max_thickness = cell['max_thickness']
    cell_wall_thickness = np.random.uniform(min_thickness, max_thickness)
    cell['cell_wall_thickness'] = cell_wall_thickness

# Collect all points
points = np.array([[cell['x'], cell['y']] for cell in cells])

# Construct Voronoi diagram
vor = Voronoi(points)

# Define bounding box for the core (left, bottom, right, top)
bounding_box = [x_positions[0], y_min, x_positions[-1], y_max]

# Get finite Voronoi regions and clip them to the core boundary
regions = voronoi_finite_polygons_2d(vor, bounding_box)

# Create Plotly figure
fig = go.Figure()

# Map points to regions and add polygons to Plotly figure
for point_index, region in regions:
    cell = cells[point_index]

    # Add Voronoi cell to Plotly figure (Clipped within bounding box)
    fig.add_trace(go.Scatter(
        x=region[:, 0],
        y=region[:, 1],
        mode='lines',
        fill='toself',
        fillcolor='peru' if cell['cell_type'] == 'Early Wood' else 'saddlebrown',
        line=dict(width=cell['cell_wall_thickness'], color='black'),
        name=f"Year: {cell['Year']}, {cell['cell_type']}",
        hoverinfo='skip'  # Adjust hover information as needed
    ))

# Customize layout for zooming and interaction
fig.update_layout(
    title="Linear Core Visualization with Aligned Voronoi Cells",
    xaxis_title="Distance from Pith (micrometers)",
    yaxis_title="Vertical Position (micrometers)",
    xaxis=dict(showgrid=False, zeroline=False),
    yaxis=dict(showgrid=False, zeroline=False),
    height=600,
    width=1000,
    showlegend=False,
    hovermode="closest"
)

# Enable zoom, pan, and autoscale
fig.update_layout(
    dragmode='zoom',  # Enables zooming
    xaxis=dict(
        fixedrange=False  # Allows panning and zooming on the x-axis
    ),
    yaxis=dict(
        fixedrange=False  # Allows panning and zooming on the y-axis
    )
)

# Show the Plotly figure in Streamlit
st.plotly_chart(fig, use_container_width=True)
