# React Interactive Applications

The React application suite provides high-performance, GPU-accelerated fractal visualizations directly in your web browser.

[**Launch All Apps**](../react/){ .md-button .md-button--primary }

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

### Diffusion Limited Aggregation

DLA simulates particle aggregation through random walks, producing fractal clusters with dimension \( D \approx 1.7 \).

**Features:**
- Step-by-step or continuous simulation
- Adjustable particle count
- Sticking probability control
- Export cluster data

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

**Features:**
- Adjustable transformation parameters
- Point count control
- Real-time rendering
- Export as image

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

Lindenmayer systems (L-systems) use formal grammars to generate plant-like structures.

**Example Rules:**
```
Axiom: F
Rules: F → F[+F]F[-F]F
```

**Features:**
- Custom axiom and rules
- Adjustable angle and length
- Multiple preset configurations
- Step-through generation

---

## Noise Generators

### Pink Noise (1/f Noise)

Generates signals with power spectral density:

\[
S(f) \propto \frac{1}{f^\alpha}
\]

where \( \alpha \approx 1 \) for pink noise.

**Features:**
- Adjustable spectral exponent
- Real-time audio playback
- Waveform visualization
- Spectrum analysis

---

### Fractional Brownian Motion

Self-affine random process controlled by the Hurst exponent \( H \):

- \( H > 0.5 \): Persistent (trending)
- \( H = 0.5 \): Standard Brownian motion
- \( H < 0.5 \): Anti-persistent (mean-reverting)

**Features:**
- Hurst exponent slider
- 1D trace and 2D surface generation
- Export data for analysis

---

## Mathematical Visualizations

### Riemann Zeta

Visualization of the Riemann zeta function:

\[
\zeta(s) = \sum_{n=1}^{\infty} \frac{1}{n^s}
\]

**Features:**
- Complex plane exploration
- Zero highlighting
- Critical strip focus
- Domain coloring

---

### Riemann Zeta 3D

Three-dimensional surface plot of \( |\zeta(s)| \).

**Features:**
- Interactive rotation
- Adjustable domain
- Multiple visualization modes
- Pole detection

---

## Conway's Game of Life

Cellular automaton with emergent complexity from simple rules.

**Rules:**
1. Live cell with 2-3 neighbors survives
2. Dead cell with exactly 3 neighbors becomes alive
3. All other cells die or stay dead

**Features:**
- Pattern library
- Custom pattern drawing
- Speed control
- Population statistics

---

## Waves Visualization

Wave interference patterns demonstrating harmonic superposition.

**Features:**
- Multiple wave sources
- Frequency and amplitude control
- Interference pattern visualization
- Connection to Fourier analysis

---

## Technical Details

### Performance

- WebGL 2.0 for GPU-accelerated rendering
- Shader-based computation for Mandelbrot/Julia
- Canvas 2D for simpler visualizations
- React 18 with optimized rendering

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
