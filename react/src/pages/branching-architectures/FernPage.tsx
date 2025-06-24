import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Typography, Grid, Slider, Button, Box, Paper, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import { MathRenderer } from '../../components/math/MathRenderer';
import { PlayArrow, Pause, Refresh } from '@mui/icons-material';

interface FernParams {
  numPoints: number;
  animationSpeed: number;
  fernType: 'barnsley' | 'thelypteridaceae' | 'culcita' | 'fishbone';
}

const FERN_TYPES = {
  barnsley: [
    { a: 0, b: 0, c: 0, d: 0.16, e: 0, f: 0, p: 0.01 },
    { a: 0.85, b: 0.04, c: -0.04, d: 0.85, e: 0, f: 1.6, p: 0.85 },
    { a: 0.2, b: -0.26, c: 0.23, d: 0.22, e: 0, f: 1.6, p: 0.07 },
    { a: -0.15, b: 0.28, c: 0.26, d: 0.24, e: 0, f: 0.44, p: 0.07 }
  ],
  thelypteridaceae: [
    { a: 0, b: 0, c: 0, d: 0.25, e: 0, f: -0.4, p: 0.02 },
    { a: 0.95, b: 0.005, c: -0.005, d: 0.93, e: -0.002, f: 0.5, p: 0.84 },
    { a: 0.035, b: -0.2, c: 0.16, d: 0.04, e: -0.09, f: 0.02, p: 0.07 },
    { a: -0.04, b: 0.2, c: 0.16, d: 0.04, e: 0.083, f: 0.12, p: 0.07 }
  ],
  culcita: [
    { a: 0, b: 0, c: 0, d: 0.16, e: 0, f: 0, p: 0.01 },
    { a: 0.85, b: 0.04, c: -0.04, d: 0.85, e: 0, f: 1.6, p: 0.85 },
    { a: 0.2, b: -0.26, c: 0.23, d: 0.22, e: 0, f: 1.6, p: 0.07 },
    { a: -0.15, b: 0.28, c: 0.26, d: 0.24, e: 0, f: 0.44, p: 0.07 }
  ],
  fishbone: [
    { a: 0, b: 0, c: 0, d: 0.25, e: 0, f: -0.14, p: 0.02 },
    { a: 0.85, b: 0.02, c: -0.02, d: 0.83, e: 0, f: 1, p: 0.84 },
    { a: 0.09, b: -0.28, c: 0.3, d: 0.11, e: 0, f: 0.6, p: 0.07 },
    { a: -0.09, b: 0.28, c: 0.3, d: 0.09, e: 0, f: 0.7, p: 0.07 }
  ]
};

export const FernPage: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const [isAnimating, setIsAnimating] = useState(false);
  const [currentPoint, setCurrentPoint] = useState(0);
  const [params, setParams] = useState<FernParams>({
    numPoints: 50000,
    animationSpeed: 100,
    fernType: 'barnsley'
  });

  const [points, setPoints] = useState<{ x: number; y: number }[]>([]);

  const generateFern = useCallback(() => {
    const transforms = FERN_TYPES[params.fernType];
    const newPoints: { x: number; y: number }[] = [];
    
    let x = 0;
    let y = 0;
    
    for (let i = 0; i < params.numPoints; i++) {
      const rand = Math.random();
      let cumulativeP = 0;
      let selectedTransform = transforms[0];
      
      // Select transform based on probability
      for (const transform of transforms) {
        cumulativeP += transform.p;
        if (rand <= cumulativeP) {
          selectedTransform = transform;
          break;
        }
      }
      
      // Apply the transformation
      const newX = selectedTransform.a * x + selectedTransform.b * y + selectedTransform.e;
      const newY = selectedTransform.c * x + selectedTransform.d * y + selectedTransform.f;
      
      x = newX;
      y = newY;
      
      newPoints.push({ x, y });
    }
    
    setPoints(newPoints);
    setCurrentPoint(0);
  }, [params.fernType, params.numPoints]);

  const drawFern = useCallback(() => {
    if (!canvasRef.current || points.length === 0) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Find bounds
    const visiblePoints = points.slice(0, currentPoint + 1);
    if (visiblePoints.length === 0) return;
    
    const minX = Math.min(...points.map(p => p.x));
    const maxX = Math.max(...points.map(p => p.x));
    const minY = Math.min(...points.map(p => p.y));
    const maxY = Math.max(...points.map(p => p.y));
    
    const padding = 50;
    const scaleX = (canvas.width - 2 * padding) / (maxX - minX || 1);
    const scaleY = (canvas.height - 2 * padding) / (maxY - minY || 1);
    const scale = Math.min(scaleX, scaleY);
    
    const offsetX = canvas.width / 2 - (minX + maxX) / 2 * scale;
    const offsetY = padding - minY * scale;
    
    // Create gradient for depth effect
    const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
    gradient.addColorStop(0, '#90EE90');  // Light green
    gradient.addColorStop(0.3, '#228B22'); // Forest green
    gradient.addColorStop(1, '#006400');   // Dark green
    
    ctx.fillStyle = gradient;
    
    // Draw points
    visiblePoints.forEach((point, index) => {
      const x = point.x * scale + offsetX;
      const y = (point.y * scale) + offsetY;
      
      // Vary point size and opacity based on density and position
      const alpha = Math.min(1, 0.1 + (index / visiblePoints.length) * 0.9);
      const size = 1 + (point.y - minY) / (maxY - minY || 1);
      
      ctx.globalAlpha = alpha;
      ctx.beginPath();
      ctx.arc(x, y, size, 0, 2 * Math.PI);
      ctx.fill();
    });
    
    ctx.globalAlpha = 1;
  }, [points, currentPoint]);

  const animate = useCallback(() => {
    if (currentPoint < points.length - 1) {
      setCurrentPoint(prev => Math.min(prev + Math.ceil(params.animationSpeed / 10), points.length - 1));
      animationRef.current = requestAnimationFrame(animate);
    } else {
      setIsAnimating(false);
    }
  }, [currentPoint, points.length, params.animationSpeed]);

  useEffect(() => {
    drawFern();
  }, [drawFern]);

  useEffect(() => {
    generateFern();
  }, [generateFern]);

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

  const handleParamChange = (key: keyof FernParams, value: number | string) => {
    setParams(prev => ({ ...prev, [key]: value }));
  };

  const toggleAnimation = () => {
    if (isAnimating) {
      setIsAnimating(false);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    } else {
      setCurrentPoint(0);
      setIsAnimating(true);
    }
  };

  const showFullFern = () => {
    setCurrentPoint(points.length - 1);
    setIsAnimating(false);
  };

  const resetFern = () => {
    setCurrentPoint(0);
    setIsAnimating(false);
  };

  return (
    <div className="page-container">
      <Typography variant="h3" component="h1" className="page-title">
        Barnsley Ferns
      </Typography>
      <Typography variant="body1" className="page-description">
        Explore the beautiful fractal ferns generated using Iterated Function Systems (IFS).
      </Typography>

      <Paper sx={{ p: 3, mb: 3, backgroundColor: 'background.paper' }}>
        <Typography variant="h6" gutterBottom>
          Iterated Function System (IFS)
        </Typography>
        <Typography variant="body2" sx={{ mb: 2 }}>
          Barnsley ferns are generated using a probabilistic iterated function system with affine transformations:
        </Typography>
        <MathRenderer 
          math="\begin{pmatrix} x_{n+1} \\ y_{n+1} \end{pmatrix} = \begin{pmatrix} a & b \\ c & d \end{pmatrix} \begin{pmatrix} x_n \\ y_n \end{pmatrix} + \begin{pmatrix} e \\ f \end{pmatrix}" 
          block 
        />
        <Typography variant="body2" sx={{ mt: 2 }}>
          Each transformation is selected randomly based on probability <MathRenderer math="p_i" />, creating 
          the characteristic self-similar structure. The classic Barnsley fern uses four transformations 
          representing the stem, leaves, and smaller leaflets.
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
                backgroundColor: '#000'
              }}
            />
            <Typography variant="body2" sx={{ mt: 1, textAlign: 'center' }}>
              Points: {currentPoint + 1} / {points.length}
            </Typography>
          </Box>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Box className="controls-area">
            <Typography variant="h6" gutterBottom>
              Fern Parameters
            </Typography>

            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>Fern Type</InputLabel>
              <Select
                value={params.fernType}
                label="Fern Type"
                onChange={(e) => handleParamChange('fernType', e.target.value)}
              >
                <MenuItem value="barnsley">Barnsley Fern</MenuItem>
                <MenuItem value="thelypteridaceae">Thelypteridaceae</MenuItem>
                <MenuItem value="culcita">Culcita</MenuItem>
                <MenuItem value="fishbone">Fishbone Fern</MenuItem>
              </Select>
            </FormControl>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Number of Points: {params.numPoints.toLocaleString()}</Typography>
              <Slider
                value={params.numPoints}
                onChange={(_, value) => handleParamChange('numPoints', value as number)}
                min={5000}
                max={100000}
                step={5000}
                valueLabelDisplay="auto"
                valueLabelFormat={(value) => `${(value / 1000).toFixed(0)}k`}
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Animation Speed: {params.animationSpeed}</Typography>
              <Slider
                value={params.animationSpeed}
                onChange={(_, value) => handleParamChange('animationSpeed', value as number)}
                min={10}
                max={500}
                step={10}
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
                {isAnimating ? 'Pause' : 'Animate'} Growth
              </Button>

              <Button
                variant="outlined"
                onClick={showFullFern}
                fullWidth
              >
                Show Complete Fern
              </Button>

              <Button
                variant="outlined"
                onClick={resetFern}
                startIcon={<Refresh />}
                fullWidth
              >
                Reset
              </Button>
            </Box>

            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" gutterBottom>
                Current Fern
              </Typography>
              <Typography variant="body2">
                Type: <strong>{params.fernType.charAt(0).toUpperCase() + params.fernType.slice(1)}</strong>
              </Typography>
              <Typography variant="body2">
                Transforms: <strong>{FERN_TYPES[params.fernType].length}</strong>
              </Typography>
              <Typography variant="body2">
                Fractal Dimension: <strong>≈ 1.66</strong>
              </Typography>
            </Box>
          </Box>
        </Grid>
      </Grid>
    </div>
  );
};