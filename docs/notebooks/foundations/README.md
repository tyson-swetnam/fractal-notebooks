# Part 1: Foundations - Jupyter Notebooks

This directory contains Jupyter notebooks supporting Part 1 (Foundations) of the Fractal Notebooks documentation, covering the mathematical foundations, history, and fundamental concepts of fractal geometry.

## Organization by Chapter

### Chapter 1: History of Fractal Mathematics
**Covers**: Cantor, Koch, Sierpinski, Julia, Mandelbrot, self-similarity vs self-affinity, biological applications, complex dimensions

- `ch1_classic_fractals.ipynb` - Classic fractals (Cantor set, Sierpinski triangle, Koch curve)
- `ch1_iterated_function_systems.ipynb` - Barnsley's fern and IFS-based fractals
- `ch1_complex_dimensions.ipynb` - Riemann zeta function and complex dimensional tilings

### Chapter 2: Mathematical Foundations
**Covers**: Topological vs fractal dimension, Hausdorff-Besicovitch dimension, box-counting, differential box-counting, power laws, Hurst exponent, lacunarity

- `ch2_dimension_theory.ipynb` - Box-counting and differential box-counting methods
- `ch2_hurst_exponent.ipynb` - Power laws, Hurst exponent, and self-affinity measures

### Chapter 3: Fractal Dimensionality
**Covers**: 1D (pink noise, fBm, Cantor), 2D (fBs, Mandelbrot/Julia, Sierpinski, Koch), 3D (Menger sponge, DLA, branching), 4D (time-evolving)

- `ch3_1d_fractals.ipynb` - 1D fractals: fBm, pink noise, Cantor sets
- `ch3_2d_fractals.ipynb` - 2D fractals: Sierpinski, Koch, fBs, zeta tilings
- `ch3_3d_fractals.ipynb` - 3D fractals: Menger sponge, DLA, branching trees, zeta space

## Current Files Mapping

The following shows how existing notebooks map to the new organization:

| Current File | New Organization | Status |
|-------------|------------------|---------|
| `fractals.ipynb` | Split into `ch1_classic_fractals.ipynb`, `ch3_1d_fractals.ipynb`, `ch3_2d_fractals.ipynb`, `ch3_3d_fractals.ipynb` | To be reorganized |
| `ferns.ipynb` | Becomes `ch1_iterated_function_systems.ipynb` | To be updated |
| `fractal_generators.ipynb` | Merge into `ch3_3d_fractals.ipynb` | To be merged |
| `dla.ipynb` | Merge into `ch3_3d_fractals.ipynb` | To be merged |
| `old_dla.ipynb` | Deprecated (merged into ch3) | To be removed |
| `dbc.ipynb` | Becomes `ch2_dimension_theory.ipynb` | To be updated |
| `zeta_space.ipynb` | Merge into `ch3_2d_fractals.ipynb` | To be merged |
| `zeta_3d.ipynb` | Split between `ch1_complex_dimensions.ipynb` and `ch3_3d_fractals.ipynb` | To be split |
| `torch_test.ipynb` | Deprecated (not relevant) | To be removed |

## Environment Setup

### Using Conda/Mamba

Create the environment from the provided file:

```bash
mamba env create -f environment.yml
mamba activate fractal-foundations
```

Or with conda:

```bash
conda env create -f environment.yml
conda activate fractal-foundations
```

### Manual Installation

```bash
# Create environment
mamba create -n fractal-foundations python=3.10 -y
mamba activate fractal-foundations

# Install core dependencies
mamba install -c conda-forge numpy scipy matplotlib jupyter jupyterlab ipywidgets plotly numba

# Install OpenCV for image processing (dbc notebook)
pip install opencv-python
```

### GPU Support (Optional)

For notebooks that use CUDA acceleration:

```bash
mamba install -c conda-forge cudatoolkit=11.8 pycuda
```

## Notebook Structure

Each notebook follows this standard structure:

1. **Title and Overview**
   - Clear title indicating chapter and topic
   - Brief description of concepts covered
   - Learning objectives

2. **Requirements**
   ```python
   # List of imports with version requirements
   import numpy as np  # >=1.20.0
   import matplotlib.pyplot as plt  # >=3.5.0
   ```

3. **Theoretical Background**
   - Markdown cells explaining the mathematics
   - LaTeX equations for formulas
   - References to relevant literature

4. **Implementation**
   - Well-commented code cells
   - Each cell can execute independently
   - Clear variable names

5. **Visualization**
   - Properly labeled plots
   - Interactive widgets where appropriate
   - Multiple visualization approaches

6. **Exercises** (optional)
   - Practice problems
   - Parameter exploration suggestions

7. **References**
   - Citations to papers and textbooks
   - Links to related resources

## Dependencies

### Core Requirements
- Python >= 3.10
- NumPy >= 1.20.0
- Matplotlib >= 3.5.0
- SciPy >= 1.7.0
- Jupyter/JupyterLab
- ipywidgets >= 8.0.0

### Visualization
- Plotly >= 5.0.0

### Performance
- Numba >= 0.55.0

### Optional (GPU)
- CUDA Toolkit 11.8
- PyCUDA

### Image Processing (for DBC)
- OpenCV (opencv-python)

## Running the Notebooks

1. **Start JupyterLab**:
   ```bash
   jupyter lab
   ```

2. **Navigate** to the `foundations/` directory

3. **Select kernel**: Choose "fractal-foundations" from the kernel selector

4. **Run cells** sequentially from top to bottom

## Notes

- All notebooks are designed to run sequentially from top to bottom
- Random seeds are set where appropriate for reproducibility
- GPU-accelerated cells are optional and will fall back to CPU if CUDA is unavailable
- Large visualizations may take time to render
- Interactive widgets require `ipywidgets` extensions to be enabled

## Troubleshooting

### Widgets not displaying
```bash
jupyter nbextension enable --py widgetsnbextension
jupyter labextension install @jupyter-widgets/jupyterlab-manager
```

### Import errors
Ensure you've activated the correct environment:
```bash
mamba activate fractal-foundations
```

### CUDA errors
GPU-accelerated cells are optional. If you encounter CUDA errors, you can either:
1. Skip those cells
2. Use the CPU-based alternatives provided
3. Install CUDA toolkit for your system

## Contributing

When adding or modifying notebooks:
1. Follow the standard structure outlined above
2. Test all cells execute successfully in order
3. Include proper markdown documentation
4. Add equations using LaTeX notation
5. Ensure visualizations are properly labeled
6. Update this README with any new dependencies

## Version History

- **v1.0** (2025-12-19): Initial organization of foundations notebooks aligned with Part 1 chapters
