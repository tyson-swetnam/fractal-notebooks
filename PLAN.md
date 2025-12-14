# PLAN.md - Website Restructuring Plan

This document outlines a proposed restructuring of the Fractal Notebooks documentation to create a logical progression through fractal mathematics, dimensionality, and their applications to natural phenomena.

## Current State Analysis

### Existing Content
- **Main Paper**: `index.md`, `introduction.md`, `methods.md`, `results.md`, `discussion.md`, `conclusion.md`
- **Reference Material**: `glossary.md`, `dims.md`, `references.md`
- **Applications**: `applications.md`, `dbc.md`, `tree_roots.md`, `installation.md`
- **Jupyter Notebooks**: DLA, ferns, fractals, DBC, Riemann zeta (2D/3D)

### New Material (notes_gemini/)
- `biological_space.md` - WBE model extensions, DLA, complex dimensions, Riemann zeta
- `hypotheses.md` - Three testable research hypotheses framework
- `spectral_geometry.md` - Fractal strings, complex dimensions, Apollonian packings, R-trees

### Issues with Current Structure
1. Content duplication between `index.md` and `dims.md`
2. Single monolithic paper structure doesn't accommodate new advanced topics
3. No clear separation between tutorial/background and research content
4. New notes_gemini content not integrated

---

## Proposed New Structure

### Part I: Foundations (No IMRD Structure)

These chapters provide mathematical and historical background. They are educational/tutorial in nature.

#### Chapter 1: History of Fractal Mathematics
**File**: `docs/foundations/history.md`

- 1.1 Pre-Mandelbrot: Cantor, Koch, Sierpinski, Julia
- 1.2 Benoit Mandelbrot and the birth of fractal geometry (1975-1985)
- 1.3 Self-similarity vs Self-affinity: Mandelbrot's distinction
- 1.4 Fractals enter biology: Sernetz, West, Brown, Enquist
- 1.5 Modern developments: Complex dimensions and spectral geometry

#### Chapter 2: Mathematical Foundations
**File**: `docs/foundations/mathematics.md`

- 2.1 Topological vs Fractal Dimension
- 2.2 Hausdorff-Besicovitch Dimension
- 2.3 Box-Counting (Minkowski-Bouligand) Dimension
- 2.4 Differential Box-Counting for grayscale/continuous data
- 2.5 Power laws and scaling relations: $N \propto \varepsilon^{-D}$
- 2.6 The Hurst exponent and fractional Brownian motion
- 2.7 Lacunarity: measuring texture and gaps

#### Chapter 3: Fractal Dimensionality (1D through 4D)
**File**: `docs/foundations/dimensionality.md`

- 3.1 One-Dimensional Fractals
  - 1/f noise (pink noise)
  - Fractional Brownian motion
  - Cantor sets
- 3.2 Two-Dimensional Fractals
  - Fractional Brownian surfaces
  - Mandelbrot and Julia sets
  - Sierpinski triangle/carpet
  - Koch curves
- 3.3 Three-Dimensional Fractals
  - Menger sponge
  - 3D DLA clusters
  - Branching networks
- 3.4 Four-Dimensional Fractals
  - Time-evolving fractals
  - Spacetime fractality

#### Chapter 4: Glossary and Equations
**File**: `docs/foundations/glossary.md`

- Comprehensive glossary (expand from existing)
- Summary of key equations
- Quick reference for fractal dimension formulas

---

### Part II: Metabolic Scaling Theory and Biological Fractals

This is the core research paper. Uses full IMRD structure.

#### Chapter 5: Self-Affinity in Vascular Organisms
**File Structure**:
- `docs/metabolic-scaling/abstract.md`
- `docs/metabolic-scaling/introduction.md`
- `docs/metabolic-scaling/methods.md`
- `docs/metabolic-scaling/results.md`
- `docs/metabolic-scaling/discussion.md`
- `docs/metabolic-scaling/conclusion.md`
- `docs/metabolic-scaling/references.md`

##### Introduction
- The distinction between self-similarity and self-affinity
- Historical misuse of "self-similar" in ecology literature
- Table 1: Literature review of fractal dimension measurements
- Research questions and hypotheses

##### Methods
- Metabolic Scaling Theory (WBE) framework
- Derivation of branching ratios: $\xi = n^{-1/2}$, $\gamma = n^{-1/3}$
- Volume and mass dimension predictions: $d_m = 3/2$
- Differential box-counting methodology
- FracLac analysis procedures

##### Results
- Table 2: Synthetic fractal dimensions (L-systems, Barnsley fern)
- Table 3: Observed leaf mass dimensions
- Table 4: Observed branch/root mass dimensions
- Table 5: Forest canopy height model dimensions
- Statistical validation of MST predictions

##### Discussion
- Convergence toward self-affinity from MST
- Path fractions and branching asymmetry
- Non-vascular organisms: DLA and Eden models
- Why vascular life forms dominate

##### Conclusion
- Self-affine vs self-similar: implications for ecology
- Entropy maximization through mass transfer
- Future directions

##### References
- Complete bibliography

---

### Part III: Complex Dimensions and Spectral Geometry

Advanced mathematical theory chapter. Uses full IMRD structure.

#### Chapter 6: Spectral Geometry of Fractal Information
**File Structure**:
- `docs/spectral-geometry/abstract.md`
- `docs/spectral-geometry/introduction.md`
- `docs/spectral-geometry/methods.md`
- `docs/spectral-geometry/results.md`
- `docs/spectral-geometry/discussion.md`
- `docs/spectral-geometry/conclusion.md`
- `docs/spectral-geometry/references.md`

##### Introduction
- The geometry of complexity: spectral duality
- Failure of uniformity assumptions
- Lapidus-van Frankenhuijsen theory of complex dimensions
- Research objectives

##### Methods
- Fractal strings and geometric zeta functions: $\zeta_{\mathcal{L}}(s) = \sum_{j=1}^{\infty} \ell_j^s$
- Complex dimensions as poles
- The Cantor string example
- Explicit formulas and oscillations
- Fractal sprays in higher dimensions

##### Results
- The Riemann Zeta distribution (Zipf's Law)
- Algorithmic oscillations in divide-and-conquer sorting
- Mellin transform analysis (Flajolet)
- Apollonian gasket packing: $\delta \approx 1.30568$
- Zagier's theorem and connection to Riemann Hypothesis

##### Discussion
- Spectral zeta functions and "hearing the shape of a drum"
- R-tree performance on fractal data
- Faloutsos-Kamel fractal dimension cost model
- Universal spectral chirality

##### Conclusion
- The "Fractal Riemann Hypothesis"
- Sorting as packing: unified perspective
- Implications for spatial databases and algorithms

##### References

---

### Part IV: Biological Space-Filling and Thermodynamic Geometry

Biological applications chapter. Uses full IMRD structure.

#### Chapter 7: Self-Affine Fractals in Biological Systems
**File Structure**:
- `docs/biological-geometry/abstract.md`
- `docs/biological-geometry/introduction.md`
- `docs/biological-geometry/methods.md`
- `docs/biological-geometry/results.md`
- `docs/biological-geometry/discussion.md`
- `docs/biological-geometry/conclusion.md`
- `docs/biological-geometry/references.md`

##### Introduction
- The geometric imperative of biological existence
- Self-affine vs self-similar in biology
- Pre-fractals and finite scale constraints

##### Methods
- WBE model and anisotropic branching
  - Radial scaling (area-preserving): $\beta_r = n^{-1/2}$
  - Longitudinal scaling (space-filling): $\beta_l = n^{-1/3}$
- Iterated Function Systems (IFS) for ferns
- Thermodynamic formalism: partition functions
- DLA models for non-vascular organisms

##### Results
- Deviations and "wiggles": complex dimension signatures
- Lichen DLA morphology: $D \approx 1.6-1.7$
- Kelp forests: hydrodynamic DLA
- Crown shyness: Voronoi tessellations
- Apollonian packing in forest canopies
- Root foraging: spectral dimensions

##### Discussion
- Complex dimensions and log-periodic oscillations
- The Riemann zeta function and biological rhythms
- Periodical cicadas and prime numbers
- Phyllotaxis and the Golden Mean

##### Conclusion
- Organisms as "zeta function machines"
- Table: Summary of fractal strategies in biology

##### References

---

### Part V: Research Framework and Testable Hypotheses

Proposed experimental research. Uses full IMRD structure.

#### Chapter 8: Testable Hypotheses in Fractal Ecology
**File Structure**:
- `docs/hypotheses/abstract.md`
- `docs/hypotheses/introduction.md`
- `docs/hypotheses/methods.md`
- `docs/hypotheses/results.md` (expected/preliminary)
- `docs/hypotheses/discussion.md`
- `docs/hypotheses/conclusion.md`
- `docs/hypotheses/references.md`

##### Introduction
- Research framework: fractal geometry of biological assembly
- Three scales: Micro (DLA), Meso (branching), Macro (canopy)
- Null vs alternative hypothesis structure

##### Methods

**Hypothesis 1: Stochastic Geometry in Lichens/Algae**
- DLA and sticking probability
- Nutrient scarcity-compactness trade-off
- Sand Box Method for dimension calculation
- Experimental design with agar media gradients

**Hypothesis 2: Angiosperms vs Gymnosperms**
- WBE predictions: monofractal vs multifractal
- Path fraction analysis
- TLS point cloud acquisition
- QSM extraction and WTMM analysis

**Hypothesis 3: Canopy Topography and Gap Dynamics**
- Differential Box Counting on CHM
- Zeta distribution of gap sizes
- Apollonian gasket analogy
- Airborne LiDAR methodology

##### Results (Expected/Preliminary)
- Predicted outcomes under $H_0$ and $H_A$
- Preliminary data if available

##### Discussion
- Implications for ecological theory
- Connections to MST and thermodynamics
- Cross-scale synthesis

##### Conclusion
- Summary of mathematical approaches by domain
- Future experimental priorities

##### References

---

### Part VI: Interactive Applications

#### Chapter 9: Tools and Demonstrations
**File**: `docs/applications/index.md`

- 9.1 Installation Guide (`docs/applications/installation.md`)
- 9.2 React Interactive Applications (`docs/applications/react-apps.md`)
  - Mandelbrot/Julia explorers
  - DLA simulators
  - Tree/Fern generators
  - Riemann zeta visualizations
- 9.3 Streamlit Applications (`docs/applications/streamlit-apps.md`)
- 9.4 Differential Box-Counting Tool (`docs/applications/dbc.md`)
- 9.5 3D Branching Visualization (`docs/applications/tree-roots-3d.md`)

---

### Part VII: Jupyter Notebooks

#### Chapter 10: Computational Notebooks
**File**: `docs/notebooks/index.md`

- 10.1 Diffusion Limited Aggregation (`notebooks/dla.ipynb`)
- 10.2 Barnsley's Ferns (`notebooks/ferns.ipynb`)
- 10.3 Self-Similar Fractals (`notebooks/fractals.ipynb`)
- 10.4 Self-Affine Fractal Generators (`notebooks/fractal_generators.ipynb`)
- 10.5 Differential Box-Counting (`notebooks/dbc.ipynb`)
- 10.6 Riemann Zeta 2D (`notebooks/zeta_space.ipynb`)
- 10.7 Riemann Zeta 3D (`notebooks/zeta_3d.ipynb`)

---

## Navigation Structure (mkdocs.yml)

```yaml
nav:
  - Home: index.md

  - Part I - Foundations:
    - History of Fractals: foundations/history.md
    - Mathematical Foundations: foundations/mathematics.md
    - Fractal Dimensionality: foundations/dimensionality.md
    - Glossary & Equations: foundations/glossary.md

  - Part II - Metabolic Scaling:
    - Abstract: metabolic-scaling/abstract.md
    - Introduction: metabolic-scaling/introduction.md
    - Methods: metabolic-scaling/methods.md
    - Results: metabolic-scaling/results.md
    - Discussion: metabolic-scaling/discussion.md
    - Conclusion: metabolic-scaling/conclusion.md
    - References: metabolic-scaling/references.md

  - Part III - Spectral Geometry:
    - Abstract: spectral-geometry/abstract.md
    - Introduction: spectral-geometry/introduction.md
    - Methods: spectral-geometry/methods.md
    - Results: spectral-geometry/results.md
    - Discussion: spectral-geometry/discussion.md
    - Conclusion: spectral-geometry/conclusion.md
    - References: spectral-geometry/references.md

  - Part IV - Biological Geometry:
    - Abstract: biological-geometry/abstract.md
    - Introduction: biological-geometry/introduction.md
    - Methods: biological-geometry/methods.md
    - Results: biological-geometry/results.md
    - Discussion: biological-geometry/discussion.md
    - Conclusion: biological-geometry/conclusion.md
    - References: biological-geometry/references.md

  - Part V - Research Hypotheses:
    - Abstract: hypotheses/abstract.md
    - Introduction: hypotheses/introduction.md
    - Methods: hypotheses/methods.md
    - Expected Results: hypotheses/results.md
    - Discussion: hypotheses/discussion.md
    - Conclusion: hypotheses/conclusion.md
    - References: hypotheses/references.md

  - Part VI - Applications:
    - Overview: applications/index.md
    - Installation: applications/installation.md
    - React Apps: applications/react-apps.md
    - Streamlit Apps: applications/streamlit-apps.md
    - Box-Counting Tool: applications/dbc.md
    - 3D Visualization: applications/tree-roots-3d.md

  - Part VII - Notebooks:
    - Overview: notebooks/index.md
    - DLA: notebooks/old_dla.ipynb
    - Ferns: notebooks/ferns.ipynb
    - Self-Similar Fractals: notebooks/fractals.ipynb
    - Self-Affine Generators: notebooks/fractal_generators.ipynb
    - Differential Box-Counting: notebooks/dbc.ipynb
    - Riemann Zeta 2D: notebooks/zeta_space.ipynb
    - Riemann Zeta 3D: notebooks/zeta_3d.ipynb

  - Interactive React Apps: react/
```

---

## Migration Plan

### Phase 1: Directory Structure
1. Create new directories under `docs/`:
   - `foundations/`
   - `metabolic-scaling/`
   - `spectral-geometry/`
   - `biological-geometry/`
   - `hypotheses/`
   - `applications/`

### Phase 2: Content Migration
1. Move and refactor existing content:
   - `introduction.md` → `metabolic-scaling/introduction.md` (with edits)
   - `methods.md` → `metabolic-scaling/methods.md`
   - `results.md` → `metabolic-scaling/results.md`
   - `discussion.md` → `metabolic-scaling/discussion.md`
   - `conclusion.md` → `metabolic-scaling/conclusion.md`
   - `references.md` → `metabolic-scaling/references.md`
   - `glossary.md` → `foundations/glossary.md`
   - `dims.md` → `foundations/dimensionality.md`

2. Extract and organize from `index.md`:
   - Abstract → `metabolic-scaling/abstract.md`
   - 1D/2D/3D content → `foundations/dimensionality.md`

### Phase 3: New Content Integration
1. Process `notes_gemini/spectral_geometry.md`:
   - Split into IMRD sections under `spectral-geometry/`

2. Process `notes_gemini/biological_space.md`:
   - Split into IMRD sections under `biological-geometry/`

3. Process `notes_gemini/hypotheses.md`:
   - Split into IMRD sections under `hypotheses/`

### Phase 4: New Content Creation
1. Write `foundations/history.md` (new)
2. Write `foundations/mathematics.md` (new, consolidate from existing)
3. Write chapter abstracts for each research section
4. Create index pages for applications and notebooks

### Phase 5: Navigation and Integration
1. Update `mkdocs.yml` with new navigation
2. Update internal links throughout
3. Test build and fix broken references
4. Update `index.md` as landing page

---

## Content Sources Mapping

| New Section | Primary Source | Secondary Sources |
|-------------|---------------|-------------------|
| History | New content | introduction.md (history parts) |
| Mathematics | glossary.md, methods.md | dims.md |
| Dimensionality | dims.md, index.md | - |
| Glossary | glossary.md | - |
| Metabolic Scaling | introduction.md, methods.md, results.md, discussion.md, conclusion.md | - |
| Spectral Geometry | notes_gemini/spectral_geometry.md | - |
| Biological Geometry | notes_gemini/biological_space.md | discussion.md (parts) |
| Hypotheses | notes_gemini/hypotheses.md | - |
| Applications | applications.md, dbc.md, tree_roots.md, installation.md | - |

---

## Timeline Estimate

This restructuring involves:
- Creating ~25-30 new markdown files
- Refactoring existing content from ~10 files
- Processing 3 large notes_gemini documents
- Updating mkdocs.yml navigation
- Cross-linking and consistency checking

The work should be done incrementally, chapter by chapter, to maintain a working site throughout.

---

## Open Questions for User

1. Should each "Part" have its own landing/index page summarizing the chapters?
2. Should references be consolidated into one master file or kept per-chapter?
3. Are there additional notes or content files not yet in the repository?
4. What is the preferred citation style for references?
5. Should the React applications be documented in more detail?
