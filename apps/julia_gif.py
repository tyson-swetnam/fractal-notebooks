import numpy as np
from PIL import Image
import imageio

def generate_julia_frame(width, height, zoom, cX, cY, moveX, moveY, max_iter):
    bitmap = Image.new("RGBA", (width, height), (0, 0, 0, 0))  # Transparent background
    pix = bitmap.load()

    for x in range(width):
        for y in range(height):
            # Map pixel position to complex plane
            zx = 1.5 * (x - width / 2) / (0.5 * zoom * width) + moveX
            zy = 1.0 * (y - height / 2) / (0.5 * zoom * height) + moveY
            i = 0

            # Iteration of the Julia set formula
            while zx * zx + zy * zy < 4 and i < max_iter:
                tmp = zx * zx - zy * zy + cX
                zy, zx = 2.0 * zx * zy + cY, tmp
                i += 1

            if i < max_iter:
                # Reversed grayscale color mapping
                color = int(255 * (1 - i / max_iter))
                pix[x, y] = (color, color, color, 255)  # Opaque pixel
            else:
                pix[x, y] = (0, 0, 0, 0)  # Transparent pixel

    return bitmap

# Parameters
width, height = 800, 600     # Resolution of each frame
moveX, moveY = 0.0, 0.0      # Panning
max_iter = 255               # Max iterations
frames = []
zoom = 1.0
num_frames = 60              # Total number of frames in the animation

# Generate frames for the animation
for frame_num in range(num_frames):
    alpha = frame_num / num_frames * 2 * np.pi
    cX = 0.7885 * np.cos(alpha)
    cY = 0.7885 * np.sin(alpha)
    frame = generate_julia_frame(width, height, zoom, cX, cY, moveX, moveY, max_iter)
    frames.append(np.array(frame))

# Save frames as a GIF
imageio.mimsave('julia_animation.gif', frames, format='GIF', duration=0.1, loop=0)
