# Methods

This section presents the mathematical foundations, measurement protocols, and experimental designs for testing three hypotheses spanning the micro, meso, and macro scales of fractal organization in biological systems.

---

## Hypothesis 1: Stochastic Geometry in Lichens and Algae

### Theoretical Background: Diffusion Limited Aggregation

Non-vascular organisms such as lichens, mosses, and colonial algae grow by accreting nutrients from surrounding fluid media (air or water). This growth process is captured by **Diffusion Limited Aggregation (DLA)**, a model in which particles performing random walks cluster upon contact with an existing aggregate. The resulting morphology is fundamentally determined by the **sticking probability** \(p\)---the likelihood that a nutrient particle attaches upon first contact with the aggregate surface.

The fractal dimension \(D\) of DLA clusters depends systematically on \(p\):

**Standard DLA (\(p = 1\)):** Particles stick immediately upon contact. This creates strong "screening" effects in which outer branches intercept all incoming particles, starving interior regions. The result is open, dendritic structures with characteristic dimension:

\[
D_{\text{DLA}} \approx 1.71 \quad \text{(in 2D)}
\]

**Reaction-Limited Aggregation (\(p \ll 1\)):** Particles bounce off many times before attaching, allowing penetration into the cluster's interior "fjords." The result is compact, dense structures approaching:

\[
D_{\text{RLA}} \to 2.0 \quad \text{as } p \to 0
\]

### The Nutrient Scarcity-Compactness Trade-off

We hypothesize that the sticking probability \(p\) in biological systems reflects nutrient availability. In nutrient-poor environments, organisms maximize their interception radius by adopting low-\(p\) effective growth kinetics, producing open dendritic forms. In nutrient-rich environments, organisms maximize biomass density by adopting high-\(p\) effective kinetics, producing compact forms.

**Null Hypothesis (\(H_0\)):** The fractal dimension of lichen/algal thalli is invariant (\(D \approx 1.7\)) regardless of nutrient concentration or substrate diffusion rates, indicating a fixed genetic morphological constraint.

**Alternative Hypothesis (\(H_A\)):** The fractal dimension of the thallus is dynamic and inversely proportional to nutrient availability. In nutrient-poor environments (diffusion-limited regime), organisms exhibit \(D \approx 1.7\) (maximizing interception radius). In nutrient-rich environments (reaction-limited regime), organisms exhibit \(D \to 2.0\) (maximizing biomass density).

### The Sand Box Method for Dimension Calculation

The fractal dimension is computed using the **Sand Box Method**, a generalization of box counting that measures how mass accumulates within circles of increasing radius centered on the aggregate. For a fractal object, the mass \(M(R)\) enclosed within radius \(R\) scales as:

\[
M(R) \sim R^{D}
\]

The dimension \(D\) is estimated from the slope of \(\log M(R)\) versus \(\log R\):

\[
D = \lim_{R \to \infty} \frac{\log M(R)}{\log R}
\]

In practice, we fit a linear regression over the scaling regime where power-law behavior holds, excluding small \(R\) (boundary effects) and large \(R\) (finite-size effects).

### Experimental Design

**Study Organisms:** Cultivate clonal replicates of a foliose lichen (e.g., *Parmelia sulcata*) or colonial green alga (e.g., *Pediastrum boryanum*) to control for genetic variation.

**Nutrient Gradient:** Prepare agar growth media with controlled nutrient diffusivities by varying:

- Agar concentration (0.5%--2.0%) to modulate viscosity and diffusion coefficient
- Nutrient concentration (nitrogen, phosphorus) across a 10-fold range
- Temperature to modify diffusion rates while holding concentration constant

**Image Acquisition:** Capture high-resolution digital micrographs (minimum 4000 x 4000 pixels) under standardized illumination. Multiple time points enable tracking of morphological development.

**Image Processing:**

1. Convert to grayscale and apply Gaussian smoothing to reduce noise
2. Binarize using Otsu's method to extract the thallus boundary
3. Skeletonize to obtain the fractal backbone for dimension calculation

**Statistical Analysis:** For each treatment condition, compute \(D\) for \(n \geq 20\) replicate colonies. Compare across treatments using ANOVA with post-hoc Tukey HSD tests. Correlate \(D\) with measured diffusion coefficients using linear regression.

---

## Hypothesis 2: Branching Architecture in Angiosperms versus Gymnosperms

### Theoretical Background: The West-Brown-Enquist Model

The **West-Brown-Enquist (WBE) Model** proposes that vascular plant branching networks have evolved to maximize resource distribution while minimizing transport costs. The model predicts specific scaling relationships arising from three principles:

1. **Space-filling:** The branching network must service the entire volume of the organism
2. **Terminal unit invariance:** Capillaries (leaf petioles, fine roots) have species-invariant dimensions
3. **Energy minimization:** Transport costs are minimized subject to hydraulic constraints

These principles yield the celebrated \(3/4\) power scaling of metabolic rate \(B\) with mass \(M\):

\[
B \propto M^{3/4}
\]

The model further predicts **area-preserving branching**, often called Leonardo's Rule:

\[
r_{\text{parent}}^2 = \sum_{i} r_{\text{daughter},i}^2
\]

where \(r\) denotes branch radius. This implies a branching ratio:

\[
\beta_k = \frac{r_{k+1}}{r_k} = n^{-1/2}
\]

for \(n\) daughter branches at each node.

### Monofractal versus Multifractal Scaling

The WBE model implicitly assumes **monofractal** (self-similar) branching: the same scaling relationships hold throughout the tree. However, evolutionary history may impose different topological constraints on gymnosperms and angiosperms:

**Gymnosperms:** Typically exhibit **monopodial** (excurrent) branching with a dominant central leader. This architecture approximates self-similar fractal geometry with a single characteristic dimension.

**Angiosperms:** Often exhibit **sympodial** (decurrent) branching with multiple competing leaders. This architecture may produce **multifractal** scaling, characterized by a spectrum of local dimensions rather than a single global dimension.

### The Path Fraction Metric

We introduce the **Path Fraction** (\(P_f\)) as a topological metric quantifying transport efficiency:

\[
P_f = \frac{\sum_{i} L_i}{L_{\max} \cdot N}
\]

where \(L_i\) is the path length from root to leaf \(i\), \(L_{\max}\) is the maximum possible path length, and \(N\) is the number of terminal branches. High \(P_f\) indicates vertical hydraulic optimization; low \(P_f\) indicates horizontal spread and hydraulic redundancy.

### Hypothesis Formulation

**Null Hypothesis (\(H_0\)):** Both gymnosperm and angiosperm branching networks converge to a single universal fractal dimension (\(D \approx 2.5\) for the woody network) and obey the WBE area-preserving rule.

**Alternative Hypothesis (\(H_A\)):** Gymnosperms exhibit **monofractal** scaling with dimensions close to WBE predictions (\(D \approx 2.5\)). Angiosperms exhibit **multifractal** scaling (a spectrum of dimensions \(f(\alpha)\) rather than a single \(D\)) due to adaptive reticulation and hydraulic segmentation that violates area-preserving branching rules.

### TLS Point Cloud Acquisition

**Terrestrial Laser Scanning (TLS)** provides millimeter-accurate three-dimensional point clouds of tree architecture. The scanning protocol proceeds as follows:

**Instrument:** Phase-shift or time-of-flight terrestrial laser scanner (e.g., FARO Focus, RIEGL VZ-400)

**Scan Design:** Multiple scan positions (minimum 4--6) arranged around each target tree to minimize occlusion. Registration via spherical targets or natural features.

**Point Cloud Processing:**

1. Register multiple scans into unified coordinate system
2. Filter ground points and understory vegetation
3. Isolate individual tree point clouds

### QSM Extraction and Analysis

**Quantitative Structure Models (QSM)** reconstruct tree architecture as networks of fitted cylinders from TLS point clouds:

1. Segment point cloud into branch sections
2. Fit cylinders to each section, estimating position, orientation, radius, and length
3. Establish topological connectivity between cylinders
4. Export as graph structure with geometric attributes

From QSM output, extract:

- Branch radius sequences from trunk to terminals
- Branching angles and ratios at each node
- Path lengths through the network

### WTMM Multifractal Analysis

The **Wavelet Transform Modulus Maxima (WTMM)** method characterizes multifractal scaling by analyzing how local singularities distribute across scales:

1. Compute the continuous wavelet transform of the branch radius sequence
2. Identify modulus maxima chains across scales
3. Partition the structure function by moment order \(q\)
4. Extract the multifractal spectrum \(f(\alpha)\) via Legendre transform

The **spectrum width** \(\Delta \alpha = \alpha_{\max} - \alpha_{\min}\) quantifies multifractality:

- Narrow spectrum (\(\Delta \alpha \approx 0\)): monofractal, single scaling exponent
- Wide spectrum (\(\Delta \alpha > 0.5\)): multifractal, heterogeneous local dimensions

### Experimental Design

**Study Organisms:** Select mature specimens of comparable mass (\(\pm 20\%\)) representing:

- Gymnosperms: *Pinus ponderosa*, *Picea engelmannii*, *Pseudotsuga menziesii*
- Angiosperms: *Quercus gambelii*, *Populus tremuloides*, *Acer grandidentatum*

**Sample Size:** Minimum \(n = 10\) individuals per species for statistical power.

**Measurements:** For each tree, acquire TLS point cloud, extract QSM, compute:

- Box-counting dimension of branch network
- Multifractal spectrum \(f(\alpha)\) and width \(\Delta \alpha\)
- Path fraction \(P_f\)
- Deviations from Leonardo's Rule at each branching node

**Statistical Analysis:** Compare gymnosperm versus angiosperm groups using:

- Two-sample t-tests for \(\Delta \alpha\) and \(P_f\)
- Kolmogorov-Smirnov tests for spectrum shape differences
- Mixed-effects models with species nested within clade

---

## Hypothesis 3: Canopy Topography and Gap Dynamics

### Theoretical Background: Self-Affine Fractal Surfaces

Forest canopies present rough surfaces whose texture reflects the spatial arrangement of individual tree crowns and canopy gaps. Unlike self-similar fractals (which scale identically in all directions), canopy surfaces are **self-affine**: vertical (\(z\)) and horizontal (\(x, y\)) coordinates scale differently.

For a self-affine surface, the surface fractal dimension \(D_{\text{surf}}\) satisfies:

\[
2 \leq D_{\text{surf}} \leq 3
\]

where \(D_{\text{surf}} = 2\) represents a smooth plane and \(D_{\text{surf}} = 3\) represents a volume-filling surface.

### Differential Box Counting

**Differential Box Counting (DBC)** extends standard box counting to grayscale images and continuous surfaces. For a Canopy Height Model (CHM) represented as a height field \(z(x, y)\):

1. Partition the \((x, y)\) plane into grid cells of side \(r\)
2. For each cell \((i, j)\), count the number of boxes of height \(r\) needed to cover the height range:

\[
n_r(i,j) = \left\lceil \frac{\max(z_{ij}) - \min(z_{ij})}{r} \right\rceil
\]

3. Sum over all cells to obtain total box count:

\[
N_r = \sum_{i,j} n_r(i,j)
\]

4. The surface dimension is estimated from the scaling relationship:

\[
D_{\text{surf}} = \lim_{r \to 0} \frac{\log N_r}{\log (1/r)}
\]

In practice, fit a linear regression of \(\log N_r\) versus \(\log(1/r)\) over the valid scaling regime.

### Gap Size Distributions and the Zeta Function

Canopy gaps---openings in the canopy created by tree mortality---exhibit size distributions that may follow power laws characteristic of self-organized critical systems. The probability \(P(S)\) of a gap having area \(S\) follows:

\[
P(S) \sim S^{-\lambda}
\]

where \(\lambda\) is the gap scaling exponent. This distribution is mathematically related to the **Riemann Zeta function**:

\[
\zeta(s) = \sum_{n=1}^{\infty} n^{-s}
\]

which generates the Zipf distribution when \(s = \lambda\).

### The Apollonian Gasket Analogy

We conjecture a geometric relationship between canopy surface dimension and gap exponent, analogous to the **Apollonian gasket**---a fractal packing of circles where each interstice is filled with the largest possible circle.

In an Apollonian gasket, the fractal dimension \(D_{\text{AG}} \approx 1.3057\) of the residual set (the gasket itself) determines the power-law distribution of circle sizes. We hypothesize an analogous relationship for forest canopies:

\[
D_{\text{surf}} \approx 3 - (\lambda - 1)
\]

This predicts that forests with larger gaps (smaller \(\lambda\)) will have rougher canopy surfaces (larger \(D_{\text{surf}}\)).

### Hypothesis Formulation

**Null Hypothesis (\(H_0\)):** Forest canopy gaps are randomly distributed (Poisson process), and the canopy surface dimension \(D_{\text{surf}}\) is uncorrelated with the gap size scaling exponent \(\lambda\).

**Alternative Hypothesis (\(H_A\)):** Old-growth forests self-organize into a critical state where gap sizes follow a **Zeta distribution** (\(P(S) \propto S^{-\lambda}\)). The fractal dimension of the canopy surface (\(D_{\text{surf}}\)) is coupled to the gap exponent such that \(D_{\text{surf}}\) increases as \(\lambda\) decreases, converging to a universal "critical roughness" in mature, resilient ecosystems.

### Airborne LiDAR Methodology

**Airborne Laser Scanning (ALS)** provides landscape-scale topographic data at sub-meter resolution:

**Data Acquisition:**

- Discrete-return or full-waveform LiDAR
- Point density: minimum 4 points/m\(^2\) for canopy structure
- Flight parameters: altitude 500--1000 m, scan angle \(<15^\circ\)

**CHM Generation:**

1. Classify point cloud into ground and non-ground returns
2. Generate Digital Terrain Model (DTM) from ground returns
3. Generate Digital Surface Model (DSM) from first returns
4. Compute CHM as \(\text{CHM} = \text{DSM} - \text{DTM}\)

**Gap Identification:**

1. Apply height threshold (CHM \(< 2\) m) to identify gap pixels
2. Perform connected-component labeling to delineate individual gaps
3. Calculate gap area and perimeter for each component

### Experimental Design

**Study Sites:** Select a successional gradient representing:

- Young plantation (10--30 years): even-aged monoculture
- Mid-successional (50--100 years): developing structure
- Old-growth (\(>200\) years): complex, multi-aged structure

Replicate across \(n \geq 5\) sites per successional stage.

**Measurements:** For each site:

1. Generate 1-m resolution CHM
2. Compute \(D_{\text{surf}}\) via DBC across scales \(r = 2, 4, 8, 16, 32, 64\) m
3. Identify and measure all gaps \(> 4\) m\(^2\)
4. Fit gap size distribution to Zeta (power-law) model
5. Test goodness-of-fit against Poisson and exponential alternatives

**Statistical Analysis:**

- Correlate \(D_{\text{surf}}\) with \(\lambda\) across sites using Pearson correlation
- Test the predicted relationship \(D_{\text{surf}} = 3 - (\lambda - 1)\) using regression
- Compare gap size distributions between successional stages using Kolmogorov-Smirnov tests
- Evaluate model fit using AIC/BIC for competing distribution families
