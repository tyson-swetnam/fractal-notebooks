---
type: Index
title: Notebooks
description: >-
  How the Jupyter notebooks of this project are published as pre-rendered pages,
  which conda environments run them, and the catalogue of the 18 rendered
  notebooks: Part I chapters, Part II methods and results, fractal
  demonstrations and Fractal RAG examples.
resource: https://tyson-swetnam.github.io/fractal-notebooks/notebooks/
tags: [notebook, jupyter, part-i, part-ii, rag]
generated:
  by: claude-code/claude-fable-5-1
  at: "2026-10-24T00:00:00Z"
status: stable
---

# Notebooks

Jupyter notebooks carry the computational side of this project: the figures of the Part I
chapters are produced in them, the Part II manuscript's equations and tables are re-derived
in them, and the fractal generators that the text describes are implemented in them.
Eighteen notebooks are published here as rendered pages. The research notebooks that are
not published (lidar canopy analyses, GPU experiments, reviewer companions, work in
progress) are catalogued on [Research Notebooks](research.md) with links to GitHub and
nbviewer.

## How notebooks are published

- **Pre-rendered from stored outputs.** Each page is generated from the committed `.ipynb`
  by `scripts/render_notebooks.py` (nbconvert); nothing executes at build time, so the
  outputs you see are the ones saved in the notebook on the date given in the page banner.
- **Static figures only.** Matplotlib figures are extracted as images. Plotly figures appear
  as the PNG snapshot saved with them; where none was saved, a note links to nbviewer.
  `ipywidgets` controls (sliders, interactive plots) cannot run in a static page and are
  replaced by an italic *Interactive widget* note. A cell that raised an exception is shown
  as a failure admonition with the exception name and message, not a traceback.
- **Every page links its source.** The banner at the top of each notebook page links the
  `.ipynb` on GitHub, on nbviewer and in Google Colab, plus the raw file; the same links
  are in the page's frontmatter (`notebook.source`, `notebook.raw`, `notebook.nbviewer`,
  `notebook.colab`) together with cell, figure and error counts. The notebooks themselves
  are not hosted on this site.
- **Pages are committed.** The rendered Markdown and the extracted images live in the
  repository next to the notebooks and are drift-checked in CI, so a notebook change that
  is not re-rendered fails the build.

## Environments

| Environment file | Env / kernel name | Stack | Used by |
|---|---|---|---|
| [`environments/fractal-foundations-gpu.yml`](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/environments/fractal-foundations-gpu.yml){target=_blank} | `fractal-foundations-gpu` | Python 3.10, CUDA 12.2 toolkit, PyTorch, CuPy, PyCUDA, Numba, NumPy, SciPy, Matplotlib, Plotly, ipywidgets, OpenCV | The fractal demonstrations (`dla`, `fractal_generators`, `dbc`) and the GPU research notebooks; targets NVIDIA driver 535.x |
| [`environments/3dep-environment.yml`](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/environments/3dep-environment.yml){target=_blank} | `3dep` | Python 3.11, PDAL, GDAL, rasterio, rioxarray, geopandas, rio-cogeo, ipyleaflet, py3dep | The lidar and canopy-height-model notebooks (3DEP, Barro Colorado Island, Sierra Nevada) |
| [`docs/notebooks/streamlit-plotly.yaml`](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/streamlit-plotly.yaml){target=_blank} | `streamlit-plotly` | Python 3.11, Streamlit, Plotly, Numba, NumPy, SciPy, Matplotlib, ipywidgets | `fractal_generators` and the Streamlit apps |

The Part I chapter notebooks and the Part II methods and results notebooks need only the
scientific Python stack (NumPy, SciPy, Matplotlib, SymPy, Numba) and run on CPU in any of
these environments or in Colab.

```bash
mamba env create -f environments/fractal-foundations-gpu.yml
mamba activate fractal-foundations-gpu
python -m ipykernel install --user --name fractal-foundations-gpu
jupyter lab docs/notebooks
```

To run a notebook in Google Colab, open its page here and use the Colab link in the banner,
or replace `github.com` with `colab.research.google.com/github` in its GitHub URL.

## Part I chapter notebooks

Companion notebooks to the [Foundations](../foundations/index.md) chapters; the figures are
the ones used in the chapters.

| Notebook | Chapter | What it does | Status |
|---|---|---|---|
| [Chapter 1: History of Fractal Mathematics](foundations/1_history.md) | [History](../foundations/history.md) | Constructs the classical fractals in historical order: Cantor set, Koch snowflake, Sierpinski triangle and carpet, Weierstrass function, Julia and Mandelbrot sets, with a summary table of their dimensions | 6 figures; executed. One cell raises a `ValueError` in the Sierpinski carpet routine (the figure still renders) and the Weierstrass cell was never run |
| [Chapter 2: Mathematical Foundations of Fractals](foundations/2_mathematics.md) | [Mathematics](../foundations/mathematics.md) | Topological versus fractal dimension, box-counting and differential box-counting, power laws and scaling relations, the Hurst exponent and fractional Brownian motion, lacunarity | 8 figures; executed |
| [Chapter 3: Fractal Dimensionality (1D through 4D)](foundations/3_dimensionality.md) | [Dimensionality](../foundations/dimensionality.md) | Fractals in one to four dimensions: fBm traces and Cantor dust, fractional Brownian surfaces and tilings, the Menger sponge, DLA and branching, time-evolving fractals | 9 figures; executed |
| [Chapter 4: Zeta Space Tilings](foundations/4_zeta_space.md) | [History §1.6](../foundations/history.md#16-modern-developments-complex-dimensions-and-spectral-geometry) (complex dimensions) | The Riemann zeta function, single-shape and multi-shape zeta tilings, the effect of the exponent p, and the connection to Apollonian gaskets | 5 figures; executed (CPU only) |

## Fractal demonstrations

Stand-alone notebooks that implement the generators discussed across Part I.

| Notebook | What it does | Environment | Status |
|---|---|---|---|
| [Diffusion Limited Aggregation (DLA)](foundations/dla.md) | Random-walk DLA with Numba, from the Witten-Sander model to its biological look-alikes: E. coli colonies in agar, stromatolites on a tidal flat, branching bryophytes, radial lichens, and L-systems for fruticose lichen morphology | `fractal-foundations-gpu` (runs on CPU) | 16 figures; executed. Two Plotly figures and two widgets are shown as placeholders |
| [Foundations of Fractal Geometry](foundations/fractals.md) | Quick tour of the essential constructions: the Cantor set (1D), Sierpinski triangle (2D) and Menger sponge (3D), fractional Brownian motion as the self-affine example, and a dimension reference table | scientific Python stack | 4 figures; re-executed 2026-10-24 |
| [Self-Affine Fractal Generators](foundations/fractal_generators.md) | Recursive branching trees: 2D trees drawn with Matplotlib under ipywidgets sliders for depth, branch angle, length and width factors, then 3D trees built from tapered-cylinder meshes and rendered with Plotly; almost entirely code (one markdown cell) | `streamlit-plotly` | 7 figures; executed. Plotly figures are shown as their PNG snapshots, the 7 widgets as placeholders |
| [Riemann Zeta Space Tiling (interactive)](foundations/zeta_space.md) | Fills a plane with circles, squares, triangles or random polygons whose areas follow A0 / i^p, so that the total converges to A0 ζ(p); ipywidgets controls for the shape set, plane area, exponent p, shape count and orientation. The interactive precursor of the Chapter 4 notebook | scientific Python stack | widget-only outputs, no static figures (marked `draft`); the sliders are shown as placeholders, so run it locally or read the Chapter 4 notebook for the figures |

## Part II notebooks

Companion notebooks to the [Metabolic Scaling](../metabolic-scaling/index.md) manuscript.
Every cell ran in order; each computation is tagged `[COMPUTED]` (reproduced in the
notebook) or `[ASSERTED]` (taken from the literature or the manuscript).

Methods, accompanying the [Methods](../metabolic-scaling/methods.md) section:

| Notebook | What it does | Status |
|---|---|---|
| [MST and Allometric Relationships](metabolic-scaling/methods/1_mst_allometry.md) | The allometric power law (Eq. 9), Kleiber's 3/4 law, and the self-similar versus self-affine framing of the WBE model | 1 figure; executed |
| [Branching Ratios and the Space-Filling Dimension](metabolic-scaling/methods/2_branching_ratios.md) | Branching ratios (Eq. 10), the space-filling Hausdorff dimension D = ln n / ln(1/γ), the metabolic exponent θ = D/(D+1) = 3/4, and a recursive bifurcating tree with WBE ratios | 1 figure; executed |
| [Volume and Mass-Dimension Predictions](metabolic-scaling/methods/3_volume_mass_dimension.md) | Volume relations (Eqs. 11 to 13), the projected-area box-counting argument (Eqs. 14 to 18), and the reconciliation of D = 3, d = 3/2 and 4/3, worked symbolically with SymPy | text output only (symbolic); executed |
| [DBC and the FracLac Protocol](metabolic-scaling/methods/4_dbc_fraclac.md) | Differential box-counting from scratch (Sarkar and Chaudhuri), fBm surfaces of known dimension D = 3 − H, the FracLac protocol used in the paper, and one log-log DBC regression | 1 figure; executed |

Results, accompanying the [Results](../metabolic-scaling/results.md) section:

| Notebook | What it does | Status |
|---|---|---|
| [Synthetic Fractal Dimensions](metabolic-scaling/results/1_synthetic_dimensions.md) | Regenerates the synthetic fractals of Table 1 and recomputes their box-counting and mass dimensions and lacunarity against the published values | 3 figures; executed |
| [Observed Leaf and Branch / Root Mass Dimensions](metabolic-scaling/results/2_observed_leaf_branch_root.md) | Summary statistics for the published Tables 2 and 3, a method demonstration on synthetic proxies, and the observed dimensions against the d = 3/2 prediction | 3 figures; executed |
| [Forest Canopy Dimensions and Statistical Validation](metabolic-scaling/results/3_canopy_statistical_validation.md) | Group statistics for Table 4, one-sample t-tests and a TOST equivalence test against d = 3/2, and a combined forest plot | 1 figure; executed |

## Fractal RAG examples

Code-only pages: the notebooks were never executed because they need a running Weaviate
instance and the `fractal_rag` package (see [Local Setup](../fractal-rag/local-setup.md)).

| Notebook | What it does |
|---|---|
| [01 — Quickstart: Connect and First Query](../fractal-rag/notebooks/01_quickstart.md) | Connect to Weaviate, sanity-check the collections, browse the concept ontology, run a first hybrid search and pull the full content of a hit |
| [02 — Hybrid Search Patterns](../fractal-rag/notebooks/02_hybrid_search.md) | How `target_vector` and `alpha` shift the keyword and vector balance, filtering by source type and by year, and `near_object` queries for more-like-this retrieval |
| [03 — Concept Ontology](../fractal-rag/notebooks/03_concept_ontology.md) | List concepts by domain, search definitions semantically, find every artifact that references a concept, and sanity-check the tagging quality |

## Research notebooks

Seventy-three further notebooks live in the repository but are not rendered here: the 3DEP
canopy-height-model workflows for 18 US forest sites, the Barro Colorado Island and Sierra
Nevada lidar analyses, the reviewer companions to the Part II manuscript, the five
metabolic-scaling tutorials, GPU DLA experiments, the Blender point-cloud tools, and three
notebooks that are still work in progress. [Research Notebooks](research.md) lists each
one with its environment, execution state, and GitHub and nbviewer links.

## Adding a notebook to the site

1. Commit the `.ipynb` with its outputs saved (figures as PNG; keep interactive outputs to
   a minimum).
2. Add a `[[notebook]]` entry to `scripts/notebooks.toml` (title, description, tags,
   companion page, environment, date) and a nav entry in `zensical.toml`.
3. Run `python scripts/render_notebooks.py` and commit the generated page together with
   its `_files/` directory.
