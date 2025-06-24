import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Typography, Grid, Slider, Button, Box, Paper } from '@mui/material';
import { MathRenderer } from '../../components/math/MathRenderer';
import { PlayArrow, Pause, Refresh } from '@mui/icons-material';

interface BrownianParams {
  numSteps: number;
  stepSize: number;
  animationSpeed: number;
  showFractalDimension: boolean;
}

export const BrownianMotionPage: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<NodeJS.Timeout>();
  const [isAnimating, setIsAnimating] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [fractalDimension, setFractalDimension] = useState<number>(0);
  const [params, setParams] = useState<BrownianParams>({
    numSteps: 2048,
    stepSize: 1.0,
    animationSpeed: 50,
    showFractalDimension: true
  });

  const [path, setPath] = useState<{ x: number; y: number }[]>([]);

  const generateRandomWalk = useCallback(() => {
    const newPath: { x: number; y: number }[] = [];
    let x = 0;
    let y = 0;
    
    newPath.push({ x: 0, y: 0 });
    
    for (let i = 1; i < params.numSteps; i++) {
      const angle = Math.random() * 2 * Math.PI;
      x += Math.cos(angle) * params.stepSize;
      y += Math.sin(angle) * params.stepSize;
      newPath.push({ x, y });
    }
    
    setPath(newPath);
    setCurrentStep(0);
  }, [params.numSteps, params.stepSize]);

  const calculateFractalDimension = useCallback((pathData: { x: number; y: number }[]) => {
    if (pathData.length < 10) return 0;
    
    // Box-counting method for fractal dimension
    const scales = [1, 2, 4, 8, 16, 32];
    const counts: number[] = [];
    
    scales.forEach(scale => {
      const boxes = new Set<string>();
      pathData.forEach(point => {
        const boxX = Math.floor(point.x / scale);
        const boxY = Math.floor(point.y / scale);
        boxes.add(`${boxX},${boxY}`);
      });
      counts.push(boxes.size);
    });
    
    // Linear regression on log-log plot
    const logScales = scales.map(s => Math.log(1/s));
    const logCounts = counts.map(c => Math.log(c));
    
    const n = logScales.length;
    const sumX = logScales.reduce((a, b) => a + b, 0);
    const sumY = logCounts.reduce((a, b) => a + b, 0);
    const sumXY = logScales.reduce((sum, x, i) => sum + x * logCounts[i], 0);
    const sumXX = logScales.reduce((sum, x) => sum + x * x, 0);
    
    const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
    return Math.abs(slope);
  }, []);

  const drawPath = useCallback(() => {
    if (!canvasRef.current || path.length === 0) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Find bounds
    const minX = Math.min(...path.map(p => p.x));
    const maxX = Math.max(...path.map(p => p.x));
    const minY = Math.min(...path.map(p => p.y));
    const maxY = Math.max(...path.map(p => p.y));
    
    const margin = 50;
    const scaleX = (canvas.width - 2 * margin) / (maxX - minX || 1);
    const scaleY = (canvas.height - 2 * margin) / (maxY - minY || 1);
    const scale = Math.min(scaleX, scaleY);
    
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    
    ctx.strokeStyle = '#007acc';
    ctx.lineWidth = 1;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    
    ctx.beginPath();
    const visibleSteps = Math.min(currentStep, path.length - 1);
    
    for (let i = 0; i <= visibleSteps; i++) {
      const point = path[i];
      const x = centerX + (point.x - (minX + maxX) / 2) * scale;
      const y = centerY + (point.y - (minY + maxY) / 2) * scale;
      
      if (i === 0) {
        ctx.moveTo(x, y);
        // Mark starting point
        ctx.fillStyle = '#00ff00';
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, 2 * Math.PI);
        ctx.fill();
        ctx.beginPath();
        ctx.strokeStyle = '#007acc';
      } else {
        ctx.lineTo(x, y);
      }
    }
    ctx.stroke();
    
    // Mark current position
    if (visibleSteps > 0 && visibleSteps < path.length) {
      const current = path[visibleSteps];
      const x = centerX + (current.x - (minX + maxX) / 2) * scale;
      const y = centerY + (current.y - (minY + maxY) / 2) * scale;
      ctx.fillStyle = '#ff0000';
      ctx.beginPath();
      ctx.arc(x, y, 3, 0, 2 * Math.PI);
      ctx.fill();
    }
  }, [path, currentStep]);

  const animate = useCallback(() => {
    if (currentStep < path.length - 1) {
      setCurrentStep(prev => prev + 1);
      animationRef.current = setTimeout(() => {
        animate();
      }, 101 - params.animationSpeed);
    } else {
      setIsAnimating(false);
    }
  }, [currentStep, path.length, params.animationSpeed]);

  useEffect(() => {
    drawPath();
  }, [drawPath]);

  useEffect(() => {
    if (path.length > 100 && params.showFractalDimension) {
      const dim = calculateFractalDimension(path.slice(0, currentStep + 1));
      setFractalDimension(dim);
    }
  }, [path, currentStep, params.showFractalDimension, calculateFractalDimension]);

  useEffect(() => {
    generateRandomWalk();
  }, [generateRandomWalk]);

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

  const handleParamChange = (key: keyof BrownianParams, value: number | boolean) => {
    setParams(prev => ({ ...prev, [key]: value }));
  };

  const toggleAnimation = () => {
    if (isAnimating) {
      setIsAnimating(false);
      if (animationRef.current) {
        clearTimeout(animationRef.current);
      }
    } else {
      setIsAnimating(true);
    }
  };

  const resetWalk = () => {
    setIsAnimating(false);
    if (animationRef.current) {
      clearTimeout(animationRef.current);
    }
    setCurrentStep(0);
    generateRandomWalk();
  };

  return (
    <div className="page-container">
      <Typography variant="h3" component="h1" className="page-title">
        Brownian Motion
      </Typography>
      <Typography variant="body1" className="page-description">
        Visualize the random walk of Brownian motion and explore its fractal properties.
      </Typography>

      <Paper sx={{ p: 3, mb: 3, backgroundColor: 'background.paper' }}>
        <Typography variant="h6" gutterBottom>
          Mathematical Definition
        </Typography>
        <Typography variant="body2" sx={{ mb: 2 }}>
          Brownian motion is a continuous-time stochastic process representing random motion. 
          In discrete form, it's a random walk where each step is:
        </Typography>
        <MathRenderer math="X_n = X_{n-1} + \epsilon_n" block />
        <Typography variant="body2" sx={{ mt: 2 }}>
          where <MathRenderer math="\epsilon_n" /> is a random step with uniform angular distribution. 
          The fractal dimension D is typically around 1.5 for 2D Brownian motion.
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
                maxWidth: '100%',
                height: 'auto',
                border: '1px solid #333',
                borderRadius: '4px',
                backgroundColor: '#000'
              }}
            />
          </Box>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Box className="controls-area">
            <Typography variant="h6" gutterBottom>
              Brownian Motion Controls
            </Typography>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Steps: {params.numSteps}</Typography>
              <Slider
                value={params.numSteps}
                onChange={(_, value) => handleParamChange('numSteps', value as number)}
                min={100}
                max={5000}
                step={100}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Step Size: {params.stepSize.toFixed(1)}</Typography>
              <Slider
                value={params.stepSize}
                onChange={(_, value) => handleParamChange('stepSize', value as number)}
                min={0.1}
                max={5.0}
                step={0.1}
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

            {params.showFractalDimension && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Fractal Analysis
                </Typography>
                <Typography variant="body2">
                  Current Dimension: <strong>{fractalDimension.toFixed(3)}</strong>
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Steps: {currentStep + 1} / {path.length}
                </Typography>
              </Box>
            )}

            <Box sx={{ display: 'flex', gap: 1, flexDirection: 'column' }}>
              <Button
                variant="contained"
                onClick={toggleAnimation}
                startIcon={isAnimating ? <Pause /> : <PlayArrow />}
                fullWidth
              >
                {isAnimating ? 'Pause' : 'Play'} Animation
              </Button>

              <Button
                variant="outlined"
                onClick={resetWalk}
                startIcon={<Refresh />}
                fullWidth
              >
                New Random Walk
              </Button>
            </Box>
          </Box>
        </Grid>
      </Grid>
    </div>
  );
};