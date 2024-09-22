# app.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

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
            'MinCellWallThickness': [2, 1.9, 1.8, 1.7, 1.6],
        }
        df = pd.DataFrame(data)
    return df

def generate_points_in_rectangle(x_start, x_end, y_min, y_max, num_points):
    x = np.random.uniform(x_start, x_end, num_points)
    y = np.random.uniform(y_min, y_max, num_points)
    points = np.vstack((x, y)).T
    return points

def voronoi_finite_polygons_2d(vor, radius=None):
    """
    Reconstruct finite Voronoi polygons in 2D.
    """
    if vor.points.shape[1] != 2:
        raise ValueError("Requires 2D input.")
    new_regions = []
    new_vertices = vor.vertices.tolist()
    center = vor.points.mean(axis=0)
    if radius is None:
        radius = vor.points.ptp().max() * 2
    # Map ridge vertices to ridges
    all_ridges = {}
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges.setdefault(p1, []).append((p2, v1, v2))
        all_ridges.setdefault(p2, []).append((p1, v1, v2))
    for p1, region in enumerate(vor.point_region):
        vertices = vor.regions[region]
        if all(v >= 0 for v in vertices):
            new_regions.append(vertices)
            continue
        ridges = all_ridges[p1]
        new_region = [v for v in vertices if v >= 0]
        for p2, v1, v2 in ridges:
            if v2 < 0:
                v1, v2 = v2, v1
            if v1 >= 0:
                continue
            # Compute the missing endpoint
            t = vor.points[p2] - vor.points[p1]
            t /= np.linalg.norm(t)
            n = np.array([-t[1], t[0]])  # Perpendicular vector
            midpoint = vor.points[[p1, p2]].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n)) * n
            far_point = vor.vertices[v2] + direction * radius
            new_vertices.append(far_point.tolist())
            new_region.append(len(new_vertices) - 1)
        new_regions.append(new_region)
    return new_regions, np.array(new_vertices)

# Set the title of the Streamlit app
st.title("Tree Growth Rings Simulation - Linear Core Visualization with Voronoi Cells")

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

for ring in rings:
    total_length = ring['x_end'] - ring['x_start']
    num_cells = int(total_length / cell_size)
    if num_cells < 1:
        num_cells = 1  # Ensure at least one cell
    ring['num_cells'] = num_cells
    
    # Early wood cells
    early_length = ring['early_end'] - ring['x_start']
    num_early_cells = int(early_length / cell_size)
    if num_early_cells < 1:
        num_early_cells = 1
    ring['num_early_cells'] = num_early_cells
    
    # Late wood cells
    num_late_cells = num_cells - num_early_cells
    if num_late_cells < 0:
        num_late_cells = 0
    ring['num_late_cells'] = num_late_cells
    
    # Generate early wood points
    early_points = generate_points_in_rectangle(
        ring['x_start'], ring['early_end'], y_min, y_max, ring['num_early_cells'])
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
    
    # Generate late wood points
    if num_late_cells > 0:
        late_points = generate_points_in_rectangle(
            ring['early_end'], ring['x_end'], y_min, y_max, num_late_cells)
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

# Get finite Voronoi regions
regions, vertices = voronoi_finite_polygons_2d(vor)

# Map points to regions
cell_polygons = []
for idx, region in enumerate(regions):
    polygon = vertices[region]
    cell = cells[idx]
    cell_polygons.append((cell, polygon))

# Create the plot
fig, ax = plt.subplots(figsize=(10, 6))

patches = []
colors = []
line_widths = []

for cell, polygon in cell_polygons:
    poly = Polygon(polygon, closed=True)
    patches.append(poly)
    if cell['cell_type'] == 'Early Wood':
        colors.append('peru')  # Lighter color for early wood
    else:
        colors.append('saddlebrown')  # Darker color for late wood
    # Normalize line widths for plotting
    line_width = (cell['cell_wall_thickness'] / max(df_growth['MaxCellWallThickness'])) * 2
    line_widths.append(line_width)

# Create patch collection
p = PatchCollection(patches, facecolor=colors, edgecolor='black', linewidths=line_widths)

ax.add_collection(p)

# Set plot limits
ax.set_xlim(points[:, 0].min() - cell_size, points[:, 0].max() + cell_size)
ax.set_ylim(points[:, 1].min() - cell_size, points[:, 1].max() + cell_size)

ax.set_aspect('equal')
ax.set_xlabel('Distance from Pith (micrometers)')
ax.set_ylabel('Vertical Position (micrometers)')
ax.set_title('Linear Core Visualization with Voronoi Cells')

# Add legend
from matplotlib.lines import Line2D

legend_elements = [
    Line2D([0], [0], marker='s', color='w', label='Early Wood', markerfacecolor='peru', markersize=15),
    Line2D([0], [0], marker='s', color='w', label='Late Wood', markerfacecolor='saddlebrown', markersize=15)
]
ax.legend(handles=legend_elements, loc='upper right')

st.pyplot(fig)
