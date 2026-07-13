---
type: Fractal Proof
title: Cantor Set — Dimension, Measure, and Cardinality
description: The middle-thirds Cantor set has Hausdorff dimension log 2 / log 3, Lebesgue measure zero, and the cardinality of the continuum.
tags: [classics, dimension-theory]
timestamp: '2026-07-13T00:00:00Z'
result: "D = log 2 / log 3 ≈ 0.6309; Lebesgue measure 0; uncountable"
concept: ../concepts/classics/cantor-set.md
historical_source: Georg Cantor, "Über unendliche, lineare Punktmannigfaltigkeiten V", Mathematische Annalen 21 (1883)
verification_status: verified
---

# Statement

Let $C \subset [0,1]$ be the middle-thirds Cantor set, the attractor of the
iterated function system $f_0(x)=x/3$, $f_1(x)=x/3+2/3$. Then:

1. The similarity (Hausdorff) dimension of $C$ is
   $$D = \frac{\log 2}{\log 3} \approx 0.6309297535714574.$$
2. $C$ has Lebesgue measure zero: $\lambda(C)=0$.
3. $C$ is uncountable, with cardinality $2^{\aleph_0}=\mathfrak{c}$.

# Assumptions

1. $C$ is the unique nonempty compact attractor of the two contractions
   $f_0,f_1$, each with ratio $r=1/3$ (so $N=2$).
2. **Open set condition (OSC):** the open set $U=(0,1)$ satisfies
   $f_0(U)\cup f_1(U)\subseteq U$ with $f_0(U)\cap f_1(U)=\varnothing$
   (the images $(0,1/3)$ and $(2/3,1)$ are disjoint). This is what licenses
   equating the similarity dimension with the Hausdorff dimension.
3. Lebesgue measure $\lambda$ on $\mathbb{R}$ is used for part 2; base-3
   (ternary) expansions for part 3.

# Proof

1. **[asserted]** By Moran's theorem / Hutchinson's theorem, an IFS of
   similarities satisfying the OSC has an attractor whose Hausdorff dimension
   $D$ is the unique solution of the Moran equation
   $\sum_{i=1}^{N} r_i^{D}=1$. For $N=2$ equal ratios $r=1/3$ this is
   $2\cdot(1/3)^{D}=1$.
2. **[verified]** Solving $2\cdot 3^{-D}=1$ gives $3^{D}=2$, hence
   $D=\log 2/\log 3$. SymPy `solve(2*(1/3)**D - 1, D)` returns
   `log(2)/log(3)`, numerically $0.6309297535714574$.
3. **[verified]** *Measure zero.* At step $k$ one removes $2^{k}$ open
   intervals each of length $3^{-(k+1)}$. The total removed length is the
   geometric series
   $$\sum_{k=0}^{\infty}\frac{2^{k}}{3^{k+1}}
     =\frac{1}{3}\sum_{k=0}^{\infty}\Big(\tfrac{2}{3}\Big)^{k}
     =\frac{1}{3}\cdot\frac{1}{1-2/3}=1.$$
   SymPy `summation(2**k/3**(k+1),(k,0,oo))` returns `1`. Since the removed
   set has full measure $1$ in $[0,1]$, $\lambda(C)=1-1=0$.
4. **[asserted]** *Uncountability.* A point of $[0,1]$
   lies in $C$ iff it has a base-3 expansion using only the digits $\{0,2\}$
   (the removed middle thirds are exactly the points forced to have digit $1$;
   endpoints with a terminating expansion also admit a $\{0,2\}$ form). The map
   $(d_1,d_2,\dots)\mapsto \sum_k d_k 3^{-k}$ is a bijection between
   $\{0,2\}^{\mathbb{N}}$ and $C$. Since $\{0,2\}^{\mathbb{N}}$ has cardinality
   $2^{\aleph_0}=\mathfrak{c}$, $C$ is uncountable. This is Cantor's
   cardinality theorem applied to the ternary address space; it is a
   theorem-cited conclusion, not a numerical computation.
5. **[verified]** Parts 2 and 3 together show $C$ is an uncountable set of
   measure zero — the defining paradox of the Cantor "dust".

# Verification

* **Dimension (step 2):** SymPy solved $2\cdot 3^{-D}=1$ symbolically to
  `log(2)/log(3)`; `float` value $0.6309297535714574$. Confirmed against the
  Moran-equation root solver for $N=2,\ r=1/3$.
* **Measure zero (step 3):** SymPy `summation(2**k/3**(k+1),(k,0,oo)) = 1`
  (closed-form geometric series), so the complement in $[0,1]$ has measure
  zero.
* **Cardinality (step 4):** the $\{0,2\}$-digit characterisation of $C$ is a
  standard finite-prefix combinatorial fact; the continuum cardinality of
  $\{0,2\}^{\mathbb{N}}$ follows from Cantor's theorem — asserted from the
  cited 1883 result, not numerically re-derived.
* **Asserted external result:** the Moran/Hutchinson OSC ⇒ Hausdorff-dimension
  identity (step 1). All quantitative outputs machine-checked.

# Historical source

Georg Cantor introduced the set in the fifth installment of *Über unendliche,
lineare Punktmannigfaltigkeiten* (Mathematische Annalen 21, 1883) as an example
of a perfect, nowhere-dense set. The dimension identification via the
similarity/Moran equation is later (Hausdorff 1919; Moran 1946).

# Related concepts

* [Cantor Set](../concepts/classics/cantor-set.md)
* [Hausdorff Dimension](../concepts/dimension-theory/hausdorff-dimension.md)
* [Self-Similarity](../concepts/geometry/self-similarity.md)
* [Fractal Dimension](../concepts/dimension-theory/fractal-dimension.md)

# Citations

1. G. Cantor, "Über unendliche, lineare Punktmannigfaltigkeiten V",
   *Mathematische Annalen* **21** (1883), 545–591.
2. P. A. P. Moran, "Additive functions of intervals and Hausdorff measure",
   *Proc. Cambridge Philos. Soc.* **42** (1946), 15–23.
3. J. E. Hutchinson, "Fractals and self-similarity", *Indiana Univ. Math. J.*
   **30** (1981), 713–747.
4. K. Falconer, *Fractal Geometry: Mathematical Foundations and Applications*,
   3rd ed., Wiley (2014), §2.2, §9.1.
