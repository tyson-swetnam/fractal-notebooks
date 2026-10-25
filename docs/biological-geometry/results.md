---
type: Paper Section
title: Biological Geometry — Results
description: >-
  Results for Part IV: log-periodic wiggles as complex-dimension signatures, lichen
  DLA morphology, hydrodynamic DLA in kelp forests, crown shyness as weighted Voronoi
  tessellation with zeta-distributed gaps, Apollonian canopy packing, preferential
  attachment and root spectral dimensions.
resource: https://tyson-swetnam.github.io/fractal-notebooks/biological-geometry/results/
tags: [paper, part-iv, biological, dla, branching, forest-ecology]
paper:
  title: "Architectures of the Infinite: Self-Affine Fractals, Complex Dimensions, and the Thermodynamic Geometries of Biological Space-Filling"
  part_title: Biological Space-Filling and Thermodynamic Geometry
  landing: https://tyson-swetnam.github.io/fractal-notebooks/biological-geometry/
  stage: chapter-draft
sources:
  - id: de-marchi-cassi1993
    resource: https://doi.org/10.1142/S0218348X9300037X
    title: Fractal geometry and ecology of lichens (De Marchi and Cassi 1993, Fractals)
  - id: kelp-map2020
    resource: https://doi.org/10.3390/rs12040694
    title: A high-resolution global map of giant kelp (Macrocystis pyrifera) forests and intertidal green algae with Sentinel-2 imagery (Mora-Soto et al. 2020, Remote Sensing)
  - id: vanderzee2021
    resource: https://pmc.ncbi.nlm.nih.gov/articles/PMC8557382/
    title: Understanding crown shyness from a 3-D perspective (van der Zee, Lau and Shenkin 2021, Annals of Botany)
  - id: wiki-apollonian
    resource: https://en.wikipedia.org/wiki/Apollonian_gasket
    title: Apollonian gasket (Wikipedia)
  - id: root-foraging2016
    resource: https://pmc.ncbi.nlm.nih.gov/articles/PMC5048097/
    title: Hybrid artificial root foraging optimizer based multilevel threshold for image segmentation (2016, PMC)
  - id: gwynne-miller2021
    resource: https://doi.org/10.1214/20-AOP1471
    title: "Random walk on random planar maps: spectral dimension, resistance and displacement (Gwynne and Miller 2021, Annals of Probability)"
generated:
  by: human:tswetnam
  at: "2025-12-14T00:00:00Z"
status: draft
---

# Results: Fractal Signatures in Biological Systems

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.

## 3.1 Deviations and "Wiggles": The Signature of Complex Dimensions

Empirical data on metabolic scaling often show systematic deviations from the predicted \( 3/4 \) power law. These deviations appear as log-periodic oscillations or "wiggles" around the regression line. Rather than dismissing these as noise, the theory of complex fractal dimensions interprets them as the intrinsic signature of discrete self-similarity.

A fractal string with a discrete scaling ratio \( \gamma \) possesses a set of complex dimensions:

\[
\mathcal{D} = \left\{D + i\frac{2\pi k}{\ln \gamma}\right\}
\]

The real part \( D \) gives the trend (the power law), while the imaginary part \( i\frac{2\pi k}{\ln \gamma} \) manifests as a periodic modulation in the logarithmic domain.

In biological terms, this means that growth rates and metabolic fluxes do not scale monotonically. They pulse. These pulses correspond to the discrete addition of hierarchical levels---the "quantum" jumps of branching generations. The organism vibrates geometrically as it grows, and the frequency of these vibrations is determined by its branching architecture.

## 3.2 Lichen DLA Morphology

The DLA model produces characteristic dendritic morphologies in lichen with measurable properties:

- **Fractal Dimension**: \( D \approx 1.6 - 1.7 \) for crustose and foliose lichens

- **Harmonic Measure Distribution**: Highly non-uniform, with exponentially decaying probability in fjord regions

- **Ecological Interpretation**: This geometry is an adaptation to starvation. A compact, circular thallus (\( D = 2 \)) would minimize surface area and starve. The fractal thallus maximizes the surface-to-volume ratio, effectively "trawling" the air for dilute resources.

## 3.3 Kelp Forests: Hydrodynamic DLA

Giant kelp forests exhibit spatial fractal patterns arising from hydrodynamic DLA:

- **Spatial Fractal Dimension**: \( D \approx 1.3 - 1.5 \) for holdfast distributions

- **Recruitment Limitation**: The existing forest acts as a sieve, intercepting drifting spores

- **Topological Resilience**: Graph-theoretic analysis reveals that fractal patchiness enhances resilience. The spectral dimension of the spatial graph (\( d_s \)) is often lower than the Euclidean dimension, indicating a "large world" topology---dispersal is slow, but local connectivity is high, fostering local biodiversity hotspots.

## 3.4 Crown Shyness: Voronoi Tessellations and the "Shy" Gap

In mature forests, tree crowns often exhibit **crown shyness**, maintaining a distinct gap between neighbors to prevent abrasion and disease transmission. This phenomenon essentially computes a Voronoi Tessellation of the canopy space.

### 3.4.1 Mechanism

Each tree acts as a seed point. The "cell" is the territory accessible to that tree's light-foraging branches. The boundaries are defined by the "shy" zones where reciprocal pruning occurs.

### 3.4.2 Weighted Voronoi Diagrams

Since trees vary in vigor, this is a **Weighted Voronoi diagram** (or Laguerre tessellation). A dominant tree with a higher growth rate pushes the boundary into the territory of a weaker neighbor.

### 3.4.3 Gap Size Distribution

The distribution of gap sizes in such a canopy follows a **Zeta distribution** (discrete power law), governed by the Riemann Zeta function:

\[
P(k) = \frac{k^{-\lambda}}{\zeta(\lambda)}
\]

where \( k \) is the gap size rank and \( \lambda \) is the scaling exponent.

- \( \lambda < 2 \): Indicates a forest dominated by large, disturbance-driven gaps (treefalls), typical of dynamic rainforests.

- \( \lambda > 2 \): Indicates a "closed" canopy dominated by small, interstitial gaps (shyness), typical of stable old-growth forests.

## 3.5 Apollonian Packing in Forest Canopies

The theoretical limit of canopy packing can be modeled using **Apollonian Circle Packing**. In this fractal construction, smaller circles are iteratively fitted into the curvilinear triangular gaps between larger touching circles.

While real trees do not touch, the size distribution of trees in a mature forest often mirrors the power-law distribution of circle radii in an Apollonian gasket:

\[
N(r) \sim r^{-D}
\]

where \( D \approx 1.3057 \) (the Hausdorff dimension of the residual set). This suggests that the forest fills space by inserting smaller trees into the light gaps left by larger trees, iterating down to the scale of saplings, limited only by the "exclusion zones" of crown shyness.

## 3.6 The "Rich-Get-Richer" Mechanism: Preferential Attachment

The assembly of fractal canopies is driven by **Preferential Attachment**, a dynamic well-known in network theory as the "Rich-Get-Richer" mechanism:

- **Light Asymmetry**: A tree that is slightly taller or has a larger crown intercepts more light. This surplus energy fuels faster growth, which further expands the crown, intercepting even more light.

- **Spatial Sorting**: This positive feedback loop amplifies small initial differences, leading to a heavy-tailed (Pareto) distribution of tree sizes:

\[
N(S) \sim S^{-\gamma}
\]

- **Invasion Dynamics**: This mechanism also explains the "Rich-Get-Richer" paradox in invasion ecology: biodiversity hotspots (areas rich in native species and resources) are more susceptible to invasion, not less. The same high resource availability that supports diverse native flora also fuels the explosive growth of invasive species via preferential attachment dynamics.

## 3.7 Root Foraging: Spectral Dimensions

Below ground, the competition for space is even more intense. Roots forage in a dark, heterogeneous medium, solving a search problem that is mathematically isomorphic to traversing a graph.

### 3.7.1 Chemotropism as Gradient Descent

Root systems employ algorithms strikingly similar to Bacterial Foraging Optimization (BFO) or Artificial Bee Colony algorithms:

- **Exploration vs. Exploitation**: Roots must balance exploring new soil volume (high cost, uncertain reward) with exploiting known nutrient patches (low cost, diminishing returns).

- **Algorithm**: The root performs a "random walk" (growth) that is biased by chemotropism (sensing nutrient gradients). This is effectively a gradient descent optimization in chemical potential space.

### 3.7.2 Spectral Dimensions of Root Networks

The efficiency of this foraging is determined by the **spectral dimension** (\( d_s \)) of the root network. The spectral dimension characterizes the diffusion probability \( P(t) \sim t^{-d_s/2} \) on the network:

- **Compact Exploration** (\( d_s < 2 \)): A root system with low spectral dimension (e.g., highly branched, herring-bone topology) is "recurrent." A nutrient ion diffusing near the root is likely to hit it. This topology is optimal for intensive exploitation of rich patches.

- **Non-Compact Exploration** (\( d_s > 2 \)): A root system with high spectral dimension (e.g., sparse, elongated topology) is "transient." It covers distance quickly. This topology is optimal for extensive exploration in nutrient-poor soils.

Plants exhibit **phenotypic plasticity**, actively adjusting their branching angles and internode lengths to tune the spectral dimension of their roots in response to local soil quality---a dynamic topological computation.

**Table 2: Spectral Dimension Strategies in Root Systems**

| Strategy | Spectral Dimension | Topology | Optimal Environment |
|----------|-------------------|----------|---------------------|
| Compact Exploration | \( d_s < 2 \) | Highly branched, herring-bone | Rich nutrient patches |
| Non-Compact Exploration | \( d_s > 2 \) | Sparse, elongated | Nutrient-poor soils |
| Typical Range | \( d_s \approx 1.2 - 1.8 \) | Intermediate | Variable conditions |
