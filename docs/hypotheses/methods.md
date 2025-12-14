# Methods

This section presents the mathematical foundations, measurement protocols, and experimental designs for testing the five primary hypotheses and four spatial distribution hypotheses.

---

## Data Source

### Input Data Requirements

- **Data Type:** High-resolution LiDAR point clouds converted to Canopy Height Models (CHM)
- **Resolution:** \(\le 0.5\) meters/pixel
- **Coordinate System:** UTM or local coordinate system with known datum

### Sample Groups

- **Group A:** Confirmed Old Growth (Reference State) - forests \(>200\) years with documented disturbance-free history
- **Group B:** Late-Successional with Disturbance (Windthrow/Fire) - forests 50--150 years with known disturbance events
- **Group C:** Monoculture Plantation (Control) - even-aged managed stands 20--50 years

### Pre-Processing: Normalization (nCHM)

Before running Differential Box Counting (DBC), decouple tree height from terrain elevation:

1. **DTM (Digital Terrain Model):** Represents bare earth (ridges, valleys)
2. **DSM (Digital Surface Model):** Represents top of canopy
3. **nCHM (Normalized Canopy Height Model):** \(\text{DSM} - \text{DTM}\)

This ensures measurement of canopy roughness rather than terrain roughness.

---

## Hypothesis 1: The "Optimal Filling" Hypothesis (Fractal Dimension)

### Theoretical Background

Old-growth forests maximize light interception while minimizing self-shading. This optimization results in specific fractal dimensions that can be measured using Differential Box Counting.

**Ecological Metabolic Scaling Theory** suggests that forests self-organize to maximize light interception and gas exchange while minimizing transport costs (water). A forest with "optimal" packing would effectively utilize all available vertical and horizontal space.

**Interpretation of \(D\):**

- **High \(D\) (High Complexity):** Indicates efficient space packing. The forest has a multi-layered structure (understory, mid-story, canopy) maximizing the "surface area" available for photosynthesis.
- **Low \(D\) (Low Complexity):** Indicates poor packing; the canopy appears as a flat sheet.

### Hypothesis Formulation

**\(H_{1a}\) (Alternative):** The Fractal Dimension (\(D\)) of the Canopy Height Map for old-growth forests will be significantly higher than that of monoculture plantations or recently disturbed stands, converging toward a theoretical maximum (\(D \approx 2.7\) for volumetric surface, or \(D \approx 1.7\) for 2D cross-sections).

**\(H_{10}\) (Null):** There is no significant difference in \(D\) between old-growth, disturbed, and managed forests.

### Method: Differential Box Counting (DBC)

**Algorithm:** Sarkar & Chaudhuri method

For a CHM represented as a height field \(z(x, y)\):

1. Partition the \((x, y)\) plane into grid cells of side \(r\)
2. For each cell \((i, j)\), calculate the height variance in the box
3. Output: Slope of \(\log(N_r)\) vs \(\log(1/r)\) determines \(D\)

\[
D_{\text{surf}} = \lim_{r \to 0} \frac{\log N_r}{\log (1/r)}
\]

### Statistical Test

**ANOVA** to compare mean Fractal Dimension (\(D\)) across Groups A, B, and C with post-hoc Tukey HSD tests.

---

## Hypothesis 2: The "Scale Invariance" Hypothesis (Lacunarity)

### Theoretical Background

Disturbance creates characteristic gap sizes (breaks in scaling), whereas steady-state forests exhibit scale invariance (gaps of all sizes). Lacunarity measures the "texture" or gappiness of the distribution:

- **Low Lacunarity:** Homogeneous forest; gaps are small and uniform. Diagnosis: Monoculture/Plantation or very young, dense forest.
- **High Lacunarity:** Heterogeneous forest; large gaps mixed with dense clusters. Diagnosis: Late-Successional/Old Growth with "very large trees, gaps with small trees, and openings."

### Hypothesis Formulation

**\(H_{2a}\) (Alternative):** In old-growth forests, the Lacunarity curve \(\Lambda(r)\) will follow a strict power-law decay (linear on a log-log plot), indicating scale invariance. In disturbed forests, \(\Lambda(r)\) will exhibit "spectral kinks" (deviations from linearity) corresponding to the specific physical scale of the disturbance.

**\(H_{20}\) (Null):** Lacunarity decay curves will not distinctively differentiate between forest ages or disturbance histories.

### Method: Gliding Box Algorithm

**Calculation:**

\[
\Lambda(r) = \frac{\sigma^2(r)}{\mu^2(r)} + 1
\]

where \(\sigma\) and \(\mu\) are the variance and mean of "canopy mass" per box size \(r\).

**Spectral Check:** Perform Fourier Transform on the residuals of the Lacunarity curve to identify dominant oscillating frequencies (Complex Dimensions).

### Statistical Test

**Regression analysis** of Lacunarity curves. Calculate the \(R^2\) of a linear fit on log-log axes. We predict \(R^2_{\text{Group A}} > R^2_{\text{Group B}}\).

---

## Hypothesis 3: The "Zeta" Distribution of Gaps (Metabolic Scaling)

### Theoretical Background

The frequency of canopy gaps is driven by the death of trees, which follows metabolic scaling laws. If the Zeta function \(\zeta(s)\) describes the system, finding the pole of the Zeta function (where the sum diverges) reveals the fractal dimension of the object distribution.

### Hypothesis Formulation

**\(H_{3a}\) (Alternative):** The size-frequency distribution of canopy gaps in old-growth forests will follow a Power Law distribution \(P(A) \sim A^{-\alpha}\) where the exponent \(\alpha\) approximates the Zeta function parameter associated with 2D packing (\(\alpha \approx 2.0\), related to \(\zeta(2)\)).

**\(H_{30}\) (Null):** Gap sizes will follow an Exponential or Lognormal distribution (characteristic of random, non-interacting events) rather than a Power Law.

### Method: Gap Frequency Analysis

1. **Thresholding:** Define "Gap" as pixels \(< 2m\) height (or relative height)
2. **Measurement:** Calculate area of contiguous gap polygons
3. **Statistical Test:** Use Maximum Likelihood Estimation (MLE) to fit Power Law vs. Lognormal distributions
4. **Goodness of Fit:** Calculate the Kolmogorov-Smirnov (KS) distance to determine fit quality

### Statistical Test

**Likelihood Ratio Test (LRT)** comparing Power Law models vs. Exponential models for gap sizes.

---

## Hypothesis 4: Universal Repulsion (The "Spectral DNA")

### Theoretical Background

Trees compete for resources, creating a "zone of exclusion" (repulsion) similar to energy level repulsion in quantum systems. The **Montgomery-Odlyzko Law** states that the spacing between the non-trivial zeros of the Riemann Zeta function follows the statistics of the **Gaussian Unitary Ensemble (GUE)**.

### Hypothesis Formulation

**\(H_{4a}\) (Alternative):** The Nearest Neighbor Spacing (NNS) distribution of dominant tree apices in old-growth forests will fit the **Wigner-Dyson distribution** (specifically GUE or GOE statistics), indicating rigid repulsion.

\[
P(s) = \frac{\pi s}{2} e^{-\pi s^2/4} \quad \text{(GOE)}
\]

or

\[
P(s) = \frac{32 s^2}{\pi^2} e^{-4s^2/\pi} \quad \text{(GUE)}
\]

**\(H_{40}\) (Null):** The NNS distribution will fit a **Poisson distribution**, indicating that tree location is random and non-interacting:

\[
P(s) = e^{-s}
\]

### Method: Point Pattern Analysis (Repulsion)

1. **Identification:** Local Maximum Filter to identify tree apices from CHM
2. **Metric:** Calculate normalized nearest neighbor distances
3. **Comparison:** Compare empirical distribution against Poisson (Random) and Wigner-Dyson (Universal Repulsion) curves

### Statistical Test

**\(\chi^2\) (Chi-Squared) goodness-of-fit test** comparing tree spacing histograms to Wigner-Dyson vs. Poisson probability density functions.

---

## Hypothesis 5: Biotic Decoupling (The Topographic Test)

### Theoretical Background

Mature ecosystems buffer environmental constraints (niche construction). The "Biotic Decoupling" hypothesis suggests that old-growth forests have built enough biomass/soil (organic layer) to buffer the underlying geology.

### Accounting for Topography

Topography acts as an **environmental filter** that distorts the "perfect" packing:

1. **Anisotropy Correction:** Use **Cosine Correction** on pixel areas during box-counting. The area of a pixel is not \(x \cdot y\), but \((x \cdot y) / \cos(\theta)\), where \(\theta\) is local slope.

2. **Topographic Wetness Index (TWI):** Generate from DTM
   - High TWI = Valleys (Deep soil, water, nutrients)
   - Low TWI = Ridges (Shallow soil, dry)

3. **Local Fractal Dimension:** Calculate using a moving window (e.g., \(50m \times 50m\))

### Hypothesis Formulation

**\(H_{5a}\) (Alternative):** In Old Growth stands, the correlation coefficient between \(D_{\text{local}}\) and Topography will be **lower** than in young or disturbed stands. The "Universal Repulsion" (GUE statistics) will persist even across topographic gradients in old growth.

**\(H_{50}\) (Null):** No difference in correlation between fractal dimension and topography across forest age classes.

### Method: Geographically Weighted Regression (GWR)

Perform GWR of the Local Fractal Dimension (\(D_{\text{local}}\)) against:
- Slope
- Topographic Wetness Index (TWI)
- Solar Insolation (aspect-corrected)

### Statistical Test

**Comparison of correlation coefficients** between Groups A, B, and C using Fisher's z-transformation.

---

## Four Spatial Distribution Hypotheses from Fractal String Theory

These additional hypotheses provide specific predictions about the spatial arrangement of trees and gaps in old-growth forests.

### Method: Transect Analysis (Fractal String Gap Hypothesis)

1. Draw straight line transects through forest
2. Record sequence of intervals: Tree — Gap — Tree — Gap
3. Analyze distribution of gap lengths \(L_j\)

**Prediction:** In old-growth, \(N(L) \sim L^{-D}\) where \(D\) is the boundary dimension. No single gap size dominates (scale invariance).

### Method: GUE Pair Correlation (Prime Number Repulsion Hypothesis)

The probability of finding two giant trees distance \(r\) apart follows:

\[
g(r) = 1 - \left(\frac{\sin(\pi r)}{\pi r}\right)^2
\]

**Test:** Compare empirical pair correlation function to GUE prediction vs. Poisson (\(g(r) = 1\)) vs. hexagonal lattice.

### Method: Log-Periodic Oscillation Detection (Complex Dimension Hypothesis)

1. Plot Lacunarity against \(\log(r)\)
2. Identify periodic waves in the curve
3. Measure frequency and amplitude of oscillations

**Prediction:** Constant, low-amplitude frequency in steady-state forests indicates self-similar construction.

### Method: Size-Density Scaling (Riemann Gas Hypothesis)

Calculate number density \(N\) of trees with mass greater than \(m\):

\[
N(>m) \sim m^{-\alpha}
\]

**Prediction:** \(\alpha \approx 2\) (related to \(\zeta(2) = \pi^2/6 \approx 1.645\)), representing the "critical density" threshold.

---

## Statistical Analysis Plan Summary

| Hypothesis | Method | Primary Test | Secondary Tests |
|------------|--------|--------------|-----------------|
| H1 (Optimal Filling) | DBC | ANOVA | Post-hoc Tukey HSD |
| H2 (Scale Invariance) | Gliding Box Lacunarity | Linear regression \(R^2\) | Fourier analysis of residuals |
| H3 (Zeta Distribution) | Gap size frequency | LRT (Power Law vs. Exponential) | KS goodness-of-fit |
| H4 (Universal Repulsion) | Point pattern analysis | \(\chi^2\) (GUE vs. Poisson) | Pair correlation function |
| H5 (Biotic Decoupling) | GWR | Correlation comparison | Fisher's z-test |

---

## Sample Size and Power Considerations

Based on expected effect sizes from pilot studies:

- **Minimum sites per group:** \(n = 10\)
- **Minimum plot size:** 1 hectare (100m \(\times\) 100m)
- **LiDAR point density:** \(\geq 4\) points/m\(^2\)

Power analysis indicates these sample sizes provide \(>80\%\) power to detect differences of:
- \(\Delta D = 0.2\) between forest types (H1)
- \(\Delta R^2 = 0.3\) in Lacunarity linearity (H2)
- Shift from exponential to power-law distribution (H3)
- Shift from Poisson to GUE spacing (H4)
