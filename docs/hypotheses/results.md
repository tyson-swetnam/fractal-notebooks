# Results

This section outlines expected outcomes under null and alternative hypotheses for each of the three proposed studies, including predicted measurement ranges and statistical power considerations.

---

## Hypothesis 1: Stochastic Geometry in Lichens and Algae

### Expected Outcomes Under \(H_0\)

If the null hypothesis is correct---that lichen/algal fractal dimension is genetically fixed regardless of environmental conditions---we predict:

**Fractal Dimension:** Invariant across all nutrient treatments at \(D = 1.71 \pm 0.05\), consistent with standard DLA.

**Statistical Pattern:** No significant correlation between nutrient concentration (or diffusion coefficient) and measured \(D\). ANOVA across treatment groups will yield \(F\)-statistics with \(p > 0.05\).

**Morphological Constancy:** Colony morphology remains dendritic regardless of nutrient availability, with consistent branch spacing and tip density.

### Expected Outcomes Under \(H_A\)

If the alternative hypothesis is correct---that fractal dimension responds dynamically to nutrient availability---we predict:

**Low-Nutrient Conditions (Diffusion-Limited):**

- Open, dendritic morphology
- \(D = 1.65\)--\(1.75\)
- High surface-area-to-mass ratio
- Tip-dominated growth patterns

**High-Nutrient Conditions (Reaction-Limited):**

- Compact, space-filling morphology
- \(D = 1.85\)--\(1.95\)
- High biomass density
- Uniform radial expansion

**Intermediate Conditions:**

- Transitional morphologies
- \(D\) values spanning the range continuously
- Mixed growth patterns

**Statistical Pattern:** Strong negative correlation (\(r < -0.7\)) between nutrient availability and \(D\). ANOVA will show significant treatment effects (\(p < 0.01\)).

### Predicted Measurement Ranges

| Treatment | Nutrient Level | Predicted \(D\) (\(H_0\)) | Predicted \(D\) (\(H_A\)) |
|-----------|----------------|---------------------------|---------------------------|
| Low agar, low N | Very low | \(1.71 \pm 0.05\) | \(1.68 \pm 0.04\) |
| Standard agar, medium N | Medium | \(1.71 \pm 0.05\) | \(1.78 \pm 0.05\) |
| High agar, high N | High | \(1.71 \pm 0.05\) | \(1.92 \pm 0.04\) |

### Power Analysis

For detecting a difference of \(\Delta D = 0.15\) between low and high nutrient treatments with \(\sigma = 0.05\):

- Effect size (Cohen's \(d\)): \(d = 0.15/0.05 = 3.0\)
- Required sample size per group: \(n = 6\) for 95% power at \(\alpha = 0.05\)
- Recommended sample size: \(n = 20\) per treatment to accommodate biological variability

---

## Hypothesis 2: Branching Architecture in Angiosperms versus Gymnosperms

### Expected Outcomes Under \(H_0\)

If the null hypothesis is correct---that both clades converge to universal WBE-predicted architecture---we predict:

**Fractal Dimension:** Both gymnosperms and angiosperms exhibit \(D = 2.5 \pm 0.1\) for the woody branch network.

**Multifractal Spectrum:** Narrow spectrum width \(\Delta \alpha < 0.2\) for both groups, indicating monofractal scaling.

**Leonardo's Rule:** Both groups satisfy area-preserving branching:

\[
\frac{r_{\text{parent}}^2}{\sum r_{\text{daughter}}^2} = 1.0 \pm 0.1
\]

**Path Fraction:** No systematic difference in \(P_f\) between clades.

### Expected Outcomes Under \(H_A\)

If the alternative hypothesis is correct---that gymnosperms and angiosperms exhibit distinct fractal architectures---we predict:

**Gymnosperms (Monofractal):**

- Box-counting dimension: \(D = 2.4\)--\(2.6\)
- Spectrum width: \(\Delta \alpha = 0.1\)--\(0.2\)
- Leonardo's Rule adherence: deviations \(< 10\%\)
- High path fraction: \(P_f > 0.7\)
- Excurrent crown form with single dominant axis

**Angiosperms (Multifractal):**

- Box-counting dimension: \(D = 2.2\)--\(2.8\) (higher variance)
- Spectrum width: \(\Delta \alpha = 0.4\)--\(0.8\)
- Leonardo's Rule violations: deviations \(> 20\%\) common
- Lower path fraction: \(P_f = 0.4\)--\(0.6\)
- Decurrent crown form with multiple competing axes

**Statistical Pattern:** Significant between-clade differences in \(\Delta \alpha\) (\(t\)-test \(p < 0.001\)) and \(P_f\) (\(p < 0.01\)).

### Predicted Measurement Ranges

| Metric | Gymnosperm (\(H_0\)) | Gymnosperm (\(H_A\)) | Angiosperm (\(H_0\)) | Angiosperm (\(H_A\)) |
|--------|----------------------|----------------------|----------------------|----------------------|
| \(D\) | \(2.5 \pm 0.1\) | \(2.5 \pm 0.1\) | \(2.5 \pm 0.1\) | \(2.5 \pm 0.2\) |
| \(\Delta \alpha\) | \(< 0.2\) | \(0.15 \pm 0.05\) | \(< 0.2\) | \(0.55 \pm 0.15\) |
| \(P_f\) | \(0.6 \pm 0.1\) | \(0.75 \pm 0.08\) | \(0.6 \pm 0.1\) | \(0.50 \pm 0.10\) |
| Leonardo deviation | \(< 10\%\) | \(5 \pm 3\%\) | \(< 10\%\) | \(25 \pm 10\%\) |

### Power Analysis

For detecting a difference of \(\Delta(\Delta \alpha) = 0.4\) between clades with pooled \(\sigma = 0.15\):

- Effect size (Cohen's \(d\)): \(d = 0.4/0.15 = 2.67\)
- Required sample size per group: \(n = 5\) for 90% power at \(\alpha = 0.05\)
- Recommended sample size: \(n = 10\) per species, 3 species per clade, to capture within-clade variance

### Covariates and Confounds

The following variables should be controlled or included as covariates:

- **Tree size:** Include DBH and total height in models
- **Site conditions:** Block by site or include soil moisture and light availability
- **Ontogenetic stage:** Compare trees of similar relative age
- **Measurement artifacts:** Assess TLS occlusion and QSM reconstruction error

---

## Hypothesis 3: Canopy Topography and Gap Dynamics

### Expected Outcomes Under \(H_0\)

If the null hypothesis is correct---that gaps are randomly distributed and \(D_{\text{surf}}\) is independent of gap patterns---we predict:

**Gap Size Distribution:** Exponential or Poisson distribution, not power-law:

\[
P(S) \sim e^{-S/\bar{S}}
\]

with characteristic scale \(\bar{S}\) (mean gap size).

**Surface Dimension:** \(D_{\text{surf}}\) values vary independently of gap characteristics, driven primarily by crown geometry.

**Successional Pattern:** No systematic trend in \(D_{\text{surf}}\) or gap distribution parameters across successional stages.

**Correlation:** No significant relationship between \(D_{\text{surf}}\) and \(\lambda\) (if power-law fits are attempted despite poor fit).

### Expected Outcomes Under \(H_A\)

If the alternative hypothesis is correct---that old-growth forests self-organize to critical states---we predict:

**Young Plantation:**

- Near-uniform canopy: \(D_{\text{surf}} = 2.1\)--\(2.3\)
- Few gaps; distribution poorly characterized or exponential
- No power-law scaling (insufficient range)

**Mid-Successional:**

- Developing heterogeneity: \(D_{\text{surf}} = 2.3\)--\(2.5\)
- Emerging power-law signature with \(\lambda = 2.5\)--\(3.0\)
- Truncated distribution (largest gaps limited by stand age)

**Old-Growth:**

- Maximum roughness: \(D_{\text{surf}} = 2.5\)--\(2.8\)
- Clear power-law distribution with \(\lambda = 1.8\)--\(2.2\)
- Extended scaling regime spanning 2+ orders of magnitude
- \(D_{\text{surf}}\) and \(\lambda\) coupled per the predicted relationship

**Statistical Pattern:** Strong negative correlation between \(D_{\text{surf}}\) and \(\lambda\) across sites (\(r < -0.8\)). The relationship \(D_{\text{surf}} = 3 - (\lambda - 1)\) explains \(> 60\%\) of variance.

### Predicted Measurement Ranges

| Stage | Age (yr) | \(D_{\text{surf}}\) (\(H_0\)) | \(D_{\text{surf}}\) (\(H_A\)) | \(\lambda\) (\(H_A\)) |
|-------|----------|-------------------------------|-------------------------------|------------------------|
| Plantation | 20 | \(2.2 \pm 0.2\) | \(2.15 \pm 0.10\) | N/A (exponential) |
| Mid-succession | 75 | \(2.3 \pm 0.2\) | \(2.40 \pm 0.12\) | \(2.7 \pm 0.3\) |
| Old-growth | 250 | \(2.4 \pm 0.2\) | \(2.65 \pm 0.10\) | \(2.0 \pm 0.2\) |

### Power Analysis

For detecting a correlation of \(r = -0.8\) between \(D_{\text{surf}}\) and \(\lambda\):

- Required sample size: \(n = 7\) sites for 80% power at \(\alpha = 0.05\)
- Recommended sample size: \(n = 15\)+ sites across the successional gradient to establish robust regression relationships

For comparing gap distributions between stages using Kolmogorov-Smirnov test with effect size \(d = 0.5\):

- Required sample size: \(n = 100\)+ gaps per stage for 90% power
- Old-growth sites typically contain 200--500 measurable gaps per km\(^2\)

### Methodological Considerations

**Scale Dependence:** DBC results depend on the range of box sizes analyzed. Report scaling exponents only over regimes where \(R^2 > 0.95\) for log-log regression.

**Edge Effects:** Gaps intersecting plot boundaries must be handled consistently (exclude, or use correction factors).

**Minimum Mappable Gap:** Detection threshold depends on CHM resolution. Report as methodological parameter.

**Temporal Dynamics:** Gap distributions are non-stationary. Single time-point analysis captures snapshot; repeat surveys enable dynamic modeling.

---

## Summary of Testable Predictions

The following table summarizes key quantitative predictions distinguishing null from alternative hypotheses:

| Hypothesis | Metric | \(H_0\) Prediction | \(H_A\) Prediction | Discriminating Power |
|------------|--------|--------------------|--------------------|----------------------|
| H1 (DLA) | \(D\) vs nutrients | No correlation | \(r < -0.7\) | High |
| H1 (DLA) | \(D\) range | \(1.66\)--\(1.76\) | \(1.65\)--\(1.95\) | Medium |
| H2 (Branching) | \(\Delta \alpha\) | \(< 0.2\) both | Gymnosperm \(\ll\) Angiosperm | High |
| H2 (Branching) | Leonardo deviation | \(< 10\%\) both | Angiosperm \(> 20\%\) | High |
| H3 (Canopy) | Gap distribution | Exponential | Power-law | High |
| H3 (Canopy) | \(D_{\text{surf}}\) vs \(\lambda\) | No correlation | \(r < -0.8\) | High |
