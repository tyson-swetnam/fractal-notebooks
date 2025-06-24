import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Typography, Grid, Slider, Button, Box, Paper } from '@mui/material';
import { MathRenderer } from '../../components/math/MathRenderer';
import { PlayArrow, Pause, Refresh } from '@mui/icons-material';

interface SaprophyteParams {
  gridSize: number;
  numParticles: number;
  maxSteps: number;
  upwardBias: number;
  animationSpeed: number;
  batchSize: number;
}

export const SaprophyteDLAPage: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<NodeJS.Timeout>();
  const [isAnimating, setIsAnimating] = useState(false);
  const [currentParticle, setCurrentParticle] = useState(0);
  const [params, setParams] = useState<SaprophyteParams>({
    gridSize: 300,
    numParticles: 6000,
    maxSteps: 2500,
    upwardBias: 0.8,
    animationSpeed: 75,
    batchSize: 25
  });

  const [grid, setGrid] = useState<number[][]>([]);
  const [clusterSize, setClusterSize] = useState(0);

  const initializeGrid = useCallback(() => {
    console.log('Initializing hanging saprophyte grid with size:', params.gridSize);
    
    const newGrid = Array(params.gridSize).fill(null).map(() => Array(params.gridSize).fill(0));
    
    // Create attachment surface at the top (hanging substrate)
    const attachmentHeight = 2;
    let seedCount = 0;
    
    for (let y = 0; y < attachmentHeight; y++) {
      for (let x = 0; x < params.gridSize; x++) {
        newGrid[x][y] = 1;
        seedCount++;
      }
    }
    
    console.log('Created hanging substrate with', seedCount, 'particles');
    console.log('Attachment rows:', 0, 'to', attachmentHeight - 1);
    
    setGrid(newGrid);
    setClusterSize(seedCount);
    setCurrentParticle(0);
  }, [params.gridSize]);

  const performBiasedRandomWalk = useCallback((currentGrid: number[][]): { x: number; y: number } | null => {
    // Start particle at top (hanging from substrate)
    let x = Math.floor(Math.random() * params.gridSize);
    let y = Math.floor(Math.random() * 3); // Start near top attachment

    // Ensure starting position is valid
    x = Math.max(0, Math.min(params.gridSize - 1, x));
    y = Math.max(0, Math.min(params.gridSize - 1, y));

    for (let step = 0; step < params.maxSteps; step++) {
      const prob = Math.random();
      
      // Enhanced downward bias for hanging saprophyte growth
      if (prob < params.upwardBias && y < params.gridSize - 1) {
        y++; // Move down (primary direction for hanging growth)
      } else if (prob < params.upwardBias + (1 - params.upwardBias) * 0.3 && x > 0) {
        x--; // Move left
      } else if (prob < params.upwardBias + (1 - params.upwardBias) * 0.6 && x < params.gridSize - 1) {
        x++; // Move right
      } else if (y > 0) {
        y--; // Occasionally move up (rare)
      }

      // Check if adjacent to cluster (including diagonals for better connectivity)
      const neighbors = [
        [x, y - 1], [x - 1, y], [x + 1, y], [x, y + 1],
        [x - 1, y - 1], [x + 1, y - 1], [x - 1, y + 1], [x + 1, y + 1]
      ];

      for (const [nx, ny] of neighbors) {
        if (nx >= 0 && nx < params.gridSize && ny >= 0 && ny < params.gridSize) {
          if (currentGrid[nx][ny] === 1) {
            // Only stick if current position is empty
            if (currentGrid[x][y] === 0) {
              // Higher sticking probability for downward growth (closer to substrate)
              const stickProb = y > params.gridSize * 0.3 ? 0.8 : 0.6;
              if (Math.random() < stickProb) {
                return { x, y };
              }
            }
          }
        }
      }

      // If walker reaches very bottom or moves too far horizontally, restart
      if (y >= params.gridSize - 3 || x <= 2 || x >= params.gridSize - 2) {
        // Respawn at top (hanging area)
        x = Math.floor(Math.random() * params.gridSize);
        y = Math.floor(Math.random() * 5);
        x = Math.max(2, Math.min(params.gridSize - 2, x));
        y = Math.max(0, Math.min(10, y));
      }
    }

    return null;
  }, [params.gridSize, params.maxSteps, params.upwardBias]);

  const simulateStep = useCallback(() => {
    if (currentParticle >= params.numParticles) {
      setIsAnimating(false);
      return;
    }

    setGrid(prevGrid => {
      if (!prevGrid || prevGrid.length === 0) {
        console.warn('Grid not initialized, skipping step');
        return prevGrid;
      }

      const newGrid = prevGrid.map(row => [...row]);
      let newClusterSize = clusterSize;
      let successfulSticks = 0;

      // Process multiple particles per step
      for (let i = 0; i < params.batchSize && currentParticle + i < params.numParticles; i++) {
        try {
          const result = performBiasedRandomWalk(newGrid);
          if (result && result.x >= 0 && result.x < params.gridSize && 
              result.y >= 0 && result.y < params.gridSize) {
            if (newGrid[result.x][result.y] === 0) {
              newGrid[result.x][result.y] = 1;
              newClusterSize++;
              successfulSticks++;
            }
          }
        } catch (error) {
          console.warn('Error in random walk:', error);
          continue;
        }
      }

      // Debug logging for first few steps
      if (currentParticle < 100 && currentParticle % 25 === 0) {
        console.log(`Step ${currentParticle}: ${successfulSticks} new particles, cluster size: ${newClusterSize}`);
      }

      setClusterSize(newClusterSize);
      setCurrentParticle(prev => prev + params.batchSize);
      return newGrid;
    });
  }, [currentParticle, params.numParticles, params.batchSize, performBiasedRandomWalk, clusterSize, params.gridSize]);

  const drawGrid = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || grid.length === 0) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const cellSize = Math.min(canvas.width / params.gridSize, canvas.height / params.gridSize);
    const offsetX = (canvas.width - params.gridSize * cellSize) / 2;
    const offsetY = (canvas.height - params.gridSize * cellSize) / 2;

    // Draw background (soil-like)
    ctx.fillStyle = '#2c1810';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw saprophyte growth with green gradient
    for (let x = 0; x < params.gridSize; x++) {
      for (let y = 0; y < params.gridSize; y++) {
        if (grid[x] && grid[x][y] === 1) {
          // Create depth-based coloring for hanging growth effect
          const depthFactor = y / params.gridSize; // 0 at top, 1 at bottom
          const baseGreen = 40 + depthFactor * 120; // Darker at top, lighter hanging down
          const intensity = 0.6 + depthFactor * 0.4;
          
          // Top attachment (substrate) is darker brown
          if (y <= 1) {
            ctx.fillStyle = `rgba(139, 69, 19, ${intensity})`;
          } else {
            ctx.fillStyle = `rgba(34, ${Math.floor(baseGreen)}, 34, ${intensity})`;
          }
          
          const pixelX = offsetX + x * cellSize;
          const pixelY = offsetY + y * cellSize;
          
          if (cellSize >= 2) {
            ctx.fillRect(pixelX, pixelY, cellSize, cellSize);
            
            // Add glow effect for better visibility
            ctx.fillStyle = `rgba(255, 255, 255, 0.2)`;
            ctx.fillRect(pixelX, pixelY, cellSize, cellSize);
          } else if (cellSize >= 1) {
            ctx.fillRect(Math.floor(pixelX), Math.floor(pixelY), Math.ceil(cellSize), Math.ceil(cellSize));
          } else {
            // For very small cells, draw multiple pixels for visibility
            ctx.fillRect(Math.floor(pixelX), Math.floor(pixelY), 1, 1);
            ctx.fillStyle = `rgba(255, 255, 255, 0.8)`;
            ctx.fillRect(Math.floor(pixelX), Math.floor(pixelY), 1, 1);
          }
        }
      }
    }

    // Add some texture for organic look (simplified)
    ctx.globalCompositeOperation = 'screen';
    for (let x = 0; x < params.gridSize; x += 3) {
      for (let y = 0; y < params.gridSize; y += 3) {
        if (grid[x] && grid[x][y] === 1 && Math.random() < 0.15) {
          const pixelX = offsetX + x * cellSize;
          const pixelY = offsetY + y * cellSize;
          ctx.fillStyle = `rgba(255, 255, 255, 0.2)`;
          
          if (cellSize >= 1) {
            ctx.fillRect(pixelX, pixelY, Math.max(1, cellSize), Math.max(1, cellSize));
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

  const handleParamChange = (key: keyof SaprophyteParams, value: number) => {
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

  const showFullGrowth = () => {
    setIsAnimating(false);
    setCurrentParticle(params.numParticles);
    
    // Generate full hanging saprophyte growth quickly
    const newGrid = Array(params.gridSize).fill(0).map(() => Array(params.gridSize).fill(0));
    
    // Create same hanging substrate as initialization
    const attachmentHeight = 2;
    let newClusterSize = 0;
    
    for (let y = 0; y < attachmentHeight; y++) {
      for (let x = 0; x < params.gridSize; x++) {
        newGrid[x][y] = 1;
        newClusterSize++;
      }
    }
    
    let currentGrid = newGrid;
    
    for (let i = 0; i < params.numParticles; i++) {
      const result = performBiasedRandomWalk(currentGrid);
      if (result && currentGrid[result.x][result.y] === 0) {
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
        Hanging Saprophyte DLA Simulation
      </Typography>
      <Typography variant="body1" className="page-description">
        Simulate the downward hanging growth of saprophyte organisms using biased diffusion-limited aggregation.
      </Typography>

      <Paper sx={{ p: 3, mb: 3, backgroundColor: 'background.paper' }}>
        <Typography variant="h6" gutterBottom>
          Biased DLA with Downward Hanging Growth
        </Typography>
        <Typography variant="body2" sx={{ mb: 2 }}>
          Hanging saprophytes are decomposer organisms that grow downward from an attachment substrate. 
          The movement probability includes gravitational bias:
        </Typography>
        <MathRenderer 
          math="P(\text{down}) = b, \quad P(\text{left}) = P(\text{right}) = \frac{1-b}{2}" 
          block 
        />
        <Typography variant="body2" sx={{ mt: 2 }}>
          where <MathRenderer math="b" /> is the downward bias parameter (typically 0.8). 
          This creates characteristic hanging branching patterns as organisms grow downward 
          from their attachment point at the top, resembling stalactite-like growth.
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
              Organism Size: {clusterSize} | Progress: {currentParticle} / {params.numParticles}
            </Typography>
            <Typography variant="caption" sx={{ display: 'block', textAlign: 'center', color: 'text.secondary' }}>
              Grid: {params.gridSize}x{params.gridSize} | Foundation: {params.gridSize * 2} particles
            </Typography>
          </Box>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Box className="controls-area">
            <Typography variant="h6" gutterBottom>
              Saprophyte Parameters
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
                min={2000}
                max={20000}
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
                min={0.6}
                max={0.95}
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
                sx={{ backgroundColor: '#228B22' }}
              >
                {isAnimating ? 'Pause' : 'Start'} Growth
              </Button>

              <Button
                variant="outlined"
                onClick={showFullGrowth}
                fullWidth
              >
                Complete Growth
              </Button>

              <Button
                variant="outlined"
                onClick={resetSimulation}
                startIcon={<Refresh />}
                fullWidth
              >
                Reset Organism
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
                Growth Pattern: <strong>Upward Biased</strong>
              </Typography>
            </Box>
          </Box>
        </Grid>
      </Grid>
    </div>
  );
};