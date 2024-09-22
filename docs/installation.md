# Creating a Python Environment

[Download `pytorch-gpu.yaml`](notebooks/pytorch-gpu.yaml)

## Install Mini-conda and Mamba

### Mac

1. Download the Miniconda installer for macOS from the [official website](https://docs.conda.io/en/latest/miniconda.html).
2. Open a terminal and run the following command to install Miniconda:
    ```bash
    bash Miniconda3-latest-MacOSX-x86_64.sh
    ```
3. Follow the prompts to complete the installation.
4. Install Mamba by running:
    ```bash
    conda install mamba -n base -c conda-forge
    ```

### Windows

1. Download the Miniconda installer for Windows from the [official website](https://docs.conda.io/en/latest/miniconda.html).
2. Run the installer and follow the prompts to complete the installation.
3. Open the Anaconda Prompt from the Start Menu.
4. Install Mamba by running:
    ```bash
    conda install mamba -n base -c conda-forge
    ```

### Ubuntu Linux

1. Download the Miniconda installer for Linux from the [official website](https://docs.conda.io/en/latest/miniconda.html).
2. Open a terminal and run the following command to install Miniconda:
    ```bash
    bash Miniconda3-latest-Linux-x86_64.sh
    ```
3. Follow the prompts to complete the installation.
4. Install Mamba by running:
    ```bash
    conda install mamba -n base -c conda-forge
    ```

## Using Conda (Mamba)

```bash
git clone https://github.com/tyson-swetnam/fractal-notebooks
cd notebooks
mamba env create -f pytorch-gpu.yaml
## Using Conda  (Mamba)

```bash
git clone https://github.com/tyson-swetnam/fractal-notebooks
cd notebooks
mamba env create -f pytorch-gpu.yaml

```

## Ensuring CUDA is Installed

To leverage GPU acceleration with PyTorch, you need to ensure that CUDA is installed on your machine. Follow the steps below for your operating system:

### Mac

CUDA is not natively supported on macOS. You will need to use a Linux or Windows machine for CUDA support.

### Windows

1. Visit the [NVIDIA CUDA Toolkit website](https://developer.nvidia.com/cuda-downloads).
2. Select your operating system, architecture, and version.
3. Download and run the installer.
4. Follow the prompts to complete the installation.
5. Verify the installation by running the following command in the Command Prompt:
    ```bash
    nvcc --version
    ```

### Ubuntu Linux

1. Visit the [NVIDIA CUDA Toolkit website](https://developer.nvidia.com/cuda-downloads).
2. Select your operating system, architecture, and version.
3. Follow the instructions provided for your specific configuration.
4. After installation, verify the installation by running:
    ```bash
    nvcc --version
    ```

### Verifying CUDA Installation in Python

After installing CUDA, you can verify that PyTorch can access the GPU by running the following Python code:

```python
import torch
print(torch.cuda.is_available())
```