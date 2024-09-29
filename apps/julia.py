import numpy as np
from PIL import Image

def generate_julia(width, height, zoom, cX, cY, moveX, moveY, max_iter):
    # Create an empty image
    bitmap = Image.new("RGB", (width, height), "black")
    pix = bitmap.load()

    # Generate the Julia fractal
    for x in range(width):
        for y in range(height):
            zx = 1.5 * (x - width / 2) / (0.5 * zoom * width) + moveX
            zy = 1.0 * (y - height / 2) / (0.5 * zoom * height) + moveY
            i = max_iter

            while zx * zx + zy * zy < 4 and i > 1:
                tmp = zx * zx - zy * zy + cX
                zy, zx = 2.0 * zx * zy + cY, tmp
                i -= 1

            # Map the iteration count to a color
            r = int(255 * i / max_iter)
            g = int(255 * i / max_iter)
            b = int(255 * i / max_iter)
            pix[x, y] = (r, g, b)

    # Save the image
    bitmap.save("julia_set.png", "PNG")

# Parameters for the Julia Set
width, height = 1920, 1080  # High resolution
zoom = 1
cX, cY = -0.7, 0.27015      # Constants for the Julia Set
moveX, moveY = 0.0, 0.0     # Panning
max_iter = 255              # Max iterations

generate_julia(width, height, zoom, cX, cY, moveX, moveY, max_iter)
