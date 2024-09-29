# Setup

# Requirements

To run the example applications,  you will need to install a Python virtual environment or use a Python package manager. We recommend using `pip` or `conda` environments with `mamba` solvers.

```bash
cd apps
pip install requirements.txt
```

1. **Creating a `conda` environment**

```bash
cd notebooks
mamba env create -f streamlit-plotly.yaml

```

2. **Activate the Conda Environment:**

    ```bash
    mamba activate fractal-env
    ```

3. **Install Jupyter and Create a Jupyter Kernel:**

    ```bash
    mamba install -c conda-forge jupyterlab ipykernel
    python -m ipykernel install --name fractal-env --display-name "Fractal Env"
    ```

These steps will create a Conda environment, activate it, and set up a Jupyter kernel named "Fractal Env" that you can use in Jupyter notebooks.