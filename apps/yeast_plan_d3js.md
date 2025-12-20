# Yeast Colony Simulation with D3.js Force-Directed Graph

## Overview

A real-time, interactive yeast colony simulation using D3.js force-directed network graphs embedded in a Streamlit application. The simulation models both **normal yeast** (separating cells) and **snowflake yeast** (permanently attached cells) with realistic cell dynamics including growth, shrinkage, death, and mobility.

## Core Concept

Model yeast cells as **nodes** in a D3.js force simulation, with **links** representing the permanent attachments between mother-daughter cells in snowflake yeast. This approach naturally handles:
- Cell mobility via force simulation
- Attachment constraints via link forces
- Collision avoidance via collision detection
- Visual representation of cell state (size, color, opacity)

---

## Data Model

### Cell Node Structure

```javascript
{
  id: string,              // Unique cell identifier
  x: number,               // Current x position
  y: number,               // Current y position
  vx: number,              // Velocity x (managed by D3)
  vy: number,              // Velocity y (managed by D3)
  radius: number,          // Current cell radius (grows/shrinks)
  targetRadius: number,    // Target radius for growth animation
  aspectRatio: number,     // Length/width ratio (1.2 ancestral, 2.7 evolved)
  orientation: number,     // Rotation angle in radians
  age: number,             // Simulation ticks since birth
  generation: number,      // Distance from founder cell
  energy: number,          // 0-100, affects growth/division/death
  state: string,           // 'growing' | 'mature' | 'dividing' | 'dying' | 'dead'
  parentId: string | null, // ID of parent cell (for snowflake)
  budsProduced: number,    // Count of daughter cells produced
  maxBuds: number,         // Maximum daughters (typically 4-6)
  isSnowflake: boolean     // Whether cell stays attached
}
```

### Link Structure (Snowflake Yeast Only)

```javascript
{
  source: string,          // Parent cell ID
  target: string,          // Daughter cell ID
  strength: number,        // Link rigidity (high for snowflake)
  distance: number,        // Target distance (sum of radii)
  poleAngle: number        // Which pole of parent (0 or PI)
}
```

---

## Simulation Mechanics

### 1. Cell Lifecycle

```
BIRTH → GROWING → MATURE → [DIVIDING] → DYING → DEAD → REMOVED
                    ↑          ↓
                    └──────────┘ (new daughter)
```

**State Transitions:**
- `GROWING`: Cell radius increases toward targetRadius
- `MATURE`: Cell can divide if energy > threshold and buds available
- `DIVIDING`: Brief state during daughter cell creation
- `DYING`: Cell shrinks, opacity decreases
- `DEAD`: Cell removed from simulation after fade-out

### 2. Energy System

Each cell has an `energy` value (0-100) that:
- **Increases**: When cell has space (low local density)
- **Decreases**: When crowded (high local density) or old
- **Affects**: Division probability, growth rate, death probability

```javascript
// Energy update per tick
cell.energy += (1 - localDensity) * energyGainRate;
cell.energy -= ageDecayRate * (cell.age / maxAge);
cell.energy = clamp(cell.energy, 0, 100);

// Death check
if (cell.energy < deathThreshold) {
  cell.state = 'dying';
}
```

### 3. Growth & Shrinkage

```javascript
// Growing cells
if (cell.state === 'growing') {
  cell.radius += growthRate * (cell.energy / 100);
  if (cell.radius >= cell.targetRadius) {
    cell.state = 'mature';
  }
}

// Dying cells
if (cell.state === 'dying') {
  cell.radius -= shrinkRate;
  cell.opacity -= fadeRate;
  if (cell.radius < minRadius || cell.opacity < 0.1) {
    cell.state = 'dead';
  }
}
```

### 4. Division Logic

**Normal Yeast:**
- Daughter buds at random angle from mother
- After brief attachment, daughter **separates** (no link created)
- Both cells receive separation impulse (velocity push)

**Snowflake Yeast (Polar Budding):**
- Daughter buds at mother's pole (end of long axis)
- Permanent link created between mother and daughter
- Daughter's free pole faces outward for future budding

```javascript
function divide(mother) {
  const poleAngle = getAvailablePole(mother);  // 0 or PI from orientation
  const budDirection = mother.orientation + poleAngle;

  const daughter = {
    id: generateId(),
    x: mother.x + Math.cos(budDirection) * (mother.radius + initialRadius),
    y: mother.y + Math.sin(budDirection) * (mother.radius + initialRadius),
    radius: initialRadius,
    targetRadius: mother.targetRadius * budSizeRatio,
    orientation: budDirection,  // Aligned with mother (end-to-end)
    generation: mother.generation + 1,
    parentId: mother.id,
    state: 'growing',
    // ...
  };

  if (mother.isSnowflake) {
    // Create permanent link
    links.push({
      source: mother.id,
      target: daughter.id,
      distance: mother.radius + daughter.targetRadius,
      strength: 1.0
    });
  } else {
    // Apply separation impulse
    const impulse = separationForce;
    daughter.vx = Math.cos(budDirection) * impulse;
    daughter.vy = Math.sin(budDirection) * impulse;
    mother.vx = -Math.cos(budDirection) * impulse * 0.5;
    mother.vy = -Math.sin(budDirection) * impulse * 0.5;
  }

  mother.budsProduced++;
  return daughter;
}
```

---

## D3.js Force Simulation

### Force Configuration

```javascript
const simulation = d3.forceSimulation(nodes)
  // Collision: cells don't overlap
  .force('collision', d3.forceCollide()
    .radius(d => d.radius * 1.05)
    .strength(0.8)
    .iterations(3))

  // Links: snowflake attachments (only for snowflake mode)
  .force('link', d3.forceLink(links)
    .id(d => d.id)
    .distance(d => d.distance)
    .strength(d => d.strength))

  // Center: gentle pull toward center (prevents drift)
  .force('center', d3.forceCenter(width/2, height/2)
    .strength(0.01))

  // Boundary: keep cells in canvas
  .force('boundary', forceBoundary(width, height, padding))

  // Random motion: Brownian diffusion (normal yeast only)
  .force('brownian', forceBrownian(diffusionStrength))

  .alphaDecay(0.01)  // Slow decay for continuous simulation
  .velocityDecay(0.3);
```

### Custom Forces

**Boundary Force:**
```javascript
function forceBoundary(width, height, padding) {
  return function(alpha) {
    for (const node of nodes) {
      if (node.x < padding) node.vx += (padding - node.x) * 0.1;
      if (node.x > width - padding) node.vx += (width - padding - node.x) * 0.1;
      if (node.y < padding) node.vy += (padding - node.y) * 0.1;
      if (node.y > height - padding) node.vy += (height - padding - node.y) * 0.1;
    }
  };
}
```

**Brownian Motion Force (Normal Yeast):**
```javascript
function forceBrownian(strength) {
  return function(alpha) {
    for (const node of nodes) {
      if (!node.isSnowflake || node.parentId === null) {
        node.vx += (Math.random() - 0.5) * strength;
        node.vy += (Math.random() - 0.5) * strength;
      }
    }
  };
}
```

**Orientation Alignment Force (Snowflake):**
```javascript
// Keep daughter orientation aligned with link direction
function forceOrientation() {
  return function(alpha) {
    for (const link of links) {
      const dx = link.target.x - link.source.x;
      const dy = link.target.y - link.source.y;
      const targetAngle = Math.atan2(dy, dx);
      link.target.orientation = targetAngle;
    }
  };
}
```

---

## Rendering

### Canvas-Based Rendering (Performance)

```javascript
function render() {
  ctx.clearRect(0, 0, width, height);

  // Draw links first (behind cells)
  ctx.strokeStyle = 'rgba(0, 0, 0, 0.2)';
  ctx.lineWidth = 1;
  for (const link of links) {
    ctx.beginPath();
    ctx.moveTo(link.source.x, link.source.y);
    ctx.lineTo(link.target.x, link.target.y);
    ctx.stroke();
  }

  // Draw cells as ellipses
  for (const node of nodes) {
    if (node.state === 'dead') continue;

    ctx.save();
    ctx.translate(node.x, node.y);
    ctx.rotate(node.orientation);

    // Color by generation or state
    ctx.fillStyle = getColor(node);
    ctx.globalAlpha = node.state === 'dying' ? node.opacity : 0.85;

    // Draw ellipse
    ctx.beginPath();
    ctx.ellipse(0, 0,
      node.radius * node.aspectRatio,  // rx (semi-major)
      node.radius,                      // ry (semi-minor)
      0, 0, 2 * Math.PI);
    ctx.fill();
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 0.5;
    ctx.stroke();

    ctx.restore();
  }

  requestAnimationFrame(render);
}
```

### Color Schemes

```javascript
function getColor(node) {
  if (node.isSnowflake) {
    // Viridis-like for generation
    return d3.interpolateViridis(node.generation / maxGeneration);
  } else {
    // Warm colors for age
    return d3.interpolateYlOrBr(0.3 + 0.5 * node.age / maxAge);
  }
}
```

---

## Streamlit Integration

### App Structure

```python
# apps/yeast_d3js.py

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Yeast Colony Simulation", layout="wide")

st.title("Yeast Colony Simulation")
st.markdown("Interactive D3.js force-directed simulation of yeast growth")

# Sidebar controls
st.sidebar.header("Simulation Parameters")

mode = st.sidebar.radio("Yeast Type", ["Normal (Separating)", "Snowflake (Attached)"])

col1, col2 = st.sidebar.columns(2)
with col1:
    initial_cells = st.slider("Initial Cells", 1, 10, 3)
    max_cells = st.slider("Max Cells", 50, 500, 200)
with col2:
    division_rate = st.slider("Division Rate", 0.1, 1.0, 0.5)
    aspect_ratio = st.slider("Aspect Ratio", 1.0, 3.0, 1.2 if mode == "Normal" else 2.0)

death_enabled = st.sidebar.checkbox("Enable Cell Death", True)
brownian_motion = st.sidebar.slider("Brownian Motion", 0.0, 2.0, 0.5)

# Generate HTML with parameters
html_content = generate_d3_html(
    mode=mode,
    initial_cells=initial_cells,
    max_cells=max_cells,
    division_rate=division_rate,
    aspect_ratio=aspect_ratio,
    death_enabled=death_enabled,
    brownian_motion=brownian_motion
)

# Embed D3 visualization
components.html(html_content, height=700, scrolling=False)

# Stats display
st.sidebar.markdown("---")
st.sidebar.markdown("### Simulation Stats")
st.sidebar.markdown("Cell count and other stats update in real-time in the canvas")
```

### D3.js HTML Template

The `generate_d3_html()` function returns a complete HTML document with:
1. D3.js library (CDN)
2. Canvas element
3. Simulation code with injected parameters
4. Stats overlay
5. Play/pause/reset controls

---

## User Controls

### In-Canvas Controls

- **Play/Pause**: Toggle simulation running
- **Reset**: Clear and restart with initial cells
- **Speed**: Adjust simulation tick rate

### Streamlit Sidebar

- **Yeast Type**: Normal vs Snowflake
- **Initial Cells**: Starting colony size
- **Max Cells**: Population cap
- **Division Rate**: How often cells divide
- **Aspect Ratio**: Cell elongation (1.0 = circular)
- **Enable Death**: Toggle cell death mechanics
- **Brownian Motion**: Random movement strength (normal yeast)

---

## Implementation Phases

### Phase 1: Basic Simulation ✅
- [x] D3.js force simulation setup
- [x] Cell nodes with collision detection
- [x] Basic rendering (circles first)
- [x] Cell division (without attachment)
- [x] Streamlit embedding

### Phase 2: Snowflake Mode ✅
- [x] Link-based attachments
- [x] Polar budding logic
- [x] Orientation alignment
- [x] End-to-end cell rendering (ellipses)

### Phase 3: Lifecycle Dynamics ✅
- [x] Energy system
- [x] Growth animation
- [x] Death and shrinkage
- [x] Cell removal

### Phase 4: Polish ✅
- [x] Color schemes by generation/age (5 schemes: Viridis, Plasma, Warm, Energy, Cool)
- [x] Stats overlay (cells, births, deaths, max gen, avg energy, oldest age)
- [x] Performance optimization (high-performance mode with reduced effects)
- [x] Parameter tuning for realism

---

## File Structure

```
apps/
├── yeast_d3js.py           # Streamlit app
├── yeast_d3js_template.html # D3.js template (optional, can be inline)
└── yeast_plan_d3js.md      # This plan document
```

---

## Technical Notes

### Performance Considerations

- **Canvas rendering**: Much faster than SVG for 200+ cells
- **Node limit**: Cap at ~500 cells for smooth 60fps
- **Force iterations**: Balance accuracy vs speed
- **Dead cell cleanup**: Remove from arrays, not just hide

### D3.js Version

Use D3.js v7 (latest):
```html
<script src="https://d3js.org/d3.v7.min.js"></script>
```

### Browser Compatibility

Modern browsers only (Chrome, Firefox, Safari, Edge). Canvas 2D and ES6+ required.

---

## References

- D3.js Force Simulation: https://d3js.org/d3-force
- Ratcliff Lab Snowflake Yeast: https://ratclifflab.biosci.gatech.edu/
- Canvas Ellipse API: https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/ellipse
