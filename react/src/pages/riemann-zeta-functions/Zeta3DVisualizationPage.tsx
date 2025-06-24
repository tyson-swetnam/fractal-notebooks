import React, { useState, useEffect, useCallback } from 'react';
import { Typography, Grid, Slider, Button, Box, Paper, FormControl, InputLabel, Select, MenuItem, SelectChangeEvent, Checkbox, FormControlLabel, Tab, Tabs } from '@mui/material';
import { MathRenderer } from '../../components/math/MathRenderer';
import { PlayArrow, Pause, Refresh, RotateRight } from '@mui/icons-material';
// @ts-ignore
import Plot from 'react-plotly.js';

interface Zeta3DParams {
  shapeTypes: ('Sphere' | 'Cube' | 'Tetrahedron')[];
  volumeSpace: number;
  initialVolume: number;
  exponent: number;
  numShapes: number;
  maxParticleSize: number;
  minParticleSize: number;
  animationSpeed: number;
  rotationX: number;
  rotationY: number;
  rotationZ: number;
}

interface Shape3D {
  x: number;
  y: number;
  z: number;
  size: number;
  type: 'Sphere' | 'Cube' | 'Tetrahedron';
  color: string;
  volume: number;
}

// Riemann Zeta function approximation
const riemannZeta = (s: number): number => {
  if (s === 1) return Infinity;
  if (s < 1) return NaN;
  
  let sum = 0;
  const maxTerms = 10000;
  
  for (let n = 1; n <= maxTerms; n++) {
    sum += 1 / Math.pow(n, s);
  }
  
  return sum;
};


const generateCubeVertices = (x: number, y: number, z: number, size: number) => {
  const half = size / 2;
  return {
    x: [x-half, x+half, x+half, x-half, x-half, x+half, x+half, x-half],
    y: [y-half, y-half, y+half, y+half, y-half, y-half, y+half, y+half],
    z: [z-half, z-half, z-half, z-half, z+half, z+half, z+half, z+half]
  };
};

const generateTetrahedronVertices = (x: number, y: number, z: number, size: number) => {
  return {
    x: [x, x+size, x+size/2, x+size/2],
    y: [y, y, y+Math.sqrt(3)*size/2, y+Math.sqrt(3)*size/6],
    z: [z, z, z, z+Math.sqrt(6)*size/3]
  };
};

export const Zeta3DVisualizationPage: React.FC = () => {
  const animationRef = React.useRef<number>();
  const [activeTab, setActiveTab] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);
  const [currentShape, setCurrentShape] = useState(0);
  const [autoRotate, setAutoRotate] = useState(false);
  const [params, setParams] = useState<Zeta3DParams>({
    shapeTypes: ['Sphere', 'Tetrahedron'], // Notebook uses spheres and tetrahedra primarily
    volumeSpace: 10000, // A_volume from notebook
    initialVolume: 100, // A0 from notebook  
    exponent: 1.2, // p value from notebook
    numShapes: 2000, // Increased from notebook's approach
    maxParticleSize: 50, // max_particle_size from notebook
    minParticleSize: 0.1, // min_particle_size from notebook
    animationSpeed: 30,
    rotationX: 0.3,
    rotationY: 0.2,
    rotationZ: 0.1
  });

  const [shapes, setShapes] = useState<Shape3D[]>([]);
  const [zetaValue, setZetaValue] = useState(0);

  const generateShapeVolumes = useCallback(() => {
    const zeta_p = riemannZeta(params.exponent);
    setZetaValue(zeta_p);
    
    if (!isFinite(zeta_p)) {
      console.warn('Zeta function diverges for this exponent');
      return [];
    }
    
    // Start with the initial volume (A0 in the notebook)
    const volumes: number[] = [params.initialVolume];
    
    let i = 1;
    while (volumes.length < params.numShapes) {
      // Using the notebook's formula: A0 / (i^p)
      const volume = params.initialVolume / Math.pow(i, params.exponent);
      if (volume <= 0) break;
      
      // Calculate approximate size as sphere radius to check bounds
      const sphereRadius = Math.pow(3 * volume / (4 * Math.PI), 1/3);
      
      if (sphereRadius > params.maxParticleSize) {
        i++;
        continue;
      }
      
      if (sphereRadius < params.minParticleSize) {
        break;
      }
      
      volumes.push(volume);
      i++;
    }
    
    // Shuffle volumes to distribute sizes among shapes (from notebook)
    // This creates better spatial distribution of different sizes
    for (let i = volumes.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [volumes[i], volumes[j]] = [volumes[j], volumes[i]];
    }
    
    return volumes;
  }, [params.initialVolume, params.exponent, params.numShapes, params.maxParticleSize, params.minParticleSize]);

  const isOverlapping3D = useCallback((x: number, y: number, z: number, size: number, existingShapes: Shape3D[]): boolean => {
    for (const shape of existingShapes) {
      const dx = x - shape.x;
      const dy = y - shape.y;
      const dz = z - shape.z;
      const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);
      
      // Approximate all shapes as spheres for overlap checking
      const radius1 = size;
      const radius2 = shape.size;
      
      if (distance < (radius1 + radius2)) {
        return true;
      }
    }
    return false;
  }, []);

  const generateShapes3D = useCallback(() => {
    const volumes = generateShapeVolumes();
    const L = Math.pow(params.volumeSpace, 1/3);
    const newShapes: Shape3D[] = [];
    
    const colors = {
      Sphere: '#4285f4',
      Cube: '#34a853',
      Tetrahedron: '#ea4335'
    };
    
    for (let idx = 0; idx < volumes.length; idx++) {
      const volume = volumes[idx];
      const shapeType = params.shapeTypes[Math.floor(Math.random() * params.shapeTypes.length)];
      
      // Calculate size based on shape type using notebook formulas
      let size: number;
      if (shapeType === 'Sphere') {
        // Sphere: radius = (3V / 4π)^(1/3)
        size = Math.pow(3 * volume / (4 * Math.PI), 1/3);
      } else if (shapeType === 'Cube') {
        // Cube: side length = V^(1/3)
        size = Math.pow(volume, 1/3);
      } else { // Tetrahedron
        // Tetrahedron: edge length using notebook formula
        // Volume = (sqrt(2)/12) * a^3, so a = (12V/sqrt(2))^(1/3)
        size = Math.pow(volume * 12 / Math.sqrt(2), 1/3);
      }
      
      let placed = false;
      let currentSize = size;
      
      // Use notebook's size reduction strategy
      while (currentSize >= params.minParticleSize && !placed) {
        const maxAttempts = 1000;
        
        for (let attempt = 0; attempt < maxAttempts; attempt++) {
          // Generate position within the space bounds
          const x = Math.random() * (L - 2 * currentSize) + currentSize - L/2;
          const y = Math.random() * (L - 2 * currentSize) + currentSize - L/2; 
          const z = Math.random() * (L - 2 * currentSize) + currentSize - L/2;
          
          if (!isOverlapping3D(x, y, z, currentSize, newShapes)) {
            newShapes.push({ 
              x, y, z, 
              size: currentSize, 
              type: shapeType, 
              color: colors[shapeType],
              volume: volume * Math.pow(currentSize / size, 3) // Adjust volume for size reduction
            });
            placed = true;
            break;
          }
        }
        
        if (!placed) {
          // Use notebook's size reduction strategy: divide by 2
          currentSize /= 2.0;
        }
      }
      
      // Log placement failure like in notebook (but don't spam console)
      if (!placed && idx < 10) {
        console.log(`Could not place shape ${idx + 1} even after reducing to minimum size.`);
      }
    }
    
    // Sort shapes by z-depth for proper rendering
    newShapes.sort((a, b) => b.z - a.z);
    
    setShapes(newShapes);
    setCurrentShape(0);
  }, [generateShapeVolumes, params.volumeSpace, params.shapeTypes, params.minParticleSize, isOverlapping3D]);

  // Generate Plotly 3D data from shapes
  const getPlotlyData3D = useCallback(() => {
    const visibleShapes = isAnimating ? shapes.slice(0, currentShape + 1) : shapes;
    const traces: any[] = [];
    
    visibleShapes.forEach((shape, index) => {
      if (shape.type === 'Sphere') {
        traces.push({
          type: 'scatter3d',
          mode: 'markers',
          x: [shape.x],
          y: [shape.y], 
          z: [shape.z],
          marker: {
            size: shape.size * 10,
            color: shape.color,
            opacity: 0.8
          },
          hoverinfo: 'text',
          text: `Sphere ${index + 1}<br>Volume: ${shape.volume.toFixed(2)}`,
          showlegend: false
        });
      } else if (shape.type === 'Cube') {
        const vertices = generateCubeVertices(shape.x, shape.y, shape.z, shape.size);
        traces.push({
          type: 'mesh3d',
          x: vertices.x,
          y: vertices.y,
          z: vertices.z,
          i: [0, 0, 0, 1, 1, 2, 2, 3, 4, 4, 5, 6],
          j: [1, 3, 4, 2, 5, 3, 6, 7, 5, 7, 6, 7],
          k: [2, 4, 5, 6, 6, 7, 7, 4, 7, 6, 7, 2],
          color: shape.color,
          opacity: 0.7,
          hoverinfo: 'text',
          text: `Cube ${index + 1}<br>Volume: ${shape.volume.toFixed(2)}`,
          showlegend: false
        });
      } else if (shape.type === 'Tetrahedron') {
        const vertices = generateTetrahedronVertices(shape.x, shape.y, shape.z, shape.size);
        traces.push({
          type: 'mesh3d',
          x: vertices.x,
          y: vertices.y,
          z: vertices.z,
          i: [0, 0, 0, 1],
          j: [1, 2, 3, 2],
          k: [2, 3, 1, 3],
          color: shape.color,
          opacity: 0.7,
          hoverinfo: 'text',
          text: `Tetrahedron ${index + 1}<br>Volume: ${shape.volume.toFixed(2)}`,
          showlegend: false
        });
      }
    });
    
    return traces;
  }, [shapes, currentShape, isAnimating]);

  // Plotly 3D layout configuration
  const plotlyLayout = {
    scene: {
      xaxis: {
        visible: true,
        range: [-Math.pow(params.volumeSpace, 1/3)/2, Math.pow(params.volumeSpace, 1/3)/2],
        title: 'X Axis'
      },
      yaxis: {
        visible: true,
        range: [-Math.pow(params.volumeSpace, 1/3)/2, Math.pow(params.volumeSpace, 1/3)/2],
        title: 'Y Axis'
      },
      zaxis: {
        visible: true,
        range: [-Math.pow(params.volumeSpace, 1/3)/2, Math.pow(params.volumeSpace, 1/3)/2],
        title: 'Z Axis'
      },
      camera: {
        eye: {
          x: Math.cos(params.rotationY) * Math.cos(params.rotationX) * 2,
          y: Math.sin(params.rotationY) * Math.cos(params.rotationX) * 2,
          z: Math.sin(params.rotationX) * 2
        }
      },
      bgcolor: 'rgba(0,0,0,0.9)',
      aspectmode: 'cube'
    },
    showlegend: false,
    margin: { l: 0, r: 0, t: 0, b: 0 },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)'
  };

  const plotlyData = getPlotlyData3D();



  const animate = useCallback(() => {
    if (autoRotate) {
      setParams(prev => ({
        ...prev,
        rotationX: prev.rotationX + 0.01,
        rotationY: prev.rotationY + 0.008,
        rotationZ: prev.rotationZ + 0.005
      }));
    }
    
    if (isAnimating && currentShape < shapes.length - 1) {
      setCurrentShape(prev => prev + 1);
    } else if (isAnimating) {
      setIsAnimating(false);
    }
    
    animationRef.current = requestAnimationFrame(() => {
      setTimeout(animate, 101 - params.animationSpeed);
    });
  }, [autoRotate, isAnimating, currentShape, shapes.length, params.animationSpeed]);

  useEffect(() => {
    animate();
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [animate]);

  useEffect(() => {
    generateShapes3D();
  }, [generateShapes3D]);

  const handleParamChange = (key: keyof Zeta3DParams, value: number | string | boolean | string[]) => {
    setParams(prev => ({ ...prev, [key]: value }));
  };

  const handleShapeTypesChange = (event: SelectChangeEvent<string[]>) => {
    const value = event.target.value;
    handleParamChange('shapeTypes', typeof value === 'string' ? value.split(',') : value);
  };

  const toggleAnimation = () => {
    if (!isAnimating && currentShape >= shapes.length - 1) {
      setCurrentShape(0);
    }
    setIsAnimating(!isAnimating);
  };

  const resetSimulation = () => {
    setIsAnimating(false);
    generateShapes3D();
  };

  const resetRotation = () => {
    setParams(prev => ({
      ...prev,
      rotationX: 0.3,
      rotationY: 0.2,
      rotationZ: 0.1
    }));
  };

  const resetToNotebookDefaults = () => {
    setParams({
      shapeTypes: ['Sphere', 'Tetrahedron'],
      volumeSpace: 10000,
      initialVolume: 100,
      exponent: 1.2,
      numShapes: 2000,
      maxParticleSize: 50,
      minParticleSize: 0.1,
      animationSpeed: 30,
      rotationX: 0.3,
      rotationY: 0.2,
      rotationZ: 0.1
    });
    setIsAnimating(false);
  };

  return (
    <div className="page-container">
      <Typography variant="h3" component="h1" className="page-title">
        3D Riemann Zeta Visualization
      </Typography>
      <Typography variant="body1" className="page-description">
        Explore three-dimensional space-filling patterns using the Riemann Zeta function to govern volumetric distributions.
      </Typography>

      <Paper sx={{ p: 3, mb: 3, backgroundColor: 'background.paper' }}>
        <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
          <Tab label="Visualization" />
          <Tab label="Mathematics" />
        </Tabs>
        
        {activeTab === 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6" gutterBottom>
              Interactive 3D Riemann Zeta Visualization
            </Typography>
            <Typography variant="body2">
              Explore three-dimensional space-filling patterns using the Riemann Zeta function with interactive 
              3D rendering. Adjust parameters to see how mathematical relationships govern 3D distributions.
            </Typography>
          </Box>
        )}
        
        {activeTab === 1 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6" gutterBottom>
              3D Zeta Volume Distribution Theory
            </Typography>
            <Typography variant="body2" sx={{ mb: 2 }}>
              This implementation follows the mathematical framework where the Riemann Zeta function governs 
              the volume distribution of 3D shapes. Each shape's volume follows the power law:
            </Typography>
            <MathRenderer 
              math="V_i = \frac{A_0}{i^p}" 
              block 
            />
            <Typography variant="body2" sx={{ mt: 2, mb: 2 }}>
              Where <MathRenderer math="A_0" /> is the initial volume and <MathRenderer math="p" /> is the exponent. 
              The shape sizes are calculated from volume using geometry-specific formulas:
            </Typography>
            <MathRenderer 
              math="\text{Sphere radius: } r = \left(\frac{3V}{4\pi}\right)^{1/3}" 
              block 
            />
            <MathRenderer 
              math="\text{Tetrahedron edge: } a = \left(\frac{12V}{\sqrt{2}}\right)^{1/3}" 
              block 
            />
            <Typography variant="body2" sx={{ mt: 2 }}>
              Current ζ({params.exponent}) = {zetaValue.toFixed(4)}. Volumes are shuffled for better 
              spatial distribution, and overlap detection ensures physical constraints are satisfied.
            </Typography>
          </Box>
        )}
      </Paper>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <Box className="visualization-area">
            <Plot
              data={plotlyData as any}
              layout={plotlyLayout as any}
              style={{ width: '100%', height: '700px' }}
              config={{
                displayModeBar: true,
                displaylogo: false,
                modeBarButtonsToRemove: ['select2d', 'lasso2d', 'autoScale2d', 'resetCameraDefault3d']
              }}
            />
            <Typography variant="body2" sx={{ mt: 1, textAlign: 'center' }}>
              3D Shapes: {shapes.length} | Animation: {((currentShape + 1) / Math.max(shapes.length, 1) * 100).toFixed(1)}% | Interactive Plotly 3D View
            </Typography>
          </Box>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Box className="controls-area">
            <Typography variant="h6" gutterBottom>
              3D Zeta Parameters
            </Typography>

            <Box sx={{ mb: 3 }}>
              <FormControl fullWidth>
                <InputLabel>Shape Types</InputLabel>
                <Select
                  multiple
                  value={params.shapeTypes}
                  label="Shape Types"
                  onChange={handleShapeTypesChange}
                >
                  <MenuItem value="Sphere">Spheres</MenuItem>
                  <MenuItem value="Cube">Cubes</MenuItem>
                  <MenuItem value="Tetrahedron">Tetrahedra</MenuItem>
                </Select>
              </FormControl>
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Volume Space (A_volume): {params.volumeSpace}</Typography>
              <Slider
                value={params.volumeSpace}
                onChange={(_, value) => handleParamChange('volumeSpace', value as number)}
                min={1000}
                max={50000}
                step={1000}
                marks={[
                  { value: 10000, label: '10k' },
                  { value: 25000, label: '25k' },
                  { value: 50000, label: '50k' }
                ]}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Initial Volume (A₀): {params.initialVolume}</Typography>
              <Slider
                value={params.initialVolume}
                onChange={(_, value) => handleParamChange('initialVolume', value as number)}
                min={10}
                max={500}
                step={10}
                marks={[
                  { value: 100, label: '100' },
                  { value: 200, label: '200' },
                  { value: 300, label: '300' }
                ]}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Exponent (p): {params.exponent}</Typography>
              <Slider
                value={params.exponent}
                onChange={(_, value) => handleParamChange('exponent', value as number)}
                min={1.05}
                max={2.5}
                step={0.05}
                marks={[
                  { value: 1.2, label: '1.2' },
                  { value: 1.5, label: '1.5' },
                  { value: 2.0, label: '2.0' }
                ]}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Number of Shapes: {params.numShapes}</Typography>
              <Slider
                value={params.numShapes}
                onChange={(_, value) => handleParamChange('numShapes', value as number)}
                min={100}
                max={5000}
                step={100}
                marks={[
                  { value: 1000, label: '1k' },
                  { value: 2000, label: '2k' },
                  { value: 3000, label: '3k' }
                ]}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Max Particle Size: {params.maxParticleSize}</Typography>
              <Slider
                value={params.maxParticleSize}
                onChange={(_, value) => handleParamChange('maxParticleSize', value as number)}
                min={10}
                max={100}
                step={5}
                marks={[
                  { value: 25, label: '25' },
                  { value: 50, label: '50' },
                  { value: 75, label: '75' }
                ]}
                valueLabelDisplay="auto"
              />
            </Box>

            <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
              Rotation Controls
            </Typography>

            <Box sx={{ mb: 2 }}>
              <Typography gutterBottom>Rotation X: {params.rotationX.toFixed(2)}</Typography>
              <Slider
                value={params.rotationX}
                onChange={(_, value) => handleParamChange('rotationX', value as number)}
                min={-Math.PI}
                max={Math.PI}
                step={0.1}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography gutterBottom>Rotation Y: {params.rotationY.toFixed(2)}</Typography>
              <Slider
                value={params.rotationY}
                onChange={(_, value) => handleParamChange('rotationY', value as number)}
                min={-Math.PI}
                max={Math.PI}
                step={0.1}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography gutterBottom>Rotation Z: {params.rotationZ.toFixed(2)}</Typography>
              <Slider
                value={params.rotationZ}
                onChange={(_, value) => handleParamChange('rotationZ', value as number)}
                min={-Math.PI}
                max={Math.PI}
                step={0.1}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={autoRotate}
                    onChange={(e) => setAutoRotate(e.target.checked)}
                  />
                }
                label="Auto Rotate"
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
                sx={{ backgroundColor: '#4285f4' }}
              >
                {isAnimating ? 'Pause' : 'Start'} Animation
              </Button>

              <Button
                variant="outlined"
                onClick={resetRotation}
                startIcon={<RotateRight />}
                fullWidth
              >
                Reset Rotation
              </Button>

              <Button
                variant="outlined"
                onClick={resetSimulation}
                startIcon={<Refresh />}
                fullWidth
              >
                Generate New 3D Scene
              </Button>

              <Button
                variant="outlined"
                onClick={resetToNotebookDefaults}
                fullWidth
                sx={{ mt: 1 }}
              >
                Reset to Notebook Defaults
              </Button>
            </Box>

            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" gutterBottom>
                3D Statistics
              </Typography>
              <Typography variant="body2">
                Zeta Value: <strong>ζ({params.exponent}) = {zetaValue.toFixed(6)}</strong>
              </Typography>
              <Typography variant="body2">
                Placed Shapes: <strong>{shapes.length}</strong>
              </Typography>
              <Typography variant="body2">
                Packing Efficiency: <strong>{((shapes.length / params.numShapes) * 100).toFixed(1)}%</strong>
              </Typography>
            </Box>
          </Box>
        </Grid>
      </Grid>
    </div>
  );
};