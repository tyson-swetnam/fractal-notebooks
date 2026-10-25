---
type: Guide
title: "React Interactive Applications"
description: >-
  Guide to the fifteen React apps (sixteen routes including the home page):
  Mandelbrot and Julia sets, Brownian motion, Game of Life, noise and wave
  dynamics, L-system plants, Barnsley ferns, fractal and Pythagoras trees, DLA,
  a 3D tree with roots and zeta space tilings, with deep links.
resource: https://tyson-swetnam.github.io/fractal-notebooks/applications/react-apps/
tags: [app, react, complex-dynamics, branching, riemann-zeta]
generated:
  by: human:tswetnam
  at: "2025-12-14T00:00:00Z"
status: stable
---

# React Interactive Applications

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.

The React application suite provides high-performance, GPU-accelerated fractal visualizations directly in your web browser.

[**Launch All Apps**](https://tyson-swetnam.github.io/fractal-notebooks/react/){ .md-button .md-button--primary }

## Open an App

The suite is a single-page React application served from `/react/` and routed client-side with a HashRouter, so every app has a stable deep link of the form `…/react/#/<route>`. Because the routing happens in JavaScript, the links below only work in a browser; the sections that follow describe what each app does.

| App | Launch | Documented in |
|---|---|---|
| Home | [react/#/](https://tyson-swetnam.github.io/fractal-notebooks/react/#/) | Landing page with the category menus |
| Mandelbrot Set | [#/mandelbrot](https://tyson-swetnam.github.io/fractal-notebooks/react/#/mandelbrot) | [Mandelbrot Set](#mandelbrot-set) |
| Julia Sets | [#/julia](https://tyson-swetnam.github.io/fractal-notebooks/react/#/julia) | [Julia Sets](#julia-sets) |
| Brownian Motion | [#/brownian](https://tyson-swetnam.github.io/fractal-notebooks/react/#/brownian) | [Brownian Motion](#brownian-motion) |
| Conway's Game of Life | [#/conway](https://tyson-swetnam.github.io/fractal-notebooks/react/#/conway) | [Conway's Game of Life](#conways-game-of-life) |
| Noise Patterns | [#/noise](https://tyson-swetnam.github.io/fractal-notebooks/react/#/noise) | [Noise Generators](#noise-generators) |
| Wave Dynamics | [#/waves](https://tyson-swetnam.github.io/fractal-notebooks/react/#/waves) | [Waves Visualization](#waves-visualization) |
| Plant Architecture Lab | [#/plant-lab](https://tyson-swetnam.github.io/fractal-notebooks/react/#/plant-lab) | [L-System Trees](#l-system-trees) |
| Fern Frond 3D | [#/fern-frond-3d](https://tyson-swetnam.github.io/fractal-notebooks/react/#/fern-frond-3d) | [Barnsley Fern](#barnsley-fern) |
| Diffusion-Limited Aggregation | [#/dla](https://tyson-swetnam.github.io/fractal-notebooks/react/#/dla) | [Diffusion Limited Aggregation](#diffusion-limited-aggregation) |
| Barnsley Ferns | [#/ferns](https://tyson-swetnam.github.io/fractal-notebooks/react/#/ferns) | [Barnsley Fern](#barnsley-fern) |
| Fractal Trees | [#/trees](https://tyson-swetnam.github.io/fractal-notebooks/react/#/trees) | [Fractal Trees](#fractal-trees) |
| Pythagoras Tree | [#/pythagoras](https://tyson-swetnam.github.io/fractal-notebooks/react/#/pythagoras) | [Pythagoras Tree](#pythagoras-tree) |
| 3D Tree with Roots | [#/tree-roots-3d](https://tyson-swetnam.github.io/fractal-notebooks/react/#/tree-roots-3d) | [3D Tree and Root Visualization](tree-roots-3d.md) |
| Zeta Space Tiling | [#/zeta-space-tiling](https://tyson-swetnam.github.io/fractal-notebooks/react/#/zeta-space-tiling) | [Riemann Zeta](#riemann-zeta) |
| 3D Zeta Visualization | [#/zeta-3d-visualization](https://tyson-swetnam.github.io/fractal-notebooks/react/#/zeta-3d-visualization) | [Riemann Zeta 3D](#riemann-zeta-3d) |

---

## Fractal Visualizations

### Mandelbrot Set

The Mandelbrot set is defined as the set of complex numbers \( c \) for which the iteration:

\[
z_{n+1} = z_n^2 + c, \quad z_0 = 0
\]

remains bounded.

**Features:**
- Real-time zoom and pan
- Adjustable iteration count
- Multiple color schemes
- WebGL-accelerated rendering

**Controls:**
- Click and drag to pan
- Scroll to zoom
- Adjust max iterations for detail

---

### Julia Sets

Julia sets use the same iteration as the Mandelbrot set, but \( c \) is fixed and the initial value \( z_0 \) varies:

\[
z_{n+1} = z_n^2 + c
\]

**Features:**
- Interactive parameter selection
- Real-time preview
- Connection to Mandelbrot set visualization
- Click on Mandelbrot to select Julia parameter

---

### Brownian Motion

A random walk in the plane: at each step the particle moves a fixed distance in a uniformly random direction, \( z_{n+1} = z_n + \epsilon_n \), and the app traces the path as it grows.

**Features:**
- Adjustable random-walk parameters with animated path drawing
- Box-counting estimate of the fractal dimension of the trace
- Mathematical background panel; see [Chapter 3 §3.1.2](../foundations/dimensionality.md#312-fractional-brownian-motion) for the fractional generalisation with Hurst exponent \( H \)

---

### Diffusion Limited Aggregation

DLA simulates particle aggregation through random walks, producing fractal clusters with dimension \( D \approx 1.7 \).

**Features:**
- Step-by-step or continuous simulation
- Adjustable particle count
- Sticking probability control
- Export cluster data

**Vector-field guidance:** in addition to their random walk, particles can drift under a *radial*, *spiral* or *uniform* vector field, producing directional spreading patterns. Rendering uses WebGL shaders with a Canvas fallback, and a statistics panel tracks the growing cluster.

**Algorithm:**
1. Start with a seed particle at center
2. Release particles at random boundary positions
3. Particles random walk until they stick to the cluster
4. Repeat to grow the structure

---

### Barnsley Fern

The Barnsley fern is generated using an Iterated Function System (IFS) with four affine transformations.

**Transformations:**

| Transform | Probability | Description |
|-----------|-------------|-------------|
| \( f_1 \) | 0.01 | Stem |
| \( f_2 \) | 0.85 | Main leaflet |
| \( f_3 \) | 0.07 | Left leaflet |
| \( f_4 \) | 0.07 | Right leaflet |

The coefficients of the four maps are listed in the [glossary](../foundations/glossary.md#barnsley-fern).

**Features:**
- Adjustable transformation parameters
- Point count control
- Real-time rendering
- Export as image

A companion app, [Fern Frond 3D](https://tyson-swetnam.github.io/fractal-notebooks/react/#/fern-frond-3d), renders a frond in three dimensions.

---

## Branching Architectures

### Pythagoras Tree

A self-similar fractal tree where each branch generates two smaller branches forming a right triangle.

**Features:**
- Adjustable branching angle
- Iteration depth control
- Color gradient by depth
- Animation support

**Mathematics:**
At depth \( n \), the side length is \( r^n \) where \( r = \cos\theta \) for angle \( \theta \).

---

### L-System Trees

Lindenmayer systems (L-systems) use formal grammars to generate plant-like structures. The **Plant Architecture Lab** ([#/plant-lab](https://tyson-swetnam.github.io/fractal-notebooks/react/#/plant-lab)) grows bryophytes, ferns, lichens and vascular plants from L-systems with one 3D engine and nine botanically informed growth forms, and reports an estimated box-counting dimension for each form.

**Example Rules:**
```
Axiom: F
Rules: F → F[+F]F[-F]F
```

**Features:**
- Growth-form presets (plant and lichen forms)
- Branch angle, angle variation, iterations, length and width falloff, and tropism controls
- Toggle for leaves and other organs
- Statistics panel with the estimated fractal dimension

---

### Fractal Trees

Recursive branching with natural variation and selectable growth styles: each branch spawns smaller branches scaled in length and width, and the app reports an approximate fractal dimension that rises with the branching factor.

**Features:**
- Tree-style presets and a mathematics panel
- Length and width scaling, branching factor and depth controls
- Plotly rendering with animated growth

---

## Noise Generators

The **Noise Patterns** app ([#/noise](https://tyson-swetnam.github.io/fractal-notebooks/react/#/noise)) generates white, pink, red and Brownian traces in four tabs, with optional power spectral density and fractal-dimension overlays, so the spectral exponents can be compared directly.

### Pink Noise (1/f Noise)

Generates signals with power spectral density:

\[
S(f) \propto \frac{1}{f^\alpha}
\]

where \( \alpha \approx 1 \) for pink noise.

**Features:**
- Adjustable spectral exponent
- Waveform visualization
- Spectrum analysis

---

### Fractional Brownian Motion

Self-affine random process controlled by the Hurst exponent \( H \):

- \( H > 0.5 \): Persistent (trending)
- \( H = 0.5 \): Standard Brownian motion
- \( H < 0.5 \): Anti-persistent (mean-reverting)

---

## Mathematical Visualizations

### Riemann Zeta

**Zeta Space Tiling** ([#/zeta-space-tiling](https://tyson-swetnam.github.io/fractal-notebooks/react/#/zeta-space-tiling); the page titles itself *Bourke Random Tiling*) fills a square plane with non-overlapping shapes after Paul Bourke's random space-filling algorithm. The \( i \)-th shape placed has area

\[
A_i = \frac{A_0}{i^{c}}, \qquad \sum_{i=1}^{\infty} A_i = A_0 \sum_{i=1}^{\infty} \frac{1}{i^{c}} = A_0\,\zeta(c),
\]

so for \( c > 1 \) the total area converges to \( A_0 \zeta(c) \), where \( A_0 \) is the chosen maximum shape area. Each shape is dropped at a random position and orientation and retried (up to 1000 times) if it crosses the plane boundary or overlaps an earlier shape, using Bourke's line-segment intersection and point-in-polygon tests behind a bounding-circle check.

**Features:**
- Shape set: circles, triangles, squares or a mix, drawn in black on a Plotly canvas with pan and zoom
- Power-law exponent \( c \) (0.001 to 2.5, default 2), maximum shape area \( A_0 \) (1 to 50), plane size (10 to 50) and iteration count (100 to 10 000)
- Hover shows each shape's area and placement index; a statistics panel reports the number of shapes placed
- "Generate New Tiling" redraws with new random positions; a Mathematics tab states the power law and the \( \zeta(c) \) normalisation

The Jupyter counterpart is the [Chapter 4: Zeta Space Tilings](../notebooks/foundations/4_zeta_space.md) notebook.

---

### Riemann Zeta 3D

**3D Zeta Visualization** ([#/zeta-3d-visualization](https://tyson-swetnam.github.io/fractal-notebooks/react/#/zeta-3d-visualization)) is the three-dimensional counterpart: spheres, cubes and tetrahedra with volumes

\[
V_i = \frac{A_0}{i^{p}}, \qquad p > 1,
\]

are packed into a cubic volume without overlap. Each volume is converted to a sphere radius, cube edge or tetrahedron edge, the list is shuffled, and each shape is placed at a random position (spherical overlap test, 1000 attempts); a shape that does not fit is halved until it does or reaches the minimum size.

**Features:**
- Any combination of spheres, cubes and tetrahedra, rendered as Plotly `scatter3d` markers and `mesh3d` meshes
- Exponent \( p \) (1.05 to 2.5, default 1.2), initial volume \( A_0 \), total volume, number of shapes and maximum particle size, with \( \zeta(p) \) computed live
- Camera rotation sliders with auto-rotate, and an animation that adds the shapes one by one at adjustable speed
- Statistics panel with \( \zeta(p) \), shapes placed and packing efficiency; "Reset to Notebook Defaults" restores the parameters of the `zeta_3d` research notebook

The Jupyter counterpart is the [`foundations/zeta_3d`](../notebooks/research.md#work-in-progress) research notebook.

---

## Conway's Game of Life

Cellular automaton with emergent complexity from simple rules, rendered full-screen with WebGL shaders.

**Rules:**
1. Live cell with 2-3 neighbors survives
2. Dead cell with exactly 3 neighbors becomes alive
3. All other cells die or stay dead

**Features:**
- Preset pattern library and game controls
- 240 × 120 grid at 75% initial density by default, with speed control
- Four colour schemes (classic, neon, fire, ocean) with cell-age shading
- Population statistics

---

## Waves Visualization

Wave interference patterns demonstrating harmonic superposition: a tidal component plus three wave components and a noise term,

\[
y(t) = A_{\text{tide}} \sin\left(\frac{2\pi t}{T_{\text{tide}}}\right) + \sum_{i=1}^{3} A_i \sin(2\pi f_i t + \phi_i) + \epsilon(t)
\]

**Features:**
- Multiple wave sources
- Frequency and amplitude control
- Toggle to show the individual components
- Connection to Fourier analysis

---

## Technical Details

### Performance

- WebGL 2.0 for GPU-accelerated rendering
- Shader-based computation for Mandelbrot/Julia
- Canvas 2D for simpler visualizations
- React 18 with optimized rendering

### Features

- KaTeX-rendered equations and a mathematical-context panel on every page
- Material-UI theming with light, dark and system modes
- Dropdown navigation organised by category (1D/2D/3D Fractals, Riemann Zeta Functions, Branching Architectures)
- Responsive layout for desktop, tablet and mobile

### Browser Compatibility

| Browser | Support |
|---------|---------|
| Chrome 90+ | Full |
| Firefox 88+ | Full |
| Safari 14+ | Full |
| Edge 90+ | Full |

### Development

Source code is in `react/src/pages/` organized by category:
- `fractals-1d-2d-3d/` - Core fractal visualizations
- `branching-architectures/` - Tree and plant structures
- `riemann-zeta-functions/` - Zeta function visualizations

Each page is wired in two places: an import plus `<Route>` in `App.tsx`, and an entry in the nav config in `components/layout/Navigation.tsx`. For setup and development instructions see the [React README](https://github.com/tyson-swetnam/fractal-notebooks/tree/main/react#readme).
