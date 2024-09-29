from PIL import Image

def generate_mandelbrot(width, height, max_iter):
    # Create a new grayscale image
    image = Image.new('L', (width, height))
    pixels = image.load()

    # Define the region of the complex plane to visualize
    re_start, re_end = -2.0, 1.0
    im_start, im_end = -1.5, 1.5

    for x in range(width):
        for y in range(height):
            # Map pixel position to a point in the complex plane
            c = complex(
                re_start + (x / width) * (re_end - re_start),
                im_start + (y / height) * (im_end - im_start)
            )
            z = 0 + 0j
            n = 0

            # Iterate the Mandelbrot formula
            while abs(z) <= 2 and n < max_iter:
                z = z * z + c
                n += 1

            # Set the pixel color (black or white)
            if n == max_iter:
                pixels[x, y] = 0    # Black for points inside the set
            else:
                pixels[x, y] = 255  # White for points outside the set

    # Save the image
    image.save('mandelbrot_set1.png', 'PNG')

# Parameters for the Mandelbrot Set
width, height = 3840, 2160  # Image size
max_iter = 1000            # Maximum number of iterations

generate_mandelbrot(width, height, max_iter)
