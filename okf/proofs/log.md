# Proof Bundle Change Log

## 2026-07-13

* **Update**: Added 3 proof documents while addressing the gaps memo — `menger-sponge-dimension.md` ($\log 20/\log 3 \approx 2.7268$, verified), `barnsley-fern-dimension.md` (box-counting $\approx 1.83$ from 2M chaos-game points, partially-verified — no closed form as the OSC fails), and `mandelbrot-boundary-dimension.md` (Shishikura's $\dim_H\partial\mathcal{M}=2$, deliberately `unverified` as a template for cited-but-uncomputable results). Bundle now holds 12 proofs.
* **Creation**: Initialized the `okf/proofs/` OKF v0.1 bundle with 9 `type: Fractal Proof` documents capturing the quantitative results stated in `docs/foundations/history.md`. All 13 checkable quantitative claims on the history page were machine-verified (SymPy / NumPy) in the `fractal-proof` environment prior to capture; steps resting on named theorems (Moran, Hardy, Fatou–Julia) are tagged `[asserted]` with citations.
