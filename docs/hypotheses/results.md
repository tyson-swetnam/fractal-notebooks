# Expected Results

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.

This section outlines expected outcomes under null and alternative hypotheses for each of the five primary hypotheses, including predicted measurement ranges and statistical considerations.

---

## Hypothesis 1: The "Optimal Filling" Hypothesis (Fractal Dimension)

### Expected Outcomes Under \(H_{10}\) (Null)

If the null hypothesis is correct---that there is no difference in fractal dimension across forest types---we predict:

- **Fractal Dimension:** Invariant across all groups at \(D = 2.3 \pm 0.2\)
- **ANOVA:** \(F\)-statistic with \(p > 0.05\)
- No systematic trend with forest age or disturbance history

### Expected Outcomes Under \(H_{1a}\) (Alternative)

If the alternative hypothesis is correct---that old-growth forests exhibit higher fractal dimensions due to optimal space packing---we predict:

**Group A (Old Growth):**

- \(D_{\text{surf}} = 2.6\)--\(2.8\)
- Multi-layered canopy structure
- Maximum "surface area" for photosynthesis

**Group B (Late-Successional with Disturbance):**

- \(D_{\text{surf}} = 2.3\)--\(2.5\)
- Developing heterogeneity
- Recovering toward optimal packing

**Group C (Monoculture Plantation):**

- \(D_{\text{surf}} = 2.1\)--\(2.3\)
- Near-uniform canopy ("flat sheet")
- Poor space utilization

### Predicted Measurement Ranges

| Group | Forest Type | \(D_{\text{surf}}\) (\(H_0\)) | \(D_{\text{surf}}\) (\(H_A\)) |
|-------|-------------|-------------------------------|-------------------------------|
| A | Old Growth (>200 yr) | \(2.3 \pm 0.2\) | \(2.70 \pm 0.10\) |
| B | Late-Successional | \(2.3 \pm 0.2\) | \(2.40 \pm 0.12\) |
| C | Plantation (20-50 yr) | \(2.3 \pm 0.2\) | \(2.15 \pm 0.10\) |

---

## Hypothesis 2: The "Scale Invariance" Hypothesis (Lacunarity)

### Expected Outcomes Under \(H_{20}\) (Null)

If the null hypothesis is correct---that Lacunarity curves do not differentiate forest types---we predict:

- No significant difference in \(R^2\) of linear fit on log-log axes
- Similar "kink" patterns across all forest types
- Deviations from linearity random rather than systematic

### Expected Outcomes Under \(H_{2a}\) (Alternative)

If the alternative hypothesis is correct---that old-growth exhibits scale invariance while disturbed forests show spectral kinks---we predict:

**Group A (Old Growth):**

- \(\Lambda(r)\) follows strict power-law decay
- \(R^2 > 0.95\) for linear regression on log-log plot
- No characteristic gap scale dominates

**Group B (Late-Successional with Disturbance):**

- \(\Lambda(r)\) exhibits "spectral kinks" at specific scales
- \(R^2 = 0.7\)--\(0.9\) due to deviations
- Kink position corresponds to disturbance scale (e.g., logging road width, windthrow radius)

**Group C (Monoculture Plantation):**

- \(\Lambda(r)\) shows strong characteristic scale
- \(R^2 < 0.8\) with systematic deviation
- Kink at tree spacing interval

### Disturbance Signatures

| Disturbance Type | Expected Kink Scale | Interpretation |
|------------------|---------------------|----------------|
| Recent Tree Fall | 15--25 m | Single large gap |
| Windthrow | 30--50 m | Cluster of gaps |
| Logging Road | 10--15 m | Linear feature |
| Fire | Variable | Patch-dependent |

---

## Hypothesis 3: The "Zeta" Distribution of Gaps (Metabolic Scaling)

### Expected Outcomes Under \(H_{30}\) (Null)

If the null hypothesis is correct---that gap sizes follow exponential rather than power-law distributions---we predict:

**Gap Size Distribution:**

\[
P(S) \sim e^{-S/\bar{S}}
\]

- Characteristic mean gap size \(\bar{S}\)
- Exponential tail (rapid decline)
- Likelihood Ratio Test favors exponential model

### Expected Outcomes Under \(H_{3a}\) (Alternative)

If the alternative hypothesis is correct---that gap sizes follow a Zeta (power-law) distribution in old-growth---we predict:

**Old Growth (Group A):**

- Power-law distribution: \(P(A) \sim A^{-\alpha}\)
- Exponent: \(\alpha = 1.8\)--\(2.2\) (related to \(\zeta(2) = \pi^2/6\))
- Extended scaling regime: 2+ orders of magnitude
- Self-Organized Criticality confirmed

**Late-Successional (Group B):**

- Truncated power-law with exponential cutoff
- \(\alpha = 2.3\)--\(2.8\)
- Limited scaling range

**Plantation (Group C):**

- Exponential or lognormal distribution
- No power-law signature
- Characteristic gap size dominates

### Gap Distribution Parameters

| Group | Distribution Type | Exponent \(\alpha\) | Scaling Range |
|-------|-------------------|---------------------|---------------|
| A (Old Growth) | Power Law | \(2.0 \pm 0.2\) | \(10^1\)--\(10^4\) m\(^2\) |
| B (Late-Successional) | Truncated Power Law | \(2.5 \pm 0.3\) | \(10^1\)--\(10^3\) m\(^2\) |
| C (Plantation) | Exponential | N/A | N/A |

---

## Hypothesis 4: Universal Repulsion (The "Spectral DNA")

### Expected Outcomes Under \(H_{40}\) (Null)

If the null hypothesis is correct---that tree locations are random---we predict:

**Nearest Neighbor Spacing (NNS):**

- Poisson distribution: \(P(s) = e^{-s}\)
- No repulsion between dominant trees
- \(\chi^2\) test favors Poisson model

### Expected Outcomes Under \(H_{4a}\) (Alternative)

If the alternative hypothesis is correct---that old-growth trees exhibit GUE-like repulsion---we predict:

**Old Growth (Group A):**

- Wigner-Dyson distribution (GOE/GUE statistics)
- Linear repulsion at small distances: \(P(s) \propto s\) as \(s \to 0\)
- Characteristic "level repulsion" signature
- \(\chi^2\) test strongly favors GUE over Poisson

**Physical Interpretation:**

- Small \(s\): Rare to find two dominant trees very close (competition)
- Medium \(s\): Most likely spacing (optimal resource sharing)
- Large \(s\): Exponential tail (random long-range)

### The GUE Pair Correlation Function

In old-growth forests, the probability of finding two giant trees at distance \(r\) should follow:

\[
g(r) = 1 - \left(\frac{\sin(\pi r)}{\pi r}\right)^2
\]

| Model | Pair Correlation at \(r=0\) | Physical Meaning |
|-------|----------------------------|------------------|
| Poisson | \(g(0) = 1\) | No repulsion; random |
| GUE | \(g(0) = 0\) | Strong repulsion; competition |
| Hexagonal Lattice | \(g(0) = 0\), periodic peaks | Perfect order |

**Prediction:** Old-growth forests should fall between GUE (soft repulsion) and lattice (hard repulsion), indicating evolutionary optimization of spacing.

---

## Hypothesis 5: Biotic Decoupling (The Topographic Test)

### Expected Outcomes Under \(H_{50}\) (Null)

If the null hypothesis is correct---that fractal dimension correlates equally with topography across all forest types---we predict:

- Similar correlation coefficients between \(D_{\text{local}}\) and TWI/Slope across Groups A, B, C
- No significant difference by Fisher's z-test

### Expected Outcomes Under \(H_{5a}\) (Alternative)

If the alternative hypothesis is correct---that old-growth forests "buffer" topographic constraints---we predict:

**Group A (Old Growth):**

- Weak correlation: \(|r| < 0.3\) between \(D_{\text{local}}\) and topography
- Forest structure independent of underlying terrain
- "Biotic Decoupling" achieved

**Group B (Late-Successional):**

- Moderate correlation: \(|r| = 0.4\)--\(0.6\)
- Partial decoupling; some terrain signature remains

**Group C (Plantation):**

- Strong correlation: \(|r| > 0.6\)
- Forest structure follows terrain (valleys dense, ridges sparse)
- "Environmentally Driven" system

### Predicted Correlations with Topography

| Group | \(r\) (D vs. TWI) | \(r\) (D vs. Slope) | Interpretation |
|-------|-------------------|---------------------|----------------|
| A (Old Growth) | \(0.15 \pm 0.10\) | \(-0.20 \pm 0.10\) | Biotically decoupled |
| B (Late-Successional) | \(0.45 \pm 0.15\) | \(-0.40 \pm 0.15\) | Transitioning |
| C (Plantation) | \(0.70 \pm 0.10\) | \(-0.65 \pm 0.12\) | Environmentally driven |

---

## Four Spatial Distribution Hypotheses: Expected Signatures

### Fractal String Gap Hypothesis

**Old Growth Prediction:**

- Gap lengths along transects: \(N(L) \sim L^{-D}\) with \(D \approx 1.3\)
- Scale invariance: no characteristic gap size
- Log-log plot linear over 1.5+ decades

### Prime Number Repulsion (GUE) Hypothesis

**Old Growth Prediction:**

- Pair correlation function matches GUE: \(g(r) = 1 - \left(\frac{\sin(\pi r)}{\pi r}\right)^2\)
- Strong rejection of Poisson null
- Spacing statistics match quantum chaotic systems

### Complex Dimension (Oscillation) Hypothesis

**Old Growth Prediction:**

- Lacunarity vs. \(\log(r)\) shows periodic oscillation
- Period: \(p = 2\pi/\omega\) where \(\omega\) is imaginary part of complex dimension
- Amplitude: Low, constant (steady state)
- Interpretation: Forest constructed via recursive, self-similar algorithm

### Riemann Gas Density Hypothesis

**Old Growth Prediction:**

- Number density: \(N(>m) \sim m^{-2}\)
- Packing density: \(\approx 1.645\) (related to \(\zeta(2) = \pi^2/6\))
- System at "Edge of Chaos"---critical density threshold

---

## Summary of Testable Predictions

| Hypothesis | Metric | \(H_0\) Prediction | \(H_A\) Prediction | Discriminating Power |
|------------|--------|--------------------|--------------------|----------------------|
| H1 (Optimal Filling) | \(D_{\text{surf}}\) across groups | No difference | Old Growth > Plantation | High |
| H2 (Scale Invariance) | Lacunarity \(R^2\) | Similar across groups | Old Growth > Disturbed | High |
| H3 (Zeta Distribution) | Gap size distribution | Exponential | Power Law (\(\alpha \approx 2\)) | High |
| H4 (Universal Repulsion) | NNS distribution | Poisson | GUE/Wigner-Dyson | High |
| H5 (Biotic Decoupling) | \(r\)(D vs. Topography) | Similar across groups | Old Growth < Plantation | Medium |

---

## Significance / Expected Outcomes

If **Hypotheses 3 and 4** are confirmed, this provides evidence that biological systems (forests) at equilibrium converge upon the same mathematical "universality classes" found in:

- **Number Theory:** Riemann Zeta function
- **Quantum Chaos:** Random Matrix Theory (GUE)

This would establish a non-destructive, remote-sensing method for identifying forests that have reached:

- **"Optimal Packing" (Old Growth):** Maximum metabolic efficiency, self-organized criticality
- **"Sub-optimal" (Immature/Degraded):** Transitioning toward or recovering from critical state
