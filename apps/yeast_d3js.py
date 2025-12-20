"""
Yeast Colony Simulation with D3.js Force-Directed Graph

Phase 1: Basic simulation with cell division, collision, and mobility.
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
st.sidebar.subheader("Cell Dynamics")

division_rate = st.sidebar.slider(
    "Division Rate",
    0.001, 0.05, 0.015,
    format="%.3f",
    help="Probability of division per tick for mature cells"
)

cell_radius = st.sidebar.slider(
    "Cell Radius",
    5, 20, 10,
    help="Base radius of cells in pixels"
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
        <div id="mode-label">{"Snowflake Yeast (Attached)" if is_snowflake else "Normal Yeast (Separating)"}</div>
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

        // Color scales
        const generationColor = d3.scaleSequential(d3.interpolateViridis).domain([0, 10]);
        const ageColor = d3.scaleSequential(d3.interpolateYlOrBr).domain([0, 500]);

        // Create a new cell
        function createCell(x, y, parentId = null, generation = 0) {{
            return {{
                id: nextId++,
                x: x,
                y: y,
                vx: 0,
                vy: 0,
                radius: CONFIG.cellRadius * 0.5,  // Start small
                targetRadius: CONFIG.cellRadius * (0.9 + Math.random() * 0.2),
                age: 0,
                generation: generation,
                parentId: parentId,
                budsProduced: 0,
                maxBuds: 4 + Math.floor(Math.random() * 3),
                state: 'growing',
                isSnowflake: CONFIG.isSnowflake
            }};
        }}

        // Initialize simulation
        function init() {{
            nodes = [];
            links = [];
            nextId = 0;
            tickCount = 0;

            // Create initial cells
            const centerX = width / 2;
            const centerY = height / 2;

            for (let i = 0; i < CONFIG.initialCells; i++) {{
                const angle = (2 * Math.PI * i) / CONFIG.initialCells;
                const offset = CONFIG.cellRadius * 2;
                const cell = createCell(
                    centerX + Math.cos(angle) * offset,
                    centerY + Math.sin(angle) * offset
                );
                cell.radius = cell.targetRadius;  // Initial cells start mature
                cell.state = 'mature';
                nodes.push(cell);
            }}

            setupSimulation();
            updateStats();
        }}

        // Setup D3 force simulation
        function setupSimulation() {{
            simulation = d3.forceSimulation(nodes)
                .force('collision', d3.forceCollide()
                    .radius(d => d.radius * 1.1)
                    .strength(0.8)
                    .iterations(2))
                .force('center', d3.forceCenter(width / 2, height / 2).strength(0.005))
                .force('link', d3.forceLink(links)
                    .id(d => d.id)
                    .distance(d => d.distance || 20)
                    .strength(d => d.strength || 0.5))
                .alphaDecay(0.005)
                .velocityDecay(0.4)
                .on('tick', onTick);
        }}

        // Custom forces applied each tick
        function applyCustomForces() {{
            const padding = CONFIG.cellRadius * 2;

            for (const node of nodes) {{
                // Boundary force
                if (node.x < padding) node.vx += (padding - node.x) * 0.1;
                if (node.x > width - padding) node.vx += (width - padding - node.x) * 0.1;
                if (node.y < padding) node.vy += (padding - node.y) * 0.1;
                if (node.y > height - padding) node.vy += (height - padding - node.y) * 0.1;

                // Brownian motion (reduced for snowflake)
                if (!CONFIG.isSnowflake || node.parentId === null) {{
                    node.vx += (Math.random() - 0.5) * CONFIG.brownianStrength;
                    node.vy += (Math.random() - 0.5) * CONFIG.brownianStrength;
                }}
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
                        links.push({{
                            source: parent,
                            target: cell,
                            distance: parent.radius + cell.targetRadius,
                            strength: 0.8
                        }});
                        simulation.force('link').links(links);
                    }}
                }}
            }}

            // Update collision radius
            simulation.force('collision').radius(d => d.radius * 1.1);
        }}

        // Cell division
        function divide(mother) {{
            // Random budding angle for normal yeast
            // For snowflake, we'll improve this in Phase 2
            const budAngle = Math.random() * 2 * Math.PI;

            const separation = mother.radius + CONFIG.cellRadius * 0.5;
            const newX = mother.x + Math.cos(budAngle) * separation;
            const newY = mother.y + Math.sin(budAngle) * separation;

            // Check bounds
            if (newX < 0 || newX > width || newY < 0 || newY > height) {{
                return null;
            }}

            const daughter = createCell(newX, newY, mother.id, mother.generation + 1);
            mother.budsProduced++;

            // Separation impulse for normal yeast
            if (!CONFIG.isSnowflake) {{
                const impulse = 2;
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
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
                ctx.lineWidth = 1.5;
                for (const link of links) {{
                    ctx.beginPath();
                    ctx.moveTo(link.source.x, link.source.y);
                    ctx.lineTo(link.target.x, link.target.y);
                    ctx.stroke();
                }}
            }}

            // Draw cells
            for (const node of nodes) {{
                ctx.save();

                // Color based on mode
                let color;
                if (CONFIG.isSnowflake) {{
                    color = generationColor(Math.min(node.generation, 10));
                }} else {{
                    color = ageColor(Math.min(node.age, 500));
                }}

                // Glow effect
                ctx.shadowColor = color;
                ctx.shadowBlur = 8;

                // Fill
                ctx.fillStyle = color;
                ctx.globalAlpha = 0.85;
                ctx.beginPath();
                ctx.arc(node.x, node.y, node.radius, 0, 2 * Math.PI);
                ctx.fill();

                // Border
                ctx.shadowBlur = 0;
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
                ctx.lineWidth = 1;
                ctx.stroke();

                // Generation indicator for snowflake
                if (CONFIG.isSnowflake && node.generation > 0) {{
                    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
                    ctx.font = '8px sans-serif';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(node.generation, node.x, node.y);
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
                simulation.force('center', d3.forceCenter(width / 2, height / 2).strength(0.005));
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

**Snowflake Yeast**: Cells remain attached after division, forming fractal-like clusters.

*Phase 1: Basic simulation with circles*
""")
