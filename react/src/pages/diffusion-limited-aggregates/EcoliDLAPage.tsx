import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Typography, Slider, Button, Box, Paper, Drawer } from '@mui/material';
import { PlayArrow, Pause, Refresh, Settings } from '@mui/icons-material';

interface DLAParams {
  numWalkers: number;
  stickDistance: number;
  stepSize: number;
  animationSpeed: number;
  killRadius: number;
  spawnRadius: number;
  maxColonySize: number;
  attractionStrength: number;
}

interface Particle {
  x: number;
  y: number;
  stuck: boolean;
  generation: number;
  angle: number; // For directional growth bias
}

// WebGL shader sources
const vertexShaderSource = `
  attribute vec2 a_position;
  attribute float a_size;
  attribute vec3 a_color;
  
  uniform vec2 u_resolution;
  
  varying vec3 v_color;
  varying float v_size;
  
  void main() {
    vec2 position = ((a_position / u_resolution) * 2.0 - 1.0) * vec2(1, -1);
    gl_Position = vec4(position, 0, 1);
    gl_PointSize = a_size;
    v_color = a_color;
    v_size = a_size;
  }
`;

const fragmentShaderSource = `
  precision mediump float;
  
  varying vec3 v_color;
  varying float v_size;
  
  void main() {
    vec2 coord = gl_PointCoord - vec2(0.5);
    float dist = length(coord);
    
    // Create circular particles with soft edges
    float alpha = 1.0 - smoothstep(0.0, 0.5, dist);
    
    // Add glow effect
    float glow = 1.0 - smoothstep(0.0, 1.0, dist * 2.0);
    
    gl_FragColor = vec4(v_color, alpha * 0.9 + glow * 0.1);
  }
`;

export const EcoliDLAPage: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const glRef = useRef<WebGLRenderingContext | null>(null);
  const programRef = useRef<WebGLProgram | null>(null);
  const animationRef = useRef<number>();
  
  const [isAnimating, setIsAnimating] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [dimensions, setDimensions] = useState({ width: window.innerWidth, height: window.innerHeight });
  
  const [params, setParams] = useState<DLAParams>({
    numWalkers: 50, // Fewer walkers, more selective
    stickDistance: 3,
    stepSize: 2,
    animationSpeed: 60,
    killRadius: Math.min(window.innerWidth, window.innerHeight) * 0.4,
    spawnRadius: Math.min(window.innerWidth, window.innerHeight) * 0.45,
    maxColonySize: 15000,
    attractionStrength: 0.1 // Slight bias toward cluster
  });

  const [cluster, setCluster] = useState<Particle[]>([]);
  const [walkers, setWalkers] = useState<Particle[]>([]);

  // WebGL setup
  const initWebGL = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    canvas.width = dimensions.width;
    canvas.height = dimensions.height;

    const gl = canvas.getContext('webgl');
    if (!gl) {
      console.error('WebGL not supported');
      return;
    }

    glRef.current = gl;

    // Create shaders
    const vertexShader = gl.createShader(gl.VERTEX_SHADER);
    const fragmentShader = gl.createShader(gl.FRAGMENT_SHADER);
    
    if (!vertexShader || !fragmentShader) return;

    gl.shaderSource(vertexShader, vertexShaderSource);
    gl.shaderSource(fragmentShader, fragmentShaderSource);
    
    gl.compileShader(vertexShader);
    gl.compileShader(fragmentShader);

    // Check shader compilation
    if (!gl.getShaderParameter(vertexShader, gl.COMPILE_STATUS)) {
      console.error('Vertex shader error:', gl.getShaderInfoLog(vertexShader));
      return;
    }
    if (!gl.getShaderParameter(fragmentShader, gl.COMPILE_STATUS)) {
      console.error('Fragment shader error:', gl.getShaderInfoLog(fragmentShader));
      return;
    }

    // Create program
    const program = gl.createProgram();
    if (!program) return;

    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);
    
    // Check program linking
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      console.error('Program link error:', gl.getProgramInfoLog(program));
      return;
    }
    
    programRef.current = program;

    // Enable blending for glow effects
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

    console.log('WebGL initialized successfully');
    console.log('Canvas dimensions:', canvas.width, 'x', canvas.height);
    console.log('WebGL version:', gl.getParameter(gl.VERSION));
  }, [dimensions]);

  // True DLA algorithm - one walker at a time, proper random walk
  const createRandomWalker = useCallback((): Particle => {
    const centerX = dimensions.width / 2;
    const centerY = dimensions.height / 2;
    
    // Spawn on circle at spawn radius
    const angle = Math.random() * 2 * Math.PI;
    const x = centerX + params.spawnRadius * Math.cos(angle);
    const y = centerY + params.spawnRadius * Math.sin(angle);
    
    return {
      x,
      y,
      stuck: false,
      generation: 0,
      angle: Math.random() * 2 * Math.PI
    };
  }, [dimensions, params.spawnRadius]);

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

  // Move walker with true random walk and slight attraction
  const moveWalker = useCallback((walker: Particle, clusterParticles: Particle[]): Particle => {
    const centerX = dimensions.width / 2;
    const centerY = dimensions.height / 2;
    
    // Find nearest cluster particle for slight attraction
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
    
    // Random walk with slight bias toward nearest cluster point
    let moveAngle = Math.random() * 2 * Math.PI;
    
    if (nearestParticle && nearestDist < 100) {
      const attractionAngle = Math.atan2(
        nearestParticle.y - walker.y,
        nearestParticle.x - walker.x
      );
      
      // Blend random angle with attraction angle
      const blend = params.attractionStrength;
      moveAngle = moveAngle * (1 - blend) + attractionAngle * blend;
    }
    
    const newX = walker.x + params.stepSize * Math.cos(moveAngle);
    const newY = walker.y + params.stepSize * Math.sin(moveAngle);
    
    // Check boundaries - kill walker if too far
    const distFromCenter = Math.sqrt(
      (newX - centerX) ** 2 + (newY - centerY) ** 2
    );
    
    if (distFromCenter > params.killRadius) {
      // Return new random walker
      return createRandomWalker();
    }
    
    return {
      ...walker,
      x: newX,
      y: newY,
      angle: moveAngle
    };
  }, [dimensions, params.stepSize, params.attractionStrength, params.killRadius, createRandomWalker]);

  // Initialize simulation
  const initializeSimulation = useCallback(() => {
    console.log('Initializing DLA simulation...');
    const centerX = dimensions.width / 2;
    const centerY = dimensions.height / 2;

    // Start with single seed particle
    const initialCluster: Particle[] = [
      { 
        x: centerX, 
        y: centerY, 
        stuck: true, 
        generation: 0,
        angle: 0
      }
    ];

    // Create initial walkers
    const initialWalkers: Particle[] = [];
    for (let i = 0; i < params.numWalkers; i++) {
      initialWalkers.push(createRandomWalker());
    }

    setCluster(initialCluster);
    setWalkers(initialWalkers);
    console.log('DLA simulation initialized with', initialWalkers.length, 'walkers');
  }, [dimensions, params.numWalkers, createRandomWalker]);

  // Simulation step - process one walker at a time
  const simulateStep = useCallback(() => {
    if (cluster.length >= params.maxColonySize) {
      setIsAnimating(false);
      return;
    }

    setWalkers(prevWalkers => {
      const newWalkers = [...prevWalkers];
      let newClusterParticle: Particle | null = null;

      // Process walkers one by one
      for (let i = 0; i < newWalkers.length; i++) {
        const walker = newWalkers[i];
        
        if (!walker.stuck) {
          // Check if walker should stick
          if (checkSticking(walker, cluster)) {
            newClusterParticle = { ...walker, stuck: true };
            // Replace with new walker
            newWalkers[i] = createRandomWalker();
            break; // Only one particle sticks per frame
          } else {
            // Move walker
            newWalkers[i] = moveWalker(walker, cluster);
          }
        }
      }

      // Add new particle to cluster if one stuck
      if (newClusterParticle) {
        setCluster(prevCluster => {
          const newCluster = [...prevCluster, newClusterParticle!];
          if (newCluster.length % 100 === 0) {
            console.log('Colony size:', newCluster.length);
          }
          return newCluster;
        });
      }

      return newWalkers;
    });
  }, [cluster, params.maxColonySize, checkSticking, moveWalker, createRandomWalker]);

  // WebGL rendering
  const render = useCallback(() => {
    const gl = glRef.current;
    const program = programRef.current;
    if (!gl || !program) return;

    gl.viewport(0, 0, dimensions.width, dimensions.height);
    gl.clearColor(0.02, 0.05, 0.1, 1.0); // Dark blue background
    gl.clear(gl.COLOR_BUFFER_BIT);

    gl.useProgram(program);

    // Prepare data arrays
    const allParticles = [...cluster, ...walkers.filter(w => !w.stuck)];
    if (allParticles.length === 0) return;

    const positions: number[] = [];
    const sizes: number[] = [];
    const colors: number[] = [];

    allParticles.forEach(particle => {
      positions.push(particle.x, particle.y);
      
      if (particle.stuck) {
        // Cluster particles - bright colors based on generation/position
        const centerX = dimensions.width / 2;
        const centerY = dimensions.height / 2;
        const distFromCenter = Math.sqrt(
          (particle.x - centerX) ** 2 + (particle.y - centerY) ** 2
        );
        
        // Color based on distance from center and generation
        const hue = (distFromCenter * 0.5 + particle.generation * 30) % 360;
        const sat = 0.8;
        const light = 0.7;
        
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
        sizes.push(4 + Math.random() * 2);
      } else {
        // Walker particles - cyan/white
        colors.push(0.4, 0.8, 1.0);
        sizes.push(2);
      }
    });

    // Create buffers
    const positionBuffer = gl.createBuffer();
    const sizeBuffer = gl.createBuffer();
    const colorBuffer = gl.createBuffer();

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

    // Set resolution uniform
    const resolutionLocation = gl.getUniformLocation(program, 'u_resolution');
    gl.uniform2f(resolutionLocation, dimensions.width, dimensions.height);

    // Draw
    gl.drawArrays(gl.POINTS, 0, allParticles.length);

    // Cleanup
    gl.deleteBuffer(positionBuffer);
    gl.deleteBuffer(sizeBuffer);
    gl.deleteBuffer(colorBuffer);
  }, [cluster, walkers, dimensions]);

  // Animation loop
  const animate = useCallback(() => {
    simulateStep();
    render();
    
    if (isAnimating) {
      animationRef.current = requestAnimationFrame(() => {
        setTimeout(animate, 101 - params.animationSpeed);
      });
    }
  }, [isAnimating, simulateStep, render, params.animationSpeed]);

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
    initWebGL();
  }, [initWebGL]);

  // Initialize simulation
  useEffect(() => {
    initializeSimulation();
  }, [initializeSimulation]);

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

  const handleParamChange = (key: keyof DLAParams, value: number) => {
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
  };

  return (
    <div style={{ 
      position: 'fixed', 
      top: 0, 
      left: 0, 
      width: '100vw', 
      height: '100vh', 
      overflow: 'hidden',
      backgroundColor: '#0a0f1a'
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

      {/* Control button */}
      <Button
        variant="contained"
        onClick={() => setDrawerOpen(true)}
        sx={{
          position: 'fixed',
          top: 20,
          right: 20,
          zIndex: 1000,
          backgroundColor: 'rgba(0,0,0,0.8)',
          '&:hover': { backgroundColor: 'rgba(0,0,0,0.9)' }
        }}
        startIcon={<Settings />}
      >
        Controls
      </Button>

      {/* Title overlay */}
      <Typography
        variant="h4"
        sx={{
          position: 'fixed',
          top: 20,
          left: 20,
          color: 'white',
          textShadow: '2px 2px 4px rgba(0,0,0,0.8)',
          zIndex: 999
        }}
      >
        E. coli DLA Colony Growth
      </Typography>

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
        <Typography variant="body2">Bacteria: {cluster.length}</Typography>
        <Typography variant="body2">Walkers: {walkers.length}</Typography>
        <Typography variant="body2">Max Generation: {cluster.length > 0 ? Math.max(...cluster.map(p => p.generation)) : 0}</Typography>
      </Box>

      {/* Controls drawer */}
      <Drawer
        anchor="right"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      >
        <Box sx={{ width: 350, p: 3 }}>
          <Typography variant="h5" gutterBottom>
            DLA Parameters
          </Typography>

          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="body2" sx={{ mb: 2 }}>
              True Diffusion-Limited Aggregation with agent-based bacterial modeling 
              from Vassallo et al. (2019). WebGL-accelerated full-screen visualization.
            </Typography>
            <Typography variant="body2" sx={{ fontStyle: 'italic', fontSize: '0.8em' }}>
              DOI: 10.1140/epjb/e2019-100265-0
            </Typography>
          </Paper>

          <Box sx={{ mb: 3 }}>
            <Typography gutterBottom>Number of Walkers: {params.numWalkers}</Typography>
            <Slider
              value={params.numWalkers}
              onChange={(_, value) => handleParamChange('numWalkers', value as number)}
              min={10}
              max={200}
              step={10}
            />
          </Box>

          <Box sx={{ mb: 3 }}>
            <Typography gutterBottom>Stick Distance: {params.stickDistance}</Typography>
            <Slider
              value={params.stickDistance}
              onChange={(_, value) => handleParamChange('stickDistance', value as number)}
              min={1}
              max={10}
              step={0.5}
            />
          </Box>

          <Box sx={{ mb: 3 }}>
            <Typography gutterBottom>Step Size: {params.stepSize}</Typography>
            <Slider
              value={params.stepSize}
              onChange={(_, value) => handleParamChange('stepSize', value as number)}
              min={0.5}
              max={5}
              step={0.1}
            />
          </Box>

          <Box sx={{ mb: 3 }}>
            <Typography gutterBottom>Animation Speed: {params.animationSpeed}</Typography>
            <Slider
              value={params.animationSpeed}
              onChange={(_, value) => handleParamChange('animationSpeed', value as number)}
              min={1}
              max={100}
            />
          </Box>

          <Box sx={{ mb: 3 }}>
            <Typography gutterBottom>Attraction Strength: {(params.attractionStrength * 100).toFixed(0)}%</Typography>
            <Slider
              value={params.attractionStrength}
              onChange={(_, value) => handleParamChange('attractionStrength', value as number)}
              min={0}
              max={0.5}
              step={0.01}
            />
          </Box>

          <Box sx={{ display: 'flex', gap: 1, flexDirection: 'column', mb: 3 }}>
            <Button
              variant="contained"
              onClick={toggleAnimation}
              startIcon={isAnimating ? <Pause /> : <PlayArrow />}
              fullWidth
            >
              {isAnimating ? 'Pause' : 'Start'} Growth
            </Button>

            <Button
              variant="outlined"
              onClick={resetSimulation}
              startIcon={<Refresh />}
              fullWidth
            >
              Reset Colony
            </Button>
          </Box>
        </Box>
      </Drawer>
    </div>
  );
};