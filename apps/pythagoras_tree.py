import matplotlib.pyplot as plt
import numpy as np

def draw_pythagoras_tree(ax, x, y, size, angle, depth, max_depth):
    if depth > max_depth:
        return

    # Calculate the coordinates of the square
    # Starting from the bottom-left corner and moving counter-clockwise
    square = np.array([
        [0, 0],
        [0, size],
        [size, size],
        [size, 0],
        [0, 0]
    ])

    # Rotation matrix
    theta = np.radians(angle)
    R = np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta),  np.cos(theta)]
    ])
    # Rotate the square
    square = square @ R.T

    # Translate the square to position (x, y)
    square[:, 0] += x
    square[:, 1] += y

    # Draw the square in black
    ax.fill(square[:, 0], square[:, 1], color='black', edgecolor='black')

    # Calculate new size for the child squares
    new_size = size * np.sqrt(2) / 2

    # Left branch
    left_angle = angle + 45
    left_x = square[1, 0]
    left_y = square[1, 1]

    # Right branch
    right_angle = angle - 45
    right_x = square[2, 0] - new_size * np.cos(np.radians(right_angle))
    right_y = square[2, 1] - new_size * np.sin(np.radians(right_angle))

    # Recursive calls for left and right branches
    draw_pythagoras_tree(ax, left_x, left_y, new_size, left_angle, depth + 1, max_depth)
    draw_pythagoras_tree(ax, right_x, right_y, new_size, right_angle, depth + 1, max_depth)

# Set up the plot with white background
fig, ax = plt.subplots(facecolor='white')
ax.set_aspect('equal')
ax.axis('off')

# Starting parameters
x0, y0 = 0, 0   # Starting position
size = 1        # Size of the initial square
angle = 0       # Initial angle
depth = 0       # Starting depth
max_depth = 12  # Maximum recursion depth

# Draw the Pythagoras Tree
draw_pythagoras_tree(ax, x0, y0, size, angle, depth, max_depth)

# Let matplotlib automatically adjust the view
# Removed fixed axis limits to enable automatic cropping
# ax.set_xlim(-5, 5)
# ax.set_ylim(0, 10)

# Save the plot as a black and white PNG file, cropped to the content
plt.savefig('pythagoras_tree.png', dpi=2400, bbox_inches='tight', pad_inches=0, facecolor='white')

# Optionally display the plot
plt.show()
