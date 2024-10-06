import numpy as np
import matplotlib.pyplot as plt

def draw_tree(x1, y1, angle, depth, angle_range_deg, length_factor, linewidth_factor, 
             length_scale, width_scale, branching_factor, branching_scale, initial_depth, ax):
    if depth < 0:
        return

    # Calculate scaling based on depth
    scale_exponent = initial_depth - depth
    scaled_length = length_factor * (length_scale ** scale_exponent)
    scaled_width = linewidth_factor * (width_scale ** scale_exponent)
    
    # Calculate the end point of the current branch
    x2 = x1 + np.cos(angle) * scaled_length
    y2 = y1 + np.sin(angle) * scaled_length

    # Draw the branch in black
    ax.plot([x1, x2], [y1, y2], color='black', linewidth=scaled_width)
    
    # Determine the number of branches at the current depth
    current_branching_factor = max(1, int(branching_factor * (branching_scale ** scale_exponent)))
    
    # Calculate the range of angles for the branches
    angle_range = np.deg2rad(angle_range_deg)
    angles = np.linspace(angle - angle_range / 2, angle + angle_range / 2, current_branching_factor)
    
    # Recursively draw each branch
    for branch_angle in angles:
        draw_tree(
            x2, y2, branch_angle, depth - 1, angle_range_deg, length_factor, linewidth_factor, 
            length_scale, width_scale, branching_factor, branching_scale, initial_depth, ax
        )

def plot_tree():
    # Configuration Parameters
    depth = 9                # Depth of recursion
    angle_range_deg = 60     # Spread of branches in degrees
    length_factor = 100      # Base length of branches
    linewidth_factor = 2    # Base width of branches
    length_scale = 0.7       # Scaling factor for branch lengths
    width_scale = 0.7        # Scaling factor for branch widths
    branching_factor = 2     # Number of branches at each node
    branching_scale = 1.0    # Scaling factor for branching factor
    
    # Set up the plot with white background
    fig, ax = plt.subplots(figsize=(8, 8), facecolor='white')
    ax.set_aspect('equal')
    ax.axis('off')  # Hide axes for a cleaner look

    # Starting parameters
    x0, y0 = 0, 0             # Starting position at the origin
    initial_angle = np.pi / 2 # Initial angle pointing upwards

    # Draw the fractal tree
    draw_tree(
        x0, y0, initial_angle, depth, angle_range_deg, length_factor, linewidth_factor, 
        length_scale, width_scale, branching_factor, branching_scale, depth, ax
    )
    
    # Adjust plot limits to fit the tree tightly
    plt.tight_layout()
    
    # Save the plot as a black and white PNG file, cropped to the content
    plt.savefig('branching_tree.png', dpi=300, bbox_inches='tight', pad_inches=0, facecolor='white')
    
    # Display the plot
    plt.show()

if __name__ == "__main__":
    plot_tree()
