"""
Yeast Colony Simulation with D3.js Force-Directed Graph

Phase 2: Polar budding, ellipse rendering, and orientation alignment.
Uses D3.js force simulation embedded in Streamlit via components.html().
"""

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Yeast Colony Simulation",
    page_icon="🧫",
    layout="wide"
)

st.title("Yeast Colony Simulation")
st.markdown("Interactive D3.js force-directed simulation of yeast growth dynamics")

# Sidebar controls
st.sidebar.header("Simulation Parameters")

mode = st.sidebar.radio(
    "Yeast Type",
    ["Normal (Separating)", "Snowflake (Attached)"],
    help="Normal yeast cells separate after division. Snowflake yeast remain attached."
)
is_snowflake = mode == "Snowflake (Attached)"

st.sidebar.markdown("---")
st.sidebar.subheader("Colony Settings")

initial_cells = st.sidebar.slider("Initial Cells", 1, 10, 3)
max_cells = st.sidebar.slider("Max Cells", 50, 500, 200)

st.sidebar.markdown("---")
st.sidebar.subheader("Cell Morphology")

aspect_ratio = st.sidebar.slider(
    "Aspect Ratio",
    1.0, 3.0, 1.2 if not is_snowflake else 2.0,
    step=0.1,
    help="Cell elongation (length/width). Evolved snowflake yeast: ~2.7"
)

cell_radius = st.sidebar.slider(
    "Cell Radius",
    5, 20, 10,
    help="Base radius (minor axis) of cells in pixels"
)

st.sidebar.markdown("---")
st.sidebar.subheader("Cell Dynamics")

division_rate = st.sidebar.slider(
    "Division Rate",
    0.001, 0.05, 0.012,
    format="%.3f",
    help="Probability of division per tick for mature cells"
)

bud_angle_deviation = st.sidebar.slider(
    "Bud Angle Deviation",
    0, 45, 15 if is_snowflake else 180,
    help="Max angle deviation from polar axis (snowflake) or full random (normal)"
)

brownian_strength = st.sidebar.slider(
    "Brownian Motion",
    0.0, 2.0, 0.5 if not is_snowflake else 0.1,
    help="Random movement strength"
)

st.sidebar.markdown("---")
st.sidebar.subheader("Simulation Control")

simulation_speed = st.sidebar.slider(
    "Speed",
    0.1, 3.0, 1.0,
    help="Simulation tick multiplier"
)


def generate_d3_html(
    is_snowflake: bool,
    initial_cells: int,
    max_cells: int,
    division_rate: float,
    cell_radius: int,
    aspect_ratio: float,
    bud_angle_deviation: int,
    brownian_strength: float,
    simulation_speed: float
) -> str:
    """Generate the complete HTML with D3.js simulation."""

    return f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: #1a1a2e;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        #container {{
            position: relative;
            width: 100%;
            height: 650px;
        }}
        canvas {{
            display: block;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-radius: 8px;
        }}
        #stats {{
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(0, 0, 0, 0.7);
            color: #fff;
            padding: 10px 15px;
            border-radius: 6px;
            font-size: 13px;
            line-height: 1.6;
        }}
        #controls {{
            position: absolute;
            top: 10px;
            right: 10px;
            display: flex;
            gap: 8px;
        }}
        button {{
            background: rgba(255, 255, 255, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: #fff;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            transition: background 0.2s;
        }}
        button:hover {{
            background: rgba(255, 255, 255, 0.25);
        }}
        button.active {{
            background: rgba(76, 175, 80, 0.5);
            border-color: rgba(76, 175, 80, 0.8);
        }}
        #mode-label {{
            position: absolute;
            bottom: 10px;
            left: 10px;
            background: rgba(0, 0, 0, 0.7);
            color: #fff;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div id="container">
        <canvas id="canvas"></canvas>
        <div id="stats">
            <div>Cells: <span id="cell-count">0</span> / {max_cells}</div>
            <div>Generation: <span id="max-gen">0</span></div>
            <div>Tick: <span id="tick-count">0</span></div>
        </div>
        <div id="controls">
            <button id="pause-btn" class="active">Pause</button>
            <button id="reset-btn">Reset</button>
        </div>
        <div id="mode-label">{"Snowflake Yeast (Polar Budding)" if is_snowflake else "Normal Yeast (Separating)"}</div>
    </div>

    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script>
        // Configuration from Streamlit
        const CONFIG = {{
            isSnowflake: {str(is_snowflake).lower()},
            initialCells: {initial_cells},
            maxCells: {max_cells},
            divisionRate: {division_rate},
            cellRadius: {cell_radius},
            aspectRatio: {aspect_ratio},
            budAngleDeviation: {bud_angle_deviation} * Math.PI / 180,  // Convert to radians
            brownianStrength: {brownian_strength},
            simulationSpeed: {simulation_speed}
        }};

        // Canvas setup
        const container = document.getElementById('container');
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');

        let width = container.clientWidth;
        let height = 650;
        canvas.width = width;
        canvas.height = height;

        // Simulation state
        let nodes = [];
        let links = [];
        let nextId = 0;
        let tickCount = 0;
        let isPaused = false;
        let simulation;

        // Track used poles for each cell (for polar budding)
        const usedPoles = new Map();  // cellId -> Set of used pole angles (0 or PI)

        // Color scales
        const generationColor = d3.scaleSequential(d3.interpolateViridis).domain([0, 10]);
        const ageColor = d3.scaleSequential(d3.interpolateYlOrBr).domain([0, 500]);

        // Create a new cell
        function createCell(x, y, orientation, parentId = null, generation = 0) {{
            const cell = {{
                id: nextId++,
                x: x,
                y: y,
                vx: 0,
                vy: 0,
                radius: CONFIG.cellRadius * 0.5,  // Start small (minor axis)
                targetRadius: CONFIG.cellRadius * (0.9 + Math.random() * 0.2),
                aspectRatio: CONFIG.aspectRatio,
                orientation: orientation,  // Angle of long axis in radians
                age: 0,
                generation: generation,
                parentId: parentId,
                budsProduced: 0,
                maxBuds: 4 + Math.floor(Math.random() * 2),
                state: 'growing',
                isSnowflake: CONFIG.isSnowflake
            }};
            usedPoles.set(cell.id, new Set());
            return cell;
        }}

        // Initialize simulation
        function init() {{
            nodes = [];
            links = [];
            usedPoles.clear();
            nextId = 0;
            tickCount = 0;

            // Create initial cells
            const centerX = width / 2;
            const centerY = height / 2;

            for (let i = 0; i < CONFIG.initialCells; i++) {{
                const angle = (2 * Math.PI * i) / CONFIG.initialCells;
                const offset = CONFIG.cellRadius * CONFIG.aspectRatio * 2;
                const cell = createCell(
                    centerX + Math.cos(angle) * offset,
                    centerY + Math.sin(angle) * offset,
                    angle + Math.PI / 2  // Orientation perpendicular to radial
                );
                cell.radius = cell.targetRadius;  // Initial cells start mature
                cell.state = 'mature';
                nodes.push(cell);
            }}

            setupSimulation();
            updateStats();
        }}

        // Get effective collision radius considering ellipse shape
        function getCollisionRadius(node) {{
            // Use geometric mean of semi-axes for collision
            return node.radius * Math.sqrt(node.aspectRatio) * 1.1;
        }}

        // Setup D3 force simulation
        function setupSimulation() {{
            simulation = d3.forceSimulation(nodes)
                .force('collision', d3.forceCollide()
                    .radius(d => getCollisionRadius(d))
                    .strength(0.7)
                    .iterations(2))
                .force('center', d3.forceCenter(width / 2, height / 2).strength(0.003))
                .force('link', d3.forceLink(links)
                    .id(d => d.id)
                    .distance(d => d.distance || 20)
                    .strength(d => d.strength || 0.6))
                .alphaDecay(0.005)
                .velocityDecay(0.35)
                .on('tick', onTick);
        }}

        // Custom forces applied each tick
        function applyCustomForces() {{
            const padding = CONFIG.cellRadius * CONFIG.aspectRatio * 2;

            for (const node of nodes) {{
                // Boundary force
                if (node.x < padding) node.vx += (padding - node.x) * 0.1;
                if (node.x > width - padding) node.vx += (width - padding - node.x) * 0.1;
                if (node.y < padding) node.vy += (padding - node.y) * 0.1;
                if (node.y > height - padding) node.vy += (height - padding - node.y) * 0.1;

                // Brownian motion (reduced for snowflake attached cells)
                const isAttached = CONFIG.isSnowflake && node.parentId !== null;
                const brownianFactor = isAttached ? 0.2 : 1.0;
                node.vx += (Math.random() - 0.5) * CONFIG.brownianStrength * brownianFactor;
                node.vy += (Math.random() - 0.5) * CONFIG.brownianStrength * brownianFactor;
            }}

            // Orientation alignment for snowflake links
            if (CONFIG.isSnowflake) {{
                for (const link of links) {{
                    const source = link.source;
                    const target = link.target;

                    // Calculate direction from source to target
                    const dx = target.x - source.x;
                    const dy = target.y - source.y;
                    const linkAngle = Math.atan2(dy, dx);

                    // Target orientation: aligned with link direction
                    // Smoothly rotate toward target orientation
                    let angleDiff = linkAngle - target.orientation;
                    // Normalize to [-PI, PI]
                    while (angleDiff > Math.PI) angleDiff -= 2 * Math.PI;
                    while (angleDiff < -Math.PI) angleDiff += 2 * Math.PI;

                    target.orientation += angleDiff * 0.1;
                }}
            }}
        }}

        // Get available pole for budding (0 = forward, PI = backward along orientation)
        function getAvailablePole(cell) {{
            const used = usedPoles.get(cell.id) || new Set();

            if (!used.has(0) && !used.has(Math.PI)) {{
                // Both available, pick randomly
                return Math.random() < 0.5 ? 0 : Math.PI;
            }} else if (!used.has(0)) {{
                return 0;
            }} else if (!used.has(Math.PI)) {{
                return Math.PI;
            }} else {{
                // Both used, pick randomly for additional buds
                return Math.random() < 0.5 ? 0 : Math.PI;
            }}
        }}

        // Update cell states
        function updateCells() {{
            const cellsToAdd = [];

            for (const cell of nodes) {{
                cell.age++;

                // Growth
                if (cell.state === 'growing') {{
                    cell.radius += (cell.targetRadius - cell.radius) * 0.05;
                    if (cell.radius >= cell.targetRadius * 0.95) {{
                        cell.state = 'mature';
                        cell.radius = cell.targetRadius;
                    }}
                }}

                // Division check for mature cells
                if (cell.state === 'mature' &&
                    cell.budsProduced < cell.maxBuds &&
                    nodes.length + cellsToAdd.length < CONFIG.maxCells) {{

                    if (Math.random() < CONFIG.divisionRate * CONFIG.simulationSpeed) {{
                        const daughter = divide(cell);
                        if (daughter) {{
                            cellsToAdd.push(daughter);
                        }}
                    }}
                }}
            }}

            // Add new cells
            for (const cell of cellsToAdd) {{
                nodes.push(cell);
                simulation.nodes(nodes);

                if (CONFIG.isSnowflake && cell.parentId !== null) {{
                    const parent = nodes.find(n => n.id === cell.parentId);
                    if (parent) {{
                        // Link distance: sum of semi-major axes (end-to-end)
                        const parentSemiMajor = parent.radius * parent.aspectRatio;
                        const childSemiMajor = cell.targetRadius * cell.aspectRatio;

                        links.push({{
                            source: parent,
                            target: cell,
                            distance: (parentSemiMajor + childSemiMajor) * 0.95,
                            strength: 0.7
                        }});
                        simulation.force('link').links(links);
                    }}
                }}
            }}

            // Update collision radius
            simulation.force('collision').radius(d => getCollisionRadius(d));
        }}

        // Cell division with polar budding for snowflake
        function divide(mother) {{
            let budAngle;
            let daughterOrientation;

            if (CONFIG.isSnowflake) {{
                // Polar budding: bud from pole of mother cell
                const pole = getAvailablePole(mother);

                // Base angle is along mother's orientation axis
                const baseAngle = mother.orientation + pole;

                // Add small deviation for branching variety
                const deviation = (Math.random() - 0.5) * 2 * CONFIG.budAngleDeviation;
                budAngle = baseAngle + deviation;

                // Daughter orientation continues the chain (aligned end-to-end)
                daughterOrientation = budAngle;

                // Mark pole as used
                const used = usedPoles.get(mother.id) || new Set();
                used.add(pole);
                usedPoles.set(mother.id, used);

            }} else {{
                // Normal yeast: random budding angle
                budAngle = Math.random() * 2 * Math.PI;
                daughterOrientation = Math.random() * 2 * Math.PI;
            }}

            // Calculate separation distance (end-to-end for ellipses)
            const motherSemiMajor = mother.radius * mother.aspectRatio;
            const daughterRadius = CONFIG.cellRadius * 0.5;  // Starting size
            const daughterSemiMajor = CONFIG.cellRadius * CONFIG.aspectRatio;  // Target size

            const separation = motherSemiMajor + daughterSemiMajor * 0.6;

            const newX = mother.x + Math.cos(budAngle) * separation;
            const newY = mother.y + Math.sin(budAngle) * separation;

            // Check bounds
            const margin = CONFIG.cellRadius * CONFIG.aspectRatio;
            if (newX < margin || newX > width - margin ||
                newY < margin || newY > height - margin) {{
                return null;
            }}

            const daughter = createCell(
                newX, newY,
                daughterOrientation,
                mother.id,
                mother.generation + 1
            );

            // Mark the parent-facing pole as used for daughter
            if (CONFIG.isSnowflake) {{
                const daughterUsed = usedPoles.get(daughter.id) || new Set();
                daughterUsed.add(Math.PI);  // Back pole faces parent
                usedPoles.set(daughter.id, daughterUsed);
            }}

            mother.budsProduced++;

            // Separation impulse for normal yeast
            if (!CONFIG.isSnowflake) {{
                const impulse = 2.5;
                daughter.vx = Math.cos(budAngle) * impulse;
                daughter.vy = Math.sin(budAngle) * impulse;
                mother.vx -= Math.cos(budAngle) * impulse * 0.3;
                mother.vy -= Math.sin(budAngle) * impulse * 0.3;
            }}

            return daughter;
        }}

        // Simulation tick
        function onTick() {{
            if (isPaused) return;

            tickCount++;
            applyCustomForces();

            // Update cells less frequently for performance
            if (tickCount % 3 === 0) {{
                updateCells();
            }}

            render();

            if (tickCount % 10 === 0) {{
                updateStats();
            }}

            // Keep simulation running
            simulation.alpha(0.3);
        }}

        // Render to canvas
        function render() {{
            ctx.clearRect(0, 0, width, height);

            // Draw links (for snowflake mode)
            if (CONFIG.isSnowflake && links.length > 0) {{
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
                ctx.lineWidth = 2;
                for (const link of links) {{
                    ctx.beginPath();
                    ctx.moveTo(link.source.x, link.source.y);
                    ctx.lineTo(link.target.x, link.target.y);
                    ctx.stroke();
                }}
            }}

            // Draw cells as ellipses
            for (const node of nodes) {{
                ctx.save();

                // Translate to cell center and rotate
                ctx.translate(node.x, node.y);
                ctx.rotate(node.orientation);

                // Color based on mode
                let color;
                if (CONFIG.isSnowflake) {{
                    color = generationColor(Math.min(node.generation, 10));
                }} else {{
                    color = ageColor(Math.min(node.age, 500));
                }}

                // Glow effect
                ctx.shadowColor = color;
                ctx.shadowBlur = 6;

                // Draw ellipse
                const semiMajor = node.radius * node.aspectRatio;  // Along orientation
                const semiMinor = node.radius;  // Perpendicular

                ctx.fillStyle = color;
                ctx.globalAlpha = 0.85;
                ctx.beginPath();
                ctx.ellipse(0, 0, semiMajor, semiMinor, 0, 0, 2 * Math.PI);
                ctx.fill();

                // Border
                ctx.shadowBlur = 0;
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
                ctx.lineWidth = 1;
                ctx.stroke();

                // Pole indicators for snowflake (small dots at ends)
                if (CONFIG.isSnowflake) {{
                    ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
                    const poleOffset = semiMajor * 0.7;

                    // Forward pole
                    ctx.beginPath();
                    ctx.arc(poleOffset, 0, 2, 0, 2 * Math.PI);
                    ctx.fill();

                    // Backward pole
                    ctx.beginPath();
                    ctx.arc(-poleOffset, 0, 2, 0, 2 * Math.PI);
                    ctx.fill();
                }}

                ctx.restore();
            }}
        }}

        // Update stats display
        function updateStats() {{
            document.getElementById('cell-count').textContent = nodes.length;
            document.getElementById('max-gen').textContent =
                nodes.length > 0 ? Math.max(...nodes.map(n => n.generation)) : 0;
            document.getElementById('tick-count').textContent = tickCount;
        }}

        // Event handlers
        document.getElementById('pause-btn').addEventListener('click', function() {{
            isPaused = !isPaused;
            this.textContent = isPaused ? 'Play' : 'Pause';
            this.classList.toggle('active', !isPaused);
            if (!isPaused) {{
                simulation.alpha(0.3).restart();
            }}
        }});

        document.getElementById('reset-btn').addEventListener('click', function() {{
            if (simulation) simulation.stop();
            init();
        }});

        // Handle resize
        window.addEventListener('resize', function() {{
            width = container.clientWidth;
            canvas.width = width;
            if (simulation) {{
                simulation.force('center', d3.forceCenter(width / 2, height / 2).strength(0.003));
            }}
        }});

        // Start simulation
        init();
    </script>
</body>
</html>
'''


# Generate and display the simulation
html_content = generate_d3_html(
    is_snowflake=is_snowflake,
    initial_cells=initial_cells,
    max_cells=max_cells,
    division_rate=division_rate,
    cell_radius=cell_radius,
    aspect_ratio=aspect_ratio,
    bud_angle_deviation=bud_angle_deviation,
    brownian_strength=brownian_strength,
    simulation_speed=simulation_speed
)

components.html(html_content, height=700, scrolling=False)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
### About
This simulation models yeast colony growth using D3.js force-directed graphs.

**Normal Yeast**: Cells divide and separate, diffusing through the medium.

**Snowflake Yeast**: Cells remain attached via **polar budding** (end-to-end), forming fractal-like clusters with aligned orientations.

*Phase 2: Ellipse rendering, polar budding, orientation alignment*
""")
