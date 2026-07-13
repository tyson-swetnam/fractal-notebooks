---
type: Fractal Proof
title: Fatou-Julia Connectedness Dichotomy
description: The Julia set $J_c$ of $z^2+c$ is connected iff the critical orbit is bounded ($c\in M$); otherwise it is totally disconnected Cantor dust.
tags: [complex-dynamics, julia-set, connectedness, fatou-julia]
timestamp: '2026-07-13T00:00:00Z'
result: "J_c connected iff 0 in K_c iff c in Mandelbrot set; else totally disconnected"
concept: ../concepts/complex-dynamics/julia-set.md
historical_source: Pierre Fatou and Gaston Julia, independent memoirs 1917-1919 (Julia, "Memoire sur l'iteration des fonctions rationnelles", 1918).
verification_status: partially-verified
---

# Statement

For $f_c(z)=z^2+c$ let $K_c=\{z:\ (f_c^n(z))_n \text{ bounded}\}$ be the filled
Julia set and $J_c=\partial K_c$ the Julia set. Then exactly one of two cases
holds:

- If the critical orbit is bounded — equivalently $0\in K_c$, equivalently
  $c\in M$ (the Mandelbrot set) — then $J_c$ is **connected**.
- Otherwise ($0\notin K_c$, $c\notin M$) $J_c$ is **totally disconnected**: a
  Cantor set ("Cantor dust"), and $K_c=J_c$.

# Assumptions

1. Quadratic family $f_c(z)=z^2+c$; $0$ is the unique finite critical point.
2. The dichotomy is a statement about the topology of $J_c$ as $c$ varies.

# Proof

1. **[asserted]** *(Fatou-Julia dichotomy for the quadratic family.)* The
   connectedness of $J_c$ is governed entirely by the fate of the critical
   orbit: $J_c$ connected $\iff$ the orbit of the critical point $0$ is
   bounded. This is the central theorem of Fatou (1917-1920) and Julia (1918),
   as sharpened by Douady-Hubbard.
2. **[asserted]** Boundedness of the critical orbit $(f_c^n(0))$ is by
   definition membership $c\in M$. Hence $J_c$ connected $\iff c\in M$.
3. **[asserted]** In the escaping case $c\notin M$, the pullback of a large
   disc under $f_c$ produces two disjoint preimages at every level; the nested
   intersection is a totally disconnected, perfect, compact set — a Cantor set
   — on which $f_c$ acts as the full 2-shift (Böttcher/symbolic-dynamics
   argument, Douady-Hubbard).

# Verification

- **Not machine-verified.** This document records a named theorem; the
  dichotomy is asserted, not re-derived. No SymPy/NumPy computation can
  establish a topological connectedness statement for all $c$.
- The *link* between "critical orbit bounded" and "$c\in M$" is definitional
  and consistent with the [Mandelbrot escape criterion](./mandelbrot-escape.md),
  which **is** machine-verified. That connection is the only computationally
  checkable piece and it is checked there.
- **Asserted from:** the Fatou-Julia theorem (Fatou 1917-1920; Julia 1918) and
  the Douady-Hubbard formalization of the quadratic family.

# Historical source

Gaston Julia, "Memoire sur l'iteration des fonctions rationnelles," *Journal de
Mathematiques Pures et Appliquees* (1918); Pierre Fatou, "Sur les equations
fonctionnelles," *Bulletin de la S.M.F.* (1919-1920). The two developed the
iteration theory of rational maps independently and near-simultaneously.

# Related concepts

- [Julia set](../concepts/complex-dynamics/julia-set.md)
- [Mandelbrot set](../concepts/complex-dynamics/mandelbrot-set.md)
- [Cantor set](../concepts/classics/cantor-set.md)

# Citations

1. Julia, G. "Memoire sur l'iteration des fonctions rationnelles." *J. Math. Pures Appl.* 8 (1918): 47-245.
2. Fatou, P. "Sur les equations fonctionnelles." *Bull. Soc. Math. France* 47-48 (1919-1920).
3. Douady, A., Hubbard, J. H. "Etude dynamique des polynomes complexes." *Publ. Math. Orsay* (1984-85).
