---
type: Fractal Proof
title: Mandelbrot Boundary — Hausdorff Dimension 2 (Shishikura)
description: The boundary of the Mandelbrot set has Hausdorff dimension 2 (Shishikura 1991/1998); this is asserted from the theorem and is not machine-verifiable.
tags: [complex-dynamics, dimension-theory]
timestamp: '2026-07-13T00:00:00Z'
result: "dim_H(∂M) = 2 (asserted, Shishikura)"
concept: ../concepts/complex-dynamics/mandelbrot-set.md
historical_source: Mitsuhiro Shishikura, "The Hausdorff dimension of the boundary of the Mandelbrot set and Julia sets" (announced 1991; Ann. of Math. 1998)
verification_status: unverified
---

# Statement

Let $\mathcal{M}$ be the Mandelbrot set and $\partial\mathcal{M}$ its boundary.
Then

$$
\dim_H(\partial\mathcal{M}) = 2,
$$

the maximal possible value for a subset of the plane. Moreover, for a generic
(residual) set of parameters $c \in \partial\mathcal{M}$, the corresponding
Julia set $J_c$ also has Hausdorff dimension $2$.

# Assumptions

1. $\dim_H$ denotes Hausdorff dimension in $\mathbb{C} \cong \mathbb{R}^2$.
2. The result concerns the boundary $\partial\mathcal{M}$, not $\mathcal{M}$
   itself (which is a full-measure planar region with topological dimension 2
   and trivially $\dim_H = 2$). The theorem's content is that the *boundary* —
   a topologically one-dimensional-looking curve — is as dimensionally rich as
   the plane.

# Proof

1. **[asserted]** *(Shishikura's theorem.)* The Hausdorff dimension of
   $\partial\mathcal{M}$ equals $2$. The proof uses the theory of
   **parabolic bifurcation** and holomorphic **motion / quadratic-like maps** to
   show that near-parabolic parameters produce Julia sets of dimension
   arbitrarily close to $2$, and transfers this to the boundary of $\mathcal{M}$
   via Douady–Hubbard's parameter–dynamical correspondence.
2. **[asserted]** The dimension-$2$ Julia-set statement for a residual set of
   $c \in \partial\mathcal{M}$ is obtained by the same near-parabolic
   enrichment argument.

# Verification

* **Not machine-verifiable.** This is a deep theorem of holomorphic dynamics; no
  finite symbolic or numerical computation establishes a Hausdorff-dimension
  statement about $\partial\mathcal{M}$. Numerical box-counting of rendered
  boundaries yields values that *drift upward toward 2* as resolution increases
  (consistent with, but not a proof of, the theorem) and can be shown as an
  illustration only — never as verification.
* This document is recorded as **`unverified`** deliberately: it is an important
  result that the history chapter should cite, and it serves as the bundle's
  template for "cited, load-bearing, but not machine-checkable." Contrast with
  [`mandelbrot-escape.md`](./mandelbrot-escape.md) (the radius-2 criterion),
  which *is* fully machine-verified.
* **Asserted from:** Shishikura (Ann. of Math. 1998; announced 1991).

# Historical source

Mitsuhiro Shishikura announced in 1991 (Stony Brook IMS preprint) and published
in 1998 (*Annals of Mathematics*) that the boundary of the Mandelbrot set has
Hausdorff dimension $2$, resolving a conjecture of Mandelbrot and settling how
irregular $\partial\mathcal{M}$ truly is. The proof introduced techniques
(parabolic bifurcation, dimension of near-parabolic Julia sets) that became
central to modern complex dynamics.

# Related concepts

* [Mandelbrot Set](../concepts/complex-dynamics/mandelbrot-set.md)
* [Julia Set](../concepts/complex-dynamics/julia-set.md)
* [Hausdorff Dimension](../concepts/dimension-theory/hausdorff-dimension.md)

# Citations

1. M. Shishikura, "The Hausdorff dimension of the boundary of the Mandelbrot set
   and Julia sets", *Annals of Mathematics* **147** (1998), 225–267 (announced:
   Stony Brook IMS preprint 1991/7).
2. A. Douady, J. H. Hubbard, "Étude dynamique des polynômes complexes",
   *Publ. Math. Orsay* (1984–85).
