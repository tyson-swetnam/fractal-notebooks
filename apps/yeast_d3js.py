"""
Yeast Colony Simulation with D3.js Force-Directed Graph

Phase 3: Energy system, growth/shrinkage, cell death and removal.
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

# Create tabs for simulation and documentation
tab_sim, tab_docs = st.tabs(["Simulation", "Documentation"])

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
st.sidebar.subheader("Appearance")

color_scheme = st.sidebar.selectbox(
    "Color Scheme",
    ["Generation (Viridis)", "Generation (Plasma)", "Age (Warm)", "Energy (Health)", "Depth (Cool)"],
    help="How cells are colored"
)

show_energy_bars = st.sidebar.checkbox("Show Energy Bars", value=True)
show_pole_indicators = st.sidebar.checkbox("Show Pole Indicators", value=False)
high_performance = st.sidebar.checkbox("High Performance Mode", value=False,
    help="Reduces visual effects for smoother performance with many cells")

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
st.sidebar.subheader("Energy & Death")

enable_death = st.sidebar.checkbox("Enable Cell Death", value=True)

energy_gain_rate = st.sidebar.slider(
    "Energy Gain Rate",
    0.1, 2.0, 0.8,
    help="How fast cells gain energy when uncrowded"
)

energy_decay_rate = st.sidebar.slider(
    "Energy Decay Rate",
    0.01, 0.5, 0.15,
    help="How fast cells lose energy from age/crowding"
)

death_threshold = st.sidebar.slider(
    "Death Threshold",
    5, 30, 15,
    help="Energy level below which cells start dying"
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
    simulation_speed: float,
    enable_death: bool,
    energy_gain_rate: float,
    energy_decay_rate: float,
    death_threshold: int,
    color_scheme: str,
    show_energy_bars: bool,
    show_pole_indicators: bool,
    high_performance: bool
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
        .stat-label {{
            color: #aaa;
        }}
    </style>
</head>
<body>
    <div id="container">
        <canvas id="canvas"></canvas>
        <div id="stats">
            <div><span class="stat-label">Cells:</span> <span id="cell-count">0</span> / {max_cells}</div>
            <div><span class="stat-label">Births:</span> <span id="birth-count">0</span></div>
            <div><span class="stat-label">Deaths:</span> <span id="death-count">0</span></div>
            <div><span class="stat-label">Max Gen:</span> <span id="max-gen">0</span></div>
            <div><span class="stat-label">Avg Energy:</span> <span id="avg-energy">100</span>%</div>
            <div><span class="stat-label">Oldest:</span> <span id="oldest-age">0</span> ticks</div>
        </div>
        <div id="controls">
            <button id="pause-btn" class="active">Pause</button>
            <button id="reset-btn">Reset</button>
        </div>
        <div id="mode-label">{"Snowflake Yeast (Polar Budding)" if is_snowflake else "Normal Yeast (Separating)"} {"+ Death" if enable_death else ""}</div>
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
            budAngleDeviation: {bud_angle_deviation} * Math.PI / 180,
            brownianStrength: {brownian_strength},
            simulationSpeed: {simulation_speed},
            enableDeath: {str(enable_death).lower()},
            energyGainRate: {energy_gain_rate},
            energyDecayRate: {energy_decay_rate},
            deathThreshold: {death_threshold},
            colorScheme: "{color_scheme}",
            showEnergyBars: {str(show_energy_bars).lower()},
            showPoleIndicators: {str(show_pole_indicators).lower()},
            highPerformance: {str(high_performance).lower()}
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
        let birthCount = 0;
        let deathCount = 0;
        let isPaused = false;
        let simulation;

        // Track used poles for each cell
        const usedPoles = new Map();

        // Color scales for different schemes
        const colorScales = {{
            'Generation (Viridis)': d3.scaleSequential(d3.interpolateViridis).domain([0, 10]),
            'Generation (Plasma)': d3.scaleSequential(d3.interpolatePlasma).domain([0, 10]),
            'Age (Warm)': d3.scaleSequential(d3.interpolateYlOrBr).domain([0, 500]),
            'Energy (Health)': d3.scaleSequential(d3.interpolateRdYlGn).domain([0, 100]),
            'Depth (Cool)': d3.scaleSequential(d3.interpolateCool).domain([0, 10])
        }};
        const energyBarColor = d3.scaleSequential(d3.interpolateRdYlGn).domain([0, 100]);

        // Get cell color based on selected scheme
        function getCellColor(node) {{
            const scheme = CONFIG.colorScheme;
            if (scheme === 'Energy (Health)') {{
                return colorScales[scheme](node.energy);
            }} else if (scheme === 'Age (Warm)') {{
                return colorScales[scheme](Math.min(node.age, 500));
            }} else {{
                // Generation-based schemes
                return colorScales[scheme](Math.min(node.generation, 10));
            }}
        }}

        // Create a new cell
        function createCell(x, y, orientation, parentId = null, generation = 0) {{
            const cell = {{
                id: nextId++,
                x: x,
                y: y,
                vx: 0,
                vy: 0,
                radius: CONFIG.cellRadius * 0.4,
                targetRadius: CONFIG.cellRadius * (0.9 + Math.random() * 0.2),
                aspectRatio: CONFIG.aspectRatio,
                orientation: orientation,
                age: 0,
                generation: generation,
                parentId: parentId,
                budsProduced: 0,
                maxBuds: 4 + Math.floor(Math.random() * 2),
                state: 'growing',
                energy: 80 + Math.random() * 20,  // Start with 80-100 energy
                opacity: 1.0,
                isSnowflake: CONFIG.isSnowflake
            }};
            usedPoles.set(cell.id, new Set());
            return cell;
        }}

        // Calculate local density around a cell
        function getLocalDensity(cell) {{
            const detectionRadius = CONFIG.cellRadius * CONFIG.aspectRatio * 4;
            let neighborCount = 0;
            let totalOverlap = 0;

            for (const other of nodes) {{
                if (other.id === cell.id || other.state === 'dead') continue;

                const dx = other.x - cell.x;
                const dy = other.y - cell.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < detectionRadius) {{
                    neighborCount++;
                    const minDist = (cell.radius + other.radius) * Math.sqrt(CONFIG.aspectRatio);
                    if (dist < minDist * 1.5) {{
                        totalOverlap += 1 - (dist / (minDist * 1.5));
                    }}
                }}
            }}

            // Density is combination of neighbor count and overlap
            return Math.min(1, (neighborCount / 8) + totalOverlap * 0.5);
        }}

        // Initialize simulation
        function init() {{
            nodes = [];
            links = [];
            usedPoles.clear();
            nextId = 0;
            tickCount = 0;
            birthCount = 0;
            deathCount = 0;

            const centerX = width / 2;
            const centerY = height / 2;

            for (let i = 0; i < CONFIG.initialCells; i++) {{
                const angle = (2 * Math.PI * i) / CONFIG.initialCells;
                const offset = CONFIG.cellRadius * CONFIG.aspectRatio * 2;
                const cell = createCell(
                    centerX + Math.cos(angle) * offset,
                    centerY + Math.sin(angle) * offset,
                    angle + Math.PI / 2
                );
                cell.radius = cell.targetRadius;
                cell.state = 'mature';
                cell.energy = 100;
                nodes.push(cell);
                birthCount++;
            }}

            setupSimulation();
            updateStats();
        }}

        // Get effective collision radius
        function getCollisionRadius(node) {{
            if (node.state === 'dying' || node.state === 'dead') {{
                return node.radius * 0.5;  // Shrinking cells have smaller collision
            }}
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

        // Custom forces
        function applyCustomForces() {{
            const padding = CONFIG.cellRadius * CONFIG.aspectRatio * 2;

            for (const node of nodes) {{
                if (node.state === 'dead') continue;

                // Boundary force
                if (node.x < padding) node.vx += (padding - node.x) * 0.1;
                if (node.x > width - padding) node.vx += (width - padding - node.x) * 0.1;
                if (node.y < padding) node.vy += (padding - node.y) * 0.1;
                if (node.y > height - padding) node.vy += (height - padding - node.y) * 0.1;

                // Brownian motion (reduced for dying/attached cells)
                const isAttached = CONFIG.isSnowflake && node.parentId !== null;
                const isDying = node.state === 'dying';
                let brownianFactor = 1.0;
                if (isAttached) brownianFactor *= 0.2;
                if (isDying) brownianFactor *= 0.3;

                node.vx += (Math.random() - 0.5) * CONFIG.brownianStrength * brownianFactor;
                node.vy += (Math.random() - 0.5) * CONFIG.brownianStrength * brownianFactor;
            }}

            // Orientation alignment for snowflake links
            if (CONFIG.isSnowflake) {{
                for (const link of links) {{
                    if (link.target.state === 'dead') continue;

                    const dx = link.target.x - link.source.x;
                    const dy = link.target.y - link.source.y;
                    const linkAngle = Math.atan2(dy, dx);

                    let angleDiff = linkAngle - link.target.orientation;
                    while (angleDiff > Math.PI) angleDiff -= 2 * Math.PI;
                    while (angleDiff < -Math.PI) angleDiff += 2 * Math.PI;

                    link.target.orientation += angleDiff * 0.1;
                }}
            }}
        }}

        // Update energy for a cell
        function updateEnergy(cell) {{
            if (!CONFIG.enableDeath) {{
                cell.energy = 100;
                return;
            }}

            const density = getLocalDensity(cell);

            // Energy gain when uncrowded
            const spaceBonus = (1 - density) * CONFIG.energyGainRate;
            cell.energy += spaceBonus;

            // Energy loss from crowding
            const crowdingPenalty = density * CONFIG.energyDecayRate * 2;
            cell.energy -= crowdingPenalty;

            // Age penalty (older cells lose energy faster)
            const agePenalty = (cell.age / 2000) * CONFIG.energyDecayRate;
            cell.energy -= agePenalty;

            // Clamp energy
            cell.energy = Math.max(0, Math.min(100, cell.energy));
        }}

        // Get available pole for budding
        function getAvailablePole(cell) {{
            const used = usedPoles.get(cell.id) || new Set();

            if (!used.has(0) && !used.has(Math.PI)) {{
                return Math.random() < 0.5 ? 0 : Math.PI;
            }} else if (!used.has(0)) {{
                return 0;
            }} else if (!used.has(Math.PI)) {{
                return Math.PI;
            }} else {{
                return Math.random() < 0.5 ? 0 : Math.PI;
            }}
        }}

        // Update cell states
        function updateCells() {{
            const cellsToAdd = [];
            const cellsToRemove = [];

            for (const cell of nodes) {{
                if (cell.state === 'dead') {{
                    cellsToRemove.push(cell);
                    continue;
                }}

                cell.age++;
                updateEnergy(cell);

                // State machine
                switch (cell.state) {{
                    case 'growing':
                        // Growth rate influenced by energy
                        const growthRate = 0.03 + (cell.energy / 100) * 0.04;
                        cell.radius += (cell.targetRadius - cell.radius) * growthRate;

                        if (cell.radius >= cell.targetRadius * 0.95) {{
                            cell.state = 'mature';
                            cell.radius = cell.targetRadius;
                        }}
                        break;

                    case 'mature':
                        // Check for death
                        if (CONFIG.enableDeath && cell.energy < CONFIG.deathThreshold) {{
                            cell.state = 'dying';
                            break;
                        }}

                        // Division check
                        if (cell.budsProduced < cell.maxBuds &&
                            cell.energy > 50 &&
                            nodes.length + cellsToAdd.length < CONFIG.maxCells) {{

                            const divisionChance = CONFIG.divisionRate * CONFIG.simulationSpeed * (cell.energy / 100);
                            if (Math.random() < divisionChance) {{
                                const daughter = divide(cell);
                                if (daughter) {{
                                    cellsToAdd.push(daughter);
                                    // Division costs energy
                                    cell.energy -= 20;
                                }}
                            }}
                        }}
                        break;

                    case 'dying':
                        // Shrink and fade
                        cell.radius *= 0.97;
                        cell.opacity -= 0.02;
                        cell.energy = Math.max(0, cell.energy - 1);

                        if (cell.radius < CONFIG.cellRadius * 0.2 || cell.opacity <= 0.1) {{
                            cell.state = 'dead';
                            cell.opacity = 0;
                            deathCount++;
                        }}
                        break;
                }}
            }}

            // Remove dead cells
            for (const cell of cellsToRemove) {{
                removeCell(cell);
            }}

            // Add new cells
            for (const cell of cellsToAdd) {{
                nodes.push(cell);
                birthCount++;
                simulation.nodes(nodes);

                if (CONFIG.isSnowflake && cell.parentId !== null) {{
                    const parent = nodes.find(n => n.id === cell.parentId);
                    if (parent) {{
                        const parentSemiMajor = parent.radius * parent.aspectRatio;
                        const childSemiMajor = cell.targetRadius * cell.aspectRatio;

                        // Distance so poles touch with slight overlap for junction
                        links.push({{
                            source: parent,
                            target: cell,
                            distance: parentSemiMajor + childSemiMajor,
                            strength: 0.9
                        }});
                        simulation.force('link').links(links);
                    }}
                }}
            }}

            // Update collision radius
            simulation.force('collision').radius(d => getCollisionRadius(d));

            // Update link distances as cells grow
            for (const link of links) {{
                const parentSemiMajor = link.source.radius * link.source.aspectRatio;
                const childSemiMajor = link.target.radius * link.target.aspectRatio;
                link.distance = parentSemiMajor + childSemiMajor;
            }}
        }}

        // Remove a dead cell and its links
        function removeCell(cell) {{
            // Remove from nodes
            const nodeIndex = nodes.indexOf(cell);
            if (nodeIndex > -1) {{
                nodes.splice(nodeIndex, 1);
            }}

            // Remove links to/from this cell
            for (let i = links.length - 1; i >= 0; i--) {{
                if (links[i].source.id === cell.id || links[i].target.id === cell.id) {{
                    links.splice(i, 1);
                }}
            }}

            // Clean up usedPoles
            usedPoles.delete(cell.id);

            // Update simulation
            simulation.nodes(nodes);
            simulation.force('link').links(links);
        }}

        // Cell division
        function divide(mother) {{
            let budAngle;
            let daughterOrientation;

            if (CONFIG.isSnowflake) {{
                const pole = getAvailablePole(mother);
                const baseAngle = mother.orientation + pole;
                const deviation = (Math.random() - 0.5) * 2 * CONFIG.budAngleDeviation;
                budAngle = baseAngle + deviation;
                daughterOrientation = budAngle;

                const used = usedPoles.get(mother.id) || new Set();
                used.add(pole);
                usedPoles.set(mother.id, used);
            }} else {{
                budAngle = Math.random() * 2 * Math.PI;
                daughterOrientation = Math.random() * 2 * Math.PI;
            }}

            // Position daughter at mother's pole - daughter starts small and grows
            const motherSemiMajor = mother.radius * mother.aspectRatio;
            const initialDaughterSemiMajor = CONFIG.cellRadius * 0.4 * CONFIG.aspectRatio;
            const separation = motherSemiMajor + initialDaughterSemiMajor;

            const newX = mother.x + Math.cos(budAngle) * separation;
            const newY = mother.y + Math.sin(budAngle) * separation;

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

            // Daughter inherits some energy from mother
            daughter.energy = mother.energy * 0.6;

            if (CONFIG.isSnowflake) {{
                const daughterUsed = usedPoles.get(daughter.id) || new Set();
                daughterUsed.add(Math.PI);
                usedPoles.set(daughter.id, daughterUsed);
            }}

            mother.budsProduced++;

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

            if (tickCount % 3 === 0) {{
                updateCells();
            }}

            render();

            if (tickCount % 10 === 0) {{
                updateStats();
            }}

            simulation.alpha(0.3);
        }}

        // Render to canvas
        function render() {{
            ctx.clearRect(0, 0, width, height);

            // Draw pole-to-pole junctions (shared cell walls like sausage links)
            if (CONFIG.isSnowflake && links.length > 0) {{
                for (const link of links) {{
                    if (link.source.state === 'dead' || link.target.state === 'dead') continue;

                    const parent = link.source;
                    const child = link.target;

                    // Calculate the junction point (where poles meet)
                    const dx = child.x - parent.x;
                    const dy = child.y - parent.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < 0.1) continue;

                    const ux = dx / dist;  // Unit vector from parent to child
                    const uy = dy / dist;

                    // Parent's pole position (end of ellipse toward child)
                    const parentSemiMajor = parent.radius * parent.aspectRatio;
                    const parentPoleX = parent.x + ux * parentSemiMajor;
                    const parentPoleY = parent.y + uy * parentSemiMajor;

                    // Child's pole position (end of ellipse toward parent)
                    const childSemiMajor = child.radius * child.aspectRatio;
                    const childPoleX = child.x - ux * childSemiMajor;
                    const childPoleY = child.y - uy * childSemiMajor;

                    // Junction midpoint
                    const junctionX = (parentPoleX + childPoleX) / 2;
                    const junctionY = (parentPoleY + childPoleY) / 2;

                    // Junction dimensions - a pinched connection
                    const junctionLength = Math.max(4, Math.abs(
                        Math.sqrt((childPoleX - parentPoleX) ** 2 + (childPoleY - parentPoleY) ** 2)
                    ) + 4);
                    const junctionWidth = Math.min(parent.radius, child.radius) * 0.7;

                    // Angle of junction (along the link direction)
                    const junctionAngle = Math.atan2(dy, dx);

                    // Draw the junction as a pinched ellipse (shared cell wall)
                    ctx.save();
                    ctx.translate(junctionX, junctionY);
                    ctx.rotate(junctionAngle);

                    // Blend colors from both cells
                    const parentColor = parent.state === 'dying'
                        ? `rgb(${{Math.floor(100 + parent.energy)}}, ${{Math.floor((100 + parent.energy) * 0.8)}}, ${{Math.floor((100 + parent.energy) * 0.6)}})`
                        : getCellColor(parent);
                    const childColor = child.state === 'dying'
                        ? `rgb(${{Math.floor(100 + child.energy)}}, ${{Math.floor((100 + child.energy) * 0.8)}}, ${{Math.floor((100 + child.energy) * 0.6)}})`
                        : getCellColor(child);

                    // Draw junction as gradient between the two cell colors
                    const gradient = ctx.createLinearGradient(-junctionLength/2, 0, junctionLength/2, 0);
                    gradient.addColorStop(0, parentColor);
                    gradient.addColorStop(1, childColor);

                    ctx.globalAlpha = Math.min(parent.opacity, child.opacity) * 0.85;
                    ctx.fillStyle = gradient;

                    // Draw pinched junction shape (narrower in middle)
                    ctx.beginPath();
                    ctx.ellipse(0, 0, junctionLength / 2, junctionWidth, 0, 0, 2 * Math.PI);
                    ctx.fill();

                    // Border
                    ctx.strokeStyle = `rgba(255, 255, 255, ${{Math.min(parent.opacity, child.opacity) * 0.4}})`;
                    ctx.lineWidth = CONFIG.highPerformance ? 0.5 : 1;
                    ctx.stroke();

                    ctx.restore();
                }}
            }}

            // Draw cells
            for (const node of nodes) {{
                if (node.state === 'dead') continue;

                ctx.save();
                ctx.translate(node.x, node.y);
                ctx.rotate(node.orientation);

                // Get color from selected scheme
                let color;
                if (node.state === 'dying') {{
                    // Dying cells turn grayish
                    const gray = Math.floor(100 + node.energy);
                    color = `rgb(${{gray}}, ${{gray * 0.8}}, ${{gray * 0.6}})`;
                }} else {{
                    color = getCellColor(node);
                }}

                // Glow effect (reduced for dying cells or high-performance mode)
                if (!CONFIG.highPerformance) {{
                    ctx.shadowColor = color;
                    ctx.shadowBlur = node.state === 'dying' ? 2 : 8;
                }}

                // Draw ellipse
                const semiMajor = node.radius * node.aspectRatio;
                const semiMinor = node.radius;

                ctx.fillStyle = color;
                ctx.globalAlpha = node.opacity * 0.85;
                ctx.beginPath();
                ctx.ellipse(0, 0, semiMajor, semiMinor, 0, 0, 2 * Math.PI);
                ctx.fill();

                // Border (simplified in high-performance mode)
                if (!CONFIG.highPerformance) {{
                    ctx.shadowBlur = 0;
                }}
                ctx.strokeStyle = `rgba(255, 255, 255, ${{node.opacity * (CONFIG.highPerformance ? 0.3 : 0.5)}})`;
                ctx.lineWidth = CONFIG.highPerformance ? 0.5 : 1;
                ctx.stroke();

                // Energy bar for living cells (configurable)
                if (CONFIG.showEnergyBars && CONFIG.enableDeath && node.state !== 'dying') {{
                    const barWidth = semiMajor * 1.5;
                    const barHeight = 3;
                    const barY = semiMinor + 4;

                    ctx.globalAlpha = node.opacity * 0.7;
                    // Background
                    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
                    ctx.fillRect(-barWidth / 2, barY, barWidth, barHeight);

                    // Energy fill
                    const energyWidth = (node.energy / 100) * barWidth;
                    ctx.fillStyle = energyBarColor(node.energy);
                    ctx.fillRect(-barWidth / 2, barY, energyWidth, barHeight);
                }}

                // Pole indicators (configurable)
                if (CONFIG.showPoleIndicators && node.state !== 'dying') {{
                    ctx.globalAlpha = node.opacity * 0.6;
                    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
                    const poleOffset = semiMajor * 0.7;

                    ctx.beginPath();
                    ctx.arc(poleOffset, 0, 2, 0, 2 * Math.PI);
                    ctx.fill();

                    ctx.beginPath();
                    ctx.arc(-poleOffset, 0, 2, 0, 2 * Math.PI);
                    ctx.fill();
                }}

                ctx.restore();
            }}
        }}

        // Update stats display
        function updateStats() {{
            const livingCells = nodes.filter(n => n.state !== 'dead');
            document.getElementById('cell-count').textContent = livingCells.length;
            document.getElementById('birth-count').textContent = birthCount;
            document.getElementById('death-count').textContent = deathCount;
            document.getElementById('max-gen').textContent =
                livingCells.length > 0 ? Math.max(...livingCells.map(n => n.generation)) : 0;

            const avgEnergy = livingCells.length > 0
                ? Math.round(livingCells.reduce((sum, n) => sum + n.energy, 0) / livingCells.length)
                : 0;
            document.getElementById('avg-energy').textContent = avgEnergy;

            const oldestAge = livingCells.length > 0
                ? Math.max(...livingCells.map(n => n.age))
                : 0;
            document.getElementById('oldest-age').textContent = oldestAge;
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


# Generate the simulation HTML
html_content = generate_d3_html(
    is_snowflake=is_snowflake,
    initial_cells=initial_cells,
    max_cells=max_cells,
    division_rate=division_rate,
    cell_radius=cell_radius,
    aspect_ratio=aspect_ratio,
    bud_angle_deviation=bud_angle_deviation,
    brownian_strength=brownian_strength,
    simulation_speed=simulation_speed,
    enable_death=enable_death,
    energy_gain_rate=energy_gain_rate,
    energy_decay_rate=energy_decay_rate,
    death_threshold=death_threshold,
    color_scheme=color_scheme,
    show_energy_bars=show_energy_bars,
    show_pole_indicators=show_pole_indicators,
    high_performance=high_performance
)

# Simulation tab
with tab_sim:
    components.html(html_content, height=700, scrolling=False)

# Documentation tab
with tab_docs:
    st.header("How This Simulation Works")

    st.markdown("""
    This simulation models the growth dynamics of yeast colonies using a **force-directed graph**
    powered by D3.js. It was inspired by experimental research on the evolution of multicellularity,
    particularly the "snowflake yeast" experiments from the Ratcliff Lab at Georgia Tech.
    """)

    st.subheader("Scientific Background")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        #### The Snowflake Yeast Experiment

        In 2012, researchers led by William Ratcliff demonstrated that unicellular yeast
        (*Saccharomyces cerevisiae*) could evolve multicellular "snowflake" clusters in just
        a few weeks under selective pressure. The key discovery:

        - **Selection for settling**: By repeatedly selecting yeast that settled fastest in
          liquid culture, researchers selected for cells that stayed attached after division
        - **Polar budding**: Daughter cells bud from the mother's poles (ends), creating
          branching tree-like structures
        - **Cell elongation**: Over ~600 generations, cells evolved from spherical to elongated
          (aspect ratio ~2.7), increasing cluster size
        - **Programmed cell death**: Central cells undergo apoptosis, allowing branches to
          separate and reproduce as new clusters
        """)

    with col2:
        st.markdown("""
        #### Normal vs Snowflake Yeast

        **Normal (Separating) Yeast:**
        - Daughter cells separate from mother after division
        - Cells diffuse freely through the medium
        - Standard laboratory yeast behavior
        - Random budding direction

        **Snowflake (Attached) Yeast:**
        - Daughter cells remain attached to mother
        - Forms fractal-like branching clusters
        - Polar budding (buds emerge from cell poles)
        - Cells orient along the cluster branch
        - Represents early multicellularity
        """)

    st.divider()

    st.subheader("Parameter Reference")

    st.markdown("### Colony Settings")
    st.markdown("""
    | Parameter | Description | Scientific Relevance |
    |-----------|-------------|---------------------|
    | **Yeast Type** | Normal (separating) or Snowflake (attached) | Models wild-type vs evolved multicellular yeast |
    | **Initial Cells** | Number of cells at simulation start (1-10) | Represents founding population size |
    | **Max Cells** | Population cap (50-500) | Simulates resource/space limitations |
    """)

    st.markdown("### Cell Morphology")
    st.markdown("""
    | Parameter | Description | Scientific Relevance |
    |-----------|-------------|---------------------|
    | **Aspect Ratio** | Cell elongation (length/width, 1.0-3.0) | Evolved snowflake yeast reach ~2.7; elongation increases cluster size and settling speed |
    | **Cell Radius** | Base cell size in pixels (5-20) | Affects visual scale; real yeast are ~5 micrometers |
    """)

    st.markdown("### Cell Dynamics")
    st.markdown("""
    | Parameter | Description | Scientific Relevance |
    |-----------|-------------|---------------------|
    | **Division Rate** | Probability of division per tick (0.001-0.05) | Yeast divide every ~90 minutes in ideal conditions |
    | **Bud Angle Deviation** | Deviation from polar axis (0-180 degrees) | Low values (~15 deg) model strict polar budding in snowflake yeast; 180 deg = random budding |
    | **Brownian Motion** | Random movement strength (0.0-2.0) | Simulates thermal motion in liquid medium; reduced in attached clusters |
    """)

    st.markdown("### Energy & Death System")
    st.markdown("""
    | Parameter | Description | Scientific Relevance |
    |-----------|-------------|---------------------|
    | **Enable Cell Death** | Toggle apoptosis simulation | Central cells in real snowflake clusters undergo programmed death |
    | **Energy Gain Rate** | Energy recovery when uncrowded (0.1-2.0) | Models nutrient/oxygen access in peripheral cells |
    | **Energy Decay Rate** | Energy loss from crowding/age (0.01-0.5) | Models metabolic stress in cluster interior |
    | **Death Threshold** | Energy level triggering death (5-30) | Cells die when resources depleted |
    """)

    st.markdown("### Appearance Options")
    st.markdown("""
    | Parameter | Description |
    |-----------|-------------|
    | **Color Scheme** | How cells are colored - by generation, age, energy level, or depth |
    | **Show Energy Bars** | Display health indicator below each cell |
    | **Show Pole Indicators** | Mark cell poles (budding sites) with white dots |
    | **High Performance Mode** | Reduce visual effects for smoother performance with many cells |
    """)

    st.divider()

    st.subheader("Simulation Mechanics")

    st.markdown("""
    #### Force-Directed Layout (D3.js)

    The simulation uses D3.js force simulation with several interacting forces:

    1. **Collision Force**: Prevents cells from overlapping; respects elliptical cell shapes
    2. **Center Force**: Gentle pull toward canvas center to keep colony visible
    3. **Link Force**: Maintains connections between mother-daughter pairs (snowflake mode)
    4. **Custom Forces**: Boundary constraints and Brownian motion

    #### Cell Life Cycle

    Each cell progresses through states:

    ```
    Growing -> Mature -> (Dying -> Dead)
                 |
                 v
            Division (creates daughter)
    ```

    - **Growing**: Cell starts small, expands to full size
    - **Mature**: Can divide if energy > 50% and hasn't exceeded max buds
    - **Dying**: Shrinks and fades when energy falls below threshold
    - **Dead**: Removed from simulation

    #### Polar Budding Mechanism

    In snowflake mode, cells track which poles have been used for budding:
    - Each cell has two poles (0 and 180 degrees from orientation)
    - Daughters preferentially bud from unused poles
    - Creates the characteristic branching pattern
    - Daughter cells mark their "birth pole" as used (attached to parent)
    """)

    st.divider()

    st.subheader("Key Research References")

    st.markdown("""
    1. **Ratcliff, W.C., et al. (2012)**. "Experimental evolution of multicellularity."
       *PNAS*, 109(5), 1595-1600. [DOI: 10.1073/pnas.1115323109](https://doi.org/10.1073/pnas.1115323109)

    2. **Ratcliff, W.C., et al. (2015)**. "Origins of multicellular evolvability in snowflake yeast."
       *Nature Communications*, 6, 6102. [DOI: 10.1038/ncomms7102](https://doi.org/10.1038/ncomms7102)

    3. **Pentz, J.T., et al. (2020)**. "Ecological advantages and evolutionary limitations of
       aggregative multicellular development." *Current Biology*, 30(21), 4155-4164.

    4. **Bozdag, G.O., et al. (2023)**. "De novo evolution of macroscopic multicellularity."
       *Nature*, 617, 747-754. [DOI: 10.1038/s41586-023-06052-1](https://doi.org/10.1038/s41586-023-06052-1)
    """)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
### About
This simulation models yeast colony growth using D3.js force-directed graphs.

**Normal Yeast**: Cells divide and separate, diffusing through the medium.

**Snowflake Yeast**: Cells remain attached via **polar budding** (end-to-end), forming fractal-like clusters.

**Energy System**: Cells gain energy when uncrowded, lose energy from crowding and age. Low energy triggers death.

*Phase 4: Polish - color schemes, enhanced stats, optimizations*
""")
