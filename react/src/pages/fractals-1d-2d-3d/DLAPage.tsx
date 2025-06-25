import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Typography, Slider, Button, Box } from '@mui/material';
import { PlayArrow, Pause, Refresh, Settings } from '@mui/icons-material';

interface DLAParams {
  numWalkers: number;
  stickDistance: number;
  stepSize: number;
  animationSpeed: number;
  killRadius: number;
  maxClusterSize: number;
  directionalStrength: number;
  vectorField: 'radial' | 'spiral' | 'uniform';
}

interface Particle {
  x: number;
  y: number;
  stuck: boolean;
  generation: number;
  velocity: { x: number; y: number };
  age: number;
}

// Advanced WebGL shaders for DLA visualization
const vertexShaderSource = `
  attribute vec2 a_position;
  attribute float a_size;
  attribute vec3 a_color;
  attribute float a_alpha;
  
  uniform vec2 u_resolution;
  uniform float u_time;
  
  varying vec3 v_color;
  varying float v_alpha;
  varying float v_size;
  varying float v_time;
  
  void main() {
    vec2 position = ((a_position / u_resolution) * 2.0 - 1.0) * vec2(1, -1);
    gl_Position = vec4(position, 0, 1);
    gl_PointSize = a_size;
    v_color = a_color;
    v_alpha = a_alpha;
    v_size = a_size;
    v_time = u_time;
  }
`;

const fragmentShaderSource = `
  precision mediump float;
  
  varying vec3 v_color;
  varying float v_alpha;
  varying float v_size;
  varying float v_time;
  
  void main() {
    vec2 coord = gl_PointCoord - vec2(0.5);
    float dist = length(coord);
    
    // Create circular particles with soft edges
    float alpha = 1.0 - smoothstep(0.0, 0.5, dist);
    
    // Add pulsing glow effect based on time
    float pulse = 0.5 + 0.3 * sin(v_time * 0.005);
    float glow = (1.0 - smoothstep(0.0, 1.0, dist * 2.0)) * pulse;
    
    // Fractal-like inner structure
    float fractal = sin(dist * 20.0 + v_time * 0.01) * 0.1;
    
    float finalAlpha = (alpha * v_alpha + glow * 0.2) * (1.0 + fractal);
    
    gl_FragColor = vec4(v_color, finalAlpha);
  }
`;

export const DLAPage: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const glRef = useRef<WebGLRenderingContext | null>(null);
  const programRef = useRef<WebGLProgram | null>(null);
  const animationRef = useRef<number>();
  const timeRef = useRef<number>(0);
  
  const [isAnimating, setIsAnimating] = useState(false);
  const [dimensions, setDimensions] = useState({ width: window.innerWidth, height: window.innerHeight });
  const [useWebGL, setUseWebGL] = useState(true);
  const [isInitialized, setIsInitialized] = useState(false);
  
  const [params, setParams] = useState<DLAParams>({
    numWalkers: 20,
    stickDistance: 6,
    stepSize: 2,
    animationSpeed: 30,
    killRadius: Math.min(window.innerWidth, window.innerHeight) * 0.45,
    maxClusterSize: 5000,
    directionalStrength: 0.1,
    vectorField: 'radial'
  });

  const [cluster, setCluster] = useState<Particle[]>([]);
  const [walkers, setWalkers] = useState<Particle[]>([]);

  // WebGL initialization
  const initWebGL = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) {
      console.error('Canvas not available for WebGL initialization');
      return false;
    }

    canvas.width = dimensions.width;
    canvas.height = dimensions.height;
    canvas.style.width = dimensions.width + 'px';
    canvas.style.height = dimensions.height + 'px';

    const gl = canvas.getContext('webgl');
    if (!gl) {
      console.warn('WebGL not supported, falling back to 2D canvas');
      setUseWebGL(false);
      setIsInitialized(true);
      return true;
    }

    glRef.current = gl;

    // Create and compile shaders
    const vertexShader = gl.createShader(gl.VERTEX_SHADER);
    const fragmentShader = gl.createShader(gl.FRAGMENT_SHADER);
    
    if (!vertexShader || !fragmentShader) return false;

    gl.shaderSource(vertexShader, vertexShaderSource);
    gl.shaderSource(fragmentShader, fragmentShaderSource);
    
    gl.compileShader(vertexShader);
    gl.compileShader(fragmentShader);

    if (!gl.getShaderParameter(vertexShader, gl.COMPILE_STATUS)) {
      console.error('Vertex shader error:', gl.getShaderInfoLog(vertexShader));
      return false;
    }
    if (!gl.getShaderParameter(fragmentShader, gl.COMPILE_STATUS)) {
      console.error('Fragment shader error:', gl.getShaderInfoLog(fragmentShader));
      return false;
    }

    // Create and link program
    const program = gl.createProgram();
    if (!program) return false;

    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);
    
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      console.error('Program link error:', gl.getProgramInfoLog(program));
      return false;
    }
    
    programRef.current = program;

    // Enable blending for glow effects
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

    console.log('WebGL initialized successfully');
    setIsInitialized(true);
    return true;
  }, [dimensions]);

  // Vector field calculation for directional spread
  const getVectorField = useCallback((x: number, y: number, centerX: number, centerY: number): { x: number; y: number } => {
    const dx = x - centerX;
    const dy = y - centerY;
    const distance = Math.sqrt(dx * dx + dy * dy);
    
    if (distance === 0) return { x: 0, y: 0 };
    
    switch (params.vectorField) {
      case 'radial':
        // Radial outward spread
        return { x: dx / distance, y: dy / distance };
      
      case 'spiral':
        // Spiral outward spread
        const angle = Math.atan2(dy, dx);
        const spiralAngle = angle + distance * 0.01;
        return { 
          x: Math.cos(spiralAngle), 
          y: Math.sin(spiralAngle) 
        };
      
      case 'uniform':
        // Uniform directional field (slightly upward)
        return { x: 0.1, y: -0.9 };
      
      default:
        return { x: dx / distance, y: dy / distance };
    }
  }, [params.vectorField]);

  // Create random walker with directional bias
  const createRandomWalker = useCallback((): Particle => {
    const centerX = dimensions.width / 2;
    const centerY = dimensions.height / 2;
    
    // Calculate dynamic spawn radius based on cluster size
    const clusterRadius = cluster.length > 1 ? 
      Math.max(...cluster.map(p => Math.sqrt((p.x - centerX) ** 2 + (p.y - centerY) ** 2))) : 20;
    const spawnRadius = Math.max(clusterRadius + 25, 80);
    
    // Spawn on circle at spawn radius
    const angle = Math.random() * 2 * Math.PI;
    const x = centerX + spawnRadius * Math.cos(angle);
    const y = centerY + spawnRadius * Math.sin(angle);
    
    // Initial velocity based on vector field
    const vectorField = getVectorField(x, y, centerX, centerY);
    
    return {
      x,
      y,
      stuck: false,
      generation: 0,
      velocity: vectorField,
      age: 0
    };
  }, [dimensions, cluster, getVectorField]);

  // Check if walker should stick to cluster
  const checkSticking = useCallback((walker: Particle, clusterParticles: Particle[]): boolean => {
    for (const particle of clusterParticles) {
      const dx = walker.x - particle.x;
      const dy = walker.y - particle.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      
      if (distance <= params.stickDistance) {
        return true;
      }
    }
    return false;
  }, [params.stickDistance]);

  // Move walker with attraction toward cluster
  const moveWalker = useCallback((walker: Particle, clusterParticles: Particle[]): Particle => {
    const centerX = dimensions.width / 2;
    const centerY = dimensions.height / 2;
    
    // Find nearest cluster particle for attraction
    let nearestDist = Infinity;
    let nearestParticle: Particle | null = null;
    
    for (const particle of clusterParticles) {
      const dx = walker.x - particle.x;
      const dy = walker.y - particle.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < nearestDist) {
        nearestDist = dist;
        nearestParticle = particle;
      }
    }
    
    // Random walk component
    const randomAngle = Math.random() * 2 * Math.PI;
    let moveX = Math.cos(randomAngle);
    let moveY = Math.sin(randomAngle);
    
    // Add attraction toward nearest cluster particle
    if (nearestParticle && nearestDist < 150) {
      const attractX = (nearestParticle.x - walker.x) / nearestDist;
      const attractY = (nearestParticle.y - walker.y) / nearestDist;
      
      // Blend random movement with attraction
      const attractionStrength = 0.4;
      moveX = moveX * (1 - attractionStrength) + attractX * attractionStrength;
      moveY = moveY * (1 - attractionStrength) + attractY * attractionStrength;
    }
    
    // Add vector field influence
    const vectorField = getVectorField(walker.x, walker.y, centerX, centerY);
    const vectorStrength = params.directionalStrength;
    moveX = moveX * (1 - vectorStrength) + vectorField.x * vectorStrength;
    moveY = moveY * (1 - vectorStrength) + vectorField.y * vectorStrength;
    
    // Apply step size
    const newX = walker.x + params.stepSize * moveX;
    const newY = walker.y + params.stepSize * moveY;
    
    // Check boundaries
    const distFromCenter = Math.sqrt((newX - centerX) ** 2 + (newY - centerY) ** 2);
    
    if (distFromCenter > params.killRadius) {
      return createRandomWalker();
    }
    
    return {
      ...walker,
      x: newX,
      y: newY,
      velocity: { x: moveX, y: moveY },
      age: walker.age + 1
    };
  }, [dimensions, params.stepSize, params.directionalStrength, params.killRadius, getVectorField, createRandomWalker]);

  // Initialize simulation
  const initializeSimulation = useCallback(() => {
    console.log('Initializing DLA simulation...');
    const centerX = dimensions.width / 2;
    const centerY = dimensions.height / 2;

    // Start with single seed particle at center
    const initialCluster: Particle[] = [
      { 
        x: centerX, 
        y: centerY, 
        stuck: true, 
        generation: 0,
        velocity: { x: 0, y: 0 },
        age: 0
      }
    ];

    setCluster(initialCluster);
    
    // Create initial walkers to start the process
    const initialWalkers: Particle[] = [];
    for (let i = 0; i < params.numWalkers; i++) {
      const angle = Math.random() * 2 * Math.PI;
      const spawnRadius = 80;
      const x = centerX + spawnRadius * Math.cos(angle);
      const y = centerY + spawnRadius * Math.sin(angle);
      
      initialWalkers.push({
        x,
        y,
        stuck: false,
        generation: 0,
        velocity: { x: 0, y: 0 },
        age: 0
      });
    }
    
    setWalkers(initialWalkers);
    timeRef.current = 0;
    console.log('DLA simulation initialized with seed particle and', initialWalkers.length, 'walkers');
  }, [dimensions, params.numWalkers]);

  // Simulation step
  const simulateStep = useCallback(() => {
    if (cluster.length >= params.maxClusterSize) {
      setIsAnimating(false);
      return;
    }

    timeRef.current += 1;

    setWalkers(prevWalkers => {
      let currentWalkers = [...prevWalkers];
      
      // Maintain walker population
      while (currentWalkers.length < params.numWalkers) {
        currentWalkers.push(createRandomWalker());
      }
      
      let newClusterParticle: Particle | null = null;

      // Process each walker
      for (let i = 0; i < currentWalkers.length; i++) {
        const walker = currentWalkers[i];
        
        // Check if walker should stick
        if (checkSticking(walker, cluster)) {
          newClusterParticle = { 
            ...walker, 
            stuck: true,
            generation: cluster.length,
            age: 0
          };
          // Replace with new walker
          currentWalkers[i] = createRandomWalker();
          break; // Only one particle sticks per frame
        } else {
          // Move walker
          currentWalkers[i] = moveWalker(walker, cluster);
        }
      }

      // Add new particle to cluster if one stuck
      if (newClusterParticle) {
        setCluster(prevCluster => {
          const newCluster = [...prevCluster, newClusterParticle!];
          if (newCluster.length % 100 === 0) {
            console.log('Cluster size:', newCluster.length);
          }
          return newCluster;
        });
      }

      return currentWalkers;
    });
  }, [cluster, params.maxClusterSize, params.numWalkers, checkSticking, moveWalker, createRandomWalker]);

  // WebGL rendering
  const render = useCallback(() => {
    const gl = glRef.current;
    const program = programRef.current;
    if (!gl || !program) {
      console.warn('WebGL or program not initialized for rendering');
      return;
    }

    try {
      gl.viewport(0, 0, dimensions.width, dimensions.height);
      gl.clearColor(0.01, 0.02, 0.08, 1.0); // Deep space background
      gl.clear(gl.COLOR_BUFFER_BIT);

      gl.useProgram(program);

      const allParticles = [...cluster, ...walkers.filter(w => !w.stuck)];
      if (allParticles.length === 0) return;

      const positions: number[] = [];
      const sizes: number[] = [];
      const colors: number[] = [];
      const alphas: number[] = [];

      allParticles.forEach(particle => {
        positions.push(particle.x, particle.y);
        
        if (particle.stuck) {
          // Cluster particles - use generation-based coloring
          const centerX = dimensions.width / 2;
          const centerY = dimensions.height / 2;
          const distFromCenter = Math.sqrt(
            (particle.x - centerX) ** 2 + (particle.y - centerY) ** 2
          );
          
          // Color based on distance and generation
          const hue = (distFromCenter * 0.8 + particle.generation * 2) % 360;
          const sat = 0.9;
          const light = 0.6 + 0.3 * Math.sin(particle.generation * 0.1);
          
          // Convert HSL to RGB
          const c = (1 - Math.abs(2 * light - 1)) * sat;
          const x = c * (1 - Math.abs(((hue / 60) % 2) - 1));
          const m = light - c / 2;
          
          let r, g, b;
          if (hue < 60) { r = c; g = x; b = 0; }
          else if (hue < 120) { r = x; g = c; b = 0; }
          else if (hue < 180) { r = 0; g = c; b = x; }
          else if (hue < 240) { r = 0; g = x; b = c; }
          else if (hue < 300) { r = x; g = 0; b = c; }
          else { r = c; g = 0; b = x; }
          
          colors.push(r + m, g + m, b + m);
          sizes.push(3 + Math.random() * 3);
          alphas.push(0.9);
        } else {
          // Walker particles - cyan with age-based fading
          const ageFactor = Math.max(0.3, 1.0 - particle.age * 0.001);
          colors.push(0.4 * ageFactor, 0.8 * ageFactor, 1.0);
          sizes.push(2);
          alphas.push(ageFactor * 0.7);
        }
      });

      // Create and bind buffers
      const positionBuffer = gl.createBuffer();
      const sizeBuffer = gl.createBuffer();
      const colorBuffer = gl.createBuffer();
      const alphaBuffer = gl.createBuffer();

      // Position attribute
      gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
      gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(positions), gl.STATIC_DRAW);
      const positionLocation = gl.getAttribLocation(program, 'a_position');
      gl.enableVertexAttribArray(positionLocation);
      gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);

      // Size attribute
      gl.bindBuffer(gl.ARRAY_BUFFER, sizeBuffer);
      gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(sizes), gl.STATIC_DRAW);
      const sizeLocation = gl.getAttribLocation(program, 'a_size');
      gl.enableVertexAttribArray(sizeLocation);
      gl.vertexAttribPointer(sizeLocation, 1, gl.FLOAT, false, 0, 0);

      // Color attribute
      gl.bindBuffer(gl.ARRAY_BUFFER, colorBuffer);
      gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(colors), gl.STATIC_DRAW);
      const colorLocation = gl.getAttribLocation(program, 'a_color');
      gl.enableVertexAttribArray(colorLocation);
      gl.vertexAttribPointer(colorLocation, 3, gl.FLOAT, false, 0, 0);

      // Alpha attribute
      gl.bindBuffer(gl.ARRAY_BUFFER, alphaBuffer);
      gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(alphas), gl.STATIC_DRAW);
      const alphaLocation = gl.getAttribLocation(program, 'a_alpha');
      gl.enableVertexAttribArray(alphaLocation);
      gl.vertexAttribPointer(alphaLocation, 1, gl.FLOAT, false, 0, 0);

      // Set uniforms
      const resolutionLocation = gl.getUniformLocation(program, 'u_resolution');
      gl.uniform2f(resolutionLocation, dimensions.width, dimensions.height);
      
      const timeLocation = gl.getUniformLocation(program, 'u_time');
      gl.uniform1f(timeLocation, timeRef.current);

      // Draw
      gl.drawArrays(gl.POINTS, 0, allParticles.length);

      // Cleanup
      gl.deleteBuffer(positionBuffer);
      gl.deleteBuffer(sizeBuffer);
      gl.deleteBuffer(colorBuffer);
      gl.deleteBuffer(alphaBuffer);
      
    } catch (error) {
      console.error('WebGL rendering error:', error);
    }
  }, [cluster, walkers, dimensions]);

  // 2D Canvas fallback rendering
  const render2D = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    try {
      // Clear canvas
      ctx.clearRect(0, 0, dimensions.width, dimensions.height);
      
      // Set background gradient
      const gradient = ctx.createRadialGradient(
        dimensions.width / 2, dimensions.height / 2, 0,
        dimensions.width / 2, dimensions.height / 2, Math.max(dimensions.width, dimensions.height) / 2
      );
      gradient.addColorStop(0, '#020510');
      gradient.addColorStop(1, '#000000');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, dimensions.width, dimensions.height);

      const allParticles = [...cluster, ...walkers.filter(w => !w.stuck)];

      allParticles.forEach(particle => {
        ctx.save();
        
        if (particle.stuck) {
          // Cluster particles
          const centerX = dimensions.width / 2;
          const centerY = dimensions.height / 2;
          const distFromCenter = Math.sqrt(
            (particle.x - centerX) ** 2 + (particle.y - centerY) ** 2
          );
          
          const hue = (distFromCenter * 0.8 + particle.generation * 2) % 360;
          ctx.fillStyle = `hsl(${hue}, 90%, 65%)`;
          ctx.beginPath();
          ctx.arc(particle.x, particle.y, 2 + Math.random() * 2, 0, 2 * Math.PI);
          ctx.fill();
          
          // Add glow effect
          ctx.shadowColor = `hsl(${hue}, 90%, 65%)`;
          ctx.shadowBlur = 5;
          ctx.fill();
        } else {
          // Walker particles
          const ageFactor = Math.max(0.3, 1.0 - particle.age * 0.001);
          ctx.fillStyle = `rgba(102, 204, 255, ${ageFactor * 0.7})`;
          ctx.beginPath();
          ctx.arc(particle.x, particle.y, 1.5, 0, 2 * Math.PI);
          ctx.fill();
        }
        
        ctx.restore();
      });
    } catch (error) {
      console.error('2D Canvas rendering error:', error);
    }
  }, [cluster, walkers, dimensions]);

  // Animation loop
  const animate = useCallback(() => {
    simulateStep();
    if (useWebGL) {
      render();
    } else {
      render2D();
    }
    
    if (isAnimating) {
      animationRef.current = requestAnimationFrame(() => {
        setTimeout(animate, 101 - params.animationSpeed);
      });
    }
  }, [isAnimating, simulateStep, render, render2D, useWebGL, params.animationSpeed]);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      setDimensions({ width: window.innerWidth, height: window.innerHeight });
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Initialize WebGL when dimensions change
  useEffect(() => {
    const success = initWebGL();
    if (!success) {
      console.error('Failed to initialize WebGL');
    }
  }, [initWebGL]);

  // Initialize simulation after WebGL is ready
  useEffect(() => {
    if (!isInitialized) return;
    
    const timer = setTimeout(() => {
      initializeSimulation();
      setTimeout(() => {
        if (useWebGL) {
          render();
        } else {
          render2D();
        }
        // Auto-start the animation
        setIsAnimating(true);
      }, 100);
    }, 100);
    
    return () => clearTimeout(timer);
  }, [isInitialized, initializeSimulation, render, render2D, useWebGL]);

  // Animation control
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

  const handleParamChange = (key: keyof DLAParams, value: number | string) => {
    setParams(prev => ({ ...prev, [key]: value }));
  };

  const toggleAnimation = () => {
    setIsAnimating(!isAnimating);
  };

  const resetSimulation = () => {
    setIsAnimating(false);
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
    initializeSimulation();
    setTimeout(() => {
      if (useWebGL) {
        render();
      } else {
        render2D();
      }
    }, 100);
  };

  return (
    <div style={{ 
      position: 'fixed', 
      top: 0, 
      left: 0, 
      width: '100vw', 
      height: '100vh', 
      overflow: 'hidden',
      backgroundColor: '#000510'
    }}>
      {/* Full-screen WebGL canvas */}
      <canvas
        ref={canvasRef}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          display: 'block'
        }}
      />

      {/* Title and Info Panel */}
      <Box
        sx={{
          position: 'fixed',
          top: 80,
          left: 20,
          maxWidth: 380,
          backgroundColor: 'rgba(0,0,0,0.85)',
          backdropFilter: 'blur(10px)',
          padding: 2.5,
          borderRadius: 2,
          zIndex: 999,
          color: 'white'
        }}
      >
        <Typography variant="h4" gutterBottom sx={{ 
          fontWeight: 'bold',
          background: 'linear-gradient(45deg, #66ccff, #9966ff, #ff6699)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
          mb: 1
        }}>
          Diffusion-Limited Aggregation
        </Typography>
        
        <Typography variant="body2" sx={{ mb: 1.5, lineHeight: 1.4 }}>
          Vector-field guided DLA simulation with directional spreading from a central seed. 
          Walkers follow configurable vector fields (radial, spiral, uniform) creating 
          diverse fractal growth patterns.
        </Typography>
        
        <Typography variant="caption" sx={{ 
          fontSize: '0.75em', 
          opacity: 0.8,
          fontStyle: 'italic'
        }}>
          WebGL-accelerated • Real-time physics simulation
        </Typography>
      </Box>

      {/* Controls Panel */}
      <Box
        sx={{
          position: 'fixed',
          top: 80,
          right: 20,
          width: 300,
          backgroundColor: 'rgba(0,0,0,0.85)',
          backdropFilter: 'blur(10px)',
          padding: 3,
          borderRadius: 2,
          zIndex: 1000,
          color: 'white'
        }}
      >
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Settings fontSize="small" />
          DLA Controls
        </Typography>

        <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
          <Button
            variant="contained"
            onClick={toggleAnimation}
            startIcon={isAnimating ? <Pause /> : <PlayArrow />}
            size="small"
            fullWidth
            sx={{ backgroundColor: isAnimating ? '#d32f2f' : '#2e7d32' }}
          >
            {isAnimating ? 'Pause' : 'Start'}
          </Button>

          <Button
            variant="outlined"
            onClick={resetSimulation}
            startIcon={<Refresh />}
            size="small"
            fullWidth
            sx={{ borderColor: '#666', color: 'white' }}
          >
            Reset
          </Button>
        </Box>

        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" gutterBottom>Vector Field</Typography>
          <Box sx={{ display: 'flex', gap: 0.5 }}>
            {(['radial', 'spiral', 'uniform'] as const).map((field) => (
              <Button
                key={field}
                size="small"
                variant={params.vectorField === field ? 'contained' : 'outlined'}
                onClick={() => handleParamChange('vectorField', field)}
                sx={{ 
                  fontSize: '0.7em',
                  minWidth: 'auto',
                  px: 1,
                  color: 'white',
                  borderColor: '#666'
                }}
              >
                {field}
              </Button>
            ))}
          </Box>
        </Box>

        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" gutterBottom>Walkers: {params.numWalkers}</Typography>
          <Slider
            value={params.numWalkers}
            onChange={(_, value) => handleParamChange('numWalkers', value as number)}
            min={10}
            max={100}
            step={5}
            size="small"
            sx={{ color: '#66ccff' }}
          />
        </Box>

        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" gutterBottom>Directional Strength: {(params.directionalStrength * 100).toFixed(0)}%</Typography>
          <Slider
            value={params.directionalStrength}
            onChange={(_, value) => handleParamChange('directionalStrength', value as number)}
            min={0}
            max={0.8}
            step={0.05}
            size="small"
            sx={{ color: '#9966ff' }}
          />
        </Box>

        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" gutterBottom>Speed: {params.animationSpeed}</Typography>
          <Slider
            value={params.animationSpeed}
            onChange={(_, value) => handleParamChange('animationSpeed', value as number)}
            min={1}
            max={100}
            size="small"
            sx={{ color: '#ff6699' }}
          />
        </Box>

        <Box sx={{ mb: 1 }}>
          <Typography variant="body2" gutterBottom>Stick Distance: {params.stickDistance}</Typography>
          <Slider
            value={params.stickDistance}
            onChange={(_, value) => handleParamChange('stickDistance', value as number)}
            min={1}
            max={8}
            step={0.5}
            size="small"
            sx={{ color: '#66ccff' }}
          />
        </Box>
      </Box>

      {/* Statistics overlay */}
      <Box
        sx={{
          position: 'fixed',
          bottom: 20,
          left: 20,
          color: 'white',
          backgroundColor: 'rgba(0,0,0,0.7)',
          padding: 2,
          borderRadius: 1,
          zIndex: 999
        }}
      >
        <Typography variant="body2">Cluster Particles: {cluster.length}</Typography>
        <Typography variant="body2">Active Walkers: {walkers.length}</Typography>
        <Typography variant="body2">Max Generation: {cluster.length > 0 ? Math.max(...cluster.map(p => p.generation)) : 0}</Typography>
        <Typography variant="body2" sx={{ mt: 1, fontSize: '0.7em', opacity: 0.8 }}>
          Renderer: {useWebGL ? 'WebGL' : '2D Canvas'} | {isInitialized ? 'Ready' : 'Initializing...'}
        </Typography>
      </Box>
    </div>
  );
};