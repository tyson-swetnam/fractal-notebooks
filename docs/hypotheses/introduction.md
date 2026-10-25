---
type: Paper Section
title: Research Hypotheses — Introduction
description: >-
  Introduction to Part V: canopy height models as stochastic surfaces, the zeta(2)
  harmonic packing connection, fractal dimension versus lacunarity, the
  Montgomery-Odlyzko law and GUE repulsion, statements of the five primary and four
  fractal-string hypotheses, and chapter organisation.
resource: https://tyson-swetnam.github.io/fractal-notebooks/hypotheses/introduction/
tags: [paper, part-v, preregistration, riemann-zeta, forest-ecology, statistical-physics]
paper:
  title: "Spectral Geometry and Metabolic Scaling in Forest Canopy Architecture: A Preregistration Framework"
  part_title: Research Framework and Testable Hypotheses
  landing: https://tyson-swetnam.github.io/fractal-notebooks/hypotheses/
  stage: preregistration
sources:
  - id: odlyzko1987
    resource: https://doi.org/10.1090/S0025-5718-1987-0866115-0
    title: On the distribution of spacings between zeros of the zeta function (Odlyzko 1987, Mathematics of Computation)
  - id: bak1987
    resource: https://doi.org/10.1103/PhysRevLett.59.381
    title: "Self-organized criticality: an explanation of 1/f noise (Bak, Tang and Wiesenfeld 1987, Physical Review Letters)"
  - id: plotnick1996
    resource: https://doi.org/10.1103/PhysRevE.53.5461
    title: "Lacunarity analysis: a general technique for the analysis of spatial patterns (Plotnick et al. 1996, Physical Review E)"
  - id: lapidus-vanfrankenhuijsen2013
    resource: https://doi.org/10.1007/978-1-4614-2176-4
    title: "Fractal Geometry, Complex Dimensions and Zeta Functions: Geometry and Spectra of Fractal Strings (Lapidus and van Frankenhuijsen, 2nd ed. 2013, Springer)"
generated:
  by: human:tswetnam
  at: "2025-12-14T00:00:00Z"
status: draft
---

# Introduction

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.

## Theoretical Framework: Spectral Geometry and Forest Structure

This study investigates whether old-growth forests, defined as systems at "Self-Organized Criticality" (SOC), exhibit distinct geometric and spectral signatures compared to disturbed or managed forests. By treating the Canopy Height Map (CHM) as a stochastic surface, we propose that optimal space packing and metabolic scaling result in specific Fractal Dimensions (\(D\)) and Lacunarity (\(\Lambda\)) curves.

The central hypothesis draws on connections between the Riemann Zeta Function and the frequency distribution of object sizes in two-dimensional space. For a harmonic packing model where objects fill a 2D plane according to power-law size distributions, the Riemann Zeta function provides the normalization constant:

\[
A_{total} = \zeta(2) = \frac{\pi^2}{6} \approx 1.645
\]

This mathematical framework extends to biological systems through the concept of **Self-Organized Criticality**---the idea that complex systems naturally evolve toward critical states exhibiting scale-free behavior.

## Research Questions

This preregistration addresses three fundamental questions:

1. **Fractal Dimension:** Do old-growth forests exhibit a specific Fractal Dimension (\(D\)) that indicates optimal volumetric filling?

2. **Spectral DNA:** Does the oscillation of Lacunarity over scale (the "spectral DNA") differentiate between steady-state succession and recent disturbance?

3. **Universal Repulsion:** Do the centers of dominant tree crowns in old-growth forests exhibit spatial repulsion statistics consistent with the Gaussian Unitary Ensemble (GUE)?

## The Zeta Connection: From Number Theory to Ecology

### Harmonic Packing and the Basel Problem

Consider a theoretical region in a 2D plane filled by a countable set of non-overlapping objects with harmonic dimensions. The total area of such a packing equals \(\zeta(2)\), connecting number theory to spatial geometry.

In ecological terms, this framework suggests that forests self-organize to maximize light interception and gas exchange while minimizing transport costs. A forest with "optimal" packing would effectively utilize all available vertical and horizontal space, resulting in high fractal dimension approaching \(D \approx 2.7-2.8\) for complex rainforests or old-growth systems.

### Fractal Dimension and Lacunarity

While Fractal Dimension \(D\) tells us how objects fill space (the slope of the log-log plot of frequency vs. size), **Lacunarity** measures the "texture" or gappiness of the distribution:

- **High Lacunarity:** Heterogeneous gaps of various sizes; characteristic of late-successional/old-growth systems with stochastic disturbance history
- **Low Lacunarity:** Uniform, homogeneous structure; characteristic of monocultures or plantations

### Universal Laws of Repulsion

The **Montgomery-Odlyzko Law** establishes that the spacing between the non-trivial zeros of the Riemann Zeta function follows the statistics of the **Gaussian Unitary Ensemble (GUE)**---the same statistics used in Quantum Chaos to describe particle repulsion.

We hypothesize that the spatial distribution of dominant canopy trees in old-growth forests follows similar repulsion statistics, representing systems that have maximized their energy interactions (metabolic scaling) over long periods (centuries).

## The Five Primary Hypotheses

### Hypothesis 1: The "Optimal Filling" Hypothesis (Fractal Dimension)

Old-growth forests maximize light interception while minimizing self-shading. The Fractal Dimension of the Canopy Height Map should be significantly higher in old-growth than in monoculture plantations or recently disturbed stands.

### Hypothesis 2: The "Scale Invariance" Hypothesis (Lacunarity)

Disturbance creates characteristic gap sizes (breaks in scaling), whereas steady-state forests exhibit scale invariance. In old-growth forests, the Lacunarity curve should follow strict power-law decay (linear on log-log plot), while disturbed forests exhibit "spectral kinks."

### Hypothesis 3: The "Zeta" Distribution of Gaps (Metabolic Scaling)

The frequency of canopy gaps is driven by tree mortality following metabolic scaling laws. Gap sizes in old-growth forests should follow a Power Law distribution \(P(A) \sim A^{-\alpha}\) with exponent \(\alpha \approx 2.0\), related to \(\zeta(2)\).

### Hypothesis 4: Universal Repulsion (The "Spectral DNA")

Trees compete for resources, creating zones of exclusion similar to energy level repulsion in quantum systems. The Nearest Neighbor Spacing distribution of dominant tree apices should fit the Wigner-Dyson distribution (GUE statistics), not a Poisson distribution.

### Hypothesis 5: Biotic Decoupling (The Topographic Test)

Mature ecosystems buffer environmental constraints through niche construction. The correlation coefficient between local fractal dimension and topographic variables (slope, TWI, solar insolation) should be lower in old-growth than in young or disturbed stands.

## Four Spatial Distribution Hypotheses from Fractal String Theory

In addition to the five primary hypotheses, we present four spatial distribution hypotheses derived from Lapidus's theory of Fractal Strings:

### The "Fractal String" Gap Hypothesis

The distribution of gap lengths along any transect through an old-growth forest should follow a Zeta-based power law, with no single gap size dominating (scale invariance).

### The "Prime Number" Repulsion Hypothesis (GUE)

The spatial distribution of the largest, dominant canopy emergents will follow the GUE Pair Correlation Function rather than Poisson (random) or hexagonal (crystal) patterns.

### The Complex Dimension (Oscillation) Hypothesis

The Lacunarity curve plotted against log(box size) should exhibit periodic oscillations in old-growth forests, indicating complex dimensions and self-similar construction algorithms.

### The "Riemann Gas" Density Hypothesis

The number density of trees with mass greater than \(m\) scales according to the inverse of the Zeta function normalization, with forests hovering at the "critical density" threshold---the Edge of Chaos.

## Organization of This Chapter

The following sections develop each hypothesis in detail:

- **Methods** presents the mathematical foundations, measurement protocols, and experimental designs for testing hypotheses using LiDAR-derived Canopy Height Models and Differential Box Counting.

- **Expected Results** outlines predicted outcomes under null and alternative hypotheses, including measurement ranges and statistical power considerations.

- **Discussion** addresses implications for ecological theory, connections to metabolic scaling theory and thermodynamics, and methodological limitations.

- **Conclusion** summarizes the framework and identifies priorities for future experimental work.
