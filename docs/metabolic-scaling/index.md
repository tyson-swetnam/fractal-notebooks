---
type: Index
title: "Part II: Metabolic Scaling Theory and Biological Fractals"
description: >-
  Landing page for Part II, an unpublished manuscript arguing that the branching
  networks of vascular organisms are self-affine rather than self-similar, with
  metabolic scaling theory predictions tested by differential box-counting: table of
  contents, supporting notebooks and authors.
resource: https://tyson-swetnam.github.io/fractal-notebooks/metabolic-scaling/
tags: [research, paper, part-ii, metabolic-scaling, self-affinity]
paper:
  title: "Fractal Patterns in Nature: Self-Affinity vs Self-Similarity"
  part_title: Metabolic Scaling Theory and Biological Fractals
  landing: https://tyson-swetnam.github.io/fractal-notebooks/metabolic-scaling/
  stage: manuscript-draft
authors:
  - name: Tyson Lee Swetnam
    orcid: https://orcid.org/0000-0002-6639-7181
    affiliation: Institute for Computation and Data-enabled Insight, University of Arizona
  - name: Jon D Pelletier
    orcid: https://orcid.org/0000-0002-0702-2646
    affiliation: Department of Geosciences, University of Arizona
  - name: Brian J. Enquist
    orcid: https://orcid.org/0000-0002-6124-7096
    affiliation: Department of Ecology and Evolutionary Biology, University of Arizona
citation:
  key: swetnam2026fractals
  year: 2026
  publisher: GitHub
  url: https://github.com/tyson-swetnam/fractal-notebooks
generated:
  by: claude-code/claude-fable-5-1
  at: "2026-10-24T00:00:00Z"
status: stable
---

# Part II: Metabolic Scaling Theory and Biological Fractals

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.

!!! warning "Status: unpublished manuscript draft"
    Part II is an unpublished manuscript in preparation (Swetnam, Pelletier and Enquist).
    Several entries in the Introduction's literature table still carry DOI placeholders, and
    some cross-references to supplementary figures and tables are being finalised. Every
    equation and table in the Methods and Results sections is reproduced in the executable
    notebooks listed under [Supporting Notebooks](#supporting-notebooks).

**Fractal Patterns in Nature: Self-Affinity vs Self-Similarity**

Much of the ecological literature describes the hierarchical branching networks of vascular
organisms as self-similar fractals and measures them with self-similar dimension estimators.
This manuscript reviews that literature, argues from Metabolic Scaling Theory (MST) that such
networks are self-affine because branch radii and lengths shrink at different rates
(\( \xi = n^{-1/2} \) and \( \gamma = n^{-1/3} \)), and tests the resulting prediction of a
mass dimension \( d = 3/2 \) with differential box-counting on synthetic L-system trees, x-ray
images of leaves, branches and roots, and airborne LiDAR canopy height models. It closes by
proposing a mechanistic theory of fractal dimension, from single-celled colonies to forests, in
which entropy maximisation through mass transfer drives self-affine geometry.

## Table of Contents

This Part is organized as a manuscript. Each section links to its page; the Methods and Results sections are additionally supported by executable Jupyter notebooks that reproduce every equation, figure, and table.

### [Abstract](abstract.md)

- [Key Findings](abstract.md#key-findings)

### [Introduction](introduction.md)

- [Differentiating Between Self-Similarity and Self-Affinity](introduction.md#differentiating-between-self-similarity-and-self-affinity)
- [Table 1: Reported fractal dimensions and techniques](introduction.md#table-1-reported-fractal-dimensions-and-techniques-measuring-fractal-behavior-in-plants-or-forests)

### [Methods](methods.md)

- [Metabolic Scaling Theory](methods.md#metabolic-scaling-theory) &nbsp;·&nbsp; notebook: [MST & Allometric Relationships](../notebooks/metabolic-scaling/methods/1_mst_allometry.md)
- [Allometric Relationships](methods.md#allometric-relationships) &nbsp;·&nbsp; notebook: [MST & Allometric Relationships](../notebooks/metabolic-scaling/methods/1_mst_allometry.md)
- [Branching Ratios](methods.md#branching-ratios) &nbsp;·&nbsp; notebook: [Branching Ratios](../notebooks/metabolic-scaling/methods/2_branching_ratios.md)
- [Volume and Mass Dimension Predictions](methods.md#volume-and-mass-dimension-predictions) &nbsp;·&nbsp; notebook: [Volume & Mass Dimension](../notebooks/metabolic-scaling/methods/3_volume_mass_dimension.md)
- [Differential Box-Counting Methodology](methods.md#differential-box-counting-methodology) &nbsp;·&nbsp; notebooks: [Volume & Mass Dimension](../notebooks/metabolic-scaling/methods/3_volume_mass_dimension.md), [DBC & FracLac](../notebooks/metabolic-scaling/methods/4_dbc_fraclac.md)
- [FracLac Analysis Procedures](methods.md#fraclac-analysis-procedures) &nbsp;·&nbsp; notebook: [DBC & FracLac](../notebooks/metabolic-scaling/methods/4_dbc_fraclac.md)

### [Results](results.md)

- [Table 1: Synthetic Fractal Dimensions](results.md#table-1-synthetic-fractal-dimensions) &nbsp;·&nbsp; notebook: [Synthetic Dimensions](../notebooks/metabolic-scaling/results/1_synthetic_dimensions.md)
- [Table 2: Observed Leaf Mass Dimensions](results.md#table-2-observed-leaf-mass-dimensions) &nbsp;·&nbsp; notebook: [Observed Leaf, Branch & Root Dimensions](../notebooks/metabolic-scaling/results/2_observed_leaf_branch_root.md)
- [Table 3: Observed Branch/Root Mass Dimensions](results.md#table-3-observed-branchroot-mass-dimensions) &nbsp;·&nbsp; notebook: [Observed Leaf, Branch & Root Dimensions](../notebooks/metabolic-scaling/results/2_observed_leaf_branch_root.md)
- [Table 4: Forest Canopy Height Model Dimensions](results.md#table-4-forest-canopy-height-model-dimensions) &nbsp;·&nbsp; notebook: [Canopy Dimensions & Statistical Validation](../notebooks/metabolic-scaling/results/3_canopy_statistical_validation.md)
- [Statistical Validation](results.md#statistical-validation) &nbsp;·&nbsp; notebook: [Canopy Dimensions & Statistical Validation](../notebooks/metabolic-scaling/results/3_canopy_statistical_validation.md)

### [Discussion](discussion.md)

- [Closing in on Self-Affinity from the Metabolic Scaling Theory](discussion.md#closing-in-on-self-affinity-from-the-metabolic-scaling-theory)
- [Demonstrations of Self-Affine Fractals](discussion.md#demonstrations-of-self-affine-fractals)
- [A Fractal Theory of Ecology](discussion.md#a-fractal-theory-of-ecology)
- [Fractal Dimensions of Non-Vascular Organisms](discussion.md#fractal-dimensions-of-non-vascular-organisms)
- [Extended Applications: Explaining Why Vascular Life Forms Dominate](discussion.md#extended-applications-explaining-why-vascular-life-forms-dominate)
- [Toward a Unified Theory](discussion.md#toward-a-unified-theory)

### [Conclusion](conclusion.md)

- [Validation of Metabolic Scaling Theory](conclusion.md#validation-of-metabolic-scaling-theory)
- [Implications for Ecology](conclusion.md#implications-for-ecology)
- [Future Directions](conclusion.md#future-directions)

### [References](references.md)

- [Key Papers on Metabolic Scaling Theory](references.md#key-papers-on-metabolic-scaling-theory)
- [Fractal Geometry and Mandelbrot](references.md#fractal-geometry-and-mandelbrot)
- [Allometry and Historical Background](references.md#allometry-and-historical-background)
- [Fractal Analysis Methods](references.md#fractal-analysis-methods)
- [Ecological Applications](references.md#ecological-applications)
- [Thermodynamics and Entropy](references.md#thermodynamics-and-entropy)

### Supporting Notebooks

**Methods**

1. [MST & Allometric Relationships](../notebooks/metabolic-scaling/methods/1_mst_allometry.md) — Kleiber's law $B \propto M^{3/4}$ and the power-law allometric form.
2. [Branching Ratios](../notebooks/metabolic-scaling/methods/2_branching_ratios.md) — $\xi = n^{-1/2}$, $\gamma = n^{-1/3}$, and the space-filling $D=3$ result.
3. [Volume & Mass Dimension](../notebooks/metabolic-scaling/methods/3_volume_mass_dimension.md) — Equations 11–18 and the $d=3/2$ network mass dimension.
4. [DBC & FracLac](../notebooks/metabolic-scaling/methods/4_dbc_fraclac.md) — differential box-counting validated against fBm of known dimension.

**Results**

1. [Synthetic Dimensions (Table 1)](../notebooks/metabolic-scaling/results/1_synthetic_dimensions.md) — generated fractal trees, box-counting, DBC, and lacunarity.
2. [Observed Leaf, Branch & Root Dimensions (Tables 2–3)](../notebooks/metabolic-scaling/results/2_observed_leaf_branch_root.md) — reproduction of published mass dimensions with the DBC estimator on synthetic proxies.
3. [Canopy Dimensions & Statistical Validation (Table 4)](../notebooks/metabolic-scaling/results/3_canopy_statistical_validation.md) — forest CHM dimensions and a TOST equivalence test against $d=3/2$.

## Authors

[Tyson Lee Swetnam](https://tysonswetnam.com){target=_blank} [![](https://orcid.org/sites/default/files/images/orcid_16x16.png)](http://orcid.org/0000-0002-6639-7181){target=_blank}
Institute for Computation and Data-enabled Insight, University of Arizona

[Jon D Pelletier](http://jdpellet.github.io/){target=_blank} [![](https://orcid.org/sites/default/files/images/orcid_16x16.png)](http://orcid.org/0000-0002-0702-2646) Department of Geosciences, University of Arizona

Brian J. Enquist [![](https://orcid.org/sites/default/files/images/orcid_16x16.png)](http://orcid.org/0000-0002-6124-7096) Department of Ecology and Evolutionary Biology, University of Arizona
