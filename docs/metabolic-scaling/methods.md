---
type: Paper Section
title: Metabolic Scaling — Methods
description: >-
  Methods for Part II: metabolic scaling theory (WBE), the power-law allometric form,
  radius and length branching ratios n^(-1/2) and n^(-1/3), volume and mass dimension
  predictions (Equations 9-17) giving d = 3/2, and the FracLac differential
  box-counting procedure.
resource: https://tyson-swetnam.github.io/fractal-notebooks/metabolic-scaling/methods/
tags: [paper, part-ii, metabolic-scaling, branching, methods, image-analysis]
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
sources:
  - id: west1999science
    resource: https://doi.org/10.1126/science.284.5420.1677
    title: "The fourth dimension of life: fractal geometry and allometric scaling of organisms (West, Brown and Enquist 1999, Science)"
  - id: west1999nature
    resource: https://doi.org/10.1038/23251
    title: A general model for the structure and allometry of plant vascular systems (West, Brown and Enquist 1999, Nature)
  - id: west2009pnas
    resource: https://doi.org/10.1073/pnas.0812294106
    title: A general quantitative theory of forest structure and dynamics (West, Enquist and Brown 2009, PNAS)
  - id: enquist1998
    resource: https://doi.org/10.1038/25977
    title: Allometric scaling of plant energetics and population density (Enquist, Brown and West 1998, Nature)
  - id: enquist1999
    resource: https://doi.org/10.1038/44819
    title: Allometric scaling of production and life-history variation in vascular plants (Enquist et al. 1999, Nature)
  - id: brown2004
    resource: https://doi.org/10.1890/03-9000
    title: Toward a metabolic theory of ecology (Brown et al. 2004, Ecology)
  - id: smith2014
    resource: https://doi.org/10.1111/nph.12487
    title: Deviation from symmetrically self-similar branching in trees predicts altered hydraulics, mechanics, light interception and metabolic scaling (Smith et al. 2014, New Phytologist)
  - id: fraclac
    resource: https://imagej.net/ij/plugins/fraclac/FLHelp/Introduction.htm
    title: "FracLac for ImageJ: box-counting, differential box-counting and lacunarity (Karperien, user guide)"
generated:
  by: human:tswetnam
  at: "2024-09-22T00:00:00Z"
status: draft
---

# Methods

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.

!!! note "Supporting notebooks"
    Every equation and procedure in this section is reproduced in executable Jupyter notebooks:
    [MST & Allometric Relationships](../notebooks/metabolic-scaling/methods/1_mst_allometry.md),
    [Branching Ratios](../notebooks/metabolic-scaling/methods/2_branching_ratios.md),
    [Volume & Mass Dimension](../notebooks/metabolic-scaling/methods/3_volume_mass_dimension.md), and
    [DBC & FracLac](../notebooks/metabolic-scaling/methods/4_dbc_fraclac.md).

Today, there are numerous numerical and analytical tools for evaluating fractal dimensions. Fractal dimension can be evaluated in binary (e.g., presence vs. absence) or continuous values (e.g., grayscale). An important implication of evaluating organisms, specifically their hierarchical branching networks, is that their distribution of mass is expected to scale anisotropically across their various branching orders.

## Metabolic Scaling Theory

Metabolic Scaling Theory (MST) makes quantitative predictions about the fractal dimension of hierarchical branching networks in both three-dimensional and two-dimensional space. MST was primarily formulated by the authors West, Brown, and Enquist (hereafter WBE) (West 1999; West et al. 1999, 2009; Enquist et al. 1998, 1999, 2009; Brown and West 2000; Brown et al. 2004). West et al. (1999) provide the theoretical framework from which MST is based. Numerous papers have followed, supporting MST's theoretical strengths and refuting its weaknesses when applied to real-world phenomena. Despite its weaknesses, the theory continues to be modified and improved upon, gaining momentum as a useful null model for predicting natural phenomena.

Relative to the fractal dimensions of vascular plants, MST incorporates different power-law functions with various scaling exponents to predict branching geometry, growth rates, and size. The MST authors do not use the adjective "self-affine" to describe the fractal-like behavior; instead, they state the systems are self-similar (Table 1), which we argue is syntactically incorrect. This misuse of terminology does not affect the robustness of MST's predictions and, in some cases, should help resolve questions about observed asymmetry (Smith et al. 2014).

## Allometric Relationships

Allometric relationships are typically written as a power-law:

\[
f(\varepsilon) = C \varepsilon^{\alpha}
\]

*Equation 9*

where \(C\) is the prefactor or normalization coefficient, \( \varepsilon \) is a measure of size (such as the radii of a meristem, the length of a conduit, or the surface area of a leaf), and \( \alpha \) is the dynamic exponent (West et al. 1999, 2009; Brown et al. 2004). For example, the relationship of basal metabolic rate \( B \) to body mass \( M \) can be given as:

\[
B \propto M^{3/4}
\]

## Branching Ratios

WBE show that for a resource distribution network such as a tree, with continuous branching from the trunk to the petioles or root terminals, the primary size measures (e.g., radius \(r\) or path length \(l\)) change in regular ways between the \(k\) to \(k+1\) branching levels, often referred to as bifurcations (e.g., bifurcation for two daughter branches, trifurcation for three branches). For the general case, the bifurcation rate, also called the branching ratio of \(r\) and \(l\), can be written as:

\[
\xi = \frac{r_{k+1}}{r_k} = n^{-\frac{1}{2}}
\quad \text{and} \quad
\gamma = \frac{l_{k+1}}{l_k} = n^{-\frac{1}{3}}
\]

*Equation 10*

where \( \xi \) is the bifurcation rate, \( \gamma \) is the ratio of branch lengths respective to any \(n\) number of daughter branches, and \(k\) refers to the branching order. The invariance leads to \( \gamma = n^{-1/3} \) and \( \xi = n^{-1/2} \), and these scaling parameters are equivalent to a **Lindenmayer system** (L-system), which is itself a space-filling **Peano curve** (Peano 1890) that uses a formal grammar.

## Volume and Mass Dimension Predictions

The volume \( V_B \) of a branching network in space can be described as:

\[
V_B = \pi \sum_{k=0}^{N} n_k r_k^2 l_k \approx \gamma \xi^2 V_N \left( 1 - n^{-4/3} \right) V_N
\]

*Equation 11*

where \( n_k \) is an arbitrary branching level, \( V_N \) is the total volume space occupied, and \( l_N \) is the length, while the branching ratios are given in Equation 10 (West et al. 2009).

Distinguishing the filled volume in which a branching network occupies is equivalent to:

\[
v_n \propto l_n^3
\]

In Euclidean space, this can be approximated by a sphere:

\[
v_n = \frac{4}{3} \pi l_n^{2/3}
\]

*Equation 12*

This gives the total volume filled by the network as:

\[
V_{\text{net}} = n_k v_k \propto n_k l_k^3
\]

*Equation 13*

where the occupied volume \( V_{\text{net}} \) is preserved throughout and can be approximated at any arbitrary branching level \(k\) as \(V_{\text{net}} \propto n_k l_k^3\).

## Differential Box-Counting Methodology

To derive the mass \( M_k \) of an individual by its branch volume \(V_B\), a non-fractal quantity is expressed as:

\[
V_B = v_i L^3
\]

*Equation 14*

where \(v_i\) is the volume in units of length \(L^3\). If we display a three-dimensional object in two dimensions, looking perpendicular to the principal axis of the network, the area \(A \approx V_{\text{net}}^{2/3}\) from Equation 7 can be expressed as:

\[
A \propto n^{2/3} l_N^{2}
\]

*Equation 15*

Measuring such an object with boxes \( \varepsilon^2 \) of area becomes:

\[
A \propto V_B^{1/2} l_N^{3/2} r_N \propto L^{3/2} l_N^{3/2} r_N
\]

*Equation 16*

The number of boxes required to measure the object is:

\[
N(\varepsilon) \propto \frac{A}{\varepsilon^2} \propto L^{3/2} l_N^{3/2} (\varepsilon r_N)
\]

*Equation 17*

As \( \varepsilon \to 0 \), \( \dim \to 2 \), and for the smallest observed branch size, \( \varepsilon \), it becomes:

\[
N(\varepsilon) \propto \varepsilon^{3/2}
\]

revealing the fractal dimension of branching network volume to be \( d = \frac{3}{2} \) (West et al., unpublished).

## FracLac Analysis Procedures

Images were analyzed using the open-source image analysis software **FracLac** for ImageJ. The fractal dimension was calculated using both regular box-counting and the differential box-count technique. For differential box-counting, a power series with an exponentially increasing box size factor of 0.1 was used.
