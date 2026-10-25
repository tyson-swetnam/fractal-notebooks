---
type: Index
title: "Part V: Research Framework and Testable Hypotheses"
description: >-
  Landing page for Part V, a preregistration framework testing whether old-growth
  forests at self-organized criticality show distinct fractal dimension, lacunarity,
  zeta-distributed gap sizes and GUE-like tree spacing in LiDAR canopy height models:
  summary, section guide and implementation path.
resource: https://tyson-swetnam.github.io/fractal-notebooks/hypotheses/
tags: [research, paper, part-v, preregistration, forest-ecology, lidar]
paper:
  title: "Spectral Geometry and Metabolic Scaling in Forest Canopy Architecture: A Preregistration Framework"
  part_title: Research Framework and Testable Hypotheses
  landing: https://tyson-swetnam.github.io/fractal-notebooks/hypotheses/
  stage: preregistration
generated:
  by: claude-code/claude-fable-5-1
  at: "2026-10-24T00:00:00Z"
status: stable
---

# Part V: Research Framework and Testable Hypotheses

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.

!!! note "Status: preregistration framework"
    Part V is a preregistration: it states hypotheses, methods and expected results before any
    data are analysed, and reports no results. The analyses are being implemented in the 3DEP
    canopy height model notebooks (see [Implementation path](#implementation-path)).

**Spectral Geometry and Metabolic Scaling in Forest Canopy Architecture: A Preregistration Framework**

**Keywords:** spectral geometry, fractal dimension, lacunarity, Riemann Zeta distribution, self-organized criticality, GUE statistics, canopy structure, metabolic scaling, complex dimensions, old-growth forest

Do old-growth forests at self-organized criticality carry geometric and spectral signatures that
distinguish them from disturbed or managed stands? Treating the LiDAR canopy height model as a
stochastic surface, the framework predicts that optimal space packing and metabolic scaling
produce characteristic fractal dimension \( D \) and lacunarity \( \Lambda \) curves, that
canopy gap sizes follow a zeta (power-law) distribution with exponent near 2, and that the
spacing of dominant tree crowns follows Wigner-Dyson (GUE) repulsion statistics, like the zeros
of the Riemann zeta function, rather than Poisson randomness. Five primary hypotheses (optimal
filling, scale invariance, zeta gap distribution, universal repulsion and biotic decoupling) and
four spatial hypotheses from fractal string theory are each given null and alternative forms
together with the statistical tests (ANOVA, regression, likelihood-ratio and chi-squared tests)
that will decide them.

## Contents

1. [Abstract](abstract.md)
2. [Introduction](introduction.md)
3. [Methods](methods.md)
4. [Expected Results](results.md)
5. [Discussion](discussion.md)
6. [Conclusion](conclusion.md)
7. [References](references.md)

## Implementation path

The measurements this framework calls for (normalised canopy height models, differential
box-counting, gliding-box lacunarity, gap-size distributions and tree-apex spacing) are being
implemented in the [3DEP canopy height model notebooks](../notebooks/research.md#3dep-canopy-height-models),
which build canopy height models for a set of United States forest sites from USGS 3DEP LiDAR.
The Part II notebook [Canopy Dimensions & Statistical Validation](../notebooks/metabolic-scaling/results/3_canopy_statistical_validation.md)
shows the differential box-counting workflow on canopy height models.
