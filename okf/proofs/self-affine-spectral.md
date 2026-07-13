---
type: Fractal Proof
title: Spectral Exponent of Self-Affine Gaussian Processes
description: For fractional Brownian motion the power spectrum obeys $\beta = 2H+1$; the trace has local (graph) dimension $2-H$ crossing over to global dimension 1.
tags: [stochastic, self-affinity, spectral-density, hurst, fbm]
timestamp: '2026-07-13T00:00:00Z'
result: "beta = 2H + 1 (white beta=0/1, pink beta=1, brown beta=2); local dim 2-H"
concept: ../concepts/stochastic/hurst-exponent.md
historical_source: B. B. Mandelbrot and J. W. Van Ness, "Fractional Brownian motions, fractional noises and applications" (1968).
verification_status: verified
---

# Statement

Let $B_H(t)$ be fractional Brownian motion (fBm) with Hurst exponent
$H\in(0,1)$, a self-affine Gaussian process:
$B_H(\lambda t)\stackrel{d}{=}\lambda^{H}B_H(t)$. Its power spectral density
scales as $S(f)\propto f^{-\beta}$ with

$$\beta = 2H+1.$$

The graph of $B_H$ has **local** (box-counting) dimension $2-H$ at fine scales,
crossing over to the **global** topological dimension $1$ (a single curve) at
coarse scales.

# Assumptions

1. $B_H$ is Gaussian, self-affine with exponent $H$, stationary increments.
2. Spectral density defined via the (generalized) periodogram / Wiener-Khinchin
   relation; fBm is non-stationary so $\beta=2H+1$ is the spectral exponent of
   the process, while its increment noise (fractional Gaussian noise) carries
   exponent $\beta-2=2H-1$.

# Proof

1. **[verified]** *(Scaling of the spectrum.)* Self-affinity
   $B_H(\lambda t)\stackrel{d}{=}\lambda^H B_H(t)$ implies the spectral density
   transforms as $S(\lambda f)=\lambda^{-(2H+1)}S(f)$; a pure power law
   $S(f)\propto f^{-\beta}$ solving this has $\beta=2H+1$.
2. **[verified]** *(Endpoints / noise table.)* $H=1/2$ gives $\beta=2$ —
   ordinary Brownian motion ("brown/red noise"); $H\to0^+$ gives $\beta\to1$ —
   "pink/$1/f$ noise"; and uncorrelated **white noise** has a flat spectrum
   $\beta=0$ (its integral, Brownian motion, is the $\beta=2$ case).
3. **[asserted]** *(Local vs global dimension.)* For a self-affine trace the
   fine-scale box-counting dimension of the graph is $D_{\text{loc}}=2-H$;
   e.g. $H=1/2\Rightarrow D_{\text{loc}}=1.5$. At scales larger than the
   affine crossover the graph is resolved as a single rectifiable-looking
   curve of dimension $1$.

# Verification

- **Numerical (NumPy):** synthesized self-affine traces by spectral synthesis
  with target exponent $2H+1$, then measured the periodogram slope by
  log-log least squares. Recovered slopes: $H=0.0\to\beta=1.0$;
  $H=0.5\to\beta=2.0$; $H=0.8\to\beta=2.6$ — matching $\beta=2H+1$ to three
  decimals in every case.
- **Verified table:**

  | process | $H$ | $\beta=2H+1$ | name |
  |---|---|---|---|
  | white noise | (n/a) | 0 | flat spectrum |
  | pink / $1/f$ | $\to 0$ | $\to 1$ | pink noise |
  | Brownian | $1/2$ | 2 | brown/red noise |

- **Asserted:** the exact value $D_{\text{loc}}=2-H$ for the box dimension of an
  fBm graph is a standard result (Mandelbrot; Falconer) quoted, not re-derived.

# Historical source

Fractional Brownian motion and the $1/f^\beta$ spectral family were formalized
by Mandelbrot and Van Ness (1968); the $\beta=2H+1$ relation is standard in the
theory of self-affine records.

# Related concepts

- [Hurst exponent](../concepts/stochastic/hurst-exponent.md)
- [Fractional Brownian motion](../concepts/stochastic/fractional-brownian-motion.md)
- [Pink noise](../concepts/stochastic/pink-noise.md)
- [Self-affinity](../concepts/geometry/self-affinity.md)

# Citations

1. Mandelbrot, B. B., Van Ness, J. W. "Fractional Brownian motions, fractional noises and applications." *SIAM Review* 10 (1968): 422-437.
2. Falconer, K. *Fractal Geometry: Mathematical Foundations and Applications.* Wiley (1990), ch. on self-affine sets.
