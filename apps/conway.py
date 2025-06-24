import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.signal import convolve2d

# Conway's Game of Life with Higher Resolution

# Set higher grid size for higher resolution
GRID_SIZE = 250  # Increase this value for even higher resolution

# Initialize the grid with random values (0 or 1)
np.random.seed(42)
grid = np.random.choice([0, 1], size=(GRID_SIZE, GRID_SIZE))

def update(frame_num, img, grid):
    # Define the kernel for convolution
    kernel = np.array([[1, 1, 1],
                       [1, 0, 1],
                       [1, 1, 1]])

    # Count neighbors
    neighbor_count = convolve2d(grid, kernel, mode='same', boundary='wrap')

    # Apply rules
    new_grid = ((neighbor_count == 3) | ((grid == 1) & (neighbor_count == 2))).astype(int)

    # Update data
    img.set_data(new_grid)
    grid[:] = new_grid[:]
    return img,

# Set up the figure and axes
fig, ax = plt.subplots()
img = ax.imshow(grid, interpolation='nearest', cmap='binary')
ax.axis('off')  # Hide the axes for better visual appearance

# Create the animation
ani = animation.FuncAnimation(fig, update, fargs=(img, grid), frames=200, interval=50, blit=True)

# Save the animation as a GIF file
ani.save('game_of_life_high_res.gif', writer='pillow', fps=20)

plt.show()
