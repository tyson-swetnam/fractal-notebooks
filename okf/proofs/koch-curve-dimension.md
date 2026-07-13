---
type: Fractal Proof
title: Koch Curve — Dimension, Perimeter, and Area
description: The Koch curve has Hausdorff dimension log 4 / log 3, infinite length, and the Koch snowflake encloses finite area equal to 8/5 of the seed triangle.
tags: [classics, dimension-theory]
timestamp: '2026-07-13T00:00:00Z'
result: "D = log 4 / log 3 ≈ 1.2619; perimeter → ∞; snowflake area = (8/5) A0"
concept: ../concepts/classics/koch-curve.md
historical_source: Helge von Koch, "Sur une courbe continue sans tangente, obtenue par une construction géométrique élémentaire", Arkiv för Matematik 1 (1904)
verification_status: verified
---

# Statement

Let $K$ be the Koch curve, the attractor of the IFS of four similarities each
of ratio $r=1/3$ that replace a segment by a four-segment "bump". Then:

1. The similarity (Hausdorff) dimension is
   $$D=\frac{\log 4}{\log 3}\approx 1.2618595071429148.$$
2. The curve has infinite length: the length after $n$ generations is
   $(4/3)^{n}L_0\to\infty$.
3. The Koch snowflake (three Koch curves on the sides of an equilateral
   triangle of area $A_0$) encloses finite area
   $$A_\infty=\frac{8}{5}A_0.$$

# Assumptions

1. $K$ is the attractor of $N=4$ contracting similarities with equal ratio
   $r=1/3$.
2. **Open set condition (OSC):** the four maps send an open triangular/segment
   neighbourhood $U$ into disjoint sub-copies, $f_i(U)\cap f_j(U)=\varnothing$
   for $i\ne j$; this licenses similarity dimension $=$ Hausdorff dimension.
3. Each generation replaces every segment of length $\ell$ by four segments of
   length $\ell/3$; areas of added triangles scale as $(1/9)$ per generation.

# Proof

1. **[asserted]** By Moran/Hutchinson under the OSC, $D$ solves the Moran
   equation $\sum_{i=1}^{4}(1/3)^{D}=1$, i.e. $4\cdot 3^{-D}=1$.
2. **[verified]** Solving $4\cdot 3^{-D}=1$ gives $3^{D}=4$, so
   $D=\log 4/\log 3$. SymPy `solve(4*(1/3)**D - 1, D)` returns
   `2*log(2)/log(3)` $=\log 4/\log 3$, numerically $1.2618595071429148$.
3. **[verified]** *Infinite length.* Generation $n$ has $4^{n}$ segments each
   of length $(1/3)^{n}L_0$, so total length $L_n=(4/3)^{n}L_0$. SymPy
   `limit((4/3)**n, n, oo) = oo`; since $4/3>1$ the length diverges, and $K$ is
   not rectifiable.
4. **[verified]** *Finite snowflake area.* Start from the equilateral triangle
   of area $A_0$. At generation $n\ge 1$ one adds $3\cdot 4^{\,n-1}$ new
   triangles, each of area $A_0\,(1/9)^{n}$ (each added bump triangle is scaled
   by $1/3$ in length, hence $1/9$ in area, relative to the previous
   generation). The total added area is the convergent geometric series
   $$\sum_{n=1}^{\infty} 3\cdot 4^{\,n-1}\,A_0\,\Big(\tfrac{1}{9}\Big)^{n}
     =\frac{3A_0}{4}\sum_{n=1}^{\infty}\Big(\tfrac{4}{9}\Big)^{n}
     =\frac{3A_0}{4}\cdot\frac{4/9}{1-4/9}=\frac{3}{5}A_0,$$
   so the enclosed area is $A_\infty=A_0+\tfrac{3}{5}A_0=\tfrac{8}{5}A_0$.
5. **[verified]** SymPy `A0 + summation(3*4**(n-1)*A0*(1/9)**n, (n,1,oo))`
   simplifies to `8*A0/5` exactly, confirming that a boundary of infinite
   length encloses a finite area.

# Verification

* **Dimension (step 2):** SymPy `solve(4*3**(-D)-1, D) = 2*log(2)/log(3)`,
  `float` $1.2618595071429148$; matches the Moran root for $N=4,\ r=1/3$.
* **Perimeter (step 3):** SymPy `limit((4/3)**n, n, oo) = oo` — length diverges
  geometrically with ratio $4/3$.
* **Snowflake area (step 4–5):** SymPy
  `A0 + summation(3*4**(n-1)*A0*(1/9)**n, (n,1,oo))` simplifies to `8*A0/5`
  exactly (closed-form geometric series with ratio $4/9$): added area
  $3A_0/5$, total $8A_0/5$.
* **Asserted external result:** Moran/Hutchinson OSC ⇒ Hausdorff-dimension
  identity (step 1).

# Historical source

Helge von Koch defined the curve in 1904 as an elementary geometric example of
a continuous curve lacking a tangent at every point (nowhere differentiable),
predating and complementing Weierstrass's analytic 1872 example. The snowflake
variant and its area/perimeter paradox are standard consequences.

# Related concepts

* [Koch Curve](../concepts/classics/koch-curve.md)
* [Hausdorff Dimension](../concepts/dimension-theory/hausdorff-dimension.md)
* [Self-Similarity](../concepts/geometry/self-similarity.md)
* [Iterated Function System](../concepts/ifs/iterated-function-system.md)

# Citations

1. H. von Koch, "Sur une courbe continue sans tangente, obtenue par une
   construction géométrique élémentaire", *Arkiv för Matematik* **1** (1904),
   681–704.
2. J. E. Hutchinson, "Fractals and self-similarity", *Indiana Univ. Math. J.*
   **30** (1981), 713–747.
3. K. Falconer, *Fractal Geometry*, 3rd ed., Wiley (2014), §2.2, §9.2.
4. B. B. Mandelbrot, *The Fractal Geometry of Nature*, Freeman (1982), ch. 6.
