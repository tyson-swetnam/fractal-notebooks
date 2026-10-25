---
type: Index
title: "Part I: Foundations"
description: >-
  Landing page for Part I: four tutorial chapters on the history of fractal
  mathematics, dimension theory and measurement methods, fractals from 1D
  signals to 4D spacetime, and a glossary with the key equations, plus their
  companion Jupyter notebooks and a recommended reading order.
resource: https://tyson-swetnam.github.io/fractal-notebooks/foundations/
tags: [foundations, part-i, geometry, dimension-theory, jupyter]
generated:
  by: claude-code/claude-fable-5-1
  at: "2026-10-24T00:00:00Z"
status: stable
---

# Part I: Foundations

Part I is the tutorial half of this site. Four chapters build the vocabulary and the measurement tools that the research manuscripts in Parts II–V take for granted: where fractal geometry came from, how dimension is defined and estimated, what fractals look like in one to four dimensions, and a glossary of the terms and equations used throughout.

## The Four Chapters

| Chapter | Page | What it covers |
|---|---|---|
| 1 | [History of Fractal Mathematics](history.md) | From Cantor to Mandelbrot to modern complex dimensions; self-similarity versus self-affinity; fractals enter biology; an appendix of machine-checked proofs |
| 2 | [Mathematical Foundations of Fractals](mathematics.md) | Hausdorff dimension, box-counting and differential box-counting, power laws, the Hurst exponent and lacunarity |
| 3 | [Fractal Dimensionality (1D through 4D)](dimensionality.md) | 1D through 4D fractals with examples: 1/f noise, Brownian surfaces, Mandelbrot and Julia sets, the Menger sponge, DLA, branching networks and spacetime |
| 4 | [Glossary and Equations](glossary.md) | Quick reference for terms and formulas, including the Barnsley fern IFS maps and the ten key equations |

## Recommended Reading Order

1. **Chapter 1** first if you are new to fractals: it motivates every later definition historically and ends with the self-similar/self-affine distinction that organises the whole project.
2. **Chapter 2** next, for the measurement tools (box-counting, differential box-counting, the Hurst exponent) that the Part II methods apply to leaves, branches and forest canopies.
3. **Chapter 3** can be read selectively by dimension: §3.1 for signals and time series, §3.2 for images and terrain, §3.3 for branching networks and DLA, §3.4 for growth dynamics.
4. **Chapter 4** is a reference rather than a read-through; return to it whenever a symbol or term is unfamiliar.

Readers who come for the biology can start at [Chapter 1 §1.5](history.md#15-fractals-enter-biology-sernetz-west-brown-enquist) and continue straight to [Part II: Metabolic Scaling Theory](../metabolic-scaling/index.md).

## Companion Notebooks

<div class="grid cards" markdown>

-   :material-notebook:{ .lg .middle } **Run the chapters as code**

    ---

    Each chapter has a Jupyter notebook that reproduces its figures and computations. The notebooks are rendered as pages with their stored outputs; the source `.ipynb` files live under `docs/notebooks/foundations/` in the repository.

    - [Chapter 1 notebook — History of fractals](../notebooks/foundations/1_history.md)
    - [Chapter 2 notebook — Mathematical foundations](../notebooks/foundations/2_mathematics.md)
    - [Chapter 3 notebook — Fractal dimensionality](../notebooks/foundations/3_dimensionality.md)
    - [Zeta space notebook — Riemann zeta visualisations](../notebooks/foundations/4_zeta_space.md) that bridge §1.6 of Chapter 1 and Part III

    [:octicons-arrow-right-24: All notebooks](../notebooks/index.md)

</div>

## Where to Go Next

- Look up a term or formula in the [Glossary and Equations](glossary.md).
- Browse the machine-readable [knowledge bundles](../okf/index.md): the concept ontology and the verified proofs cited from Chapter 1.
- Continue to the research manuscripts, starting with [Part II: Metabolic Scaling Theory](../metabolic-scaling/index.md).
