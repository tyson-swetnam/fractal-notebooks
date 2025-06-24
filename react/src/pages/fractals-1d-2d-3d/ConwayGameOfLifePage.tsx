import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Typography, Grid, Button, Box, Paper, FormControl, InputLabel, Select, MenuItem, Slider } from '@mui/material';
import { MathRenderer } from '../../components/math/MathRenderer';
import { PlayArrow, Pause, SkipNext, Refresh } from '@mui/icons-material';

interface GameOfLifeParams {
  gridSize: number;
  animationSpeed: number;
  wrapEdges: boolean;
  initialDensity: number;
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
  loaf: [
    [0, 1, 1, 0],
    [1, 0, 0, 1],
    [0, 1, 0, 1],
    [0, 0, 1, 0]
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
  ]
};

export const ConwayGameOfLifePage: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<NodeJS.Timeout>();
  const [isPlaying, setIsPlaying] = useState(false);
  const [generation, setGeneration] = useState(0);
  const [params, setParams] = useState<GameOfLifeParams>({
    gridSize: 50,
    animationSpeed: 200,
    wrapEdges: true,
    initialDensity: 30
  });

  const [grid, setGrid] = useState<boolean[][]>([]);
  const [cellSize, setCellSize] = useState(10);

  const initializeGrid = useCallback(() => {
    const newGrid = Array(params.gridSize).fill(null).map(() => 
      Array(params.gridSize).fill(false)
    );
    setGrid(newGrid);
    setGeneration(0);
  }, [params.gridSize]);

  const countNeighbors = useCallback((grid: boolean[][], row: number, col: number): number => {
    let count = 0;
    const size = grid.length;
    
    for (let i = -1; i <= 1; i++) {
      for (let j = -1; j <= 1; j++) {
        if (i === 0 && j === 0) continue;
        
        let newRow = row + i;
        let newCol = col + j;
        
        if (params.wrapEdges) {
          newRow = (newRow + size) % size;
          newCol = (newCol + size) % size;
        } else {
          if (newRow < 0 || newRow >= size || newCol < 0 || newCol >= size) continue;
        }
        
        if (grid[newRow][newCol]) count++;
      }
    }
    
    return count;
  }, [params.wrapEdges]);

  const nextGeneration = useCallback((currentGrid: boolean[][]): boolean[][] => {
    const size = currentGrid.length;
    const newGrid = Array(size).fill(null).map(() => Array(size).fill(false));
    
    for (let row = 0; row < size; row++) {
      for (let col = 0; col < size; col++) {
        const neighbors = countNeighbors(currentGrid, row, col);
        const currentCell = currentGrid[row][col];
        
        // Conway's Game of Life rules
        if (currentCell) {
          // Live cell with 2 or 3 neighbors survives
          newGrid[row][col] = neighbors === 2 || neighbors === 3;
        } else {
          // Dead cell with exactly 3 neighbors becomes alive
          newGrid[row][col] = neighbors === 3;
        }
      }
    }
    
    return newGrid;
  }, [countNeighbors]);

  const drawGrid = useCallback(() => {
    if (!canvasRef.current || grid.length === 0) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    const size = Math.min(canvas.width, canvas.height);
    const cellSize = size / params.gridSize;
    setCellSize(cellSize);
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw grid lines
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 0.5;
    
    for (let i = 0; i <= params.gridSize; i++) {
      const pos = i * cellSize;
      ctx.beginPath();
      ctx.moveTo(pos, 0);
      ctx.lineTo(pos, size);
      ctx.stroke();
      
      ctx.beginPath();
      ctx.moveTo(0, pos);
      ctx.lineTo(size, pos);
      ctx.stroke();
    }
    
    // Draw live cells
    ctx.fillStyle = '#007acc';
    for (let row = 0; row < params.gridSize; row++) {
      for (let col = 0; col < params.gridSize; col++) {
        if (grid[row][col]) {
          ctx.fillRect(
            col * cellSize + 1, 
            row * cellSize + 1, 
            cellSize - 2, 
            cellSize - 2
          );
        }
      }
    }
  }, [grid, params.gridSize]);

  const step = useCallback(() => {
    setGrid(currentGrid => {
      const newGrid = nextGeneration(currentGrid);
      setGeneration(gen => gen + 1);
      return newGrid;
    });
  }, [nextGeneration]);

  const animate = useCallback(() => {
    step();
    if (isPlaying) {
      animationRef.current = setTimeout(() => {
        animate();
      }, 501 - params.animationSpeed);
    }
  }, [step, isPlaying, params.animationSpeed]);

  useEffect(() => {
    drawGrid();
  }, [drawGrid]);

  useEffect(() => {
    initializeGrid();
  }, [initializeGrid]);

  useEffect(() => {
    if (isPlaying) {
      animate();
    }
    return () => {
      if (animationRef.current) {
        clearTimeout(animationRef.current);
      }
    };
  }, [isPlaying, animate]);

  const togglePlay = () => {
    setIsPlaying(!isPlaying);
  };

  const randomize = () => {
    const density = params.initialDensity / 100; // Convert percentage to decimal
    const newGrid = Array(params.gridSize).fill(null).map(() =>
      Array(params.gridSize).fill(null).map(() => Math.random() < density)
    );
    setGrid(newGrid);
    setGeneration(0);
  };

  const clear = () => {
    initializeGrid();
  };

  const placePattern = (patternName: keyof typeof PRESET_PATTERNS) => {
    const pattern = PRESET_PATTERNS[patternName];
    const newGrid = [...grid];
    const startRow = Math.floor((params.gridSize - pattern.length) / 2);
    const startCol = Math.floor((params.gridSize - pattern[0].length) / 2);
    
    // Clear grid first
    for (let i = 0; i < params.gridSize; i++) {
      for (let j = 0; j < params.gridSize; j++) {
        newGrid[i][j] = false;
      }
    }
    
    // Place pattern
    for (let i = 0; i < pattern.length; i++) {
      for (let j = 0; j < pattern[i].length; j++) {
        if (startRow + i < params.gridSize && startCol + j < params.gridSize) {
          newGrid[startRow + i][startCol + j] = pattern[i][j] === 1;
        }
      }
    }
    
    setGrid(newGrid);
    setGeneration(0);
  };

  const handleCanvasClick = (event: React.MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current || isPlaying) return;
    
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    const col = Math.floor(x / cellSize);
    const row = Math.floor(y / cellSize);
    
    if (row >= 0 && row < params.gridSize && col >= 0 && col < params.gridSize) {
      const newGrid = [...grid];
      newGrid[row][col] = !newGrid[row][col];
      setGrid(newGrid);
    }
  };

  const handleParamChange = (key: keyof GameOfLifeParams, value: number | boolean) => {
    setParams(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className="page-container">
      <Typography variant="h3" component="h1" className="page-title">
        Conway's Game of Life
      </Typography>
      <Typography variant="body1" className="page-description">
        Explore the fascinating cellular automaton that creates complex patterns from simple rules.
      </Typography>

      <Paper sx={{ p: 3, mb: 3, backgroundColor: 'background.paper' }}>
        <Typography variant="h6" gutterBottom>
          Rules of the Game
        </Typography>
        <Typography variant="body2" sx={{ mb: 2 }}>
          Conway's Game of Life follows four simple rules for each cell based on its eight neighbors:
        </Typography>
        <Box component="ul" sx={{ pl: 3, mb: 2 }}>
          <Typography component="li" variant="body2">
            Live cell with 2-3 neighbors → survives
          </Typography>
          <Typography component="li" variant="body2">
            Live cell with &lt;2 neighbors → dies (underpopulation)
          </Typography>
          <Typography component="li" variant="body2">
            Live cell with &gt;3 neighbors → dies (overpopulation)
          </Typography>
          <Typography component="li" variant="body2">
            Dead cell with exactly 3 neighbors → becomes alive (reproduction)
          </Typography>
        </Box>
        <Typography variant="body2" sx={{ mb: 2 }}>
          Mathematically: <MathRenderer math="s'_{i,j} = f(s_{i,j}, \sum_{n \in N} s_n)" /> where N represents the 8-neighborhood.
        </Typography>
        <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
          Use the Initial Cell Density slider to control how many cells are alive when randomizing. 
          Lower densities create sparse patterns, while higher densities lead to complex initial configurations.
        </Typography>
      </Paper>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <Box className="visualization-area">
            <canvas
              ref={canvasRef}
              width={600}
              height={600}
              onClick={handleCanvasClick}
              style={{
                maxWidth: '100%',
                height: 'auto',
                border: '1px solid #333',
                borderRadius: '4px',
                backgroundColor: '#000',
                cursor: isPlaying ? 'default' : 'pointer'
              }}
            />
            <Typography variant="body2" sx={{ mt: 1, textAlign: 'center' }}>
              Generation: {generation} | Click cells to toggle (when paused)
            </Typography>
          </Box>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Box className="controls-area">
            <Typography variant="h6" gutterBottom>
              Game Controls
            </Typography>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Grid Size: {params.gridSize}×{params.gridSize}</Typography>
              <Slider
                value={params.gridSize}
                onChange={(_, value) => handleParamChange('gridSize', value as number)}
                min={20}
                max={100}
                step={5}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Speed: {params.animationSpeed}</Typography>
              <Slider
                value={params.animationSpeed}
                onChange={(_, value) => handleParamChange('animationSpeed', value as number)}
                min={50}
                max={500}
                step={25}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Initial Cell Density: {params.initialDensity}%</Typography>
              <Slider
                value={params.initialDensity}
                onChange={(_, value) => handleParamChange('initialDensity', value as number)}
                min={5}
                max={80}
                step={5}
                valueLabelDisplay="auto"
                marks={[
                  { value: 10, label: '10%' },
                  { value: 30, label: '30%' },
                  { value: 50, label: '50%' },
                  { value: 70, label: '70%' }
                ]}
              />
            </Box>

            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>Preset Patterns</InputLabel>
              <Select
                label="Preset Patterns"
                value=""
                onChange={(e) => {
                  const pattern = e.target.value as keyof typeof PRESET_PATTERNS;
                  if (pattern) placePattern(pattern);
                }}
              >
                {Object.keys(PRESET_PATTERNS).map((pattern) => (
                  <MenuItem key={pattern} value={pattern}>
                    {pattern.charAt(0).toUpperCase() + pattern.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <Box sx={{ display: 'flex', gap: 1, flexDirection: 'column' }}>
              <Button
                variant="contained"
                onClick={togglePlay}
                startIcon={isPlaying ? <Pause /> : <PlayArrow />}
                fullWidth
              >
                {isPlaying ? 'Pause' : 'Play'}
              </Button>

              <Button
                variant="outlined"
                onClick={step}
                startIcon={<SkipNext />}
                fullWidth
                disabled={isPlaying}
              >
                Step
              </Button>

              <Button
                variant="outlined"
                onClick={randomize}
                fullWidth
                disabled={isPlaying}
              >
                Randomize ({params.initialDensity}%)
              </Button>

              <Button
                variant="outlined"
                onClick={clear}
                startIcon={<Refresh />}
                fullWidth
                disabled={isPlaying}
              >
                Clear Grid
              </Button>
            </Box>
          </Box>
        </Grid>
      </Grid>
    </div>
  );
};