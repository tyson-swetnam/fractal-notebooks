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
- **Comprehensive Documentation** - MkDocs site with LaTeX equations and theory
- **Cloud Deployment** - K3s Kubernetes with GPU support for scalable computation
- **Containerization** - Docker deployment for consistent environments

## 📁 Repository Structure

- **`apps/`** - Streamlit applications for interactive fractal visualization
- **`docs/`** - MkDocs documentation with mathematical content and theory
- **`docs/notebooks/`** - Jupyter notebooks with fractal algorithms and examples
- **`k3s-deployment/`** - Kubernetes configurations for JupyterLab and Weaviate
- **`docker/`** - Docker containerization for Streamlit applications
- **`react/`** - React-based web applications for fractal exploration

## 🚀 Quick Start

### Local Documentation Development
```bash
git clone https://github.com/tyson-swetnam/fractal-notebooks.git
cd fractal-notebooks
pip install -r requirements.txt
python -m mkdocs serve
```
Access at http://localhost:8000

### Run Streamlit Applications
```bash
# Run specific applications
streamlit run apps/mandelbrot.py
streamlit run apps/branching_tree.py
streamlit run apps/julia.py
```

### Docker Deployment
```bash
cd docker/
docker build -t fractal-app .
docker run -p 8501:8501 fractal-app
```

### Kubernetes Deployment
```bash
kubectl create namespace ai-workloads
kubectl apply -f k3s-deployment/ -n ai-workloads
```

## 🔬 Core Technologies

- **Documentation**: MkDocs with Material theme, MathJax for equations
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
- `docs/README.md` - Documentation structure and MkDocs configuration
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
