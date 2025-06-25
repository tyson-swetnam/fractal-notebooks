import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Typography, Slider, Button, Box, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import { PlayArrow, Pause, SkipNext, Refresh, Settings } from '@mui/icons-material';

interface GameOfLifeParams {
  gridWidth: number;
  gridHeight: number;
  animationSpeed: number;
  wrapEdges: boolean;
  initialDensity: number;
  cellGlow: number;
  colorScheme: 'classic' | 'neon' | 'fire' | 'ocean';
}

const PRESET_PATTERNS = {
  glider: [
    [0, 1, 0],
    [0, 0, 1],
    [1, 1, 1]
  ],
  blinker: [
    [1, 1, 1]
  ],
  block: [
    [1, 1],
    [1, 1]
  ],
  beehive: [
    [0, 1, 1, 0],
    [1, 0, 0, 1],
    [0, 1, 1, 0]
  ],
  toad: [
    [0, 1, 1, 1],
    [1, 1, 1, 0]
  ],
  beacon: [
    [1, 1, 0, 0],
    [1, 1, 0, 0],
    [0, 0, 1, 1],
    [0, 0, 1, 1]
  ],
  pulsar: [
    [0,0,1,1,1,0,0,0,1,1,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0],
    [1,0,0,0,0,1,0,1,0,0,0,0,1],
    [1,0,0,0,0,1,0,1,0,0,0,0,1],
    [1,0,0,0,0,1,0,1,0,0,0,0,1],
    [0,0,1,1,1,0,0,0,1,1,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,1,1,1,0,0,0,1,1,1,0,0],
    [1,0,0,0,0,1,0,1,0,0,0,0,1],
    [1,0,0,0,0,1,0,1,0,0,0,0,1],
    [1,0,0,0,0,1,0,1,0,0,0,0,1],
    [0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,1,1,1,0,0,0,1,1,1,0,0]
  ]
};

// WebGL shaders for Conway's Game of Life
const vertexShaderSource = `
  attribute vec2 a_position;
  attribute float a_state;
  attribute float a_age;
  
  uniform vec2 u_resolution;
  uniform float u_cellSize;
  uniform float u_time;
  
  varying float v_state;
  varying float v_age;
  varying vec2 v_position;
  varying float v_time;
  
  void main() {
    vec2 cellPos = a_position * u_cellSize;
    vec2 position = ((cellPos / u_resolution) * 2.0 - 1.0) * vec2(1, -1);
    gl_Position = vec4(position, 0, 1);
    gl_PointSize = u_cellSize;
    v_state = a_state;
    v_age = a_age;
    v_position = a_position;
    v_time = u_time;
  }
`;

const fragmentShaderSource = `
  precision mediump float;
  
  uniform int u_colorScheme;
  uniform float u_cellGlow;
  uniform float u_cellSize;
  
  varying float v_state;
  varying float v_age;
  varying vec2 v_position;
  varying float v_time;
  
  vec3 getColorScheme(float age, int scheme) {
    if (scheme == 0) { // classic
      return vec3(0.0, 0.6, 1.0);
    } else if (scheme == 1) { // neon
      float hue = age * 0.1 + v_time * 0.001;
      return vec3(
        0.5 + 0.5 * sin(hue),
        0.5 + 0.5 * sin(hue + 2.094),
        0.5 + 0.5 * sin(hue + 4.188)
      );
    } else if (scheme == 2) { // fire
      float intensity = min(age * 0.05, 1.0);
      return vec3(1.0, intensity * 0.6, intensity * 0.2);
    } else { // ocean
      float wave = sin(v_position.x * 0.1 + v_time * 0.005) * 0.3 + 0.7;
      return vec3(0.1, 0.4 + wave * 0.3, 0.8 + wave * 0.2);
    }
  }
  
  void main() {
    if (v_state < 0.5) {
      discard; // Don't render dead cells
    }
    
    vec2 coord = gl_PointCoord - vec2(0.5);
    float dist = length(coord);
    
    // Create square cells with rounded corners
    float cell = 1.0 - smoothstep(0.35, 0.5, dist);
    
    // Add glow effect
    float glow = (1.0 - smoothstep(0.0, 0.7, dist)) * u_cellGlow;
    
    vec3 color = getColorScheme(v_age, u_colorScheme);
    float alpha = cell + glow * 0.3;
    
    // Pulse based on age
    float pulse = 0.8 + 0.2 * sin(v_age * 0.3 + v_time * 0.01);
    
    gl_FragColor = vec4(color * pulse, alpha);
  }
`;

export const ConwayGameOfLifePage: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const glRef = useRef<WebGLRenderingContext | null>(null);
  const programRef = useRef<WebGLProgram | null>(null);
  const animationRef = useRef<number>();
  const timeRef = useRef<number>(0);
  
  const [isAnimating, setIsAnimating] = useState(false);
  const [dimensions, setDimensions] = useState({ width: window.innerWidth, height: window.innerHeight });
  const [useWebGL, setUseWebGL] = useState(true);
  const [isInitialized, setIsInitialized] = useState(false);
  const [generation, setGeneration] = useState(0);
  
  const [params, setParams] = useState<GameOfLifeParams>({
    gridWidth: 240,
    gridHeight: 120,
    animationSpeed: 60,
    wrapEdges: true,
    initialDensity: 75,
    cellGlow: 0.5,
    colorScheme: 'neon'
  });

  const [grid, setGrid] = useState<boolean[][]>([]);
  const [cellAges, setCellAges] = useState<number[][]>([]);

  // WebGL initialization
  const initWebGL = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) {
      console.error('Canvas not available for WebGL initialization');
      return false;
    }

    canvas.width = dimensions.width;
    canvas.height = dimensions.height;
    canvas.style.width = dimensions.width + 'px';
    canvas.style.height = dimensions.height + 'px';

    const gl = canvas.getContext('webgl');
    if (!gl) {
      console.warn('WebGL not supported, falling back to 2D canvas');
      setUseWebGL(false);
      setIsInitialized(true);
      return true;
    }

    glRef.current = gl;

    // Create and compile shaders
    const vertexShader = gl.createShader(gl.VERTEX_SHADER);
    const fragmentShader = gl.createShader(gl.FRAGMENT_SHADER);
    
    if (!vertexShader || !fragmentShader) return false;

    gl.shaderSource(vertexShader, vertexShaderSource);
    gl.shaderSource(fragmentShader, fragmentShaderSource);
    
    gl.compileShader(vertexShader);
    gl.compileShader(fragmentShader);

    if (!gl.getShaderParameter(vertexShader, gl.COMPILE_STATUS)) {
      console.error('Vertex shader error:', gl.getShaderInfoLog(vertexShader));
      return false;
    }
    if (!gl.getShaderParameter(fragmentShader, gl.COMPILE_STATUS)) {
      console.error('Fragment shader error:', gl.getShaderInfoLog(fragmentShader));
      return false;
    }

    // Create and link program
    const program = gl.createProgram();
    if (!program) return false;

    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);
    
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      console.error('Program link error:', gl.getProgramInfoLog(program));
      return false;
    }
    
    programRef.current = program;

    // Enable blending for glow effects
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

    console.log('WebGL initialized successfully');
    setIsInitialized(true);
    return true;
  }, [dimensions]);

  // Initialize grid with random pattern
  const initializeGrid = useCallback(() => {
    const density = params.initialDensity / 100;
    const newGrid = Array(params.gridHeight).fill(null).map(() => 
      Array(params.gridWidth).fill(null).map(() => Math.random() < density)
    );
    const newAges = Array(params.gridHeight).fill(null).map(() => 
      Array(params.gridWidth).fill(0)
    );
    setGrid(newGrid);
    setCellAges(newAges);
    setGeneration(0);
    timeRef.current = 0;
  }, [params.gridWidth, params.gridHeight, params.initialDensity]);

  // Count neighbors with wrapping
  const countNeighbors = useCallback((grid: boolean[][], row: number, col: number): number => {
    let count = 0;
    const height = grid.length;
    const width = grid[0]?.length || 0;
    
    for (let i = -1; i <= 1; i++) {
      for (let j = -1; j <= 1; j++) {
        if (i === 0 && j === 0) continue;
        
        let newRow = row + i;
        let newCol = col + j;
        
        if (params.wrapEdges) {
          newRow = (newRow + height) % height;
          newCol = (newCol + width) % width;
        } else {
          if (newRow < 0 || newRow >= height || newCol < 0 || newCol >= width) continue;
        }
        
        if (grid[newRow][newCol]) count++;
      }
    }
    
    return count;
  }, [params.wrapEdges]);

  // Next generation calculation
  const nextGeneration = useCallback(() => {
    setGrid(currentGrid => {
      if (currentGrid.length === 0) return currentGrid;
      
      const height = currentGrid.length;
      const width = currentGrid[0]?.length || 0;
      const newGrid = Array(height).fill(null).map(() => Array(width).fill(false));
      
      setCellAges(currentAges => {
        const newAges = Array(height).fill(null).map(() => Array(width).fill(0));
        
        for (let row = 0; row < height; row++) {
          for (let col = 0; col < width; col++) {
            const neighbors = countNeighbors(currentGrid, row, col);
            const currentCell = currentGrid[row][col];
            
            // Conway's Game of Life rules
            if (currentCell) {
              // Live cell with 2 or 3 neighbors survives
              if (neighbors === 2 || neighbors === 3) {
                newGrid[row][col] = true;
                newAges[row][col] = currentAges[row][col] + 1;
              }
            } else {
              // Dead cell with exactly 3 neighbors becomes alive
              if (neighbors === 3) {
                newGrid[row][col] = true;
                newAges[row][col] = 0;
              }
            }
          }
        }
        
        return newAges;
      });
      
      setGeneration(gen => gen + 1);
      timeRef.current += 1;
      return newGrid;
    });
  }, [countNeighbors]);

  // WebGL rendering
  const render = useCallback(() => {
    const gl = glRef.current;
    const program = programRef.current;
    if (!gl || !program || grid.length === 0) return;

    try {
      gl.viewport(0, 0, dimensions.width, dimensions.height);
      gl.clearColor(0.02, 0.02, 0.08, 1.0);
      gl.clear(gl.COLOR_BUFFER_BIT);

      gl.useProgram(program);

      const cellSizeX = dimensions.width / params.gridWidth;
      const cellSizeY = dimensions.height / params.gridHeight;
      const cellSize = Math.min(cellSizeX, cellSizeY);
      
      const positions: number[] = [];
      const states: number[] = [];
      const ages: number[] = [];

      for (let row = 0; row < params.gridHeight; row++) {
        for (let col = 0; col < params.gridWidth; col++) {
          if (grid[row] && grid[row][col]) {
            positions.push(col + 0.5, row + 0.5);
            states.push(1.0);
            ages.push(cellAges[row][col]);
          }
        }
      }

      if (positions.length === 0) return;

      // Create buffers
      const positionBuffer = gl.createBuffer();
      const stateBuffer = gl.createBuffer();
      const ageBuffer = gl.createBuffer();

      // Position attribute
      gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
      gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(positions), gl.STATIC_DRAW);
      const positionLocation = gl.getAttribLocation(program, 'a_position');
      gl.enableVertexAttribArray(positionLocation);
      gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);

      // State attribute
      gl.bindBuffer(gl.ARRAY_BUFFER, stateBuffer);
      gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(states), gl.STATIC_DRAW);
      const stateLocation = gl.getAttribLocation(program, 'a_state');
      gl.enableVertexAttribArray(stateLocation);
      gl.vertexAttribPointer(stateLocation, 1, gl.FLOAT, false, 0, 0);

      // Age attribute
      gl.bindBuffer(gl.ARRAY_BUFFER, ageBuffer);
      gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(ages), gl.STATIC_DRAW);
      const ageLocation = gl.getAttribLocation(program, 'a_age');
      gl.enableVertexAttribArray(ageLocation);
      gl.vertexAttribPointer(ageLocation, 1, gl.FLOAT, false, 0, 0);

      // Set uniforms
      const resolutionLocation = gl.getUniformLocation(program, 'u_resolution');
      gl.uniform2f(resolutionLocation, dimensions.width, dimensions.height);
      
      const cellSizeLocation = gl.getUniformLocation(program, 'u_cellSize');
      gl.uniform1f(cellSizeLocation, cellSize);
      
      const timeLocation = gl.getUniformLocation(program, 'u_time');
      gl.uniform1f(timeLocation, timeRef.current);

      const colorSchemeLocation = gl.getUniformLocation(program, 'u_colorScheme');
      const colorSchemeMap = { 'classic': 0, 'neon': 1, 'fire': 2, 'ocean': 3 };
      gl.uniform1i(colorSchemeLocation, colorSchemeMap[params.colorScheme] || 1);

      const cellGlowLocation = gl.getUniformLocation(program, 'u_cellGlow');
      gl.uniform1f(cellGlowLocation, params.cellGlow);

      // Draw
      gl.drawArrays(gl.POINTS, 0, positions.length / 2);

      // Cleanup
      gl.deleteBuffer(positionBuffer);
      gl.deleteBuffer(stateBuffer);
      gl.deleteBuffer(ageBuffer);
      
    } catch (error) {
      console.error('WebGL rendering error:', error);
    }
  }, [grid, cellAges, dimensions, params.gridWidth, params.gridHeight, params.colorScheme, params.cellGlow]);

  // 2D Canvas fallback rendering
  const render2D = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || grid.length === 0) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    try {
      ctx.clearRect(0, 0, dimensions.width, dimensions.height);
      
      // Set background
      ctx.fillStyle = '#050520';
      ctx.fillRect(0, 0, dimensions.width, dimensions.height);

      const cellSizeX = dimensions.width / params.gridWidth;
      const cellSizeY = dimensions.height / params.gridHeight;

      for (let row = 0; row < params.gridHeight; row++) {
        for (let col = 0; col < params.gridWidth; col++) {
          if (grid[row] && grid[row][col]) {
            const age = cellAges[row][col];
            let color;
            
            switch (params.colorScheme) {
              case 'classic':
                color = '#0099ff';
                break;
              case 'fire':
                const intensity = Math.min(age * 0.05, 1.0);
                color = `rgb(255, ${Math.floor(intensity * 153)}, ${Math.floor(intensity * 51)})`;
                break;
              case 'ocean':
                color = `hsl(200, 80%, ${60 + Math.sin(age * 0.3) * 20}%)`;
                break;
              default: // neon
                const hue = (age * 10) % 360;
                color = `hsl(${hue}, 80%, 60%)`;
            }
            
            ctx.fillStyle = color;
            ctx.fillRect(col * cellSizeX, row * cellSizeY, cellSizeX - 1, cellSizeY - 1);
          }
        }
      }
    } catch (error) {
      console.error('2D Canvas rendering error:', error);
    }
  }, [grid, cellAges, dimensions, params.gridWidth, params.gridHeight, params.colorScheme]);

  // Animation loop
  const animate = useCallback(() => {
    nextGeneration();
    if (useWebGL) {
      render();
    } else {
      render2D();
    }
    
    if (isAnimating) {
      animationRef.current = requestAnimationFrame(() => {
        setTimeout(animate, 101 - params.animationSpeed);
      });
    }
  }, [isAnimating, nextGeneration, render, render2D, useWebGL, params.animationSpeed]);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      setDimensions({ width: window.innerWidth, height: window.innerHeight });
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Initialize WebGL when dimensions change
  useEffect(() => {
    const success = initWebGL();
    if (!success) {
      console.error('Failed to initialize WebGL');
    }
  }, [initWebGL]);

  // Initialize grid and auto-start
  useEffect(() => {
    if (!isInitialized) return;
    
    const timer = setTimeout(() => {
      initializeGrid();
      setTimeout(() => {
        if (useWebGL) {
          render();
        } else {
          render2D();
        }
        // Auto-start the animation with the dense initial pattern
        setIsAnimating(true);
      }, 100);
    }, 100);
    
    return () => clearTimeout(timer);
  }, [isInitialized, initializeGrid, render, render2D, useWebGL]);

  // Animation control
  useEffect(() => {
    if (isAnimating) {
      animate();
    }
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isAnimating, animate]);

  const handleParamChange = (key: keyof GameOfLifeParams, value: number | boolean | string) => {
    setParams(prev => ({ ...prev, [key]: value }));
  };

  const toggleAnimation = () => {
    setIsAnimating(!isAnimating);
  };

  const step = () => {
    nextGeneration();
    if (useWebGL) {
      render();
    } else {
      render2D();
    }
  };

  const randomize = () => {
    const density = params.initialDensity / 100;
    const newGrid = Array(params.gridHeight).fill(null).map(() =>
      Array(params.gridWidth).fill(null).map(() => Math.random() < density)
    );
    const newAges = Array(params.gridHeight).fill(null).map(() => 
      Array(params.gridWidth).fill(0)
    );
    setGrid(newGrid);
    setCellAges(newAges);
    setGeneration(0);
    timeRef.current = 0;
  };

  const clear = () => {
    initializeGrid();
  };

  const placePattern = (patternName: keyof typeof PRESET_PATTERNS) => {
    const pattern = PRESET_PATTERNS[patternName];
    const newGrid = Array(params.gridHeight).fill(null).map(() => Array(params.gridWidth).fill(false));
    const newAges = Array(params.gridHeight).fill(null).map(() => Array(params.gridWidth).fill(0));
    const startRow = Math.floor((params.gridHeight - pattern.length) / 2);
    const startCol = Math.floor((params.gridWidth - pattern[0].length) / 2);
    
    // Place pattern
    for (let i = 0; i < pattern.length; i++) {
      for (let j = 0; j < pattern[i].length; j++) {
        if (startRow + i < params.gridHeight && startCol + j < params.gridWidth) {
          newGrid[startRow + i][startCol + j] = pattern[i][j] === 1;
        }
      }
    }
    
    setGrid(newGrid);
    setCellAges(newAges);
    setGeneration(0);
    timeRef.current = 0;
  };

  const handleCanvasClick = (event: React.MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current || isAnimating) return;
    
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    const cellSizeX = dimensions.width / params.gridWidth;
    const cellSizeY = dimensions.height / params.gridHeight;
    const col = Math.floor(x / cellSizeX);
    const row = Math.floor(y / cellSizeY);
    
    if (row >= 0 && row < params.gridHeight && col >= 0 && col < params.gridWidth) {
      const newGrid = [...grid.map(row => [...row])];
      const newAges = [...cellAges.map(row => [...row])];
      newGrid[row][col] = !newGrid[row][col];
      newAges[row][col] = 0;
      setGrid(newGrid);
      setCellAges(newAges);
    }
  };

  return (
    <div style={{ 
      position: 'fixed', 
      top: 0, 
      left: 0, 
      width: '100vw', 
      height: '100vh', 
      overflow: 'hidden',
      backgroundColor: '#050520'
    }}>
      {/* Full-screen WebGL canvas */}
      <canvas
        ref={canvasRef}
        onClick={handleCanvasClick}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          display: 'block',
          cursor: isAnimating ? 'default' : 'pointer'
        }}
      />

      {/* Title and Info Panel */}
      <Box
        sx={{
          position: 'fixed',
          top: 80,
          left: 20,
          maxWidth: 380,
          backgroundColor: 'rgba(0,0,0,0.85)',
          backdropFilter: 'blur(10px)',
          padding: 2.5,
          borderRadius: 2,
          zIndex: 999,
          color: 'white'
        }}
      >
        <Typography variant="h4" gutterBottom sx={{ 
          fontWeight: 'bold',
          background: 'linear-gradient(45deg, #0099ff, #9933ff, #ff3399)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
          mb: 1
        }}>
          Conway's Game of Life
        </Typography>
        
        <Typography variant="body2" sx={{ mb: 1.5, lineHeight: 1.4 }}>
          A cellular automaton that creates complex patterns from simple rules. 
          Cells live, die, and reproduce based on their neighbors, creating 
          infinite emergent behaviors from just four basic rules.
        </Typography>
        
        <Typography variant="caption" sx={{ 
          fontSize: '0.75em', 
          opacity: 0.8,
          fontStyle: 'italic'
        }}>
          WebGL-accelerated • Real-time cellular evolution • Generation: {generation}
        </Typography>
      </Box>

      {/* Controls Panel */}
      <Box
        sx={{
          position: 'fixed',
          top: 80,
          right: 20,
          width: 320,
          backgroundColor: 'rgba(0,0,0,0.85)',
          backdropFilter: 'blur(10px)',
          padding: 3,
          borderRadius: 2,
          zIndex: 1000,
          color: 'white'
        }}
      >
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Settings fontSize="small" />
          Game Controls
        </Typography>

        <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
          <Button
            variant="contained"
            onClick={toggleAnimation}
            startIcon={isAnimating ? <Pause /> : <PlayArrow />}
            size="small"
            fullWidth
            sx={{ backgroundColor: isAnimating ? '#d32f2f' : '#2e7d32' }}
          >
            {isAnimating ? 'Pause' : 'Play'}
          </Button>

          <Button
            variant="outlined"
            onClick={step}
            startIcon={<SkipNext />}
            size="small"
            fullWidth
            disabled={isAnimating}
            sx={{ borderColor: '#666', color: 'white' }}
          >
            Step
          </Button>

          <Button
            variant="outlined"
            onClick={clear}
            startIcon={<Refresh />}
            size="small"
            fullWidth
            disabled={isAnimating}
            sx={{ borderColor: '#666', color: 'white' }}
          >
            Clear
          </Button>
        </Box>

        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" gutterBottom>Grid Resolution: {params.gridWidth}×{params.gridHeight}</Typography>
          <Typography variant="body2" sx={{ fontSize: '0.75em', opacity: 0.7, mb: 1 }}>
            Optimized for widescreen display
          </Typography>
        </Box>

        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" gutterBottom>Animation Speed: {params.animationSpeed}</Typography>
          <Slider
            value={params.animationSpeed}
            onChange={(_, value) => handleParamChange('animationSpeed', value as number)}
            min={10}
            max={100}
            size="small"
            sx={{ color: '#9933ff' }}
          />
        </Box>

        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" gutterBottom>Initial Density: {params.initialDensity}%</Typography>
          <Slider
            value={params.initialDensity}
            onChange={(_, value) => handleParamChange('initialDensity', value as number)}
            min={5}
            max={99}
            step={5}
            size="small"
            sx={{ color: '#ff3399' }}
          />
        </Box>

        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" gutterBottom>Cell Glow: {(params.cellGlow * 100).toFixed(0)}%</Typography>
          <Slider
            value={params.cellGlow}
            onChange={(_, value) => handleParamChange('cellGlow', value as number)}
            min={0}
            max={1}
            step={0.1}
            size="small"
            sx={{ color: '#00ffcc' }}
          />
        </Box>

        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel sx={{ color: 'white' }}>Color Scheme</InputLabel>
          <Select
            value={params.colorScheme}
            onChange={(e) => handleParamChange('colorScheme', e.target.value)}
            label="Color Scheme"
            size="small"
            sx={{ color: 'white', '.MuiOutlinedInput-notchedOutline': { borderColor: '#666' } }}
          >
            <MenuItem value="classic">Classic Blue</MenuItem>
            <MenuItem value="neon">Neon Rainbow</MenuItem>
            <MenuItem value="fire">Fire</MenuItem>
            <MenuItem value="ocean">Ocean Wave</MenuItem>
          </Select>
        </FormControl>

        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel sx={{ color: 'white' }}>Preset Patterns</InputLabel>
          <Select
            value=""
            onChange={(e) => {
              const pattern = e.target.value as keyof typeof PRESET_PATTERNS;
              if (pattern) placePattern(pattern);
            }}
            label="Preset Patterns"
            size="small"
            sx={{ color: 'white', '.MuiOutlinedInput-notchedOutline': { borderColor: '#666' } }}
          >
            {Object.keys(PRESET_PATTERNS).map((pattern) => (
              <MenuItem key={pattern} value={pattern}>
                {pattern.charAt(0).toUpperCase() + pattern.slice(1)}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <Button
          variant="outlined"
          onClick={randomize}
          fullWidth
          disabled={isAnimating}
          sx={{ borderColor: '#666', color: 'white' }}
        >
          Randomize ({params.initialDensity}%)
        </Button>
      </Box>

      {/* Statistics overlay */}
      <Box
        sx={{
          position: 'fixed',
          bottom: 20,
          left: 20,
          color: 'white',
          backgroundColor: 'rgba(0,0,0,0.7)',
          padding: 2,
          borderRadius: 1,
          zIndex: 999
        }}
      >
        <Typography variant="body2">Generation: {generation}</Typography>
        <Typography variant="body2">Grid: {params.gridWidth}×{params.gridHeight}</Typography>
        <Typography variant="body2">Living Cells: {grid.reduce((sum, row) => sum + row.filter(cell => cell).length, 0)}</Typography>
        <Typography variant="body2" sx={{ mt: 1, fontSize: '0.7em', opacity: 0.8 }}>
          Renderer: {useWebGL ? 'WebGL' : '2D Canvas'} | {isInitialized ? 'Ready' : 'Initializing...'}
        </Typography>
        <Typography variant="body2" sx={{ fontSize: '0.7em', opacity: 0.6 }}>
          Click cells to toggle (when paused)
        </Typography>
      </Box>
    </div>
  );
};