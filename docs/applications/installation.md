# Installation Guide

This guide covers setting up the development environment for running fractal visualization applications locally.

## Prerequisites

### For React Applications

- **Node.js** (v16 or later)
- **npm** (v8 or later)
- Modern web browser with WebGL support

### For Python Applications

- **Python** (v3.8 or later)
- **pip** or **conda** package manager
- Optional: CUDA-capable GPU for accelerated computation

---

## React Application Setup

### 1. Clone the Repository

```bash
git clone https://github.com/tyson-swetnam/fractal-notebooks
cd fractal-notebooks/react
```

### 2. Install Dependencies

```bash
npm ci
```

### 3. Start Development Server

```bash
npm start
```

The application will be available at `http://localhost:33000`.

### 4. Build for Production

```bash
npm run build
```

### Available Scripts

| Command | Description |
|---------|-------------|
| `npm start` | Start development server |
| `npm run build` | Create production build |
| `npm run type-check` | Run TypeScript type checking |
| `npm run lint` | Run ESLint |
| `npm run test` | Run Jest tests |

---

## Python Environment Setup

### Option 1: Using pip

```bash
cd fractal-notebooks
pip install -r requirements.txt
```

### Option 2: Using Conda with Mamba

1. **Install Miniconda**

    === "macOS"
        ```bash
        curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
        bash Miniconda3-latest-MacOSX-x86_64.sh
        ```

    === "Linux"
        ```bash
        curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
        bash Miniconda3-latest-Linux-x86_64.sh
        ```

    === "Windows"
        Download from [Miniconda website](https://docs.conda.io/en/latest/miniconda.html) and run the installer.

2. **Install Mamba (faster solver)**

    ```bash
    conda install mamba -n base -c conda-forge
    ```

3. **Create Environment**

    ```bash
    cd fractal-notebooks/docs/notebooks
    mamba env create -f streamlit-plotly.yaml
    ```

4. **Activate Environment**

    ```bash
    mamba activate fractal-env
    ```

---

## Running Streamlit Applications

After setting up the Python environment:

```bash
cd apps
streamlit run mandelbrot.py
```

### Available Applications

| File | Description |
|------|-------------|
| `mandelbrot.py` | Interactive Mandelbrot set explorer |
| `julia.py` | Julia set visualization |
| `branching_tree.py` | Self-affine branching tree generator |
| `pythagoras_tree.py` | Pythagoras tree fractal |

---

## Jupyter Notebook Setup

### Install Jupyter Kernel

```bash
mamba activate fractal-env
mamba install -c conda-forge jupyterlab ipykernel
python -m ipykernel install --name fractal-env --display-name "Fractal Env"
```

### Launch JupyterLab

```bash
jupyter lab
```

Navigate to the `docs/notebooks/` directory to access the example notebooks.

---

## GPU Acceleration (Optional)

### CUDA Setup for PyTorch

For GPU-accelerated computation with PyTorch:

=== "Linux/Windows"
    1. Visit [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)
    2. Select your OS and architecture
    3. Follow installation instructions
    4. Verify: `nvcc --version`

=== "macOS"
    CUDA is not supported on macOS. Use Metal Performance Shaders (MPS) with PyTorch 2.0+.

### Verify GPU Access

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"Device count: {torch.cuda.device_count()}")
if torch.cuda.is_available():
    print(f"Device name: {torch.cuda.get_device_name(0)}")
```

---

## Docker Setup

For containerized deployment:

```bash
cd docker
docker build -t fractal-app .
docker run -p 8501:8501 fractal-app
```

---

## Troubleshooting

### Common Issues

**Node.js version mismatch**
```bash
nvm install 18
nvm use 18
```

**Python package conflicts**
```bash
mamba env remove -n fractal-env
mamba env create -f streamlit-plotly.yaml
```

**WebGL not available**
- Update graphics drivers
- Try a different browser
- Check browser WebGL support at [get.webgl.org](https://get.webgl.org)

### Getting Help

- Open an issue on [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/issues)
- Check existing documentation in this guide
