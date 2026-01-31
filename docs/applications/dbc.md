# Differential Box-Counting Tool

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.

The Differential Box-Counting (DBC) method extends traditional box-counting to estimate the fractal dimension of grayscale images, making it suitable for analyzing continuous data like canopy height models, terrain surfaces, and biological images.

---

## Method Overview

### Traditional Box-Counting

For binary images, box-counting covers the image with boxes of size \( \varepsilon \) and counts boxes \( N(\varepsilon) \) containing the structure:

\[
D_B = \lim_{\varepsilon \to 0} \frac{\log N(\varepsilon)}{\log(1/\varepsilon)}
\]

### Differential Box-Counting

For grayscale images, DBC partitions both the spatial domain and the intensity axis. For each grid position, it counts the number of boxes needed to cover the intensity range:

\[
n_r(i,j) = \text{ceil}\left(\frac{I_{\max}(i,j) - I_{\min}(i,j)}{s}\right) + 1
\]

where:
- \( I_{\max}(i,j) \) and \( I_{\min}(i,j) \) are the maximum and minimum intensities in the box
- \( s \) is the box size in the intensity dimension

The total count is:

\[
N_r = \sum_{i,j} n_r(i,j)
\]

---

## Using the Tool

### With FracLac (ImageJ)

1. **Install FracLac**: Download from [FracLac website](https://imagej.nih.gov/ij/plugins/fraclac/fraclac.html)

2. **Prepare Image**:
   - Convert to 8-bit or 16-bit grayscale
   - Crop to region of interest

3. **Run DBC Analysis**:
   - Plugins → Fractal Analysis → FracLac → Differential Box Count
   - Set box size progression (typically power series with factor 0.1)
   - Run analysis

4. **Interpret Results**:
   - Examine the log-log plot of \( N_r \) vs \( 1/r \)
   - Linear region indicates fractal scaling
   - Slope gives fractal dimension

### With Python

```python
import numpy as np
from scipy import ndimage

def differential_box_count(image, box_sizes):
    """
    Calculate fractal dimension using differential box counting.

    Parameters:
    -----------
    image : 2D numpy array
        Grayscale image (values 0-255)
    box_sizes : list
        List of box sizes to use

    Returns:
    --------
    dimension : float
        Estimated fractal dimension
    """
    counts = []

    for size in box_sizes:
        # Grid dimensions
        h, w = image.shape
        n_h = h // size
        n_w = w // size

        total_count = 0
        for i in range(n_h):
            for j in range(n_w):
                # Extract box
                box = image[i*size:(i+1)*size, j*size:(j+1)*size]

                # Count boxes needed to cover intensity range
                i_max = np.max(box)
                i_min = np.min(box)
                n_r = np.ceil((i_max - i_min) / size) + 1
                total_count += n_r

        counts.append(total_count)

    # Linear regression on log-log data
    log_sizes = np.log(1 / np.array(box_sizes))
    log_counts = np.log(counts)

    slope, _ = np.polyfit(log_sizes, log_counts, 1)

    return slope
```

---

## Applications

### Canopy Height Models

Aerial LiDAR-derived canopy height models (CHM) exhibit fractal properties. Expected dimensions:

| Forest Type | Expected \( D_M \) | Notes |
|------------|-------------------|-------|
| Lowland Rainforest | 1.3-1.4 | Complex vertical structure |
| Mixed Conifer | 1.4-1.5 | Intermediate complexity |
| Pine Plantation | 1.5-1.6 | More uniform structure |

### Biological Tissues

Medical imaging applications:

- **Bone trabecular structure**: \( D \approx 2.2-2.4 \)
- **Tumor vasculature**: \( D \approx 1.6-1.9 \)
- **Neural branching**: \( D \approx 1.3-1.5 \)

### Terrain Analysis

Digital elevation models:

- **Smooth terrain**: \( D \approx 2.1-2.2 \)
- **Moderate terrain**: \( D \approx 2.2-2.4 \)
- **Rugged mountains**: \( D \approx 2.4-2.6 \)

---

## Best Practices

### Image Preparation

1. **Resolution**: Use highest available resolution
2. **Normalization**: Scale intensities to 0-255 range
3. **Noise reduction**: Apply gentle smoothing if needed
4. **Border effects**: Crop edges or use padding

### Box Size Selection

- **Minimum**: At least 3-4 pixels
- **Maximum**: No more than 1/4 of image dimension
- **Progression**: Power series (factor 1.5-2.0) or exponential

### Quality Assessment

- **\( r^2 \) value**: Should exceed 0.99 for reliable estimate
- **Coefficient of variation**: Low CV indicates stable estimate
- **Visual inspection**: Check log-log plot linearity

---

## Interpreting Results

### Mass Dimension vs Box Dimension

The differential box-counting method estimates the **mass dimension** \( d_M \), which may differ from the standard box-counting dimension \( D_B \):

- For self-similar fractals: \( d_M = D_B \)
- For self-affine fractals: \( d_M \) reflects the scaling of mass/intensity

### MST Predictions

Metabolic Scaling Theory predicts \( d_M = 3/2 = 1.5 \) for vascular networks when viewed in 2D projection. Empirical values typically fall in the range \( 1.45-1.55 \).

---

## References

- Sarkar, N., & Chaudhuri, B. B. (1994). An efficient differential box-counting approach to compute fractal dimension of image. *IEEE Transactions on Systems, Man, and Cybernetics*, 24(1), 115-120.

- West, G. B., Brown, J. H., & Enquist, B. J. (1999). The fourth dimension of life: fractal geometry and allometric scaling of organisms. *Science*, 284(5420), 1677-1679.
