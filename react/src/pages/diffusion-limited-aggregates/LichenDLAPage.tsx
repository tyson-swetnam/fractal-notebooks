import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Typography, Grid, Slider, Button, Box, Paper } from '@mui/material';
import { MathRenderer } from '../../components/math/MathRenderer';
import { PlayArrow, Pause, Refresh } from '@mui/icons-material';

interface LichenParams {
  gridSize: number;
  numParticles: number;
  maxSteps: number;
  animationSpeed: number;
  batchSize: number;
}

export const LichenDLAPage: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<NodeJS.Timeout>();
  const [isAnimating, setIsAnimating] = useState(false);
  const [currentParticle, setCurrentParticle] = useState(0);
  const [params, setParams] = useState<LichenParams>({
    gridSize: 200,
    numParticles: 5000,
    maxSteps: 2000,
    animationSpeed: 70,
    batchSize: 25
  });

  const [grid, setGrid] = useState<number[][]>([]);
  const [clusterSize, setClusterSize] = useState(1);

  const initializeGrid = useCallback(() => {
    try {
      // Validate grid size to prevent memory issues
      if (params.gridSize > 500) {
        console.warn('Grid size too large, limiting to 500');
        setParams(prev => ({ ...prev, gridSize: 500 }));
        return;
      }
      
      const newGrid = Array(params.gridSize).fill(null).map(() => Array(params.gridSize).fill(0));
      const center = Math.floor(params.gridSize / 2);
      newGrid[center][center] = 1;
      setGrid(newGrid);
      setClusterSize(1);
      setCurrentParticle(0);
    } catch (error) {
      console.error('Error initializing grid:', error);
      // Fallback to smaller grid size
      setParams(prev => ({ ...prev, gridSize: 200 }));
    }
  }, [params.gridSize]);

  const performRandomWalk = useCallback((currentGrid: number[][]): { x: number; y: number } | null => {
    const center = Math.floor(params.gridSize / 2);
    
    // Start from a random position near the edge but not too far
    const startRadius = Math.min(params.gridSize / 3, 50);
    const angle = Math.random() * 2 * Math.PI;
    
    let x = Math.floor(center + startRadius * Math.cos(angle));
    let y = Math.floor(center + startRadius * Math.sin(angle));
    
    // Ensure starting position is within bounds
    x = Math.max(1, Math.min(params.gridSize - 2, x));
    y = Math.max(1, Math.min(params.gridSize - 2, y));

    for (let step = 0; step < params.maxSteps; step++) {
      // Random movement (4 directions)
      const direction = Math.floor(Math.random() * 4);
      
      let newX = x, newY = y;
      switch (direction) {
        case 0: newX = x - 1; break; // Left
        case 1: newX = x + 1; break; // Right
        case 2: newY = y - 1; break; // Up
        case 3: newY = y + 1; break; // Down
      }

      // Keep within bounds
      if (newX >= 0 && newX < params.gridSize && newY >= 0 && newY < params.gridSize) {
        x = newX;
        y = newY;
      }

      // Check if adjacent to cluster (including diagonals for better connectivity)
      const neighbors = [
        [x - 1, y], [x + 1, y], [x, y - 1], [x, y + 1],
        [x - 1, y - 1], [x + 1, y - 1], [x - 1, y + 1], [x + 1, y + 1]
      ];

      for (const [nx, ny] of neighbors) {
        if (nx >= 0 && nx < params.gridSize && ny >= 0 && ny < params.gridSize) {
          if (currentGrid[nx][ny] === 1) {
            // Only stick if the position is empty
            if (currentGrid[x][y] === 0) {
              return { x, y };
            }
          }
        }
      }

      // If too far from center, respawn closer
      const distanceFromCenter = Math.sqrt((x - center) ** 2 + (y - center) ** 2);
      if (distanceFromCenter > params.gridSize / 2.5) {
        const respawnAngle = Math.random() * 2 * Math.PI;
        x = Math.floor(center + startRadius * Math.cos(respawnAngle));
        y = Math.floor(center + startRadius * Math.sin(respawnAngle));
        x = Math.max(1, Math.min(params.gridSize - 2, x));
        y = Math.max(1, Math.min(params.gridSize - 2, y));
      }
    }

    return null;
  }, [params.gridSize, params.maxSteps]);

  const simulateStep = useCallback(() => {
    if (currentParticle >= params.numParticles) {
      setIsAnimating(false);
      return;
    }

    try {
      setGrid(prevGrid => {
        if (!prevGrid || prevGrid.length === 0) {
          console.warn('Invalid grid state, reinitializing');
          return prevGrid;
        }

        const newGrid = prevGrid.map(row => [...row]);
        let newClusterSize = clusterSize;

        // Process multiple particles per step with error handling
        for (let i = 0; i < params.batchSize && currentParticle + i < params.numParticles; i++) {
          try {
            const result = performRandomWalk(newGrid);
            if (result && result.x >= 0 && result.x < params.gridSize && 
                result.y >= 0 && result.y < params.gridSize) {
              if (newGrid[result.x][result.y] === 0) {
                newGrid[result.x][result.y] = 1;
                newClusterSize++;
              }
            }
          } catch (walkError) {
            console.warn('Error in random walk:', walkError);
            continue;
          }
        }

        setClusterSize(newClusterSize);
        setCurrentParticle(prev => prev + params.batchSize);
        return newGrid;
      });
    } catch (error) {
      console.error('Error in simulation step:', error);
      setIsAnimating(false);
    }
  }, [currentParticle, params.numParticles, params.batchSize, performRandomWalk, clusterSize, params.gridSize]);

  const drawGrid = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || grid.length === 0) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    try {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const cellSize = Math.min(canvas.width / params.gridSize, canvas.height / params.gridSize);
      const offsetX = (canvas.width - params.gridSize * cellSize) / 2;
      const offsetY = (canvas.height - params.gridSize * cellSize) / 2;

      // Performance optimization: skip drawing if cells are too small
      if (cellSize < 0.5) {
        console.warn('Grid too large for efficient rendering, using optimized mode');
        // Use image data for very large grids
        const imageData = ctx.createImageData(canvas.width, canvas.height);
        const data = imageData.data;
        
        for (let x = 0; x < params.gridSize; x++) {
          for (let y = 0; y < params.gridSize; y++) {
            if (grid[x] && grid[x][y] === 1) {
              const pixelX = Math.floor(offsetX + x * cellSize);
              const pixelY = Math.floor(offsetY + y * cellSize);
              
              if (pixelX >= 0 && pixelX < canvas.width && pixelY >= 0 && pixelY < canvas.height) {
                const index = (pixelY * canvas.width + pixelX) * 4;
                if (index >= 0 && index < data.length - 3) {
                  data[index] = 255;     // Red
                  data[index + 1] = 150; // Green
                  data[index + 2] = 150; // Blue
                  data[index + 3] = 255; // Alpha
                }
              }
            }
          }
        }
        
        ctx.putImageData(imageData, 0, 0);
        return;
      }

      // Draw rock/substrate background
      ctx.fillStyle = '#2c2c2c';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Add texture to background (reduce for performance)
      const texturePoints = Math.min(100, Math.max(20, 1000 / (params.gridSize / 100)));
      for (let i = 0; i < texturePoints; i++) {
        ctx.fillStyle = `rgba(${60 + Math.random() * 40}, ${60 + Math.random() * 40}, ${60 + Math.random() * 40}, 0.3)`;
        const x = Math.random() * canvas.width;
        const y = Math.random() * canvas.height;
        ctx.fillRect(x, y, 2, 2);
      }

      // Draw lichen particles with better visibility
      const centerGridX = Math.floor(params.gridSize / 2);
      const centerGridY = Math.floor(params.gridSize / 2);
      
      for (let x = 0; x < params.gridSize; x++) {
        if (!grid[x]) continue; // Safety check
        
        for (let y = 0; y < params.gridSize; y++) {
          if (grid[x][y] === 1) {
            const distance = Math.sqrt((x - centerGridX) ** 2 + (y - centerGridY) ** 2);
            const maxDistance = params.gridSize / 2;
            const intensity = Math.max(0.5, 1 - (distance / maxDistance));
            
            const pixelX = offsetX + x * cellSize;
            const pixelY = offsetY + y * cellSize;
            
            // Draw lichen with bright colors and glow effect
            const red = Math.floor(255 * intensity);
            const green = Math.floor(100 + 100 * intensity);
            const blue = Math.floor(100 + 100 * intensity);
            
            // Main lichen body
            ctx.fillStyle = `rgba(${red}, ${green}, ${blue}, 0.9)`;
            
            if (cellSize >= 2) {
              ctx.fillRect(pixelX, pixelY, cellSize, cellSize);
              
              // Add glow effect only for larger cells
              if (cellSize >= 3) {
                ctx.fillStyle = `rgba(${red}, ${green}, ${blue}, 0.3)`;
                ctx.fillRect(pixelX - 1, pixelY - 1, cellSize + 2, cellSize + 2);
              }
            } else {
              // For small cells, draw single pixels
              ctx.fillRect(Math.floor(pixelX), Math.floor(pixelY), Math.max(1, Math.ceil(cellSize)), Math.max(1, Math.ceil(cellSize)));
              
              // Add bright center point for very small cells
              if (cellSize < 1.5) {
                ctx.fillStyle = `rgba(255, 255, 255, 0.8)`;
                ctx.fillRect(Math.floor(pixelX), Math.floor(pixelY), 1, 1);
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('Error drawing grid:', error);
      // Fallback simple drawing
      ctx.fillStyle = '#2c2c2c';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = '#ff6b6b';
      ctx.fillText('Grid too large for display', canvas.width / 2 - 80, canvas.height / 2);
    }
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

  const handleParamChange = (key: keyof LichenParams, value: number) => {
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

  const showFullLichen = () => {
    try {
      setIsAnimating(false);
      setCurrentParticle(params.numParticles);
      
      // Validate grid size
      if (params.gridSize > 500) {
        console.warn('Grid size too large for full generation, using smaller size');
        setParams(prev => ({ ...prev, gridSize: 300 }));
        return;
      }
      
      // Generate full lichen quickly
      const newGrid = Array(params.gridSize).fill(null).map(() => Array(params.gridSize).fill(0));
      const center = Math.floor(params.gridSize / 2);
      newGrid[center][center] = 1;
      
      let currentGrid = newGrid;
      let newClusterSize = 1;
      
      // Limit particles for large grids to prevent browser freeze
      const maxParticles = Math.min(params.numParticles, params.gridSize * 20);
      
      for (let i = 0; i < maxParticles; i++) {
        try {
          const result = performRandomWalk(currentGrid);
          if (result && result.x >= 0 && result.x < params.gridSize && 
              result.y >= 0 && result.y < params.gridSize) {
            if (currentGrid[result.x][result.y] === 0) {
              currentGrid[result.x][result.y] = 1;
              newClusterSize++;
            }
          }
        } catch (walkError) {
          console.warn('Error in random walk during full generation:', walkError);
          continue;
        }
        
        // Progress update for large generations
        if (i % 1000 === 0 && i > 0) {
          console.log(`Generated ${i}/${maxParticles} particles`);
        }
      }
      
      setGrid(currentGrid);
      setClusterSize(newClusterSize);
    } catch (error) {
      console.error('Error generating full lichen:', error);
      // Reset to a safe state
      setParams(prev => ({ ...prev, gridSize: 200 }));
      initializeGrid();
    }
  };

  return (
    <div className="page-container">
      <Typography variant="h3" component="h1" className="page-title">
        Lichen DLA Simulation
      </Typography>
      <Typography variant="body1" className="page-description">
        Simulate the radial growth patterns of lichen using diffusion-limited aggregation.
      </Typography>

      <Paper sx={{ p: 3, mb: 3, backgroundColor: 'background.paper' }}>
        <Typography variant="h6" gutterBottom>
          Radial DLA Growth Model
        </Typography>
        <Typography variant="body2" sx={{ mb: 2 }}>
          Lichen growth follows a radial DLA pattern where particles start from the boundary 
          and perform random walks until they stick to the growing cluster:
        </Typography>
        <MathRenderer 
          math="P_{i+1} = P_i + \vec{R}_i \cdot \Delta t" 
          block 
        />
        <Typography variant="body2" sx={{ mt: 2 }}>
          where <MathRenderer math="P_i" /> is the particle position, <MathRenderer math="\vec{R}_i" /> 
          is a random unit vector, and sticking occurs when the distance to any cluster particle 
          is less than the lattice spacing. This creates the characteristic branching patterns of lichen.
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
                borderRadius: '4px',
                backgroundColor: '#2c2c2c'
              }}
            />
            <Typography variant="body2" sx={{ mt: 1, textAlign: 'center' }}>
              Cluster Size: {clusterSize} | Progress: {currentParticle} / {params.numParticles}
            </Typography>
          </Box>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Box className="controls-area">
            <Typography variant="h6" gutterBottom>
              Lichen Parameters
            </Typography>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Grid Size: {params.gridSize}</Typography>
              <Slider
                value={params.gridSize}
                onChange={(_, value) => handleParamChange('gridSize', value as number)}
                min={100}
                max={500}
                step={25}
                valueLabelDisplay="auto"
                marks={[
                  { value: 100, label: '100' },
                  { value: 200, label: '200' },
                  { value: 300, label: '300' },
                  { value: 400, label: '400' },
                  { value: 500, label: '500' }
                ]}
              />
              <Typography variant="caption" color="text.secondary">
                Warning: Large grid sizes (&gt;300) may impact performance
              </Typography>
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Number of Particles: {params.numParticles}</Typography>
              <Slider
                value={params.numParticles}
                onChange={(_, value) => handleParamChange('numParticles', value as number)}
                min={1000}
                max={10000}
                step={500}
                valueLabelDisplay="auto"
                valueLabelFormat={(value) => `${(value / 1000).toFixed(1)}k`}
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Max Steps per Walker: {params.maxSteps}</Typography>
              <Slider
                value={params.maxSteps}
                onChange={(_, value) => handleParamChange('maxSteps', value as number)}
                min={500}
                max={5000}
                step={250}
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
                sx={{ backgroundColor: '#ff4757' }}
              >
                {isAnimating ? 'Pause' : 'Start'} Growth
              </Button>

              <Button
                variant="outlined"
                onClick={showFullLichen}
                fullWidth
              >
                Generate Complete Lichen
              </Button>

              <Button
                variant="outlined"
                onClick={resetSimulation}
                startIcon={<Refresh />}
                fullWidth
              >
                Reset Simulation
              </Button>
            </Box>

            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" gutterBottom>
                Growth Statistics
              </Typography>
              <Typography variant="body2">
                Particles: <strong>{clusterSize}</strong>
              </Typography>
              <Typography variant="body2">
                Completion: <strong>{((currentParticle / params.numParticles) * 100).toFixed(1)}%</strong>
              </Typography>
              <Typography variant="body2">
                Fractal Dimension: <strong>≈ 1.71</strong>
              </Typography>
            </Box>
          </Box>
        </Grid>
      </Grid>
    </div>
  );
};