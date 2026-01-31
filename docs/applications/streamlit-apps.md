# Streamlit Applications

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.

Streamlit applications provide Python-based interactive tools for exploring fractals and computing fractal dimensions. These applications are ideal for scientific exploration and analysis.

---

## Running Streamlit Apps

### Quick Start

```bash
cd apps
pip install -r requirements.txt
streamlit run mandelbrot.py
```

### Available Applications

| Application | File | Description |
|-------------|------|-------------|
| Mandelbrot Explorer | `mandelbrot.py` | Interactive Mandelbrot set with zoom |
| Julia Set Generator | `julia.py` | Julia set visualization with parameter control |
| Branching Tree | `branching_tree.py` | Self-affine branching structure |
| Pythagoras Tree | `pythagoras_tree.py` | Classic Pythagoras tree fractal |

---

## Mandelbrot Explorer

Interactive exploration of the Mandelbrot set with:

- **Zoom controls**: Click to zoom into regions of interest
- **Iteration depth**: Adjust maximum iterations for detail
- **Color schemes**: Multiple coloring algorithms
- **Export**: Save high-resolution images

### Usage

```bash
streamlit run apps/mandelbrot.py
```

### Mathematical Background

The Mandelbrot set consists of complex numbers \( c \) where the sequence:

\[
z_0 = 0, \quad z_{n+1} = z_n^2 + c
\]

remains bounded (i.e., \( |z_n| < 2 \) for all \( n \)).

---

## Julia Set Generator

Generate Julia sets for any complex parameter \( c \).

### Features

- **Parameter selection**: Slider controls for real and imaginary parts of \( c \)
- **Connected vs disconnected**: Visualize how the Julia set changes
- **Escape time coloring**: Multiple algorithms
- **Animation**: Animate through parameter space

### Mathematical Background

For a fixed \( c \), the Julia set is the boundary of points \( z_0 \) for which:

\[
z_{n+1} = z_n^2 + c
\]

remains bounded.

---

## Branching Tree

Generate self-affine branching structures that model plant vascular networks.

### Parameters

| Parameter | Description | Range |
|-----------|-------------|-------|
| Branching angle | Angle between child branches | 0°-90° |
| Length ratio | Ratio of child to parent length | 0.5-0.9 |
| Width ratio | Ratio of child to parent width | 0.5-0.9 |
| Iterations | Number of branching levels | 1-15 |

### Self-Affinity

When length ratio ≠ width ratio, the tree exhibits self-affine scaling:

\[
\gamma = \frac{l_{k+1}}{l_k} \neq \xi = \frac{r_{k+1}}{r_k}
\]

This matches the predictions of Metabolic Scaling Theory.

---

## Pythagoras Tree

The classic Pythagoras tree fractal using self-similar squares.

### Features

- **Angle control**: Adjust the branching angle (default 45°)
- **Depth control**: Number of iterations
- **Symmetric vs asymmetric**: Toggle symmetric branching
- **Color by depth**: Visual hierarchy

### Construction

Each iteration:
1. Draw a square on each leaf
2. Construct two smaller squares forming a right triangle
3. Repeat

With angle \( \theta \), the scaling factor is \( r = \cos\theta \).

---

## Development Guide

### Creating New Streamlit Apps

1. Create a new `.py` file in `apps/`:

```python
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("My Fractal App")

# Parameters
iterations = st.slider("Iterations", 1, 100, 50)

# Computation
# ... your fractal algorithm ...

# Display
fig, ax = plt.subplots()
ax.imshow(result)
st.pyplot(fig)
```

2. Run with `streamlit run apps/your_app.py`

### Dependencies

Key packages used:

- `streamlit`: Web interface
- `numpy`: Numerical computation
- `numba`: JIT compilation for speed
- `matplotlib`: Static visualization
- `plotly`: Interactive visualization
- `scipy`: Scientific algorithms
- `pillow`: Image processing

### Performance Tips

- Use `@st.cache_data` for expensive computations
- Use `numba` JIT for numerical loops
- Consider WebGL alternatives for real-time interaction

---

## Docker Deployment

For production deployment:

```bash
cd docker
docker build -t streamlit-fractals .
docker run -p 8501:8501 streamlit-fractals
```

The Dockerfile includes all dependencies and exposes port 8501.
