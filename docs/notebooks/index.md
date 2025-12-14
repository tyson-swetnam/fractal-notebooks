# Part VII: Computational Notebooks

This section provides Jupyter notebooks that demonstrate fractal algorithms, visualizations, and analysis methods. Each notebook is self-contained and can be run interactively.

---

## Available Notebooks

### Diffusion Limited Aggregation

[**Open DLA Notebook**](old_dla.ipynb)

Explore the physics of diffusion-limited aggregation:

- Random walk implementation
- Cluster growth dynamics
- Fractal dimension calculation (\( D \approx 1.7 \))
- Comparison with biological DLA (lichen, stromatolites)

**Key Concepts:**
- Harmonic measure and screening effects
- Sticking probability variations
- Fractal dimension estimation

---

### Barnsley's Ferns

[**Open Ferns Notebook**](ferns.ipynb)

Generate realistic fern patterns using Iterated Function Systems (IFS):

- Affine transformation mathematics
- Probability-weighted chaos game
- Parameter exploration
- Comparison with real fern morphology

**Mathematical Foundation:**
\[
f_i(x, y) = \begin{pmatrix} a_i & b_i \\ c_i & d_i \end{pmatrix} \begin{pmatrix} x \\ y \end{pmatrix} + \begin{pmatrix} e_i \\ f_i \end{pmatrix}
\]

---

### Self-Similar Fractals

[**Open Fractals Notebook**](fractals.ipynb)

Classic self-similar fractal constructions:

- **Cantor Set**: Middle-third removal, \( D = \log 2 / \log 3 \)
- **Koch Curve**: Recursive line replacement, \( D = \log 4 / \log 3 \)
- **Sierpiński Triangle**: Iterated triangle removal
- **Menger Sponge**: 3D generalization

**Dimension Calculations:**
\[
D = \frac{\log N}{\log r}
\]
where \( N \) is the number of self-similar pieces and \( r \) is the scaling factor.

---

### Self-Affine Fractal Generators

[**Open Fractal Generators Notebook**](fractal_generators.ipynb)

Comprehensive exploration of self-affine fractals:

- Fractional Brownian motion (fBm)
- Hurst exponent and persistence
- Self-affine surfaces (terrain generation)
- Branching networks with MST scaling

**Key Relationships:**
- For fBm traces: \( D = 2 - H \)
- For fBm surfaces: \( D = 3 - H \)
- MST branching: \( \xi = n^{-1/2}, \gamma = n^{-1/3} \)

---

### Differential Box-Counting

[**Open DBC Notebook**](dbc.ipynb)

Fractal dimension estimation for grayscale images:

- Method implementation from scratch
- Application to synthetic fractals
- Analysis of real biological images
- Comparison with FracLac results

**Algorithm:**
\[
N_r = \sum_{i,j} n_r(i,j), \quad D = \lim_{r \to 0} \frac{\log N_r}{\log(1/r)}
\]

---

### Riemann Zeta 2D

[**Open Zeta 2D Notebook**](zeta_space.ipynb)

Two-dimensional visualization of the Riemann zeta function:

- Complex plane domain coloring
- Zero locations along critical line
- Connection to prime number distribution
- Spectral properties

**Definition:**
\[
\zeta(s) = \sum_{n=1}^{\infty} \frac{1}{n^s} = \prod_{p \text{ prime}} \frac{1}{1 - p^{-s}}
\]

---

### Riemann Zeta 3D

[**Open Zeta 3D Notebook**](zeta_3d.ipynb)

Three-dimensional surface visualization of \( |\zeta(s)| \):

- Surface plot construction
- Pole at \( s = 1 \)
- Critical strip exploration
- Interactive rotation and zoom

---

## Running Notebooks

### Option 1: Local Installation

```bash
# Create environment
cd docs/notebooks
mamba env create -f streamlit-plotly.yaml
mamba activate fractal-env

# Install Jupyter kernel
python -m ipykernel install --name fractal-env --display-name "Fractal Env"

# Launch JupyterLab
jupyter lab
```

### Option 2: Google Colab

Most notebooks can be run on Google Colab:

1. Open the notebook on GitHub
2. Replace `github.com` with `colab.research.google.com/github` in the URL
3. Run cells in the cloud environment

### Option 3: Binder

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/tyson-swetnam/fractal-notebooks/main)

Launch interactive notebooks directly in your browser.

---

## Notebook Dependencies

| Notebook | Key Dependencies |
|----------|-----------------|
| DLA | numpy, matplotlib |
| Ferns | numpy, matplotlib |
| Fractals | numpy, matplotlib, scipy |
| Generators | numpy, numba, matplotlib, plotly |
| DBC | numpy, scipy, PIL |
| Zeta 2D | numpy, matplotlib, mpmath |
| Zeta 3D | numpy, plotly, mpmath |

---

## Contributing

To add new notebooks:

1. Create `.ipynb` file in `docs/notebooks/`
2. Include clear markdown documentation
3. Add to navigation in `mkdocs.yml`
4. Ensure all cells execute without errors
5. Clear output before committing (optional)

---

## Learning Path

**Recommended order for beginners:**

1. **Self-Similar Fractals** - Foundational concepts
2. **Barnsley's Ferns** - IFS and affine transformations
3. **Self-Affine Generators** - Beyond self-similarity
4. **DLA** - Stochastic growth processes
5. **DBC** - Dimension estimation methods
6. **Riemann Zeta** - Advanced mathematical connections
