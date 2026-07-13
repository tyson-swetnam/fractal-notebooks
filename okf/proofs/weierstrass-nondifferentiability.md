---
type: Fractal Proof
title: Weierstrass Function - Continuous Everywhere, Differentiable Nowhere
description: The Weierstrass function converges uniformly (so is continuous) yet is nowhere differentiable when $ab>1+\tfrac{3\pi}{2}$, later relaxed by Hardy to $ab\ge1$.
tags: [analysis, non-differentiability, weierstrass, continuity]
timestamp: '2026-07-13T00:00:00Z'
result: "Continuous everywhere; nowhere differentiable for ab > 1 + 3pi/2 (Hardy: ab >= 1)"
concept: ../concepts/geometry/fractal.md
historical_source: Karl Weierstrass, presented to the Berlin Academy 1872; G. H. Hardy, "Weierstrass's non-differentiable function" (1916).
verification_status: partially-verified
---

# Statement

Let $W(x)=\sum_{n=0}^{\infty} a^n \cos(b^n \pi x)$ with $0<a<1$ and $b$ a
positive odd integer. Then:

1. $W$ is **continuous** on all of $\mathbb{R}$.
2. $W$ is **differentiable nowhere** provided $ab>1+\tfrac{3\pi}{2}$
   (Weierstrass's original condition). Hardy (1916) showed non-differentiability
   holds under the weaker condition $ab\ge 1$ (with $0<a<1$, $b>1$).

# Assumptions

1. $0<a<1$ ensures the amplitude series $\sum a^n$ converges (geometric).
2. Weierstrass's construction takes $b$ an odd integer and couples $a,b$ via
   $ab>1+\tfrac{3\pi}{2}$; Hardy removed the integer/odd restriction and
   weakened the coupling to $ab\ge1$.

# Proof

1. **[verified]** *(Continuity via the Weierstrass M-test.)* Each term
   satisfies $|a^n\cos(b^n\pi x)|\le a^n=:M_n$, and $\sum_{n\ge0}M_n=
   \frac{1}{1-a}<\infty$ since $0<a<1$. By the M-test the series converges
   **uniformly**; a uniform limit of continuous functions is continuous, so
   $W\in C(\mathbb{R})$.
2. **[asserted]** *(Nowhere differentiability, Weierstrass 1872.)* Under
   $ab>1+\tfrac{3\pi}{2}$ and $b$ odd, for every $x_0$ one constructs two
   sequences of points approaching $x_0$ from opposite sides along which the
   difference quotients grow without bound with opposite signs, so no finite
   derivative can exist. The threshold constant is
   $1+\tfrac{3\pi}{2}=5.71238898038469$.
3. **[asserted]** *(Hardy's sharpening, 1916.)* Hardy proved that
   $0<a<1,\ b>1,\ ab\ge1$ already forces non-differentiability everywhere,
   dropping both the oddness of $b$ and the larger constant.

# Verification

- **Symbolic (SymPy):** the Weierstrass threshold constant evaluates to
  $1+\tfrac{3\pi}{2}=5.71238898038469$ (confirmed).
- **Verified reasoning:** Step 1 (continuity) is fully verified — the M-test
  bound $M_n=a^n$ with $\sum a^n=1/(1-a)<\infty$ is elementary and machine-
  confirmable.
- **Asserted:** Steps 2-3 (nowhere differentiability) are the conclusions of
  Weierstrass (1872) and Hardy (1916); they are cited, not re-derived here. No
  finite computation can establish "no derivative exists at any point."

# Historical source

Karl Weierstrass presented the function to the Royal Prussian Academy of
Sciences in Berlin in 1872 as the first published example of a continuous
nowhere-differentiable function. G. H. Hardy gave the definitive analysis and
weakened the hypothesis to $ab\ge1$ in 1916.

# Related concepts

- [Fractal](../concepts/geometry/fractal.md)
- [Self-affinity](../concepts/geometry/self-affinity.md)

# Citations

1. Weierstrass, K. "Uber continuirliche Functionen eines reellen Arguments, die fur keinen Werth des letzteren einen bestimmten Differentialquotienten besitzen." Read to the Berlin Academy, 18 July 1872.
2. Hardy, G. H. "Weierstrass's non-differentiable function." *Transactions of the American Mathematical Society* 17 (1916): 301-325.
