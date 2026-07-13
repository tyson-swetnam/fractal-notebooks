---
okf_version: "0.1"
---

# Fractal Notebooks — Proof Knowledge Bundle

Appendix-level proofs for the quantitative results stated in the Fractal
Notebooks documentation, primarily [Chapter 1: History of Fractal
Mathematics](https://tyson-swetnam.github.io/fractal-notebooks/foundations/history/)
(`docs/foundations/history.md`). Each document is a `type: Fractal Proof`
record that states the theorem, its assumptions, numbered proof steps, an
explicit **verification status** distinguishing machine-checked steps from
steps asserted on the authority of a named theorem, the historical source, and
a cross-link to the matching concept in [`../concepts/`](../concepts/).

## Verification conventions

Each proof step is tagged:

* **`[verified]`** — checked by symbolic or numerical computation (SymPy /
  NumPy) in the `fractal-proof` environment. The check is described in the
  step and reproducible.
* **`[asserted]`** — relied upon as the conclusion of a named, published
  theorem that is cited but **not** re-derived here (e.g. Moran's theorem,
  Hardy's theorem, the Fatou–Julia dichotomy). These are the load-bearing
  external results; the proof is only as sound as the citation.

A proof's overall `verification_status` frontmatter field is one of
`verified` (all quantitative steps machine-checked; any `[asserted]` steps are
standard textbook theorems), `partially-verified` (core computation checked,
substantive structural claims asserted), or `unverified` (no step
machine-checkable with available tools).

## Proofs

* [Cantor Set — Dimension, Measure, and Cardinality](cantor-set-dimension.md) — $D=\log 2/\log 3$, Lebesgue measure zero, uncountability.
* [Koch Curve — Dimension, Perimeter, and Area](koch-curve-dimension.md) — $D=\log 4/\log 3$, infinite perimeter, snowflake area $\tfrac{8}{5}A_0$.
* [Sierpinski Triangle and Carpet — Dimensions](sierpinski-dimension.md) — $\log 3/\log 2$ and $\log 8/\log 3$.
* [Menger Sponge — Similarity Dimension](menger-sponge-dimension.md) — $\log 20/\log 3 \approx 2.7268$.
* [Barnsley Fern — Box-Counting Dimension](barnsley-fern-dimension.md) — numerical $\approx 1.83$; no closed form (OSC fails).
* [Mandelbrot Set — Escape-Radius Criterion](mandelbrot-escape.md) — $|z|>2 \Rightarrow$ orbit escapes; radius-2 bailout.
* [Mandelbrot Boundary — Hausdorff Dimension 2](mandelbrot-boundary-dimension.md) — Shishikura's theorem (asserted, not machine-verifiable).
* [Julia Sets — Fatou–Julia Connectedness Dichotomy](julia-connectedness.md) — $J_c$ connected $\iff 0\in K_c$.
* [Weierstrass Function — Nowhere Differentiability](weierstrass-nondifferentiability.md) — continuity everywhere, differentiability nowhere.
* [Self-Affinity — Spectral Exponent Relation](self-affine-spectral.md) — $\beta = 2H+1$ for Gaussian self-affine processes.
* [Metabolic Scaling — WBE Quarter-Power Law](wbe-quarter-power.md) — $B \propto M^{3/4}$ from area-preserving, space-filling networks.
* [Complex Dimensions — Cantor String Poles](complex-dimensions-cantor.md) — $\omega_k = \tfrac{\log 2}{\log 3} + i\tfrac{2\pi k}{\log 3}$.

See [log.md](log.md) for change history.
