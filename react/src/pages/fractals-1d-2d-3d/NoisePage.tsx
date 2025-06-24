import React, { useState, useEffect, useCallback, useRef } from 'react';
import { 
  Typography, 
  Grid, 
  Box, 
  Paper, 
  Tabs, 
  Tab, 
  Button,
  Slider,
  FormControlLabel,
  Switch
} from '@mui/material';
import Plot from 'react-plotly.js';
import { MathRenderer } from '../../components/math/MathRenderer';
import { 
  generateBrownianMotion, 
  generatePinkNoise, 
  generateWhiteNoise,
  generateRedNoise,
  computePowerSpectralDensity, 
  estimateFractalDimension1D,
  NoiseSignal,
  PowerSpectralDensity 
} from '../../utils/noise';
import { PlayArrow, Pause, Refresh, Stop } from '@mui/icons-material';

interface NoiseParams {
  numSamples: number;
  scale: number;
  showPSD: boolean;
  showFractalDim: boolean;
  animationSpeed: number;
  frameCount: number;
}

interface AnimationFrame {
  timeData: number[];
  psdData: PowerSpectralDensity | null;
  fractalDim: number;
  currentSample: number;
}

export const NoisePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [params, setParams] = useState<NoiseParams>({
    numSamples: 2048,
    scale: 1.0,
    showPSD: true,
    showFractalDim: true,
    animationSpeed: 50,
    frameCount: 100
  });
  
  // Static data for full signals
  const [noiseData, setNoiseData] = useState<{
    brownian: NoiseSignal | null;
    pink: NoiseSignal | null;
    white: NoiseSignal | null;
    red: NoiseSignal | null;
  }>({
    brownian: null,
    pink: null,
    white: null,
    red: null
  });
  
  const [noisePSD, setNoisePSD] = useState<{
    brownian: PowerSpectralDensity | null;
    pink: PowerSpectralDensity | null;
    white: PowerSpectralDensity | null;
    red: PowerSpectralDensity | null;
  }>({
    brownian: null,
    pink: null,
    white: null,
    red: null
  });
  
  const [fractalDimensions, setFractalDimensions] = useState<{
    brownian: number;
    pink: number;
    white: number;
    red: number;
  }>({
    brownian: 0,
    pink: 0,
    white: 0,
    red: 0
  });

  // Animation state
  const [isAnimating, setIsAnimating] = useState(false);
  const [currentFrame, setCurrentFrame] = useState(0);
  const [animationFrames, setAnimationFrames] = useState<{
    brownian: AnimationFrame[];
    pink: AnimationFrame[];
    white: AnimationFrame[];
    red: AnimationFrame[];
  }>({
    brownian: [],
    pink: [],
    white: [],
    red: []
  });
  const animationRef = useRef<number>();
  const lastFrameTime = useRef<number>(0);

  const generateData = useCallback(() => {
    try {
      const brownian = generateBrownianMotion(params.numSamples, params.scale);
      const pink = generatePinkNoise(params.numSamples);
      const white = generateWhiteNoise(params.numSamples, params.scale);
      const red = generateRedNoise(params.numSamples, params.scale);
      
      setNoiseData({
        brownian,
        pink,
        white,
        red
      });
      
      if (params.showPSD) {
        setNoisePSD({
          brownian: computePowerSpectralDensity(brownian),
          pink: computePowerSpectralDensity(pink),
          white: computePowerSpectralDensity(white),
          red: computePowerSpectralDensity(red)
        });
      }
      
      if (params.showFractalDim) {
        setFractalDimensions({
          brownian: estimateFractalDimension1D(brownian.values),
          pink: estimateFractalDimension1D(pink.values),
          white: estimateFractalDimension1D(white.values),
          red: estimateFractalDimension1D(red.values)
        });
      }

      // Generate animation frames
      generateAnimationFrames(brownian, pink, white, red);
    } catch (error) {
      console.error('Error generating noise data:', error);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params]);

  const generateAnimationFrames = useCallback((brownian: NoiseSignal, pink: NoiseSignal, white: NoiseSignal, red: NoiseSignal) => {
    const frameCount = params.frameCount;
    const stepSize = Math.max(1, Math.floor(params.numSamples / frameCount));
    
    const brownianFrames: AnimationFrame[] = [];
    const pinkFrames: AnimationFrame[] = [];
    const whiteFrames: AnimationFrame[] = [];
    const redFrames: AnimationFrame[] = [];

    for (let i = 1; i <= frameCount; i++) {
      const currentSample = Math.min(i * stepSize, params.numSamples);
      
      // Helper function to create frames for each noise type
      const createFrame = (noiseSignal: NoiseSignal): AnimationFrame => {
        const segment = noiseSignal.values.slice(0, currentSample);
        const signal: NoiseSignal = { values: segment, samplingRate: 1.0 };
        
        return {
          timeData: segment,
          psdData: params.showPSD && segment.length > 10 ? 
            computePowerSpectralDensity(signal, Math.min(64, Math.floor(currentSample / 4))) : null,
          fractalDim: params.showFractalDim && segment.length > 4 ? 
            estimateFractalDimension1D(segment) : 1.0,
          currentSample
        };
      };

      brownianFrames.push(createFrame(brownian));
      pinkFrames.push(createFrame(pink));
      whiteFrames.push(createFrame(white));
      redFrames.push(createFrame(red));
    }

    setAnimationFrames({ 
      brownian: brownianFrames, 
      pink: pinkFrames, 
      white: whiteFrames, 
      red: redFrames 
    });
  }, [params.frameCount, params.numSamples, params.showPSD, params.showFractalDim]);

  const startAnimation = useCallback(() => {
    if (animationFrames.brownian.length === 0) return;
    
    setIsAnimating(true);
    setCurrentFrame(0);
    lastFrameTime.current = performance.now();

    const animate = (currentTime: number) => {
      if (currentTime - lastFrameTime.current >= params.animationSpeed) {
        setCurrentFrame(prev => {
          const nextFrame = prev + 1;
          if (nextFrame >= params.frameCount) {
            setIsAnimating(false);
            return 0;
          }
          return nextFrame;
        });
        lastFrameTime.current = currentTime;
      }
      
      if (isAnimating) {
        animationRef.current = requestAnimationFrame(animate);
      }
    };

    animationRef.current = requestAnimationFrame(animate);
  }, [animationFrames, params.animationSpeed, params.frameCount, isAnimating]);

  const stopAnimation = useCallback(() => {
    setIsAnimating(false);
    setCurrentFrame(0);
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
  }, []);

  const pauseAnimation = useCallback(() => {
    setIsAnimating(false);
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
  }, []);

  useEffect(() => {
    generateData();
  }, [generateData]);

  useEffect(() => {
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (isAnimating) {
      startAnimation();
    }
  }, [isAnimating, startAnimation]);

  const handleParamChange = (key: keyof NoiseParams, value: number | boolean) => {
    setParams(prev => ({ ...prev, [key]: value }));
  };

  // Get current data based on animation state
  const getCurrentData = () => {
    const noiseTypes = ['brownian', 'pink', 'white', 'red'] as const;
    const noiseType = noiseTypes[activeTab];
    
    if (isAnimating && animationFrames[noiseType].length > 0) {
      const frame = animationFrames[noiseType][currentFrame] || animationFrames[noiseType][0];
      return {
        values: frame.timeData,
        samplingRate: 1.0,
        psd: frame.psdData,
        fractalDim: frame.fractalDim,
        currentSample: frame.currentSample
      };
    } else {
      const data = noiseData[noiseType];
      const psd = noisePSD[noiseType];
      const fractalDim = fractalDimensions[noiseType];
      return {
        values: data?.values || [],
        samplingRate: data?.samplingRate || 1.0,
        psd,
        fractalDim,
        currentSample: data?.values.length || 0
      };
    }
  };

  const currentData = getCurrentData();
  const noiseTypeNames = ['Brownian Motion', 'Pink Noise', 'White Noise', 'Red Noise'];
  const noiseType = noiseTypeNames[activeTab];

  return (
    <div className="page-container">
      <Typography variant="h3" component="h1" className="page-title">
        Noise Patterns & Power Spectral Density
      </Typography>
      <Typography variant="body1" className="page-description">
        Explore white, pink, red noise and Brownian motion with their power spectral density analysis and fractal properties.
      </Typography>

      <Paper sx={{ p: 3, mb: 3, backgroundColor: 'background.paper' }}>
        <Typography variant="h6" gutterBottom>
          Mathematical Background
        </Typography>
        <Typography variant="body2" sx={{ mb: 2 }}>
          <strong>White Noise:</strong> Random signal with equal power at all frequencies: 
          <MathRenderer math="S(f) = \text{constant}" />
          where <MathRenderer math="\epsilon_i \sim \mathcal{N}(0,1)" />
        </Typography>
        <Typography variant="body2" sx={{ mb: 2 }}>
          <strong>Pink Noise:</strong> 1/f noise with power spectral density: 
          <MathRenderer math="S(f) \propto \frac{1}{f}" />
        </Typography>
        <Typography variant="body2" sx={{ mb: 2 }}>
          <strong>Brownian Motion:</strong> Generated by cumulative sum of white noise: 
          <MathRenderer math="B(t) = \sum_{i=1}^{t} \epsilon_i" />
        </Typography>
        <Typography variant="body2" sx={{ mb: 2 }}>
          <strong>Red Noise:</strong> Brownian noise with power spectral density: 
          <MathRenderer math="S(f) \propto \frac{1}{f^2}" />
        </Typography>
        <Typography variant="body2">
          <strong>Power Spectral Density:</strong> Shows how signal power is distributed across frequencies using Welch's method.
        </Typography>
      </Paper>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <Paper sx={{ p: 2 }}>
            <Tabs 
              value={activeTab} 
              onChange={(_, newValue) => setActiveTab(newValue)}
              sx={{ mb: 2 }}
              variant="fullWidth"
            >
              <Tab label="Brownian Motion" />
              <Tab label="Pink Noise" />
              <Tab label="White Noise" />
              <Tab label="Red Noise" />
            </Tabs>

            {currentData.values.length > 0 && (
              <Box sx={{ height: '400px', mb: 3 }}>
                <Plot
                  data={[
                    {
                      x: Array.from({ length: currentData.values.length }, (_, i) => i),
                      y: currentData.values,
                      type: 'scatter',
                      mode: 'lines',
                      line: { 
                        color: ['#1976d2', '#d32f2f', '#4caf50', '#ff9800'][activeTab], 
                        width: 1 
                      },
                      name: `${noiseType} Signal`
                    } as any
                  ]}
                  layout={{
                    title: { 
                      text: `${noiseType} Time Series${isAnimating ? ` (Sample ${currentData.currentSample}/${params.numSamples})` : ''}` 
                    },
                    xaxis: { 
                      title: { text: 'Sample' },
                      range: [0, params.numSamples] // Fixed range for animation
                    },
                    yaxis: { title: { text: 'Amplitude' } },
                    margin: { l: 50, r: 50, t: 50, b: 50 },
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    font: { color: '#fff' }
                  }}
                  style={{ width: '100%', height: '100%' }}
                  config={{ displayModeBar: false }}
                />
              </Box>
            )}

            {params.showPSD && currentData.psd && (
              <Box sx={{ height: '400px' }}>
                <Plot
                  data={[
                    {
                      x: currentData.psd.frequencies,
                      y: currentData.psd.power,
                      type: 'scatter',
                      mode: 'lines',
                      line: { 
                        color: ['#1976d2', '#d32f2f', '#4caf50', '#ff9800'][activeTab], 
                        width: 2 
                      },
                      name: `${noiseType} PSD`
                    } as any
                  ]}
                  layout={{
                    title: { text: `${noiseType} Power Spectral Density` },
                    xaxis: { 
                      title: { text: 'Frequency' }, 
                      type: 'log'
                    },
                    yaxis: { 
                      title: { text: 'Power' }, 
                      type: 'log'
                    },
                    margin: { l: 50, r: 50, t: 50, b: 50 },
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    font: { color: '#fff' }
                  }}
                  style={{ width: '100%', height: '100%' }}
                  config={{ displayModeBar: false }}
                />
              </Box>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Noise Parameters
            </Typography>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Samples: {params.numSamples}</Typography>
              <Slider
                value={params.numSamples}
                onChange={(_, value) => handleParamChange('numSamples', value as number)}
                min={512}
                max={8192}
                step={256}
                valueLabelDisplay="auto"
                disabled={isAnimating}
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Scale: {params.scale.toFixed(1)}</Typography>
              <Slider
                value={params.scale}
                onChange={(_, value) => handleParamChange('scale', value as number)}
                min={0.1}
                max={3.0}
                step={0.1}
                valueLabelDisplay="auto"
                disabled={isAnimating}
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Animation Speed (ms): {params.animationSpeed}</Typography>
              <Slider
                value={params.animationSpeed}
                onChange={(_, value) => handleParamChange('animationSpeed', value as number)}
                min={10}
                max={200}
                step={10}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Animation Frames: {params.frameCount}</Typography>
              <Slider
                value={params.frameCount}
                onChange={(_, value) => handleParamChange('frameCount', value as number)}
                min={50}
                max={200}
                step={10}
                valueLabelDisplay="auto"
                disabled={isAnimating}
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={params.showPSD}
                    onChange={(e) => handleParamChange('showPSD', e.target.checked)}
                  />
                }
                label="Show Power Spectral Density"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={params.showFractalDim}
                    onChange={(e) => handleParamChange('showFractalDim', e.target.checked)}
                  />
                }
                label="Show Fractal Dimension"
              />
            </Box>

            {params.showFractalDim && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Fractal Analysis
                </Typography>
                <Typography variant="body2">
                  <strong>{noiseType} D:</strong> {currentData.fractalDim.toFixed(3)}
                </Typography>
                {!isAnimating && (
                  <>
                    <Typography variant="body2">
                      <strong>Brownian Motion D:</strong> {fractalDimensions.brownian.toFixed(3)}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Pink Noise D:</strong> {fractalDimensions.pink.toFixed(3)}
                    </Typography>
                    <Typography variant="body2">
                      <strong>White Noise D:</strong> {fractalDimensions.white.toFixed(3)}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Red Noise D:</strong> {fractalDimensions.red.toFixed(3)}
                    </Typography>
                  </>
                )}
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Expected: ~1.0 for white, ~1.2-1.5 for pink, ~1.5 for Brownian, ~1.7-2.0 for red noise
                </Typography>
              </Box>
            )}

            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              {!isAnimating ? (
                <Button
                  variant="contained"
                  onClick={startAnimation}
                  startIcon={<PlayArrow />}
                  fullWidth
                  disabled={animationFrames.brownian.length === 0}
                >
                  Start Animation
                </Button>
              ) : (
                <>
                  <Button
                    variant="contained"
                    onClick={pauseAnimation}
                    startIcon={<Pause />}
                    sx={{ flex: 1 }}
                  >
                    Pause
                  </Button>
                  <Button
                    variant="outlined"
                    onClick={stopAnimation}
                    startIcon={<Stop />}
                    sx={{ flex: 1 }}
                  >
                    Stop
                  </Button>
                </>
              )}
            </Box>

            <Button
              variant="outlined"
              onClick={generateData}
              startIcon={<Refresh />}
              fullWidth
              disabled={isAnimating}
              sx={{ mt: 1 }}
            >
              Generate New Data
            </Button>
          </Paper>
        </Grid>
      </Grid>
    </div>
  );
};