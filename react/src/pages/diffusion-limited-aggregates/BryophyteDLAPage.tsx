import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Typography, Grid, Slider, Button, Box, Paper } from '@mui/material';
import { MathRenderer } from '../../components/math/MathRenderer';
import { PlayArrow, Pause, Refresh } from '@mui/icons-material';

interface BryophyteParams {
  gridSize: number;
  numParticles: number;
  maxSteps: number;
  upwardBias: number;
  stickingProbability: number;
  animationSpeed: number;
  batchSize: number;
}

export const BryophyteDLAPage: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<NodeJS.Timeout>();
  const [isAnimating, setIsAnimating] = useState(false);
  const [currentParticle, setCurrentParticle] = useState(0);
  const [params, setParams] = useState<BryophyteParams>({
    gridSize: 300,
    numParticles: 8000,
    maxSteps: 3000,
    upwardBias: 0.75,
    stickingProbability: 0.7,
    animationSpeed: 80,
    batchSize: 30
  });

  const [grid, setGrid] = useState<number[][]>([]);
  const [clusterSize, setClusterSize] = useState(0);

  const initializeGrid = useCallback(() => {
    const newGrid = Array(params.gridSize).fill(0).map(() => Array(params.gridSize).fill(0));
    
    // Create a wider and taller seed area at the bottom for better moss foundation
    const center = Math.floor(params.gridSize / 2);
    const seedWidth = Math.floor(params.gridSize * 0.15); // 15% of grid width
    const seedHeight = 3; // Multiple rows for better foundation
    
    let seedCount = 0;
    for (let y = params.gridSize - seedHeight; y < params.gridSize; y++) {
      for (let x = center - seedWidth; x <= center + seedWidth; x++) {
        if (x >= 0 && x < params.gridSize) {
          newGrid[x][y] = 1;
          seedCount++;
        }
      }
    }
    
    setGrid(newGrid);
    setClusterSize(seedCount);
    setCurrentParticle(0);
  }, [params.gridSize]);

  const performMossRandomWalk = useCallback((currentGrid: number[][]): { x: number; y: number } | null => {
    const center = Math.floor(params.gridSize / 2);
    
    // Start particle at bottom with wider spread
    let x = center + Math.floor((Math.random() - 0.5) * Math.min(params.gridSize * 0.6, 150));
    let y = params.gridSize - 1 - Math.floor(Math.random() * 5); // Start slightly above bottom
    
    // Ensure starting position is valid
    x = Math.max(0, Math.min(params.gridSize - 1, x));
    y = Math.max(0, Math.min(params.gridSize - 1, y));

    for (let step = 0; step < params.maxSteps; step++) {
      const prob = Math.random();
      
      // Enhanced upward bias with better lateral movement
      if (prob < params.upwardBias && y > 0) {
        y--; // Move up (primary direction)
      } else if (prob < params.upwardBias + (1 - params.upwardBias) * 0.4 && x > 0) {
        x--; // Move left
      } else if (prob < params.upwardBias + (1 - params.upwardBias) * 0.8 && x < params.gridSize - 1) {
        x++; // Move right
      } else if (y < params.gridSize - 1) {
        y++; // Occasionally move down (less common)
      }

      // Check if adjacent to cluster (including more neighbors for better connectivity)
      const neighbors = [
        [x, y - 1], [x - 1, y], [x + 1, y], [x, y + 1],
        [x - 1, y - 1], [x + 1, y - 1], [x - 1, y + 1], [x + 1, y + 1]
      ];

      for (const [nx, ny] of neighbors) {
        if (nx >= 0 && nx < params.gridSize && ny >= 0 && ny < params.gridSize) {
          if (currentGrid[nx][ny] === 1) {
            // Only stick if current position is empty
            if (currentGrid[x][y] === 0) {
              // Higher sticking probability for upward growth
              const stickProb = y < params.gridSize * 0.8 ? params.stickingProbability * 1.5 : params.stickingProbability;
              if (Math.random() < stickProb) {
                return { x, y };
              }
            }
          }
        }
      }

      // If walker gets too high or moves out of reasonable bounds, restart
      if (y <= 5 || x <= 5 || x >= params.gridSize - 5) {
        // Respawn at bottom
        x = center + Math.floor((Math.random() - 0.5) * Math.min(params.gridSize * 0.6, 150));
        y = params.gridSize - 1 - Math.floor(Math.random() * 10);
        x = Math.max(5, Math.min(params.gridSize - 5, x));
        y = Math.max(params.gridSize - 20, Math.min(params.gridSize - 1, y));
      }
    }

    return null;
  }, [params.gridSize, params.maxSteps, params.upwardBias, params.stickingProbability]);

  const simulateStep = useCallback(() => {
    if (currentParticle >= params.numParticles) {
      setIsAnimating(false);
      return;
    }

    setGrid(prevGrid => {
      const newGrid = prevGrid.map(row => [...row]);
      let newClusterSize = clusterSize;

      // Process multiple particles per step
      for (let i = 0; i < params.batchSize && currentParticle + i < params.numParticles; i++) {
        const result = performMossRandomWalk(newGrid);
        if (result) {
          newGrid[result.x][result.y] = 1;
          newClusterSize++;
        }
      }

      setClusterSize(newClusterSize);
      setCurrentParticle(prev => prev + params.batchSize);
      return newGrid;
    });
  }, [currentParticle, params.numParticles, params.batchSize, performMossRandomWalk, clusterSize]);

  const drawGrid = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || grid.length === 0) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const cellSize = Math.min(canvas.width / params.gridSize, canvas.height / params.gridSize);
    const offsetX = (canvas.width - params.gridSize * cellSize) / 2;
    const offsetY = (canvas.height - params.gridSize * cellSize) / 2;

    // Draw background (moist soil/rock)
    const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
    gradient.addColorStop(0, '#1a1a2e'); // Dark blue-gray at top
    gradient.addColorStop(1, '#16213e'); // Darker at bottom
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw bryophyte (moss) with blue-green gradient
    for (let x = 0; x < params.gridSize; x++) {
      for (let y = 0; y < params.gridSize; y++) {
        if (grid[x][y] === 1) {
          // Create height and position-based coloring
          const heightFactor = (params.gridSize - y) / params.gridSize;
          const center = params.gridSize / 2;
          const distanceFromCenter = Math.abs(x - center) / (params.gridSize / 2);
          
          // Moss-like blue-green colors
          const baseBlue = 70 + heightFactor * 100;
          const baseGreen = 100 + heightFactor * 155;
          const intensity = 0.5 + heightFactor * 0.5 - distanceFromCenter * 0.2;
          
          // Bottom seeds are darker
          if (y === params.gridSize - 1) {
            ctx.fillStyle = `rgba(139, 69, 19, ${Math.max(0.4, intensity)})`;
          } else {
            ctx.fillStyle = `rgba(${Math.floor(baseBlue * 0.6)}, ${baseGreen}, ${Math.floor(baseBlue)}, ${Math.max(0.3, intensity)})`;
          }
          
          const pixelX = offsetX + x * cellSize;
          const pixelY = offsetY + y * cellSize;
          
          if (cellSize >= 2) {
            ctx.fillRect(pixelX, pixelY, cellSize, cellSize);
          } else {
            ctx.fillRect(Math.floor(pixelX), Math.floor(pixelY), 1, 1);
          }
        }
      }
    }

    // Add moisture effect (small highlights)
    ctx.globalCompositeOperation = 'screen';
    for (let x = 0; x < params.gridSize; x++) {
      for (let y = 0; y < params.gridSize; y++) {
        if (grid[x][y] === 1 && Math.random() < 0.05) {
          const pixelX = offsetX + x * cellSize;
          const pixelY = offsetY + y * cellSize;
          ctx.fillStyle = `rgba(173, 216, 230, 0.3)`; // Light blue highlights
          
          if (cellSize >= 2) {
            ctx.fillRect(pixelX, pixelY, cellSize, cellSize);
          }
        }
      }
    }
    ctx.globalCompositeOperation = 'source-over';
  }, [grid, params.gridSize]);

  const animate = useCallback(() => {
    simulateStep();
    drawGrid();
    
    if (isAnimating && currentParticle < params.numParticles) {
      animationRef.current = setTimeout(animate, 101 - params.animationSpeed);
    } else {
      setIsAnimating(false);
    }
  }, [isAnimating, simulateStep, drawGrid, currentParticle, params.numParticles, params.animationSpeed]);

  useEffect(() => {
    drawGrid();
  }, [drawGrid]);

  useEffect(() => {
    initializeGrid();
  }, [initializeGrid]);

  useEffect(() => {
    if (isAnimating) {
      animate();
    }
    return () => {
      if (animationRef.current) {
        clearTimeout(animationRef.current);
      }
    };
  }, [isAnimating, animate]);

  const handleParamChange = (key: keyof BryophyteParams, value: number) => {
    setParams(prev => ({ ...prev, [key]: value }));
  };

  const toggleAnimation = () => {
    setIsAnimating(!isAnimating);
  };

  const resetSimulation = () => {
    setIsAnimating(false);
    if (animationRef.current) {
      clearTimeout(animationRef.current);
    }
    initializeGrid();
  };

  const showFullMoss = () => {
    setIsAnimating(false);
    setCurrentParticle(params.numParticles);
    
    // Generate full moss growth quickly
    const newGrid = Array(params.gridSize).fill(0).map(() => Array(params.gridSize).fill(0));
    
    // Create same seed area as initialization
    const center = Math.floor(params.gridSize / 2);
    const seedWidth = Math.floor(params.gridSize * 0.15);
    const seedHeight = 3;
    
    let newClusterSize = 0;
    for (let y = params.gridSize - seedHeight; y < params.gridSize; y++) {
      for (let x = center - seedWidth; x <= center + seedWidth; x++) {
        if (x >= 0 && x < params.gridSize) {
          newGrid[x][y] = 1;
          newClusterSize++;
        }
      }
    }
    
    let currentGrid = newGrid;
    
    for (let i = 0; i < params.numParticles; i++) {
      const result = performMossRandomWalk(currentGrid);
      if (result) {
        currentGrid[result.x][result.y] = 1;
        newClusterSize++;
      }
    }
    
    setGrid(currentGrid);
    setClusterSize(newClusterSize);
  };

  return (
    <div className="page-container">
      <Typography variant="h3" component="h1" className="page-title">
        Bryophyte (Moss) DLA Simulation
      </Typography>
      <Typography variant="body1" className="page-description">
        Simulate the branching growth patterns of bryophytes using DLA with reduced sticking probability.
      </Typography>

      <Paper sx={{ p: 3, mb: 3, backgroundColor: 'background.paper' }}>
        <Typography variant="h6" gutterBottom>
          Branching DLA with Stochastic Sticking
        </Typography>
        <Typography variant="body2" sx={{ mb: 2 }}>
          Bryophytes (mosses) exhibit complex branching patterns due to reduced sticking probability. 
          The attachment process becomes probabilistic:
        </Typography>
        <MathRenderer 
          math="P(\text{stick}|\text{adjacent}) = p_s < 1" 
          block 
        />
        <Typography variant="body2" sx={{ mt: 2 }}>
          where <MathRenderer math="p_s" /> is the sticking probability (typically 0.5). 
          Combined with upward bias <MathRenderer math="b \approx 0.6" />, this creates 
          the characteristic moss-like patterns with extensive lateral branching.
        </Typography>
      </Paper>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <Box className="visualization-area">
            <canvas
              ref={canvasRef}
              width={800}
              height={600}
              style={{
                width: '100%',
                height: 'auto',
                border: '1px solid #333',
                borderRadius: '4px'
              }}
            />
            <Typography variant="body2" sx={{ mt: 1, textAlign: 'center' }}>
              Moss Size: {clusterSize} | Progress: {currentParticle} / {params.numParticles}
            </Typography>
          </Box>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Box className="controls-area">
            <Typography variant="h6" gutterBottom>
              Bryophyte Parameters
            </Typography>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Grid Size: {params.gridSize}</Typography>
              <Slider
                value={params.gridSize}
                onChange={(_, value) => handleParamChange('gridSize', value as number)}
                min={200}
                max={500}
                step={50}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Number of Particles: {params.numParticles}</Typography>
              <Slider
                value={params.numParticles}
                onChange={(_, value) => handleParamChange('numParticles', value as number)}
                min={3000}
                max={25000}
                step={1000}
                valueLabelDisplay="auto"
                valueLabelFormat={(value) => `${(value / 1000).toFixed(0)}k`}
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Upward Bias: {(params.upwardBias * 100).toFixed(0)}%</Typography>
              <Slider
                value={params.upwardBias}
                onChange={(_, value) => handleParamChange('upwardBias', value as number)}
                min={0.5}
                max={0.9}
                step={0.05}
                valueLabelDisplay="auto"
                valueLabelFormat={(value) => `${(value * 100).toFixed(0)}%`}
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Sticking Probability: {(params.stickingProbability * 100).toFixed(0)}%</Typography>
              <Slider
                value={params.stickingProbability}
                onChange={(_, value) => handleParamChange('stickingProbability', value as number)}
                min={0.3}
                max={1.0}
                step={0.05}
                valueLabelDisplay="auto"
                valueLabelFormat={(value) => `${(value * 100).toFixed(0)}%`}
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Max Steps per Walker: {params.maxSteps}</Typography>
              <Slider
                value={params.maxSteps}
                onChange={(_, value) => handleParamChange('maxSteps', value as number)}
                min={1000}
                max={10000}
                step={500}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Animation Speed: {params.animationSpeed}</Typography>
              <Slider
                value={params.animationSpeed}
                onChange={(_, value) => handleParamChange('animationSpeed', value as number)}
                min={1}
                max={100}
                step={1}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Batch Size: {params.batchSize}</Typography>
              <Slider
                value={params.batchSize}
                onChange={(_, value) => handleParamChange('batchSize', value as number)}
                min={1}
                max={50}
                step={1}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ display: 'flex', gap: 1, flexDirection: 'column' }}>
              <Button
                variant="contained"
                onClick={toggleAnimation}
                startIcon={isAnimating ? <Pause /> : <PlayArrow />}
                fullWidth
                sx={{ backgroundColor: '#4682B4' }}
              >
                {isAnimating ? 'Pause' : 'Start'} Growth
              </Button>

              <Button
                variant="outlined"
                onClick={showFullMoss}
                fullWidth
              >
                Complete Moss Growth
              </Button>

              <Button
                variant="outlined"
                onClick={resetSimulation}
                startIcon={<Refresh />}
                fullWidth
              >
                Reset Moss
              </Button>
            </Box>

            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" gutterBottom>
                Growth Statistics
              </Typography>
              <Typography variant="body2">
                Total Cells: <strong>{clusterSize}</strong>
              </Typography>
              <Typography variant="body2">
                Completion: <strong>{((currentParticle / params.numParticles) * 100).toFixed(1)}%</strong>
              </Typography>
              <Typography variant="body2">
                Growth Pattern: <strong>Branching Moss</strong>
              </Typography>
            </Box>
          </Box>
        </Grid>
      </Grid>
    </div>
  );
};