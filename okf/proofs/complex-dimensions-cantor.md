---
type: Fractal Proof
title: Complex Dimensions of the Cantor String
description: The geometric zeta function of the Cantor string has poles at $\omega_k = \tfrac{\log 2}{\log 3} + i\tfrac{2\pi k}{\log 3}$; the real part is the Minkowski dimension, the imaginary parts encode log-periodic oscillations.
tags: [dimension-theory, complex-dimensions, cantor, zeta-function]
timestamp: '2026-07-13T00:00:00Z'
result: "omega_k = log2/log3 + i*2*pi*k/log3 ; oscillation period 2pi/log3"
concept: ../concepts/dimension-theory/complex-dimensions.md
historical_source: M. L. Lapidus and M. van Frankenhuijsen, "Fractal Geometry, Complex Dimensions and Zeta Functions" (2006); theory developed 1990s-2000s.
verification_status: verified
---

# Statement

The Cantor string $\mathcal{L}$ has lengths $\ell_j$ occurring with
multiplicities matching the middle-thirds construction, giving geometric zeta
function

$$\zeta_{\mathcal L}(s)=\frac{3^{-s}}{1-2\cdot 3^{-s}}.$$

Its poles — the **complex dimensions** of the Cantor set — are

$$\omega_k=\frac{\log 2}{\log 3}+i\,\frac{2\pi k}{\log 3},\qquad k\in\mathbb{Z}.$$

The real part $\operatorname{Re}\omega_k=\log 2/\log 3$ is the Minkowski (box)
dimension; the nonzero imaginary parts, spaced by the period
$\mathbf{p}=2\pi/\log 3$, generate the log-periodic oscillations in the
geometric counting function.

# Assumptions

1. Self-similar Cantor string built from the ratio-$1/3$ middle-thirds
   construction, so the scaling ratio is $r=1/3$ with $2$ pieces.
2. Complex dimensions are defined as the poles of the meromorphic continuation
   of $\zeta_{\mathcal L}$ (Lapidus-van Frankenhuijsen framework).

# Proof

1. **[verified]** *(Pole equation.)* Poles occur where the denominator
   vanishes: $1-2\cdot 3^{-s}=0\iff 3^{-s}=\tfrac12\iff -s\log 3=-\log 2 + 2\pi i k$,
   giving $s=\dfrac{\log 2}{\log 3}+i\dfrac{2\pi k}{\log 3}$.
2. **[verified]** *(These are exactly zeros of the denominator.)* Substituting
   $\omega_k$, one gets $3^{-\omega_k}=3^{-\log2/\log3}\cdot e^{-2\pi i k}
   =\tfrac12\cdot 1=\tfrac12$ for every integer $k$, so
   $1-2\cdot 3^{-\omega_k}=0$. SymPy simplifies $3^{-\omega_k}$ to exactly
   $1/2$.
3. **[asserted]** *(Interpretation of the pole data.)* $\operatorname{Re}\omega_k
   =\log2/\log3=0.6309297535714574$ equals the Minkowski/box dimension of the
   Cantor set. The imaginary parts $2\pi k/\log 3$ are integer multiples of the
   oscillatory period $\mathbf{p}=2\pi/\log 3=5.719201734760254$ (both numeric
   values machine-checked); their *role* as the source of the log-periodic
   (multiplicatively periodic) fluctuations in the volume of tubular
   neighborhoods is the interpretation supplied by the Lapidus-van
   Frankenhuijsen tube formula, asserted here rather than re-derived.

# Verification

- **Symbolic (SymPy):** `simplify(3**(-omega_k))` returns exactly $1/2$ for
  integer $k$, and the denominator $1-2\cdot 3^{-\omega_k}$ evaluates to
  $0+0i$ at $k=0,1,2$ (confirmed to machine precision).
- **Numerical:** $\operatorname{Re}\omega=\log2/\log3=0.6309297535714574$
  matches the Cantor Minkowski dimension; oscillation period
  $2\pi/\log3=5.719201734760254$ (both confirmed).
- **Asserted:** the identification of $\zeta_{\mathcal L}$'s poles with the
  "complex dimensions" and their role in the tube-formula oscillation is the
  Lapidus-van Frankenhuijsen theory — the framework is cited; the pole
  locations within it are the machine-verified part.

# Historical source

The theory of complex dimensions and geometric zeta functions was developed by
Michel Lapidus and collaborators through the 1990s-2000s, consolidated in
Lapidus & van Frankenhuijsen (2006).

# Related concepts

- [Complex dimensions](../concepts/dimension-theory/complex-dimensions.md)
- [Cantor set](../concepts/classics/cantor-set.md)
- [Riemann zeta function](../concepts/number-theory/riemann-zeta-function.md)
- [Box-counting dimension](../concepts/dimension-theory/box-counting-dimension.md)

# Citations

1. Lapidus, M. L., van Frankenhuijsen, M. *Fractal Geometry, Complex Dimensions and Zeta Functions: Geometry and Spectra of Fractal Strings.* Springer (2006).
2. Lapidus, M. L., Pomerance, C. "The Riemann zeta-function and the one-dimensional Weyl-Berry conjecture for fractal drums." *Proc. London Math. Soc.* 66 (1993): 41-69.
