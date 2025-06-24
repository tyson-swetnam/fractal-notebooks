import React, { useState, useEffect, useCallback } from 'react';
import { Typography, Grid, Slider, Button, Box, Paper, FormControl, InputLabel, Select, MenuItem, Tab, Tabs } from '@mui/material';
import { MathRenderer } from '../../components/math/MathRenderer';
import { PlayArrow, Pause, Refresh } from '@mui/icons-material';
// @ts-ignore
import Plot from 'react-plotly.js';

interface TreeParams {
  maxDepth: number;
  leftAngle: number;
  rightAngle: number;
  leftScale: number;
  rightScale: number;
  animationSpeed: number;
  colorMode: 'depth' | 'rainbow' | 'classic';
}

interface Square {
  x: number;
  y: number;
  width: number;
  height: number;
  angle: number;
  depth: number;
  color: string;
}

export const PythagorasTreePage: React.FC = () => {
  const animationRef = React.useRef<NodeJS.Timeout>();
  const [activeTab, setActiveTab] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);
  const [currentDepth, setCurrentDepth] = useState(0);
  const [params, setParams] = useState<TreeParams>({
    maxDepth: 12,
    leftAngle: 45,
    rightAngle: 45,
    leftScale: 0.7071,  // √2/2
    rightScale: 0.7071, // √2/2
    animationSpeed: 500,
    colorMode: 'depth'
  });

  const [squares, setSquares] = useState<Square[]>([]);

  const createChildSquare = useCallback((parent: Square, side: 'left' | 'right'): Square | null => {
    const isLeft = side === 'left';
    const angle = isLeft ? params.leftAngle : params.rightAngle;
    const scale = isLeft ? params.leftScale : params.rightScale;
    
    const newSize = parent.width * scale;
    const parentAngleRad = (parent.angle * Math.PI) / 180;
    
    // Parent square center
    const parentCenterX = parent.x + parent.width / 2;
    const parentCenterY = parent.y + parent.height / 2;
    
    // Calculate the top edge of the parent square (the hypotenuse)
    const cos = Math.cos(parentAngleRad);
    const sin = Math.sin(parentAngleRad);
    
    // Top-left and top-right corners of the parent square
    const topLeftX = parentCenterX - (parent.width / 2) * cos + (parent.height / 2) * sin;
    const topLeftY = parentCenterY - (parent.width / 2) * sin - (parent.height / 2) * cos;
    const topRightX = parentCenterX + (parent.width / 2) * cos + (parent.height / 2) * sin;
    const topRightY = parentCenterY + (parent.width / 2) * sin - (parent.height / 2) * cos;
    
    let newCenterX, newCenterY, newAngle;
    
    if (isLeft) {
      // Left child square - positioned on the left part of the top edge
      newAngle = parent.angle + angle;
      const newAngleRad = (newAngle * Math.PI) / 180;
      
      // Position the child square so its bottom-right corner touches the top-left corner of parent
      const childBottomRightX = topLeftX;
      const childBottomRightY = topLeftY;
      
      // Calculate child center from its bottom-right corner
      const childCos = Math.cos(newAngleRad);
      const childSin = Math.sin(newAngleRad);
      
      newCenterX = childBottomRightX - (newSize / 2) * childCos + (newSize / 2) * childSin;
      newCenterY = childBottomRightY - (newSize / 2) * childSin - (newSize / 2) * childCos;
      
    } else {
      // Right child square - positioned on the right part of the top edge
      newAngle = parent.angle - angle;
      const newAngleRad = (newAngle * Math.PI) / 180;
      
      // Position the child square so its bottom-left corner touches the top-right corner of parent
      const childBottomLeftX = topRightX;
      const childBottomLeftY = topRightY;
      
      // Calculate child center from its bottom-left corner
      const childCos = Math.cos(newAngleRad);
      const childSin = Math.sin(newAngleRad);
      
      newCenterX = childBottomLeftX + (newSize / 2) * childCos + (newSize / 2) * childSin;
      newCenterY = childBottomLeftY + (newSize / 2) * childSin - (newSize / 2) * childCos;
    }
    
    return {
      x: newCenterX - newSize / 2,
      y: newCenterY - newSize / 2,
      width: newSize,
      height: newSize,
      angle: newAngle,
      depth: parent.depth + 1,
      color: ''
    };
  }, [params.leftAngle, params.rightAngle, params.leftScale, params.rightScale]);

  const getSquareColor = useCallback((depth: number, maxDepth: number): string => {
    switch (params.colorMode) {
      case 'depth':
        const intensity = 1 - (depth / maxDepth);
        return `hsl(${120 * intensity}, 70%, 50%)`;
      
      case 'rainbow':
        const hue = (depth * 360) / maxDepth;
        return `hsl(${hue}, 70%, 50%)`;
      
      case 'classic':
        return depth === 0 ? '#8B4513' : '#228B22';
      
      default:
        return '#007acc';
    }
  }, [params.colorMode]);

  const generateSquares = useCallback(() => {
    const newSquares: Square[] = [];
    const initialSize = 100;
    
    // Start with the base square
    const baseSquare: Square = {
      x: -initialSize / 2,
      y: -150,
      width: initialSize,
      height: initialSize,
      angle: 0,
      depth: 0,
      color: getSquareColor(0, params.maxDepth)
    };
    
    newSquares.push(baseSquare);
    
    // Queue for breadth-first generation
    const queue: Square[] = [baseSquare];
    
    while (queue.length > 0) {
      const current = queue.shift()!;
      
      if (current.depth >= params.maxDepth) continue;
      
      // Calculate child squares
      const leftChild = createChildSquare(current, 'left');
      const rightChild = createChildSquare(current, 'right');
      
      if (leftChild) {
        leftChild.color = getSquareColor(leftChild.depth, params.maxDepth);
        newSquares.push(leftChild);
        queue.push(leftChild);
      }
      
      if (rightChild) {
        rightChild.color = getSquareColor(rightChild.depth, params.maxDepth);
        newSquares.push(rightChild);
        queue.push(rightChild);
      }
    }
    
    setSquares(newSquares);
  }, [params.maxDepth, createChildSquare, getSquareColor]);

  // Helper function to get square corners for Plotly
  const getSquareCorners = (square: Square) => {
    const centerX = square.x + square.width / 2;
    const centerY = square.y + square.height / 2;
    const halfWidth = square.width / 2;
    const halfHeight = square.height / 2;
    
    const angleRad = (square.angle * Math.PI) / 180;
    const cos = Math.cos(angleRad);
    const sin = Math.sin(angleRad);
    
    // Calculate rotated corners
    const corners = [
      [-halfWidth, -halfHeight],
      [halfWidth, -halfHeight],
      [halfWidth, halfHeight],
      [-halfWidth, halfHeight],
      [-halfWidth, -halfHeight] // Close the shape
    ].map(([dx, dy]) => [
      centerX + dx * cos - dy * sin,
      centerY + dx * sin + dy * cos
    ]);
    
    return {
      x: corners.map(corner => corner[0]),
      y: corners.map(corner => corner[1])
    };
  };

  // Prepare Plotly data from squares
  const getPlotlyData = useCallback(() => {
    const visibleSquares = squares.filter(square => square.depth <= currentDepth);
    
    return visibleSquares.map((square, index) => {
      const corners = getSquareCorners(square);
      return {
        type: 'scatter',
        x: corners.x,
        y: corners.y,
        mode: 'lines',
        fill: 'toself',
        fillcolor: square.color,
        line: {
          color: '#333',
          width: 1
        },
        hoverinfo: 'none',
        showlegend: false,
        name: `Square ${index}`
      };
    });
  }, [squares, currentDepth]);

  const animate = useCallback(() => {
    if (currentDepth < params.maxDepth) {
      setCurrentDepth(prev => prev + 1);
      animationRef.current = setTimeout(() => {
        animate();
      }, params.animationSpeed);
    } else {
      setIsAnimating(false);
    }
  }, [currentDepth, params.maxDepth, params.animationSpeed]);

  const plotlyData = getPlotlyData();

  useEffect(() => {
    generateSquares();
    setCurrentDepth(0);
  }, [generateSquares]);

  useEffect(() => {
    if (isAnimating && currentDepth < params.maxDepth) {
      animate();
    }
    return () => {
      if (animationRef.current) {
        clearTimeout(animationRef.current);
      }
    };
  }, [isAnimating, animate, currentDepth, params.maxDepth]);

  const handleParamChange = (key: keyof TreeParams, value: number | string) => {
    setParams(prev => ({ ...prev, [key]: value }));
  };

  const toggleAnimation = () => {
    if (isAnimating) {
      setIsAnimating(false);
      if (animationRef.current) {
        clearTimeout(animationRef.current);
      }
    } else {
      setCurrentDepth(0);
      setIsAnimating(true);
    }
  };

  const showFullTree = () => {
    setCurrentDepth(params.maxDepth);
    setIsAnimating(false);
  };

  const resetTree = () => {
    setCurrentDepth(0);
    setIsAnimating(false);
  };

  return (
    <div className="page-container">
      <Typography variant="h3" component="h1" className="page-title">
        Pythagoras Tree
      </Typography>
      <Typography variant="body1" className="page-description">
        Explore the classic Pythagoras tree fractal based on recursive square placement.
      </Typography>

      <Paper sx={{ p: 3, mb: 3, backgroundColor: 'background.paper' }}>
        <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
          <Tab label="Visualization" />
          <Tab label="Mathematics" />
        </Tabs>
        
        {activeTab === 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6" gutterBottom>
              Interactive Pythagoras Tree
            </Typography>
            <Typography variant="body2">
              Explore the classic Pythagoras tree fractal based on recursive square placement with customizable 
              angles and scaling factors. Watch the geometric progression with animated growth.
            </Typography>
          </Box>
        )}
        
        {activeTab === 1 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6" gutterBottom>
              Mathematical Construction
            </Typography>
            <Typography variant="body2" sx={{ mb: 2 }}>
              The Pythagoras tree is constructed by recursively placing squares on the hypotenuse of right triangles. 
              Each generation creates two child squares with scaling factors:
            </Typography>
            <MathRenderer 
              math="s_{\text{left}} = \cos(\theta), \quad s_{\text{right}} = \sin(\theta)" 
              block 
            />
            <Typography variant="body2" sx={{ mt: 2 }}>
              For the classic tree with <MathRenderer math="\theta = 45°" />, both scales equal 
              <MathRenderer math="\frac{\sqrt{2}}{2} \approx 0.707" />, giving each child square 
              area <MathRenderer math="\frac{1}{2}" /> of its parent.
            </Typography>
          </Box>
        )}
      </Paper>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <Box className="visualization-area">
            <Plot
              data={plotlyData as any}
              layout={{
                xaxis: {
                  visible: false,
                  range: [-300, 300]
                },
                yaxis: {
                  visible: false,
                  range: [-200, 400]
                },
                showlegend: false,
                margin: { l: 0, r: 0, t: 0, b: 0 },
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: '#000',
                dragmode: 'pan'
              }}
              style={{ width: '100%', height: '600px' }}
              config={{
                displayModeBar: true,
                displaylogo: false,
                modeBarButtonsToRemove: ['select2d', 'lasso2d', 'autoScale2d']
              }}
            />
            <Typography variant="body2" sx={{ mt: 1, textAlign: 'center' }}>
              Current Depth: {currentDepth} / {params.maxDepth} | 
              Squares: {squares.filter(s => s.depth <= currentDepth).length} | Interactive Plotly View
            </Typography>
          </Box>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Box className="controls-area">
            <Typography variant="h6" gutterBottom>
              Tree Parameters
            </Typography>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Max Depth: {params.maxDepth}</Typography>
              <Slider
                value={params.maxDepth}
                onChange={(_, value) => handleParamChange('maxDepth', value as number)}
                min={3}
                max={15}
                step={1}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Left Angle: {params.leftAngle}°</Typography>
              <Slider
                value={params.leftAngle}
                onChange={(_, value) => handleParamChange('leftAngle', value as number)}
                min={10}
                max={80}
                step={1}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Right Angle: {params.rightAngle}°</Typography>
              <Slider
                value={params.rightAngle}
                onChange={(_, value) => handleParamChange('rightAngle', value as number)}
                min={10}
                max={80}
                step={1}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Left Scale: {params.leftScale.toFixed(3)}</Typography>
              <Slider
                value={params.leftScale}
                onChange={(_, value) => handleParamChange('leftScale', value as number)}
                min={0.3}
                max={0.9}
                step={0.01}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Right Scale: {params.rightScale.toFixed(3)}</Typography>
              <Slider
                value={params.rightScale}
                onChange={(_, value) => handleParamChange('rightScale', value as number)}
                min={0.3}
                max={0.9}
                step={0.01}
                valueLabelDisplay="auto"
              />
            </Box>

            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>Color Mode</InputLabel>
              <Select
                value={params.colorMode}
                label="Color Mode"
                onChange={(e) => handleParamChange('colorMode', e.target.value)}
              >
                <MenuItem value="depth">Depth-based</MenuItem>
                <MenuItem value="rainbow">Rainbow</MenuItem>
                <MenuItem value="classic">Classic</MenuItem>
              </Select>
            </FormControl>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Animation Speed: {params.animationSpeed}ms</Typography>
              <Slider
                value={params.animationSpeed}
                onChange={(_, value) => handleParamChange('animationSpeed', value as number)}
                min={100}
                max={1000}
                step={50}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ display: 'flex', gap: 1, flexDirection: 'column' }}>
              <Button
                variant="contained"
                onClick={toggleAnimation}
                startIcon={isAnimating ? <Pause /> : <PlayArrow />}
                fullWidth
              >
                {isAnimating ? 'Pause' : 'Animate'} Growth
              </Button>

              <Button
                variant="outlined"
                onClick={showFullTree}
                fullWidth
              >
                Show Full Tree
              </Button>

              <Button
                variant="outlined"
                onClick={resetTree}
                startIcon={<Refresh />}
                fullWidth
              >
                Reset
              </Button>
            </Box>

            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" gutterBottom>
                Tree Statistics
              </Typography>
              <Typography variant="body2">
                Total Squares: <strong>{squares.length}</strong>
              </Typography>
              <Typography variant="body2">
                Visible Squares: <strong>{squares.filter(s => s.depth <= currentDepth).length}</strong>
              </Typography>
              <Typography variant="body2">
                Fractal Dimension: <strong>≈ 1.44</strong>
              </Typography>
            </Box>
          </Box>
        </Grid>
      </Grid>
    </div>
  );
};