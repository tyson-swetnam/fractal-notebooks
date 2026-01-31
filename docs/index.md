# Fractal Patterns in Nature: Self-Affinity vs Self-Similarity

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.

Welcome to the Fractal Notebooks project—an interdisciplinary exploration of fractal geometry in biological systems, from the mathematics of Mandelbrot to the metabolic scaling theory of vascular organisms.

---

## About This Project

Much of the scientific literature describes the fractal-like hierarchical branching networks of vascular organisms as "self-similar." This project examines this terminology and demonstrates why these structures are more accurately described as **self-affine**—scaling differently in different spatial directions.

We link metabolic scaling theory to the structural traits of organisms and propose mechanistic theories for fractal dimensions from single cells to ecosystems.

---

## Document Structure

This documentation is organized into seven parts:

### [Part I: Foundations](foundations/history.md)

Educational chapters providing mathematical and historical background:

- [**History of Fractals**](foundations/history.md) — From Cantor to Mandelbrot to modern complex dimensions
- [**Mathematical Foundations**](foundations/mathematics.md) — Hausdorff dimension, box-counting, Hurst exponent
- [**Fractal Dimensionality**](foundations/dimensionality.md) — 1D through 4D fractals with examples
- [**Glossary & Equations**](foundations/glossary.md) — Quick reference for terms and formulas

### [Part II: Metabolic Scaling Theory](metabolic-scaling/abstract.md)

The core research paper on self-affinity in vascular organisms:

- Distinction between self-similarity and self-affinity
- West-Brown-Enquist (WBE) model derivations
- Empirical validation using differential box-counting
- Tables of fractal dimensions for leaves, branches, and forest canopies

### [Part III: Spectral Geometry](spectral-geometry/abstract.md)

Advanced mathematical theory connecting fractals to the Riemann zeta function:

- Fractal strings and geometric zeta functions
- Complex dimensions and log-periodic oscillations
- Applications to algorithmic sorting and spatial indexing
- The "Fractal Riemann Hypothesis"

### [Part IV: Biological Geometry](biological-geometry/abstract.md)

Applications of self-affine geometry to biological systems:

- DLA models for lichen, algae, and kelp
- IFS models for ferns and plant architecture
- Crown shyness and Apollonian packing in forest canopies
- Root foraging and spectral dimensions

### [Part V: Research Hypotheses](hypotheses/abstract.md)

Proposed experimental research framework:

- **Hypothesis 1**: DLA geometry in lichens and algae
- **Hypothesis 2**: Monofractal vs multifractal branching in plants
- **Hypothesis 3**: Canopy gap dynamics and Zeta distributions

### [Part VI: Applications](applications/index.md)

Interactive tools and demonstrations:

- [React web applications](applications/react-apps.md) — GPU-accelerated fractal visualizations
- [Streamlit apps](applications/streamlit-apps.md) — Python-based interactive tools
- [Differential box-counting](applications/dbc.md) — Fractal dimension estimation
- [3D visualization](applications/tree-roots-3d.md) — Branching network rendering

### [Part VII: Notebooks](notebooks/index.md)

Jupyter notebooks for hands-on exploration:

- [DLA simulation](notebooks/old_dla.ipynb)
- [Barnsley ferns](notebooks/ferns.ipynb)
- [Self-similar fractals](notebooks/fractals.ipynb)
- [Self-affine generators](notebooks/fractal_generators.ipynb)
- [Riemann zeta functions](notebooks/zeta_space.ipynb)

---

## Quick Start

<div class="grid cards" markdown>

-   :material-math-integral:{ .lg .middle } **Foundations**

    ---

    Learn the mathematical background of fractal geometry

    [:octicons-arrow-right-24: Get started](foundations/history.md)

-   :material-tree:{ .lg .middle } **Metabolic Scaling**

    ---

    Explore the fractal geometry of vascular organisms

    [:octicons-arrow-right-24: Read the paper](metabolic-scaling/abstract.md)

-   :material-play-circle:{ .lg .middle } **Interactive Apps**

    ---

    Explore fractals with GPU-accelerated visualizations

    [:octicons-arrow-right-24: Launch apps](react/)

-   :material-notebook:{ .lg .middle } **Jupyter Notebooks**

    ---

    Run code and visualize fractal algorithms

    [:octicons-arrow-right-24: Open notebooks](notebooks/index.md)

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

Much of the scientific literature describes the fractal-like hierarchical branching networks of vascular organisms as 'self-similar'. Here we examine papers where fractal-like self-similarity is incorrectly described. We also link why the hierarchical branching networks in vascular organisms are 'self-affine' rather than self-similar by linking metabolic scaling theory to these structural traits. Last, we propose a mechanistic theory of fractal dimensions for single cell through multicellular life forms.

Our results demonstrate:

1. **Dimensional analysis** with appropriate self-affine mass dimension shows that many reported fractal dimensions in ecology are either incorrect or inappropriately reported.

2. **A technique for testable predictions**, including a mechanistic explanation for how individual branching networks grow and fill space and how communities of organisms emerge with fractal dimensions based on MST predictions.

These results may help reveal when communities of individuals have maximized their potential to cycle energy through an ecosystem or when they have been disturbed by exogenous forces.

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
