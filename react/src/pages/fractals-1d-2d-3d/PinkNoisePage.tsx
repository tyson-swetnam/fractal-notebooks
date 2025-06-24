import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Typography, Grid, Slider, Button, Box, Paper, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import { MathRenderer } from '../../components/math/MathRenderer';
import { PlayArrow, Pause, Refresh } from '@mui/icons-material';

interface NoiseParams {
  numSamples: number;
  noiseType: 'white' | 'pink' | 'brown';
  showSpectrum: boolean;
  animationSpeed: number;
}

export const PinkNoisePage: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const spectrumCanvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<NodeJS.Timeout>();
  const [isAnimating, setIsAnimating] = useState(false);
  const [params, setParams] = useState<NoiseParams>({
    numSamples: 2048,
    noiseType: 'pink',
    showSpectrum: true,
    animationSpeed: 50
  });

  const [noiseData, setNoiseData] = useState<number[]>([]);
  const [spectrumData, setSpectrumData] = useState<number[]>([]);

  // Simple FFT implementation for spectral analysis
  const fft = useCallback((signal: number[]): { real: number[]; imag: number[] } => {
    const N = signal.length;
    if (N <= 1) return { real: [...signal], imag: new Array(N).fill(0) };

    // Bit-reverse permutation
    const real = new Array(N);
    const imag = new Array(N).fill(0);
    for (let i = 0; i < N; i++) {
      let j = 0;
      for (let k = 0; k < Math.log2(N); k++) {
        j = (j << 1) | ((i >> k) & 1);
      }
      real[j] = signal[i];
    }

    // Cooley-Tukey FFT
    for (let len = 2; len <= N; len *= 2) {
      const angle = -2 * Math.PI / len;
      const wlen_real = Math.cos(angle);
      const wlen_imag = Math.sin(angle);

      for (let i = 0; i < N; i += len) {
        let w_real = 1;
        let w_imag = 0;

        for (let j = 0; j < len / 2; j++) {
          const u_real = real[i + j];
          const u_imag = imag[i + j];
          const v_real = real[i + j + len / 2] * w_real - imag[i + j + len / 2] * w_imag;
          const v_imag = real[i + j + len / 2] * w_imag + imag[i + j + len / 2] * w_real;

          real[i + j] = u_real + v_real;
          imag[i + j] = u_imag + v_imag;
          real[i + j + len / 2] = u_real - v_real;
          imag[i + j + len / 2] = u_imag - v_imag;

          const next_w_real = w_real * wlen_real - w_imag * wlen_imag;
          const next_w_imag = w_real * wlen_imag + w_imag * wlen_real;
          w_real = next_w_real;
          w_imag = next_w_imag;
        }
      }
    }

    return { real, imag };
  }, []);

  const generateNoise = useCallback(() => {
    const N = params.numSamples;
    let signal: number[];

    switch (params.noiseType) {
      case 'white':
        signal = Array.from({ length: N }, () => (Math.random() - 0.5) * 2);
        break;

      case 'pink':
        // Generate white noise
        const white = Array.from({ length: N }, () => (Math.random() - 0.5) * 2);
        
        // Apply 1/f filter in frequency domain
        const { real, imag } = fft(white);
        
        for (let i = 1; i < N / 2; i++) {
          const freq = i;
          const factor = 1 / Math.sqrt(freq);
          real[i] *= factor;
          imag[i] *= factor;
          real[N - i] *= factor;
          imag[N - i] *= factor;
        }

        // Inverse FFT (simplified)
        signal = real.map((r, i) => r + imag[i]);
        break;

      case 'brown':
        // Brownian noise (integrated white noise)
        const brownian = [0];
        for (let i = 1; i < N; i++) {
          brownian[i] = brownian[i - 1] + (Math.random() - 0.5) * 0.1;
        }
        signal = brownian;
        break;

      default:
        signal = Array.from({ length: N }, () => 0);
    }

    setNoiseData(signal);

    // Calculate power spectrum
    if (params.showSpectrum) {
      const { real, imag } = fft(signal);
      const spectrum = real.slice(0, N / 2).map((r, i) => 
        Math.sqrt(r * r + imag[i] * imag[i])
      );
      setSpectrumData(spectrum);
    }
  }, [params.numSamples, params.noiseType, params.showSpectrum, fft]);

  const drawSignal = useCallback(() => {
    if (!canvasRef.current || noiseData.length === 0) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const width = canvas.width;
    const height = canvas.height;
    const centerY = height / 2;

    // Find signal bounds
    const maxVal = Math.max(...noiseData.map(Math.abs));
    const scale = (height / 2 - 20) / (maxVal || 1);

    // Draw signal
    ctx.strokeStyle = getNoiseColor(params.noiseType);
    ctx.lineWidth = 1;
    ctx.beginPath();

    for (let i = 0; i < noiseData.length; i++) {
      const x = (i / noiseData.length) * width;
      const y = centerY - noiseData[i] * scale;

      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    }
    ctx.stroke();

    // Draw center line
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, centerY);
    ctx.lineTo(width, centerY);
    ctx.stroke();
  }, [noiseData, params.noiseType]);

  const drawSpectrum = useCallback(() => {
    if (!spectrumCanvasRef.current || spectrumData.length === 0 || !params.showSpectrum) return;

    const canvas = spectrumCanvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const width = canvas.width;
    const height = canvas.height;

    // Log scale for frequency and amplitude
    const logData = spectrumData.map((val, i) => ({
      freq: Math.log10(i + 1),
      amp: Math.log10(val + 1e-10)
    }));

    const maxLogFreq = Math.log10(spectrumData.length);
    const maxLogAmp = Math.max(...logData.map(d => d.amp));
    const minLogAmp = Math.min(...logData.map(d => d.amp));

    // Draw spectrum
    ctx.fillStyle = getNoiseColor(params.noiseType);
    for (let i = 1; i < logData.length; i++) {
      const x = (logData[i].freq / maxLogFreq) * width;
      const barHeight = ((logData[i].amp - minLogAmp) / (maxLogAmp - minLogAmp)) * height;
      const y = height - barHeight;

      ctx.fillRect(x - 1, y, 2, barHeight);
    }

    // Draw theoretical slopes
    ctx.strokeStyle = '#666';
    ctx.lineWidth = 1;
    ctx.setLineDash([5, 5]);

    // White noise (flat)
    if (params.noiseType === 'white') {
      const y = height * 0.5;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // Pink noise (-1 slope)
    if (params.noiseType === 'pink') {
      ctx.beginPath();
      ctx.moveTo(width * 0.1, height * 0.2);
      ctx.lineTo(width * 0.9, height * 0.8);
      ctx.stroke();
    }

    ctx.setLineDash([]);
  }, [spectrumData, params.showSpectrum, params.noiseType]);

  const getNoiseColor = (type: string) => {
    switch (type) {
      case 'white': return '#ffffff';
      case 'pink': return '#ff69b4';
      case 'brown': return '#8b4513';
      default: return '#007acc';
    }
  };

  const animate = useCallback(() => {
    generateNoise();
    if (isAnimating) {
      animationRef.current = setTimeout(() => {
        animate();
      }, 101 - params.animationSpeed);
    }
  }, [generateNoise, isAnimating, params.animationSpeed]);

  useEffect(() => {
    drawSignal();
  }, [drawSignal]);

  useEffect(() => {
    drawSpectrum();
  }, [drawSpectrum]);

  useEffect(() => {
    generateNoise();
  }, [generateNoise]);

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

  const handleParamChange = (key: keyof NoiseParams, value: number | string | boolean) => {
    setParams(prev => ({ ...prev, [key]: value }));
  };

  const toggleAnimation = () => {
    setIsAnimating(!isAnimating);
  };

  return (
    <div className="page-container">
      <Typography variant="h3" component="h1" className="page-title">
        Noise Patterns & Fractals
      </Typography>
      <Typography variant="body1" className="page-description">
        Explore different types of noise and their fractal properties through spectral analysis.
      </Typography>

      <Paper sx={{ p: 3, mb: 3, backgroundColor: 'background.paper' }}>
        <Typography variant="h6" gutterBottom>
          Noise Types & Fractal Dimensions
        </Typography>
        <Typography variant="body2" sx={{ mb: 2 }}>
          Different noise types have characteristic power spectral densities and fractal dimensions:
        </Typography>
        <Box component="ul" sx={{ pl: 3, mb: 2 }}>
          <Typography component="li" variant="body2">
            <strong>White Noise</strong>: <MathRenderer math="S(f) = \text{constant}" /> (D ≈ 1.5)
          </Typography>
          <Typography component="li" variant="body2">
            <strong>Pink Noise</strong>: <MathRenderer math="S(f) \propto 1/f" /> (D ≈ 1.0)
          </Typography>
          <Typography component="li" variant="body2">
            <strong>Brown Noise</strong>: <MathRenderer math="S(f) \propto 1/f^2" /> (D ≈ 0.5)
          </Typography>
        </Box>
        <Typography variant="body2">
          The fractal dimension relates to the spectral exponent: <MathRenderer math="D = (5 - \beta)/2" /> where <MathRenderer math="S(f) \propto 1/f^\beta" />.
        </Typography>
      </Paper>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <Box className="visualization-area">
            <Typography variant="h6" gutterBottom>
              Time Domain Signal
            </Typography>
            <canvas
              ref={canvasRef}
              width={800}
              height={300}
              style={{
                width: '100%',
                height: 'auto',
                border: '1px solid #333',
                borderRadius: '4px',
                backgroundColor: '#000',
                marginBottom: '20px'
              }}
            />

            {params.showSpectrum && (
              <>
                <Typography variant="h6" gutterBottom>
                  Power Spectrum (Log-Log Scale)
                </Typography>
                <canvas
                  ref={spectrumCanvasRef}
                  width={800}
                  height={300}
                  style={{
                    width: '100%',
                    height: 'auto',
                    border: '1px solid #333',
                    borderRadius: '4px',
                    backgroundColor: '#000'
                  }}
                />
              </>
            )}
          </Box>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Box className="controls-area">
            <Typography variant="h6" gutterBottom>
              Noise Parameters
            </Typography>

            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>Noise Type</InputLabel>
              <Select
                value={params.noiseType}
                label="Noise Type"
                onChange={(e) => handleParamChange('noiseType', e.target.value)}
              >
                <MenuItem value="white">White Noise</MenuItem>
                <MenuItem value="pink">Pink Noise (1/f)</MenuItem>
                <MenuItem value="brown">Brown Noise (1/f²)</MenuItem>
              </Select>
            </FormControl>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Samples: {params.numSamples}</Typography>
              <Slider
                value={params.numSamples}
                onChange={(_, value) => handleParamChange('numSamples', value as number)}
                min={512}
                max={4096}
                step={256}
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

            <Box sx={{ display: 'flex', gap: 1, flexDirection: 'column' }}>
              <Button
                variant="contained"
                onClick={toggleAnimation}
                startIcon={isAnimating ? <Pause /> : <PlayArrow />}
                fullWidth
                sx={{ backgroundColor: getNoiseColor(params.noiseType) }}
              >
                {isAnimating ? 'Pause' : 'Play'} Animation
              </Button>

              <Button
                variant="outlined"
                onClick={generateNoise}
                startIcon={<Refresh />}
                fullWidth
              >
                Generate New Sample
              </Button>
            </Box>

            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" gutterBottom>
                Current Properties
              </Typography>
              <Typography variant="body2">
                Type: <strong>{params.noiseType.charAt(0).toUpperCase() + params.noiseType.slice(1)} Noise</strong>
              </Typography>
              <Typography variant="body2">
                Theoretical Fractal Dimension: <strong>
                  {params.noiseType === 'white' ? '1.5' : 
                   params.noiseType === 'pink' ? '1.0' : '0.5'}
                </strong>
              </Typography>
            </Box>
          </Box>
        </Grid>
      </Grid>
    </div>
  );
};