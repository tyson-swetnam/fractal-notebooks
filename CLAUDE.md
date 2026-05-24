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
- **Fractal RAG stack** (`fractal_rag/`) - Weaviate-backed retrieval + MCP server. Design spec at `docs/superpowers/specs/2026-05-23-fractal-rag-agent-design.md`.

## Using the fractal-explorer subagent

This repo ships a custom subagent (`.claude/agents/fractal-explorer.md`) and an MCP wiring (`.mcp.json`) that connects Claude Code to a local Weaviate index over the Constellate JSONL corpus, Jupyter notebooks, and MkDocs markdown.

Bring it up:
```bash
# 1. K3s manifests under k3s-deployment/ define Weaviate 1.35 + a
#    text2vec-transformers (Arctic-embed-l-v2.0) GPU sidecar.
kubectl apply -f k3s-deployment/

# 2. Install + bootstrap the RAG package
cd fractal_rag && pip install -e ".[dev,parsers]"
fractal-rag schema bootstrap
fractal-rag pull            # gocmd-backed iRODS sync (one-time, ~30 GB)
fractal-rag ingest --source all

# 3. In Claude Code, ask questions; the `fractal-explorer` agent will
#    pick up the .mcp.json wiring automatically and answer with citations.
```
The agent is read-only by design — it only retrieves and synthesizes.

## Common Commands

### Documentation (MkDocs)
```bash
pip install -r requirements.txt
python -m mkdocs serve          # Local dev server at http://localhost:8000
mkdocs build --site-dir site    # Production build
```

### React Application (Vite)
```bash
cd react
npm ci                          # Install dependencies
npm start                       # Dev server at http://localhost:33000
npm run build                   # Production build
npm run preview                 # Preview production build
npm run type-check              # TypeScript type checking
npm run lint                    # ESLint
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
- React (Vite) builds to `/react` subdirectory with base path configured in `vite.config.ts`
- PR checks run type-check and lint for React, build test for MkDocs

## Key Dependencies

**React:** React 18, Vite 7, MUI 5, D3 7, Plotly, react-router-dom 6, TypeScript 5, KaTeX, ESLint 9
**Python (docs):** mkdocs-material, mkdocs-jupyter, mkdocstrings, pymdown-extensions
**Python (apps):** streamlit, numpy, matplotlib, plotly, scipy, numba, pillow, imageio
