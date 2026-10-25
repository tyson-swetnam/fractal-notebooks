---
okf_version: "0.2"
type: Index
title: "Fractal Patterns in Nature: Self-Affinity vs Self-Similarity"
description: >-
  Home page of Fractal Notebooks: Part I foundations of fractal geometry, Parts
  II-V research on self-affine scaling in vascular organisms, rendered Jupyter
  notebooks, React and Streamlit apps, OKF knowledge bundles and a guide for AI
  agents.
resource: https://tyson-swetnam.github.io/fractal-notebooks/
tags: [foundations, research, self-affinity, metabolic-scaling, okf]
generated:
  by: human:tswetnam
  at: "2024-09-22T00:00:00Z"
status: stable
---

# Fractal Patterns in Nature: Self-Affinity vs Self-Similarity

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.

Welcome to the Fractal Notebooks project—an interdisciplinary exploration of fractal geometry in biological systems, from the mathematics of Mandelbrot to the metabolic scaling theory of vascular organisms.

---

## About This Project

Much of the scientific literature describes the fractal-like hierarchical branching networks of vascular organisms as "self-similar." This project examines this terminology and demonstrates why these structures are more accurately described as **self-affine**—scaling differently in different spatial directions.

We link metabolic scaling theory to the structural traits of organisms and propose mechanistic theories for fractal dimensions from single cells to ecosystems.

---

## Site Structure

The site is organised into seven tabs. The original Part numbers are kept in page titles so that cross-references and citations into the manuscripts stay stable.

### [Foundations (Part I)](foundations/index.md)

Educational chapters providing mathematical and historical background:

- [**History of Fractals**](foundations/history.md) — From Cantor to Mandelbrot to modern complex dimensions
- [**Mathematical Foundations**](foundations/mathematics.md) — Hausdorff dimension, box-counting, Hurst exponent
- [**Fractal Dimensionality**](foundations/dimensionality.md) — 1D through 4D fractals with examples
- [**Glossary & Equations**](foundations/glossary.md) — Quick reference for terms and formulas

### Research (Parts II–V)

Four research manuscripts, each with a landing page and sections from Abstract to References; Part II also has supporting notebooks. They are unpublished drafts.

#### [Part II: Metabolic Scaling Theory](metabolic-scaling/index.md)

The core research paper on self-affinity in vascular organisms:

- Distinction between self-similarity and self-affinity
- West-Brown-Enquist (WBE) model derivations
- Empirical validation using differential box-counting
- Tables of fractal dimensions for leaves, branches, and forest canopies

#### [Part III: Spectral Geometry](spectral-geometry/index.md)

Advanced mathematical theory connecting fractals to the Riemann zeta function:

- Fractal strings and geometric zeta functions
- Complex dimensions and log-periodic oscillations
- Applications to algorithmic sorting and spatial indexing
- The "Fractal Riemann Hypothesis"

#### [Part IV: Biological Geometry](biological-geometry/index.md)

Applications of self-affine geometry to biological systems:

- DLA models for lichen, algae, and kelp
- IFS models for ferns and plant architecture
- Crown shyness and Apollonian packing in forest canopies
- Root foraging and spectral dimensions

#### [Part V: Research Hypotheses](hypotheses/index.md)

Preregistration framework for testing whether old-growth forest canopies, read from LiDAR canopy height models, carry the signatures of self-organised criticality:

- **Five primary hypotheses**: Optimal Filling (canopy fractal dimension), Scale Invariance (power-law lacunarity), Zeta Distribution of Gaps (gap sizes with exponent near 2), Universal Repulsion (Wigner-Dyson/GUE spacing of dominant trees) and Biotic Decoupling (weaker coupling to topography)
- **Four spatial-distribution hypotheses** from Lapidus's fractal strings: transect gap lengths, GUE pair correlation of canopy emergents, log-periodic lacunarity oscillations and "Riemann gas" tree density
- **Methods and expected results** stated before any data are analysed, with the statistical tests that will decide each hypothesis

### [Notebooks](notebooks/index.md)

Jupyter notebooks rendered as pages with their stored outputs: the four Part I chapter notebooks, the Part II methods and results notebooks, and four stand-alone fractal demonstrations — [diffusion-limited aggregation](notebooks/foundations/dla.md), [self-similar fractals](notebooks/foundations/fractals.md), [self-affine generators](notebooks/foundations/fractal_generators.md) and [Riemann zeta space](notebooks/foundations/zeta_space.md). The [notebook index](notebooks/index.md) also lists the research notebooks that are kept on GitHub only.

### [Apps (Part VI)](applications/index.md)

Interactive tools and demonstrations:

- [React web applications](applications/react-apps.md) — GPU-accelerated fractal visualizations
- [Streamlit apps](applications/streamlit-apps.md) — Python-based interactive tools
- [Differential box-counting](applications/dbc.md) — Fractal dimension estimation
- [3D visualization](applications/tree-roots-3d.md) — Branching network rendering
- [Blender DLA](applications/blender-dla.md) — 3D point-cloud generator with Geometry Nodes

### [Knowledge](okf/index.md)

Machine-readable knowledge bundles in Open Knowledge Format (OKF) v0.2: the concept ontology exported from the Fractal RAG seed, the verified proofs behind Chapter 1, and the [Fractal RAG stack](fractal-rag/index.md) that indexes this corpus for retrieval agents.

### [For AI Agents](agents.md)

How agents and harnesses should read this site: `llms.txt`, a Markdown twin of every page, the OKF frontmatter on each page, and the MCP retrieval tools.

---

## Quick Start

<div class="grid cards" markdown>

-   :material-math-integral:{ .lg .middle } **Foundations**

    ---

    Learn the mathematical background of fractal geometry

    [:octicons-arrow-right-24: Get started](foundations/index.md)

-   :material-tree:{ .lg .middle } **Metabolic Scaling**

    ---

    Explore the fractal geometry of vascular organisms

    [:octicons-arrow-right-24: Read the paper](metabolic-scaling/index.md)

-   :material-play-circle:{ .lg .middle } **Interactive Apps**

    ---

    Explore fractals with GPU-accelerated visualizations

    [:octicons-arrow-right-24: Launch apps](https://tyson-swetnam.github.io/fractal-notebooks/react/)

-   :material-notebook:{ .lg .middle } **Jupyter Notebooks**

    ---

    Run code and visualize fractal algorithms

    [:octicons-arrow-right-24: Open notebooks](notebooks/index.md)

-   :material-book-open-variant:{ .lg .middle } **Knowledge**

    ---

    OKF concept ontology, verified proofs and the Fractal RAG stack

    [:octicons-arrow-right-24: Browse the bundles](okf/index.md)

-   :material-robot:{ .lg .middle } **For AI Agents**

    ---

    llms.txt, Markdown twins and the OKF frontmatter convention

    [:octicons-arrow-right-24: Read the agent guide](agents.md)

</div>

---

## Authors

[**Tyson Lee Swetnam**](https://tysonswetnam.com){target=_blank} [![ORCID](https://orcid.org/sites/default/files/images/orcid_16x16.png)](http://orcid.org/0000-0002-6639-7181){target=_blank}
Institute for Computation and Data-enabled Insight, University of Arizona

[**Jon D Pelletier**](http://jdpellet.github.io/){target=_blank} [![ORCID](https://orcid.org/sites/default/files/images/orcid_16x16.png)](http://orcid.org/0000-0002-0702-2646){target=_blank}
Department of Geosciences, University of Arizona

**Brian J. Enquist** [![ORCID](https://orcid.org/sites/default/files/images/orcid_16x16.png)](http://orcid.org/0000-0002-6124-7096){target=_blank}
Department of Ecology and Evolutionary Biology, University of Arizona

---

## Key Concepts

### Self-Similarity vs Self-Affinity

| Property | Self-Similar | Self-Affine |
|----------|--------------|-------------|
| Scaling | Isotropic (same in all directions) | Anisotropic (different by direction) |
| Example | Koch snowflake | Tree branches |
| Dimension | Single value | Direction-dependent |
| In biology | Rare | Common |

### The \( \frac{3}{4} \) Scaling Law

Metabolic Scaling Theory predicts that metabolic rate \( B \) scales with body mass \( M \) as:

\[
B \propto M^{3/4}
\]

This quarter-power scaling emerges from the fractal geometry of resource distribution networks, where:

- Branch radius scales as \( \xi = n^{-1/2} \)
- Branch length scales as \( \gamma = n^{-1/3} \)

Since \( \xi \neq \gamma \), these networks are self-affine.

---

## Abstract

Much of the scientific literature describes the fractal-like hierarchical branching networks of vascular organisms as self-similar; Part II links metabolic scaling theory to measured structural traits to show that they are self-affine, and that many fractal dimensions reported in ecology are therefore estimated with inappropriate self-similar methods. The full abstract, key findings and manuscript outline are on the [Part II: Metabolic Scaling Theory](metabolic-scaling/index.md) landing page.

---

## Citation

If you use this work, please cite:

```bibtex
@misc{swetnam2026fractals,
  author = {Swetnam, Tyson Lee and Pelletier, Jon D and Enquist, Brian J},
  title = {Fractal Patterns in Nature: Self-Affinity vs Self-Similarity},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/tyson-swetnam/fractal-notebooks}
}
```

---

## License

This project is released under the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). See [LICENSE](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/LICENSE) for details.
