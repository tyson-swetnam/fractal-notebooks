---
type: Fractal Proof
title: Menger Sponge — Similarity Dimension
description: The Menger sponge is self-similar with N=20 sub-cubes at ratio 1/3, giving Hausdorff dimension log 20 / log 3.
tags: [classics, dimension-theory]
timestamp: '2026-07-13T00:00:00Z'
result: "D = log 20 / log 3 ≈ 2.7268"
concept: ../concepts/classics/menger-sponge.md
historical_source: Karl Menger, "Allgemeine Räume und Cartesische Räume" (1926); "Kurventheorie" (1932)
verification_status: verified
---

# Statement

Let $M \subset [0,1]^3$ be the Menger sponge, the attractor of the iterated
function system consisting of the $N=20$ contractions $x \mapsto \tfrac{1}{3}x + t_j$,
where the translations $t_j$ index the twenty sub-cubes of the $3\times3\times3$
subdivision that remain after removing the central cube and the six face-centre
cubes. Then the similarity (Hausdorff) dimension of $M$ is

$$
D = \frac{\log 20}{\log 3} \approx 2.7268330278608.
$$

# Assumptions

1. $M$ is the unique nonempty compact attractor of $N=20$ similarities, each of
   ratio $r = 1/3$.
2. **Open set condition (OSC):** taking $U = (0,1)^3$, the twenty images
   $\tfrac{1}{3}U + t_j$ are pairwise disjoint open cubes contained in $U$. The
   OSC holds, so the similarity dimension equals the Hausdorff dimension
   (Moran 1946; Hutchinson 1981).
3. Counting: the $3\times3\times3=27$ sub-cubes minus the $1$ central cube minus
   the $6$ face-centre cubes leaves $27 - 7 = 20$.

# Proof

1. **[verified]** *Cube count.* The subdivision produces $27$ sub-cubes; the
   Menger removal deletes the body-centre cube and the six face-centre cubes,
   $27 - 7 = 20$. SymPy: `27 - 7 = 20`.
2. **[asserted]** By Moran's/Hutchinson's theorem, an IFS of similarities with
   ratio $r$ satisfying the OSC has an attractor of Hausdorff dimension solving
   the Moran equation $N r^{D} = 1$, i.e. $20\cdot(1/3)^{D} = 1$.
3. **[verified]** Solving $20\cdot 3^{-D} = 1$ gives $3^{D} = 20$, hence
   $D = \log 20/\log 3$. SymPy `log(20)/log(3)` evaluates to
   $2.726833027860842$.
4. **[verified]** *Consistency check.* Each face of the Menger sponge is a
   Sierpinski carpet, whose dimension $\log 8/\log 3 \approx 1.8928$ is strictly
   less than $D$, as required for a genuinely three-dimensional-in-detail object
   ($2 < D < 3$).

# Verification

* **Cube count (step 1):** integer arithmetic $27-7=20$.
* **Dimension (step 3):** SymPy solved $20\cdot 3^{-D}=1$ to `log(20)/log(3)`;
  `float` value $2.726833027860842$.
* **Face consistency (step 4):** $\log 8/\log 3 = 1.8927892607143724 < D$,
  confirmed numerically.
* **Asserted external result:** the Moran/Hutchinson OSC $\Rightarrow$
  Hausdorff-dimension identity (step 2). All quantitative outputs machine-checked.
* **Topological note (not required for the dimension):** Menger proved $M$ is a
  *universal curve* — it has topological dimension $1$ and contains a
  homeomorphic copy of every compact metric space of topological dimension
  $\le 1$. This is asserted from Menger's curve theory, not computed here.

# Historical source

Karl Menger introduced the sponge in his dimension-theory work of the 1920s–30s
(*Allgemeine Räume und Cartesische Räume*, 1926; *Kurventheorie*, 1932) as the
three-dimensional universal curve, generalising Cantor's set (1D removal) and
Sierpinski's carpet (2D removal). The similarity-dimension identification uses
the later Moran (1946) / Hutchinson (1981) framework.

# Related concepts

* [Menger Sponge](../concepts/classics/menger-sponge.md)
* [Sierpinski Triangle](../concepts/classics/sierpinski-triangle.md)
* [Cantor Set](../concepts/classics/cantor-set.md)
* [Hausdorff Dimension](../concepts/dimension-theory/hausdorff-dimension.md)

# Citations

1. K. Menger, "Allgemeine Räume und Cartesische Räume. Erste Mitteilung",
   *Proc. Akad. Wetensch. Amsterdam* **29** (1926), 476–482.
2. P. A. P. Moran, "Additive functions of intervals and Hausdorff measure",
   *Proc. Cambridge Philos. Soc.* **42** (1946), 15–23.
3. J. E. Hutchinson, "Fractals and self-similarity", *Indiana Univ. Math. J.*
   **30** (1981), 713–747.
4. K. Falconer, *Fractal Geometry: Mathematical Foundations and Applications*,
   3rd ed., Wiley (2014), §9.1.
