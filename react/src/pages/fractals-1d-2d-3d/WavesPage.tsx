import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Typography, Grid, Slider, Button, Box, Paper, Switch, FormControlLabel } from '@mui/material';
import { MathRenderer } from '../../components/math/MathRenderer';
import { PlayArrow, Pause, Refresh } from '@mui/icons-material';

interface WaveParams {
  amplitude1: number;
  frequency1: number;
  amplitude2: number;
  frequency2: number;
  amplitude3: number;
  frequency3: number;
  tidalAmplitude: number;
  tidalPeriod: number;
  noiseLevel: number;
  timeScale: number;
  showComponents: boolean;
}

export const WavesPage: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const [isAnimating, setIsAnimating] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [params, setParams] = useState<WaveParams>({
    amplitude1: 1.0,
    frequency1: 2.0,
    amplitude2: 0.5,
    frequency2: 4.0,
    amplitude3: 0.25,
    frequency3: 8.0,
    tidalAmplitude: 2.0,
    tidalPeriod: 12.0,
    noiseLevel: 0.1,
    timeScale: 1.0,
    showComponents: true
  });

  const generateWaveform = useCallback((timeOffset: number = 0) => {
    const numSamples = 800;
    const timeSpan = 24; // 24 hours
    const dt = timeSpan / numSamples;
    
    const waveData = [];
    const components = {
      tidal: [] as number[],
      wave1: [] as number[],
      wave2: [] as number[],
      wave3: [] as number[],
      noise: [] as number[],
      composite: [] as number[]
    };

    for (let i = 0; i < numSamples; i++) {
      const t = i * dt + timeOffset;
      
      // Tidal component (long period)
      const tidal = params.tidalAmplitude * Math.sin(2 * Math.PI * t / params.tidalPeriod);
      
      // Wave components (shorter periods)
      const wave1 = params.amplitude1 * Math.sin(2 * Math.PI * params.frequency1 * t);
      const wave2 = params.amplitude2 * Math.sin(2 * Math.PI * params.frequency2 * t + Math.PI / 4);
      const wave3 = params.amplitude3 * Math.sin(2 * Math.PI * params.frequency3 * t + Math.PI / 2);
      
      // Noise component
      const noise = params.noiseLevel * (Math.random() - 0.5) * 2;
      
      // Composite signal
      const composite = tidal + wave1 + wave2 + wave3 + noise;
      
      components.tidal.push(tidal);
      components.wave1.push(wave1);
      components.wave2.push(wave2);
      components.wave3.push(wave3);
      components.noise.push(noise);
      components.composite.push(composite);
      
      waveData.push({
        time: t,
        tidal,
        wave1,
        wave2,
        wave3,
        noise,
        composite
      });
    }

    return { waveData, components };
  }, [params]);

  const drawWaves = useCallback(() => {
    if (!canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const { components } = generateWaveform(currentTime);
    
    const width = canvas.width;
    const height = canvas.height;
    const centerY = height / 2;
    
    // Find amplitude bounds
    const maxComposite = Math.max(...components.composite.map(Math.abs));
    const scale = (height / 2 - 20) / (maxComposite || 1);

    // Draw grid lines
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 0.5;
    
    // Horizontal grid
    for (let i = 0; i <= 10; i++) {
      const y = (height / 10) * i;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }
    
    // Vertical grid
    for (let i = 0; i <= 24; i++) {
      const x = (width / 24) * i;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }

    // Draw center line
    ctx.strokeStyle = '#666';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, centerY);
    ctx.lineTo(width, centerY);
    ctx.stroke();

    const drawComponent = (data: number[], color: string, lineWidth: number = 1) => {
      ctx.strokeStyle = color;
      ctx.lineWidth = lineWidth;
      ctx.beginPath();
      
      for (let i = 0; i < data.length; i++) {
        const x = (i / data.length) * width;
        const y = centerY - data[i] * scale;
        
        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      }
      ctx.stroke();
    };

    // Draw individual components if enabled
    if (params.showComponents) {
      drawComponent(components.tidal, '#00ffff', 2); // Cyan for tidal
      drawComponent(components.wave1, '#ff6b6b', 1); // Red for wave 1
      drawComponent(components.wave2, '#4ecdc4', 1); // Teal for wave 2
      drawComponent(components.wave3, '#45b7d1', 1); // Blue for wave 3
    }

    // Draw composite wave
    drawComponent(components.composite, '#ffffff', 2);

    // Draw time labels
    ctx.fillStyle = '#ccc';
    ctx.font = '12px Arial';
    for (let i = 0; i <= 24; i += 6) {
      const x = (width / 24) * i;
      ctx.fillText(`${i}h`, x + 2, height - 5);
    }

    // Draw current time indicator
    const currentTimeX = (currentTime % 24) / 24 * width;
    ctx.strokeStyle = '#ffff00';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(currentTimeX, 0);
    ctx.lineTo(currentTimeX, height);
    ctx.stroke();

  }, [generateWaveform, currentTime, params.showComponents]);

  const animate = useCallback(() => {
    setCurrentTime(prev => (prev + 0.1 * params.timeScale) % 24);
    if (isAnimating) {
      animationRef.current = requestAnimationFrame(animate);
    }
  }, [isAnimating, params.timeScale]);

  useEffect(() => {
    drawWaves();
  }, [drawWaves]);

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

  const handleParamChange = (key: keyof WaveParams, value: number | boolean) => {
    setParams(prev => ({ ...prev, [key]: value }));
  };

  const toggleAnimation = () => {
    setIsAnimating(!isAnimating);
  };

  const resetTime = () => {
    setCurrentTime(0);
  };

  return (
    <div className="page-container">
      <Typography variant="h3" component="h1" className="page-title">
        Wave Dynamics & Tidal Patterns
      </Typography>
      <Typography variant="body1" className="page-description">
        Explore the superposition of multiple wave components and tidal patterns.
      </Typography>

      <Paper sx={{ p: 3, mb: 3, backgroundColor: 'background.paper' }}>
        <Typography variant="h6" gutterBottom>
          Wave Superposition Mathematics
        </Typography>
        <Typography variant="body2" sx={{ mb: 2 }}>
          The composite wave signal is the linear superposition of multiple periodic components:
        </Typography>
        <MathRenderer 
          math="y(t) = A_{\text{tide}} \sin\left(\frac{2\pi t}{T_{\text{tide}}}\right) + \sum_{i=1}^{3} A_i \sin(2\pi f_i t + \phi_i) + \epsilon(t)" 
          block 
        />
        <Typography variant="body2" sx={{ mt: 2 }}>
          where <MathRenderer math="A_i" /> are amplitudes, <MathRenderer math="f_i" /> are frequencies, 
          <MathRenderer math="\phi_i" /> are phase shifts, and <MathRenderer math="\epsilon(t)" /> is noise.
        </Typography>
      </Paper>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <Box className="visualization-area">
            <canvas
              ref={canvasRef}
              width={800}
              height={400}
              style={{
                width: '100%',
                height: 'auto',
                border: '1px solid #333',
                borderRadius: '4px',
                backgroundColor: '#000'
              }}
            />
            <Box sx={{ mt: 2, display: 'flex', gap: 2, flexWrap: 'wrap', justifyContent: 'center' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box sx={{ width: 20, height: 2, backgroundColor: '#ffffff' }} />
                <Typography variant="body2">Composite</Typography>
              </Box>
              {params.showComponents && (
                <>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box sx={{ width: 20, height: 2, backgroundColor: '#00ffff' }} />
                    <Typography variant="body2">Tidal</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box sx={{ width: 20, height: 2, backgroundColor: '#ff6b6b' }} />
                    <Typography variant="body2">Wave 1</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box sx={{ width: 20, height: 2, backgroundColor: '#4ecdc4' }} />
                    <Typography variant="body2">Wave 2</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box sx={{ width: 20, height: 2, backgroundColor: '#45b7d1' }} />
                    <Typography variant="body2">Wave 3</Typography>
                  </Box>
                </>
              )}
            </Box>
            <Typography variant="body2" sx={{ mt: 1, textAlign: 'center' }}>
              Current Time: {currentTime.toFixed(1)} hours
            </Typography>
          </Box>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Box className="controls-area">
            <Typography variant="h6" gutterBottom>
              Wave Parameters
            </Typography>

            <FormControlLabel
              control={
                <Switch
                  checked={params.showComponents}
                  onChange={(e) => handleParamChange('showComponents', e.target.checked)}
                />
              }
              label="Show Individual Components"
              sx={{ mb: 2 }}
            />

            <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
              Tidal Component
            </Typography>
            
            <Box sx={{ mb: 2 }}>
              <Typography gutterBottom>Amplitude: {params.tidalAmplitude.toFixed(1)}</Typography>
              <Slider
                value={params.tidalAmplitude}
                onChange={(_, value) => handleParamChange('tidalAmplitude', value as number)}
                min={0}
                max={5}
                step={0.1}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Period: {params.tidalPeriod.toFixed(1)} hours</Typography>
              <Slider
                value={params.tidalPeriod}
                onChange={(_, value) => handleParamChange('tidalPeriod', value as number)}
                min={6}
                max={24}
                step={0.5}
                valueLabelDisplay="auto"
              />
            </Box>

            <Typography variant="subtitle1" gutterBottom>
              Wave Components
            </Typography>

            <Box sx={{ mb: 2 }}>
              <Typography gutterBottom>Wave 1 - Amp: {params.amplitude1.toFixed(2)}, Freq: {params.frequency1.toFixed(1)} Hz</Typography>
              <Slider
                value={params.amplitude1}
                onChange={(_, value) => handleParamChange('amplitude1', value as number)}
                min={0}
                max={2}
                step={0.05}
                valueLabelDisplay="auto"
              />
              <Slider
                value={params.frequency1}
                onChange={(_, value) => handleParamChange('frequency1', value as number)}
                min={0.5}
                max={10}
                step={0.1}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography gutterBottom>Wave 2 - Amp: {params.amplitude2.toFixed(2)}, Freq: {params.frequency2.toFixed(1)} Hz</Typography>
              <Slider
                value={params.amplitude2}
                onChange={(_, value) => handleParamChange('amplitude2', value as number)}
                min={0}
                max={2}
                step={0.05}
                valueLabelDisplay="auto"
              />
              <Slider
                value={params.frequency2}
                onChange={(_, value) => handleParamChange('frequency2', value as number)}
                min={0.5}
                max={10}
                step={0.1}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Wave 3 - Amp: {params.amplitude3.toFixed(2)}, Freq: {params.frequency3.toFixed(1)} Hz</Typography>
              <Slider
                value={params.amplitude3}
                onChange={(_, value) => handleParamChange('amplitude3', value as number)}
                min={0}
                max={2}
                step={0.05}
                valueLabelDisplay="auto"
              />
              <Slider
                value={params.frequency3}
                onChange={(_, value) => handleParamChange('frequency3', value as number)}
                min={0.5}
                max={10}
                step={0.1}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Noise Level: {params.noiseLevel.toFixed(2)}</Typography>
              <Slider
                value={params.noiseLevel}
                onChange={(_, value) => handleParamChange('noiseLevel', value as number)}
                min={0}
                max={0.5}
                step={0.01}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Time Scale: {params.timeScale.toFixed(1)}×</Typography>
              <Slider
                value={params.timeScale}
                onChange={(_, value) => handleParamChange('timeScale', value as number)}
                min={0.1}
                max={5}
                step={0.1}
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
                {isAnimating ? 'Pause' : 'Play'} Animation
              </Button>

              <Button
                variant="outlined"
                onClick={resetTime}
                startIcon={<Refresh />}
                fullWidth
              >
                Reset Time
              </Button>
            </Box>
          </Box>
        </Grid>
      </Grid>
    </div>
  );
};