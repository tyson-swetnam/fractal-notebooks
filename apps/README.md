# Streamlit Applications

This folder contains interactive Streamlit applications for real-time fractal visualization and exploration. These web-based applications provide an intuitive interface for users to experiment with fractal parameters and observe mathematical patterns in real-time.

## Applications Overview

### Core Fractal Generators
- **`mandelbrot.py`** - Interactive Mandelbrot set explorer with zoom and parameter controls
- **`julia.py`** - Julia set visualization with complex parameter manipulation
- **`julia_gif.py`** - Animated Julia set generator for creating GIF sequences

### Tree and Growth Patterns
- **`branching_tree.py`** - L-system based tree generation with branching rules
- **`tree_roots_3d.py`** - 3D root system visualization using Voronoi diagrams
- **`pythagoras_tree.py`** - Recursive Pythagoras tree fractal generator

### Noise and Natural Patterns
- **`browniannoise.py`** - Brownian motion simulation and visualization
- **`pinknoise.py`** - Pink noise generation with fractal properties
- **`waves.py`** - Wave pattern simulation with tidal animations

### Specialized Applications
- **`treerings.py`** - Tree ring growth pattern simulation using Voronoi tessellation
- **`conway.py`** - Conway's Game of Life cellular automaton
- **`cones.py`** - 3D cone fractal visualizations

### Main Applications
- **`app.py`** - Primary Streamlit application for general fractal exploration
- **`app2.py`, `app3.py`, `app4.py`** - Additional specialized fractal applications

## How to Run Applications

### Local Execution
```bash
# From the repository root
streamlit run apps/mandelbrot.py
streamlit run apps/branching_tree.py
streamlit run apps/julia.py
```

### Via Docker
```bash
# Build and run containerized version
cd docker/
docker build -t fractal-app .
docker run -p 8501:8501 fractal-app
```

### Via Kubernetes
Applications can be deployed to K3s using the configurations in `k3s-deployment/` folder.

## Application Features

### Interactive Controls
- Real-time parameter adjustment with sliders and input fields
- Zoom and pan capabilities for detailed exploration
- Color scheme selection and customization
- Export functionality for generated images

### Mathematical Accuracy
- High-precision arithmetic for complex number calculations
- Configurable iteration limits and convergence criteria
- Multiple rendering algorithms for different fractal types

### Performance Optimization
- NumPy vectorization for efficient computation
- Numba JIT compilation where applicable
- Caching for repeated calculations

## Integration with Other Folders

### Relationship to `docs/`
- Applications demonstrate concepts explained in the documentation
- Generated visualizations complement theoretical content
- Interactive exploration supports educational material

### Relationship to `docker/`
- `docker/` folder contains containerization configs for these apps
- Dockerfile specifically targets Streamlit deployment
- Requirements file includes all necessary dependencies

### Relationship to `k3s-deployment/`
- Kubernetes manifests can deploy these apps at scale
- JupyterLab deployment allows notebook-based development
- Remote VM deployment enables cloud-based access

## Dependencies

Applications require the following Python packages:
- `streamlit` - Web application framework
- `numpy` - Numerical computing
- `matplotlib` - 2D plotting
- `plotly` - Interactive 3D visualizations
- `scipy` - Scientific computing
- `pandas` - Data manipulation
- `numba` - JIT compilation
- `pillow` - Image processing
- `imageio` - Animation export

## Development Notes

- Each application is designed to be self-contained and runnable independently
- Shared utility functions should be extracted to a common module
- Generated animations and images are stored locally during runtime
- Applications follow Streamlit best practices for session state management