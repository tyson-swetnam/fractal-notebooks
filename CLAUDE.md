# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Git Commit Policy

**IMPORTANT:** After every successful prompt completion that modifies files, commit the changes immediately:

```bash
git add <modified-files>
git commit -m "<concise description of what was done>"
```

Commit message guidelines:
- Start with a verb: Add, Update, Fix, Remove, Refactor, Implement
- Keep the first line under 72 characters
- Reference the user's request when relevant
- Example: `git commit -m "Add WebGL shader for Julia set visualization"`

This ensures all changes are tracked in git history, allowing context recovery when sessions end or context windows fill.

## Project Overview

Fractal Notebooks is a collection of fractal visualization tools with three main components:
- **MkDocs documentation** (`docs/`) - Published to GitHub Pages
- **React web applications** (`react/`) - TypeScript/React fractal visualizers deployed to `/react` subdirectory
- **Streamlit Python apps** (`apps/`) - Interactive fractal generators using scientific Python stack

## Common Commands

### Documentation (MkDocs)
```bash
pip install -r requirements.txt
python -m mkdocs serve          # Local dev server at http://localhost:8000
mkdocs build --site-dir site    # Production build
```

### React Application
```bash
cd react
npm ci                          # Install dependencies
npm start                       # Dev server at http://localhost:33000
npm run build                   # Production build
npm run type-check              # TypeScript type checking
npm run lint                    # ESLint
npm run test                    # Run Jest tests
```

### Streamlit Applications
```bash
streamlit run apps/mandelbrot.py
streamlit run apps/branching_tree.py
streamlit run apps/julia.py
```

### Docker
```bash
cd docker
docker build -t fractal-app .
docker run -p 8501:8501 fractal-app
```

## Architecture

### React App Structure (`react/src/`)
- Uses HashRouter for GitHub Pages compatibility
- **Pages organized by category:**
  - `pages/fractals-1d-2d-3d/` - Mandelbrot, Julia, Brownian, Conway, Noise, PinkNoise, Waves
  - `pages/branching-architectures/` - DLA, Fern, Tree, Pythagoras, TreeRoots3D
  - `pages/riemann-zeta-functions/` - Zeta space tiling and 3D visualization
- **Components:** `components/controls/`, `components/layout/`, `components/math/`
- **Utilities:** `utils/` contains WebGL implementations for Mandelbrot/Julia (performance), noise generators, and theme configuration
- **Theming:** Custom ThemeContext with light/dark/system modes, persisted to localStorage, integrated with MUI
- **Visualization libraries:** D3, Plotly, KaTeX for math rendering

### Streamlit Apps (`apps/`)
- Each `.py` file is self-contained and runnable independently
- Uses NumPy, Matplotlib, Plotly, SciPy, Numba for computation
- Generated GIFs/images stored locally during runtime

### Documentation (`docs/`)
- MkDocs Material theme with custom color scheme (`fractals` palette)
- Jupyter notebooks embedded via `mkdocs-jupyter` plugin
- MathJax for LaTeX equation rendering
- Notebooks in `docs/notebooks/` cover DLA, ferns, fractals, DBC, Riemann zeta functions

### Kubernetes Deployment (`k3s-deployment/`)
- JupyterLab and Weaviate deployments with persistent storage
- NVIDIA device plugin for GPU workloads
- Local-path storage class configuration

## CI/CD

GitHub Actions deploys both MkDocs and React to GitHub Pages on push to `main`:
- MkDocs builds to root
- React builds to `/react` subdirectory with `PUBLIC_URL=/fractal-notebooks/react`
- PR checks run type-check and lint for React, build test for MkDocs

## Key Dependencies

**React:** React 18, MUI 5, D3 7, Plotly, react-router-dom 6, TypeScript 4.9, KaTeX
**Python (docs):** mkdocs-material, mkdocs-jupyter, mkdocstrings, pymdown-extensions
**Python (apps):** streamlit, numpy, matplotlib, plotly, scipy, numba, pillow, imageio
