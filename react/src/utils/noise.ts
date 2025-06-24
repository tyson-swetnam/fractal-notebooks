export interface NoiseSignal {
  values: number[];
  samplingRate: number;
}

export interface PowerSpectralDensity {
  frequencies: number[];
  power: number[];
}

export function generateBrownianMotion(numSamples: number, scale: number = 1.0): NoiseSignal {
  if (numSamples <= 0) {
    throw new Error('Number of samples must be positive');
  }
  
  // Use Box-Muller transform for better Gaussian noise
  const whiteNoise = generateGaussianNoise(numSamples, scale);
  const brownian = new Array(numSamples);
  
  brownian[0] = whiteNoise[0];
  for (let i = 1; i < numSamples; i++) {
    brownian[i] = brownian[i - 1] + whiteNoise[i];
  }
  
  // Normalize only if we have valid data
  if (numSamples === 1) {
    return { values: [0], samplingRate: 1.0 };
  }
  
  const mean = brownian.reduce((sum, val) => sum + val, 0) / numSamples;
  const variance = brownian.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / numSamples;
  const std = Math.sqrt(Math.max(variance, 1e-10)); // Avoid division by zero
  
  const normalized = brownian.map(val => (val - mean) / std);
  
  return {
    values: normalized,
    samplingRate: 1.0
  };
}

export function generatePinkNoise(numSamples: number): NoiseSignal {
  if (numSamples <= 0) {
    throw new Error('Number of samples must be positive');
  }
  
  if (numSamples === 1) {
    return { values: [0], samplingRate: 1.0 };
  }
  
  // Ensure power of 2 for FFT efficiency
  const fftSize = Math.pow(2, Math.ceil(Math.log2(numSamples)));
  
  // Generate Gaussian white noise
  const whiteNoise = generateGaussianNoise(fftSize, 1.0);
  
  try {
    // Apply FFT-based 1/f filtering
    const fft = computeFFT(whiteNoise);
    const nyquist = Math.floor(fftSize / 2);
    
    // Apply 1/sqrt(f) filter, avoiding f=0
    for (let i = 1; i <= nyquist; i++) {
      const freq = i / fftSize;
      const factor = 1 / Math.sqrt(freq);
      
      // Apply filter to positive frequencies
      fft.real[i] *= factor;
      fft.imag[i] *= factor;
      
      // Apply to negative frequencies (mirror)
      if (i > 0 && i < nyquist) {
        const negIndex = fftSize - i;
        fft.real[negIndex] *= factor;
        fft.imag[negIndex] *= factor;
      }
    }
    
    // Handle DC and Nyquist components
    fft.real[0] = 0; // Remove DC component
    if (nyquist < fftSize) {
      fft.real[nyquist] *= 0.1; // Reduce Nyquist component
      fft.imag[nyquist] = 0;
    }
    
    const pinkNoise = computeIFFT(fft, fftSize);
    
    // Take only the requested number of samples
    const trimmed = pinkNoise.slice(0, numSamples);
    
    // Normalize safely
    const mean = trimmed.reduce((sum, val) => sum + val, 0) / numSamples;
    const variance = trimmed.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / numSamples;
    const std = Math.sqrt(Math.max(variance, 1e-10));
    
    const normalized = trimmed.map(val => (val - mean) / std);
    
    return {
      values: normalized,
      samplingRate: 1.0
    };
  } catch (error) {
    console.warn('Pink noise generation failed, falling back to white noise:', error);
    // Fallback to white noise if pink noise generation fails
    return generateBrownianMotion(numSamples, 0.1);
  }
}

export function generateWhiteNoise(numSamples: number, scale: number = 1.0): NoiseSignal {
  if (numSamples <= 0) {
    throw new Error('Number of samples must be positive');
  }
  
  // Generate Gaussian white noise
  const noise = generateGaussianNoise(numSamples, scale);
  
  // White noise doesn't need cumulative summation, just normalization
  if (numSamples === 1) {
    return { values: [0], samplingRate: 1.0 };
  }
  
  const mean = noise.reduce((sum, val) => sum + val, 0) / numSamples;
  const variance = noise.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / numSamples;
  const std = Math.sqrt(Math.max(variance, 1e-10));
  
  const normalized = noise.map(val => (val - mean) / std);
  
  return {
    values: normalized,
    samplingRate: 1.0
  };
}

export function generateRedNoise(numSamples: number, scale: number = 1.0): NoiseSignal {
  if (numSamples <= 0) {
    throw new Error('Number of samples must be positive');
  }
  
  if (numSamples === 1) {
    return { values: [0], samplingRate: 1.0 };
  }
  
  // Ensure power of 2 for FFT efficiency
  const fftSize = Math.pow(2, Math.ceil(Math.log2(numSamples)));
  
  // Generate Gaussian white noise
  const whiteNoise = generateGaussianNoise(fftSize, scale);
  
  try {
    // Apply FFT-based 1/f^2 filtering for red noise
    const fft = computeFFT(whiteNoise);
    const nyquist = Math.floor(fftSize / 2);
    
    // Apply 1/f^2 filter (red noise), avoiding f=0
    for (let i = 1; i <= nyquist; i++) {
      const freq = i / fftSize;
      const factor = 1 / (freq * freq); // f^-2 for red noise
      
      // Apply filter to positive frequencies
      fft.real[i] *= factor;
      fft.imag[i] *= factor;
      
      // Apply to negative frequencies (mirror)
      if (i > 0 && i < nyquist) {
        const negIndex = fftSize - i;
        fft.real[negIndex] *= factor;
        fft.imag[negIndex] *= factor;
      }
    }
    
    // Handle DC and Nyquist components
    fft.real[0] = 0; // Remove DC component
    if (nyquist < fftSize) {
      fft.real[nyquist] *= 0.01; // Strongly reduce Nyquist component
      fft.imag[nyquist] = 0;
    }
    
    const redNoise = computeIFFT(fft, fftSize);
    
    // Take only the requested number of samples
    const trimmed = redNoise.slice(0, numSamples);
    
    // Normalize safely
    const mean = trimmed.reduce((sum, val) => sum + val, 0) / numSamples;
    const variance = trimmed.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / numSamples;
    const std = Math.sqrt(Math.max(variance, 1e-10));
    
    const normalized = trimmed.map(val => (val - mean) / std);
    
    return {
      values: normalized,
      samplingRate: 1.0
    };
  } catch (error) {
    console.warn('Red noise generation failed, falling back to Brownian motion:', error);
    // Fallback to Brownian motion if red noise generation fails
    return generateBrownianMotion(numSamples, scale);
  }
}

// Helper function to generate Gaussian noise using Box-Muller transform
function generateGaussianNoise(numSamples: number, scale: number = 1.0): number[] {
  const noise = new Array(numSamples);
  let hasSpare = false;
  let spare = 0; // Initialize to avoid TypeScript error
  
  for (let i = 0; i < numSamples; i++) {
    if (hasSpare) {
      noise[i] = spare * scale;
      hasSpare = false;
    } else {
      hasSpare = true;
      const u = Math.random();
      const v = Math.random();
      const mag = scale * Math.sqrt(-2.0 * Math.log(u));
      noise[i] = mag * Math.cos(2.0 * Math.PI * v);
      spare = mag * Math.sin(2.0 * Math.PI * v);
    }
  }
  
  return noise;
}

export function computePowerSpectralDensity(signal: NoiseSignal, windowSize: number = 256): PowerSpectralDensity {
  const { values, samplingRate } = signal;
  const numWindows = Math.floor(values.length / (windowSize / 2)) - 1;
  
  if (numWindows <= 0) {
    return { frequencies: [], power: [] };
  }
  
  const frequencies = Array.from({ length: windowSize / 2 }, (_, i) => (i * samplingRate) / windowSize);
  const powerSum = new Array(windowSize / 2).fill(0);
  
  // Welch's method - overlapping windows
  for (let w = 0; w < numWindows; w++) {
    const start = w * (windowSize / 2);
    const window = values.slice(start, start + windowSize);
    
    if (window.length < windowSize) continue;
    
    // Apply Hanning window
    const windowed = window.map((val, i) => 
      val * 0.5 * (1 - Math.cos(2 * Math.PI * i / (windowSize - 1)))
    );
    
    const fft = computeFFT(windowed);
    
    // Compute power for positive frequencies only
    for (let i = 0; i < windowSize / 2; i++) {
      const power = fft.real[i] * fft.real[i] + fft.imag[i] * fft.imag[i];
      powerSum[i] += power;
    }
  }
  
  // Average over windows
  const power = powerSum.map(p => p / numWindows);
  
  return { frequencies, power };
}

export function estimateFractalDimension1D(signal: number[], boxSizes?: number[]): number {
  if (!boxSizes) {
    const maxSize = Math.floor(signal.length / 4);
    boxSizes = Array.from({ length: 8 }, (_, i) => Math.floor(Math.pow(2, i + 1)))
      .filter(size => size <= maxSize);
  }
  
  const counts = boxSizes.map(size => {
    return Math.ceil(signal.length / size);
  });
  
  if (counts.length < 2) return 1.0;
  
  // Linear regression on log-log plot
  const logSizes = boxSizes.map(s => Math.log(1 / s));
  const logCounts = counts.map(c => Math.log(c));
  
  const n = logSizes.length;
  const sumX = logSizes.reduce((a, b) => a + b, 0);
  const sumY = logCounts.reduce((a, b) => a + b, 0);
  const sumXY = logSizes.reduce((sum, x, i) => sum + x * logCounts[i], 0);
  const sumXX = logSizes.reduce((sum, x) => sum + x * x, 0);
  
  const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
  return Math.abs(slope);
}

// Simple FFT implementation for noise generation
interface ComplexArray {
  real: number[];
  imag: number[];
}

function computeFFT(signal: number[]): ComplexArray {
  const n = signal.length;
  const imag = new Array(n).fill(0);
  return performFFT(signal, imag, n, true);
}

function computeIFFT(fft: ComplexArray, n: number): number[] {
  const { real, imag } = fft;
  
  // Create conjugated data for IFFT
  const conjugated = {
    real: [...real],
    imag: imag.map(x => -x)
  };
  
  // Manually perform IFFT using the FFT algorithm with conjugated input
  const result = performFFT(conjugated.real, conjugated.imag, n, false);
  
  // Scale by 1/n and return real part
  return result.real.map(x => x / n);
}

// More robust FFT implementation
function performFFT(realPart: number[], imagPart: number[], n: number, forward: boolean = true): ComplexArray {
  const real = [...realPart];
  const imag = [...imagPart];
  
  // Bit-reverse reordering
  for (let i = 1, j = 0; i < n; i++) {
    let bit = n >> 1;
    for (; j & bit; bit >>= 1) {
      j ^= bit;
    }
    j ^= bit;
    
    if (i < j) {
      [real[i], real[j]] = [real[j], real[i]];
      [imag[i], imag[j]] = [imag[j], imag[i]];
    }
  }
  
  // Cooley-Tukey FFT
  const direction = forward ? -1 : 1;
  for (let len = 2; len <= n; len <<= 1) {
    const angle = direction * 2 * Math.PI / len;
    const wLen = { real: Math.cos(angle), imag: Math.sin(angle) };
    
    for (let i = 0; i < n; i += len) {
      let w = { real: 1, imag: 0 };
      
      for (let j = 0; j < len / 2; j++) {
        const u = { real: real[i + j], imag: imag[i + j] };
        const v = {
          real: real[i + j + len / 2] * w.real - imag[i + j + len / 2] * w.imag,
          imag: real[i + j + len / 2] * w.imag + imag[i + j + len / 2] * w.real
        };
        
        real[i + j] = u.real + v.real;
        imag[i + j] = u.imag + v.imag;
        real[i + j + len / 2] = u.real - v.real;
        imag[i + j + len / 2] = u.imag - v.imag;
        
        const tempReal = w.real * wLen.real - w.imag * wLen.imag;
        w.imag = w.real * wLen.imag + w.imag * wLen.real;
        w.real = tempReal;
      }
    }
  }
  
  return { real, imag };
}