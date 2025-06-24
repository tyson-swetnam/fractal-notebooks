# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a collection of Python applications and Jupyter notebooks for simulating self-affine fractals. The project combines mathematical visualization, interactive applications, and scientific documentation to explore fractal geometry.

## Key Architecture Components

### Directory Structure
- `apps/` - Streamlit applications for interactive fractal visualization
- `docs/` - MkDocs documentation site with mathematical content and theory
- `docs/notebooks/` - Jupyter notebooks with fractal algorithms and examples
- `k3s-deployment/` - Kubernetes deployment configurations for JupyterLab and Weaviate
- `docker/` - Docker containerization for Streamlit applications
- `react/` - React-based web applications with TypeScript for fractal exploration

### Core Technologies
- **Documentation**: MkDocs with Material theme, MathJax for mathematical equations
- **Interactive Apps**: Streamlit for web-based fractal visualizations
- **Web Applications**: React with TypeScript, Material-UI, Plotly.js for interactive visualizations
- **Notebooks**: Jupyter with scientific Python stack (NumPy, Matplotlib, SciPy)
- **Deployment**: K3s Kubernetes with GPU support for AI workloads
- **Containerization**: Docker for application packaging

## Development Commands

### Documentation Development
```bash
# Install documentation dependencies
pip install -r requirements.txt

# Serve documentation locally
python -m mkdocs serve
# Access at http://localhost:8000
```

### Streamlit Applications
```bash
# Run specific Streamlit app
streamlit run apps/app.py
streamlit run apps/branching_tree.py
streamlit run apps/mandelbrot.py

# Docker deployment
cd docker/
docker build -t fractal-app .
docker run -p 8501:8501 fractal-app
```

### React Application Development
```bash
# Install dependencies
cd react/
npm ci

# Run development server (port 33000)
npm start

# Build for production
npm run build

# Test TypeScript compilation
npm run type-check

# Run linting
npm run lint
```

### Testing and Quality Assurance
```bash
# Test MkDocs build
mkdocs build --site-dir test-site

# Test React build and linting (in react/ directory)
npm run build && npm run type-check && npm run lint
```

### Kubernetes Deployment (K3s)
```bash
# Create namespace
kubectl create namespace ai-workloads

# Deploy applications
kubectl apply -f k3s-deployment/ -n ai-workloads

# Check deployment status
kubectl get all -n ai-workloads
```

## Key Application Types

### Fractal Generators
- **Mandelbrot & Julia Sets**: Complex number iterations (`mandelbrot.py`, `julia.py`)
- **Barnsley Ferns**: Iterated function systems (`notebooks/ferns.ipynb`)
- **Tree Structures**: L-systems and branching patterns (`branching_tree.py`, `tree_roots_3d.py`)
- **Noise Generation**: Brownian motion and pink noise simulations

### Analysis Tools
- **Differential Box Counting**: Fractal dimension analysis (`notebooks/dbc.ipynb`)
- **Dimensionality Studies**: Mathematical analysis of fractal properties
- **Visualization**: 2D/3D plotting with Matplotlib, Plotly, and interactive widgets

## Important Configuration Files

### MkDocs Configuration (`mkdocs.yml`)
- Uses Material theme with custom CSS and JavaScript
- Includes MathJax for mathematical notation
- Configured for Jupyter notebook rendering with `mkdocs-jupyter` plugin
- Navigation structure reflects mathematical progression from theory to applications

### Requirements Files
- Root `requirements.txt`: Documentation and MkDocs dependencies
- `docker/requirements.txt`: Streamlit application dependencies including scientific stack

### Kubernetes Configurations
- GPU-accelerated JupyterLab deployment with NVIDIA device plugin support
- Weaviate vector database for AI workloads
- Persistent volume claims for data storage
- Node selection and tolerations for GPU resources

## Development Patterns

### Streamlit Applications
- Follow pattern of data loading, parameter controls, and visualization
- Use NumPy/SciPy for mathematical computations
- Matplotlib/Plotly for plotting with interactive controls
- Session state management for parameter persistence

### Jupyter Notebooks
- Focus on educational content with mathematical explanations
- Include both theory and practical implementations
- Use interactive widgets for parameter exploration
- Export-ready for documentation inclusion

### React Applications
- TypeScript for type safety with mathematical computations
- Material-UI for consistent component design
- Plotly.js integration for interactive 3D visualizations
- React Router for multi-page navigation
- Mathematical rendering with KaTeX for LaTeX equations
- Custom hooks for fractal computation logic

### Mathematical Content
- Heavy use of LaTeX notation in documentation
- MathJax rendering for equations in web documentation
- KaTeX for React application mathematical rendering
- Consistent mathematical terminology and notation patterns

## Architecture Patterns

### Component Architecture (React)
- Page components in `src/pages/` organized by fractal type
- Reusable visualization components in `src/components/`
- Mathematical utilities in `src/utils/` for fractal algorithms
- Theme management with React Context for dark/light modes
- Type definitions in `src/types/` for external library integrations

### Deployment Architecture
- GitHub Actions CI/CD with automated testing for both MkDocs and React
- Multi-environment builds: development (port 33000), production (GitHub Pages)
- Kubernetes deployments with GPU support for JupyterLab workloads
- Docker containerization for Streamlit applications with scientific Python stack