---
type: Reference
title: Research Notebooks
description: >-
  Catalogue of the 73 research notebooks not rendered on this site: 3DEP canopy
  height models for 18 US forests, Barro Colorado Island and Sierra Nevada lidar,
  Part II reviewer companions, metabolic scaling tutorials, GPU and Blender DLA
  work, with execution state and GitHub and nbviewer links.
resource: https://tyson-swetnam.github.io/fractal-notebooks/notebooks/research/
tags: [notebook, jupyter, lidar, canopy-height-model, 3dep, forest-ecology]
sources:
  - id: ot-3dep-workflows
    resource: https://github.com/OpenTopography/OT_3DEP_Workflows
    title: OpenTopography OT_3DEP_Workflows, the upstream 3DEP tutorial notebooks
  - id: usgs-3dep
    resource: https://www.usgs.gov/3d-elevation-program
    title: USGS 3D Elevation Program (3DEP)
  - id: usgs-lidar-ept
    resource: https://github.com/hobuinc/usgs-lidar
    title: USGS 3DEP lidar point clouds as Entwine Point Tiles on AWS
  - id: smithsonian-als-panama-2023
    resource: https://smithsonian.dataone.org/datasets/ALS_Panama_2023/
    title: Smithsonian Tropical Research Institute ALS Panama 2023 (Barro Colorado Island lidar)
generated:
  by: claude-code/claude-fable-5-1
  at: "2026-10-24T00:00:00Z"
status: stable
---

# Research Notebooks

The repository holds 91 Jupyter notebooks. Eighteen are rendered as pages (see
[Notebooks](index.md)); the 73 listed here are not, because they are research in progress,
need a GPU, a CyVerse data mount or private credentials to run, or are too heavy for a
static site (one is 72 MB). They remain readable:

- **GitHub** shows a notebook with its stored outputs:
  `https://github.com/tyson-swetnam/fractal-notebooks/blob/main/<path>`
- **nbviewer** renders it, including Plotly and HTML outputs:
  `https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/<path>`
- **Colab** opens it for execution:
  `https://colab.research.google.com/github/tyson-swetnam/fractal-notebooks/blob/main/<path>`

Paths below are relative to `docs/notebooks/` in the repository. The execution state is what
the stored outputs show, as inventoried on 2026-10-24: "executed 9/28" means 9 of 28 code
cells have saved outputs. The environments are described on the
[Notebooks](index.md#environments) page.

## 3DEP canopy height models

`3dep/`: canopy height models (CHM = DSM − DTM) from USGS 3D Elevation Program lidar for US
forest research sites, and fractal analysis of the resulting surfaces. `forest_sites.yaml`
defines 17 sites (bounding box, expected maximum height, priority) and the processing rules:
0.333 m resolution at 12 or more points per m², otherwise 0.5 m; DSM = maximum and DTM =
minimum per cell, no smoothing; Cloud-Optimized GeoTIFF output. Point clouds are read
anonymously from the public USGS Entwine Point Tile bucket on AWS, so no credentials are
needed, but the notebooks write to CyVerse Data Store paths (`/home/jovyan/data-store/...`).
Environment: `3dep` ([`environments/3dep-environment.yml`](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/environments/3dep-environment.yml){target=_blank}).
The directory [README](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/3dep/README.md){target=_blank}
documents the site list and the utility modules.

### Workflow notebooks (modified)

| Notebook | What it does | Links | Status |
|---|---|---|---|
| `3dep/modified/1_forest_sites_map` | Interactive ipyleaflet maps of every site with the 3DEP coverage boundaries, to verify site placement and lidar coverage | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/3dep/modified/1_forest_sites_map.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/3dep/modified/1_forest_sites_map.ipynb) | executed 12/25; the outputs are widget maps (no static figure). Shows no 3DEP coverage for `sequoia_giant_forest` and `wind_river` |
| `3dep/modified/2_chm_user_aoi` | Template: PDAL `readers.ept` download, DSM and DTM via `writers.gdal`, CHM by subtraction, COG export; configured for the `monument_canyon_rna` test site | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/3dep/modified/2_chm_user_aoi.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/3dep/modified/2_chm_user_aoi.ipynb) | executed 9/28; ends in a GDAL `RuntimeError` on write |
| `3dep/modified/3_chm_fractal_analysis` | Template: differential box-counting, lacunarity, gap-size distributions, local maxima and topographic correlation of a CHM, testing the nine hypotheses of Part V; the area of interest is drawn with an ipyleaflet DrawControl | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/3dep/modified/3_chm_fractal_analysis.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/3dep/modified/3_chm_fractal_analysis.ipynb) | executed 12/21; 1 figure, 2 widgets |
| `3dep/modified/chm_forest_sites` | Batch CHM generation for every site in `forest_sites.yaml` | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/3dep/modified/chm_forest_sites.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/3dep/modified/chm_forest_sites.ipynb) | executed 3/16; text output only |
| `3dep/modified/sites/<site_id>/` (36 notebooks) | One `chm_<site_id>` and one `fractal_<site_id>` notebook for each of 18 sites. They are templated copies of `2_chm_user_aoi` and `3_chm_fractal_analysis` written by `generate_site_notebooks.py` with the site name and bounding box swapped in, so they are listed here once rather than as 36 pages | [GitHub directory](https://github.com/tyson-swetnam/fractal-notebooks/tree/main/docs/notebooks/3dep/modified/sites) · [nbviewer directory](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/tree/main/docs/notebooks/3dep/modified/sites/) | 10 sites entirely unexecuted; 8 CHM notebooks stopped after about 10 cells with text output only; the `rocky_mountain_subalpine`, `superior_old_growth` and `white_mountain_northern` fractal notebooks ran nearly end to end (the last ends in a `KeyError`); the `ocala_longleaf` and `redwood_humboldt` fractal notebooks fail with `FileNotFoundError` because their CHM was never produced |

Helper scripts in the same directory, formerly built as pages, are linked on GitHub only:
[`generate_site_notebooks.py`](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/3dep/modified/generate_site_notebooks.py){target=_blank},
[`utils/cog_utils.py`](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/3dep/modified/utils/cog_utils.py){target=_blank},
[`utils/validate_cogs.py`](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/3dep/modified/utils/validate_cogs.py){target=_blank} and
[`utils/update_notebooks_cog.py`](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/3dep/modified/utils/update_notebooks_cog.py){target=_blank}.

### Upstream tutorials (original)

Reference copies of the seven OpenTopography
[OT_3DEP_Workflows](https://github.com/OpenTopography/OT_3DEP_Workflows){target=_blank}
notebooks; `05` is the basis of the modified CHM workflow. They expect Colab (`condacolab`)
or the upstream `3dep` conda environment, and call USGS National Map services as well as the
EPT bucket. The upstream repository is published under the GNU GPL v3.0, so these copies
keep that licence rather than this site's CC BY 4.0; whether they are still byte-identical
to upstream has not been re-checked.

| Notebook | What it does | Links | Status |
|---|---|---|---|
| `3dep/original/01_3DEP_Generate_DEM_User_AOI` | DTM and DSM for a user-drawn area of interest | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/3dep/original/01_3DEP_Generate_DEM_User_AOI.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/3dep/original/01_3DEP_Generate_DEM_User_AOI.ipynb) | executed 6/23; 2 figures, 3 widget maps |
| `3dep/original/02_3DEP_Generate_DEM_USGS_7.5_Quadrangles` | DEMs for USGS 7.5-minute quadrangles | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/3dep/original/02_3DEP_Generate_DEM_USGS_7.5_Quadrangles.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/3dep/original/02_3DEP_Generate_DEM_USGS_7.5_Quadrangles.ipynb) | executed 2/25; 2 figures |
| `3dep/original/03_3DEP_Generate_DEM_USGS_HUCs` | DEMs for hydrologic unit (watershed) boundaries | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/3dep/original/03_3DEP_Generate_DEM_USGS_HUCs.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/3dep/original/03_3DEP_Generate_DEM_USGS_HUCs.ipynb) | executed 2/25; 2 figures |
| `3dep/original/04_3DEP_Generate_DEM_Corridors` | DEMs along linear corridors | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/3dep/original/04_3DEP_Generate_DEM_Corridors.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/3dep/original/04_3DEP_Generate_DEM_Corridors.ipynb) | executed 2/26; 2 figures |
| `3dep/original/05_3DEP_Generate_Canopy_Height_Models_User_AOI` | Canopy height model for a user area of interest; basis of `2_chm_user_aoi` | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/3dep/original/05_3DEP_Generate_Canopy_Height_Models_User_AOI.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/3dep/original/05_3DEP_Generate_Canopy_Height_Models_User_AOI.ipynb) | executed 1/33; 1 figure |
| `3dep/original/06_3DEP_Topographic_Differencing` | Elevation change between two lidar acquisitions | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/3dep/original/06_3DEP_Topographic_Differencing.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/3dep/original/06_3DEP_Topographic_Differencing.ipynb) | executed 3/30; 2 figures |
| `3dep/original/07_3DEP_Generate_Colorized_PointClouds` | Point clouds colourised with NAIP imagery | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/3dep/original/07_3DEP_Generate_Colorized_PointClouds.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/3dep/original/07_3DEP_Generate_Colorized_PointClouds.ipynb) | not executed (0/14) |

## Smithsonian: Barro Colorado Island

`smithsonian/`: fractal analysis of the 0.5 m canopy height model of Barro Colorado Island,
Panama, from the Smithsonian Tropical Research Institute's
[ALS Panama 2023](https://smithsonian.dataone.org/datasets/ALS_Panama_2023/){target=_blank}
airborne laser scanning campaign. The notebooks read the 1.1 GB CHM GeoTIFF from a CyVerse
`~/data-store` mount (not included in the repository) and ran on CyVerse on 2025-12-24 and
2025-12-25. Environment: `3dep`. The project plan is kept in the repository at
[`notes/notebooks/smithsonian/PLAN.md`](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/notes/notebooks/smithsonian/PLAN.md){target=_blank}.

| Notebook | What it does | Links | Status |
|---|---|---|---|
| `smithsonian/1_chm_exploration` | Load and explore the BCI CHM: height distributions, canopy structure and subsets of the island | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/smithsonian/1_chm_exploration.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/smithsonian/1_chm_exploration.ipynb) | executed 16/20 (the 4 closing cells never ran); 4 figures |
| `smithsonian/2_fractal_analysis` | Box-counting and differential box-counting dimensions of the BCI canopy surface | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/smithsonian/2_fractal_analysis.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/smithsonian/2_fractal_analysis.ipynb) | executed 18/22; 4 figures |
| `smithsonian/3_fractal_hypotheses` | The complete hypothesis-testing battery of `3_chm_fractal_analysis` applied to BCI | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/smithsonian/3_fractal_hypotheses.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/smithsonian/3_fractal_hypotheses.ipynb) | executed 14/20; text output only |

## Sierra Nevada Giant Forest

`sierra-nevada/`: planned analysis of the 2022 USGS 3DEP lidar (`CA_SierraNevada_B22`) over
the Giant Forest in Sequoia National Park, following the BCI workflow but starting from raw
LAZ tiles. Two of the five planned notebooks exist and neither has been executed (their
download and processing cells are commented out, "uncomment to run"). Needs PDAL and GDAL
(`3dep` environment). Plan:
[`notes/notebooks/sierra-nevada/PLAN.md`](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/notes/notebooks/sierra-nevada/PLAN.md){target=_blank}
(status: not started).

| Notebook | What it does | Links | Status |
|---|---|---|---|
| `sierra-nevada/1_download_data` | Download LAZ point-cloud tiles for the Giant Forest area of interest from the USGS staged-products server | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/sierra-nevada/1_download_data.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/sierra-nevada/1_download_data.ipynb) | not executed |
| `sierra-nevada/2_laz_to_raster` | PDAL and GDAL pipeline from LAZ to DEM, DSM and CHM rasters | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/sierra-nevada/2_laz_to_raster.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/sierra-nevada/2_laz_to_raster.ipynb) | not executed |

## Reviewer companions (Part II)

`metabolic-scaling/review/`: seven notebooks that accompany a critical review of the Part II
manuscript, [`REVIEW_metabolic-scaling.md`](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/REVIEW_metabolic-scaling.md){target=_blank}
at the repository root. Unlike the tutorials below, they exist to test the paper's claims
section by section. They share estimators, the data pull and the equivalence test through
[`fractal_review_utils.py`](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/metabolic-scaling/review/fractal_review_utils.py){target=_blank},
so launch Jupyter from this folder. The empirical cells fetch the author's private CyVerse
iRODS collection and need your own credentials (`gocmd init`); without access they fall back
to deterministic synthetic objects and say so. The stored outputs show the synthetic path
only. Environment: the scientific Python stack (the directory README points at
`fractal-foundations-gpu`).

| Notebook | What it checks | Links | Status |
|---|---|---|---|
| `metabolic-scaling/review/abstract_companion` | Turns the abstract's claims into falsifiable hypotheses; reviewer scorecard; CyVerse bootstrap | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/metabolic-scaling/review/abstract_companion.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/metabolic-scaling/review/abstract_companion.ipynb) | executed 4/4 |
| `metabolic-scaling/review/introduction_companion` | The missing estimator-bias control: fBm of known D = 3 − H measured with both estimators | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/metabolic-scaling/review/introduction_companion.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/metabolic-scaling/review/introduction_companion.ipynb) | executed 4/4; 1 figure |
| `metabolic-scaling/review/methods_companion` | Equation-by-equation re-derivation; flags broken or missing equations; reconciles 3 versus 3/2 versus 4/3 | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/metabolic-scaling/review/methods_companion.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/metabolic-scaling/review/methods_companion.ipynb) | executed 5/5 |
| `metabolic-scaling/review/results_companion` | Binary versus grayscale dimension, synthetic controls, TOST equivalence test, empirical data pull | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/metabolic-scaling/review/results_companion.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/metabolic-scaling/review/results_companion.ipynb) | executed 6/6 |
| `metabolic-scaling/review/discussion_companion` | DLA, Eden and KPZ growth versus self-affine surfaces; the unfalsifiable maximum-entropy-production claim; the 3/4 versus 2/3 omission | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/metabolic-scaling/review/discussion_companion.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/metabolic-scaling/review/discussion_companion.ipynb) | executed 4/4; 1 figure |
| `metabolic-scaling/review/conclusion_companion` | Decision table: what each conclusion still needs to be true | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/metabolic-scaling/review/conclusion_companion.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/metabolic-scaling/review/conclusion_companion.ipynb) | executed 3/3 |
| `metabolic-scaling/review/references_companion` | Programmatic DOI and citation audit of the reference list | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/metabolic-scaling/review/references_companion.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/metabolic-scaling/review/references_companion.ipynb) | executed 3/3 |

## Metabolic scaling tutorials

`metabolic-scaling/1_*` to `5_*`: five complete teaching notebooks (2025-12-24) on metabolic
scaling theory. Every cell ran in order with no errors, and each has four to seven figures.
They are not in the site navigation because the Part II
[methods and results notebooks](index.md#part-ii-notebooks) superseded them as the
manuscript's companions. Environment: the scientific Python stack (`python3` kernel; any of
the project environments).

| Notebook | What it does | Links | Status |
|---|---|---|---|
| `metabolic-scaling/1_introduction` | Introduction to Metabolic Scaling Theory: allometry, self-similarity versus self-affinity, and a timeline of the key discoveries | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/metabolic-scaling/1_introduction.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/metabolic-scaling/1_introduction.ipynb) | executed 8/9; 7 figures |
| `metabolic-scaling/2_mst_equations` | The mathematical framework: allometric power laws, Kleiber's law, and the WBE model of branching networks | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/metabolic-scaling/2_mst_equations.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/metabolic-scaling/2_mst_equations.ipynb) | executed 7/8; 7 figures |
| `metabolic-scaling/3_branching_analysis` | Branching network analysis: synthetic branching networks, branching statistics, volume distribution and asymmetry, and biologically realistic networks | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/metabolic-scaling/3_branching_analysis.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/metabolic-scaling/3_branching_analysis.ipynb) | executed 7/8; 5 figures |
| `metabolic-scaling/4_differential_box_counting` | Differential box-counting for self-affine fractals: standard box-counting on binary images versus differential box-counting on grayscale test images | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/metabolic-scaling/4_differential_box_counting.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/metabolic-scaling/4_differential_box_counting.ipynb) | executed 7/7; 6 figures |
| `metabolic-scaling/5_empirical_validation` | Empirical validation: predicted dimensions by growth form, why DBC on grayscale images gives D of about 2.1, and biologically realistic tree architecture generators | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/metabolic-scaling/5_empirical_validation.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/metabolic-scaling/5_empirical_validation.ipynb) | executed 9/10; 4 figures |

## GPU research notebooks

`foundations/`: DLA and growth-model experiments that need the `fractal-foundations-gpu`
kernel (CUDA 12.2, CuPy, PyCUDA, Numba). Design notes for the CUDA work are kept in the
repository under
[`notes/notebooks/foundations/`](https://github.com/tyson-swetnam/fractal-notebooks/tree/main/notes/notebooks/foundations){target=_blank}
(`dla_cuda_plan.md`, `PLAN_lichen_growth_updates.md`, `lichen_dla_claude.md`).

| Notebook | What it does | Links | Status |
|---|---|---|---|
| `foundations/3d_dla` | 3D diffusion-limited aggregation as a model of fruticose lichens, with Plotly 3D renderings | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/foundations/3d_dla.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/foundations/3d_dla.ipynb) | executed 12/17; 2 figures, 4 Plotly figures without a static fallback, 1 widget |
| `foundations/dla_cuda_offgrid` | Phase 1 of an off-lattice CUDA DLA implementation aiming at million-particle clusters and lichen morphologies (Usnea, Cladonia, Ramalina, crustose) | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/foundations/dla_cuda_offgrid.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/foundations/dla_cuda_offgrid.ipynb) | executed 68/68; 72 MB of Plotly and HTML output with no PNG fallback. Research in progress: the morphologies still grow spherically (see the plan) |
| `foundations/dla_slime_mold` | DLA patterns in bacterial colonies and the slime mold Physarum polycephalum, after Fujikawa and Matsushita | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/foundations/dla_slime_mold.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/foundations/dla_slime_mold.ipynb) | executed 7/16; 6 figures |
| `foundations/dla_slime_mold_cuda` | CuPy-accelerated versions of the same models, 10 to 100 times faster than the CPU implementations | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/foundations/dla_slime_mold_cuda.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/foundations/dla_slime_mold_cuda.ipynb) | executed 8/12; 5 figures |
| `foundations/yeast_colony_simulation` | Vector-based cellular model comparing normal (dispersing) and snowflake (clustering) Saccharomyces cerevisiae colony growth | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/foundations/yeast_colony_simulation.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/foundations/yeast_colony_simulation.ipynb) | executed 9/15; 2 figures plus 3 JavaScript animations (23 MB) |

## Blender point-cloud tools

`foundations/blender/`: 3D DLA simulated with Blender's Geometry Nodes and rendered with
Cycles. Six Python scripts run inside Blender (scene setup, advanced features, export to
NumPy, PLY, OBJ and CSV, batch and gallery rendering); the notebook analyses the exported
point clouds. The user-facing guide is [Blender DLA](../applications/blender-dla.md); the
directory [README](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/foundations/blender/README.md){target=_blank}
documents the scripts and presets.

| Notebook | What it does | Links | Status |
|---|---|---|---|
| `foundations/blender/dla_visualization` | Loads a point cloud exported by `dla_export.py` (`/tmp/dla_export.npz`) and analyses and visualises it with Plotly | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/foundations/blender/dla_visualization.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/foundations/blender/dla_visualization.ipynb) | executed 7/15; 3 figures, 2 Plotly figures without a static fallback. Needs Blender output to run |

Scripts (GitHub):
[`dla_blender_setup.py`](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/foundations/blender/dla_blender_setup.py){target=_blank},
[`dla_advanced_features.py`](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/foundations/blender/dla_advanced_features.py){target=_blank},
[`dla_export.py`](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/foundations/blender/dla_export.py){target=_blank},
[`dla_batch_render.py`](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/foundations/blender/dla_batch_render.py){target=_blank},
[`dla_example_renders.py`](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/foundations/blender/dla_example_renders.py){target=_blank},
[`dla_gallery_render.py`](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/foundations/blender/dla_gallery_render.py){target=_blank}.

## Work in progress

`foundations/`: three notebooks that do not run cleanly and stay unpublished until fixed.
Two notebooks that older links point at are gone: `torch_test.ipynb` (a PyTorch GPU smoke
test) and `old_dla.ipynb` (superseded by the published [DLA notebook](foundations/dla.md))
were deleted from the repository.

| Notebook | What it does | Links | Environment | Status |
|---|---|---|---|---|
| `foundations/ferns` | Barnsley's fern as an iterated function system and as an example of self-affinity (affine transformations, the fern parameters, the chaos game); the first cell is titled "Setup" | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/foundations/ferns.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/foundations/ferns.ipynb) | `fractal-foundations-gpu` (inline mamba and pip installs) | executed 3/9; `NameError: interact` in cell 5 (the ipywidgets import is missing), duplicated code cells |
| `foundations/dbc` | Differential box-counting: the fractal dimension of grayscale surfaces, with an optional CUDA path and a CPU fallback | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/foundations/dbc.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/foundations/dbc.ipynb) | `fractal-foundations` (`foundations/environment.yml`) | executed 6/12 (12 cells ran; 1 figure; `input()` prompts); the four `input()` calls mean it cannot run headless, and the stored output reads "File not found." |
| `foundations/zeta_3d` | The 3D counterpart of the zeta space tilings: spheres, cubes and tetrahedra with volumes A0 / i^p packed into a volume, with a PyCUDA kernel for the overlap test and a Matplotlib 3D rendering | [GitHub](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/foundations/zeta_3d.ipynb) · [nbviewer](https://nbviewer.org/github/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/foundations/zeta_3d.ipynb) | `pytorch-gpu` plus `pycuda` (no such environment file exists in the repository) | executed 2/6 (5 cells ran; CUDA errors: `nvcc` not found, `NameError: check_overlap_cuda`). An earlier revision, commit `c293f52`, had outputs |
