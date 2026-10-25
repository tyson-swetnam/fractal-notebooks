# Fractal Notebooks

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.

A comprehensive collection of Python applications and Jupyter notebooks for simulating self-affine fractals, combining mathematical visualization, interactive applications, and scientific documentation to explore fractal geometry.

## 🌐 Live Applications

**Interactive React Apps**: [https://tyson-swetnam.github.io/fractal-notebooks/react](https://tyson-swetnam.github.io/fractal-notebooks/react)

**Documentation**: [https://tyson-swetnam.github.io/fractal-notebooks](https://tyson-swetnam.github.io/fractal-notebooks)

## 🎯 Features

- **Interactive Streamlit Applications** - Real-time fractal visualization with parameter controls
- **Jupyter Notebooks** - Educational content with mathematical theory and implementations
- **Research-Grade Tools** - Scientific Python stack for fractal analysis and dimension calculation
- **Comprehensive Documentation** - Zensical site with LaTeX equations, pre-rendered notebooks, and OKF knowledge bundles (plus `llms.txt` and raw Markdown twins for AI agents)
- **Cloud Deployment** - K3s Kubernetes with GPU support for scalable computation
- **Containerization** - Docker deployment for consistent environments

## 📁 Repository Structure

- **`apps/`** - Streamlit applications for interactive fractal visualization
- **`docs/`** - Zensical documentation (an OKF v0.2 bundle) with mathematical content and theory
- **`docs/notebooks/`** - Jupyter notebooks with fractal algorithms and examples
- **`k3s-deployment/`** - Kubernetes configurations for JupyterLab and Weaviate
- **`docker/`** - Docker containerization for Streamlit applications
- **`react/`** - React-based web applications for fractal exploration

## 🚀 Quick Start

### Local Documentation Development
```bash
git clone https://github.com/tyson-swetnam/fractal-notebooks.git
cd fractal-notebooks
uv venv --python 3.11 .venv && uv pip install --python .venv/bin/python -r requirements-docs.txt
bash scripts/build_site.sh --serve   # full pipeline (OKF staging, notebook pages, strict build), then live reload
```
Access at http://localhost:8000

### Run Streamlit Applications
```bash
# Streamlit apps: the 12 apps/*.py files that import streamlit (see apps/README.md)
streamlit run apps/tree_roots_3d.py
# The other scripts (mandelbrot.py, julia.py, branching_tree.py, ...) are plain
# matplotlib/PIL programs that write an image or GIF next to the script
python apps/mandelbrot.py
```

### Docker Deployment
```bash
# from the repository root (the Dockerfile copies apps/)
docker build -f docker/Dockerfile -t fractal-app .
docker run -p 8501:8501 fractal-app
```

### Kubernetes Deployment
```bash
kubectl apply -k k3s-deployment/base                 # Weaviate + GPU embedding sidecar (creates the namespace)
kubectl apply -k k3s-deployment/overlays/dgx-spark   # arm64 DGX Spark: locally built CUDA sidecar
```

## 🔬 Core Technologies

- **Documentation**: Zensical (Material theme, classic variant) with MathJax for equations; OKF v0.2 frontmatter, `llms.txt` and Markdown twins for AI agents
- **Interactive Apps**: Streamlit for web-based fractal visualizations
- **Notebooks**: Jupyter with NumPy, Matplotlib, SciPy scientific stack
- **Deployment**: K3s Kubernetes with GPU support for AI workloads
- **Containerization**: Docker for application packaging and deployment

## 📚 Applications Overview

### Fractal Generators
- **Mandelbrot & Julia Sets**: Complex number iterations
- **Barnsley Ferns**: Iterated function systems
- **Tree Structures**: L-systems and branching patterns
- **Noise Generation**: Brownian motion and pink noise simulations

### Analysis Tools
- **Differential Box Counting**: Fractal dimension analysis
- **Dimensionality Studies**: Mathematical analysis of fractal properties
- **3D Visualizations**: Interactive Plotly and Matplotlib rendering

## 🤝 Contributing

Contributions are welcome! Please see individual folder README files for specific development guidelines:
- `apps/README.md` - Streamlit application development
- `CLAUDE.md` - Documentation architecture, OKF frontmatter convention, and the Zensical build pipeline (`zensical.toml`, `scripts/`)
- `k3s-deployment/README.md` - Kubernetes deployment guide

## 📄 Citation

If you use this work in your research, please cite:

```bibtex
@misc{fractal-notebooks,
  title={Fractal Notebooks: Interactive Platform for Self-Affine Fractal Analysis},
  author={Swetnam, Tyson},
  year={2026},
  url={https://github.com/tyson-swetnam/fractal-notebooks}
}
```

## 📝 License

This project is open source and available under the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).
