---
type: Fractal Proof
title: Sierpinski Triangle and Carpet — Dimensions
description: The Sierpinski triangle has Hausdorff dimension log 3 / log 2 and the Sierpinski carpet log 8 / log 3, both via the open-set condition.
tags: [classics, dimension-theory]
timestamp: '2026-07-13T00:00:00Z'
result: "Triangle D = log 3 / log 2 ≈ 1.5850; Carpet D = log 8 / log 3 ≈ 1.8928"
concept: ../concepts/classics/sierpinski-triangle.md
historical_source: Wacław Sierpiński, "Sur une courbe cantorienne qui contient une image biunivoque et continue de toute courbe donnée", C. R. Acad. Sci. Paris 162 (1916); triangle 1915
verification_status: verified
---

# Statement

1. **Sierpinski triangle** $S_\triangle$ — the attractor of $N=3$ similarities
   of ratio $r=1/2$ (the three corner half-copies of a triangle) — has
   similarity (Hausdorff) dimension
   $$D_\triangle=\frac{\log 3}{\log 2}\approx 1.584962500721156.$$
2. **Sierpinski carpet** $S_\square$ — the attractor of $N=8$ similarities of
   ratio $r=1/3$ (the eight non-central cells of a $3\times3$ grid on a
   square) — has similarity (Hausdorff) dimension
   $$D_\square=\frac{\log 8}{\log 3}\approx 1.8927892607143724.$$

# Assumptions

1. $S_\triangle$ is the attractor of $N=3$ contracting similarities with equal
   ratio $r=1/2$; $S_\square$ of $N=8$ contracting similarities with equal
   ratio $r=1/3$.
2. **Open set condition (OSC):** for the triangle, the interiors of the three
   half-scale copies are pairwise disjoint (open set $U=$ interior of the seed
   triangle); for the carpet, the eight $1/3$-scale sub-squares have pairwise
   disjoint interiors (open set $U=$ open unit square). Under the OSC the
   similarity dimension equals the Hausdorff dimension.
3. Both dimensions lie strictly between the topological dimension ($1$ for the
   triangle's gasket structure, $1$ for the carpet) and the ambient dimension
   $2$.

# Proof

1. **[asserted]** By Moran/Hutchinson under the OSC, the dimension $D$ of an
   equal-ratio IFS attractor solves the Moran equation $N\,r^{D}=1$.
2. **[verified]** *Triangle.* Solving $3\cdot(1/2)^{D}=1$ gives $2^{D}=3$, so
   $D_\triangle=\log 3/\log 2$. SymPy `solve(3*(1/2)**D - 1, D)` returns
   `log(3)/log(2)`, numerically $1.584962500721156$.
3. **[verified]** *Carpet.* Solving $8\cdot(1/3)^{D}=1$ gives $3^{D}=8$, so
   $D_\square=\log 8/\log 3$. SymPy `solve(8*(1/3)**D - 1, D)` returns
   `3*log(2)/log(3)` $=\log 8/\log 3$, numerically $1.8927892607143724$.
4. **[verified]** *Measure/area consistency (sanity check).* Each fractal is a
   $\lambda$-null set in $\mathbb{R}^2$: the triangle retains a fraction
   $(3/4)^{k}\to 0$ of the seed area after $k$ steps (removing one of four
   sub-triangles each step), and the carpet retains $(8/9)^{k}\to 0$
   (removing the central one of nine sub-squares each step). Both limits are
   $0$, consistent with $D<2$.
5. **[verified]** Both computed dimensions satisfy $1<D<2$, placing each set
   strictly between a curve and a filled region, as required of a planar
   fractal.

# Verification

* **Triangle (step 2):** SymPy `solve(3*2**(-D)-1, D) = log(3)/log(2)`, `float`
  $1.584962500721156$; matches the Moran root for $N=3,\ r=1/2$.
* **Carpet (step 3):** SymPy `solve(8*3**(-D)-1, D) = 3*log(2)/log(3)`, `float`
  $1.8927892607143724$; matches the Moran root for $N=8,\ r=1/3$.
* **Area decay (step 4):** ratios $3/4<1$ and $8/9<1$ give geometric decay to
  measure zero — elementary, machine-confirmable on finite $k$.
* **Asserted external result:** Moran/Hutchinson OSC ⇒ Hausdorff-dimension
  identity (step 1).

# Historical source

Wacław Sierpiński introduced the triangle (gasket) in 1915 and the carpet in
1916 as examples of curves — in the topological sense — that are universal for
planar continua. The Sierpinski carpet is the planar analogue whose
three-dimensional generalization is the Menger sponge (Menger 1926). Dimension
values follow from the later Moran/Hausdorff self-similarity framework.

# Related concepts

* [Sierpinski Triangle](../concepts/classics/sierpinski-triangle.md)
* [Menger Sponge](../concepts/classics/menger-sponge.md) — 3-D generalization of the carpet
* [Hausdorff Dimension](../concepts/dimension-theory/hausdorff-dimension.md)
* [Self-Similarity](../concepts/geometry/self-similarity.md)
* [Iterated Function System](../concepts/ifs/iterated-function-system.md)

# Citations

1. W. Sierpiński, "Sur une courbe dont tout point est un point de
   ramification", *C. R. Acad. Sci. Paris* **160** (1915), 302–305 (triangle).
2. W. Sierpiński, "Sur une courbe cantorienne qui contient une image
   biunivoque et continue de toute courbe donnée", *C. R. Acad. Sci. Paris*
   **162** (1916), 629–632 (carpet).
3. K. Menger, "Allgemeine Räume und Cartesische Räume", *Proc. Akad.
   Wetenschappen Amsterdam* **29** (1926), 476–482 (sponge).
4. J. E. Hutchinson, "Fractals and self-similarity", *Indiana Univ. Math. J.*
   **30** (1981), 713–747.
5. K. Falconer, *Fractal Geometry*, 3rd ed., Wiley (2014), §9.
