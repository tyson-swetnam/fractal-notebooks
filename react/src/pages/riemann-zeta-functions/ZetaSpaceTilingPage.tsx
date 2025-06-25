import React, { useState, useEffect, useCallback } from 'react';
import { Typography, Grid, Slider, Button, Box, Paper, FormControl, InputLabel, Select, MenuItem, Tab, Tabs, Link } from '@mui/material';
import { MathRenderer } from '../../components/math/MathRenderer';
import { Refresh, LightMode } from '@mui/icons-material';
// @ts-ignore
import Plot from 'react-plotly.js';

interface BourkeParams {
  c: number; // Power law exponent (c > 1)
  planeSize: number;
  maxIterations: number;
  maxArea: number; // Maximum area for the largest shape
  shapeType: 'Circle' | 'Triangle' | 'Square' | 'Mixed';
  enableShadows: boolean;
  lightAngle: number; // Illumination angle in degrees
  shadowOpacity: number;
  shadowOffset: number;
  animationSpeed: number;
  colorScheme: 'spectrum' | 'warm' | 'cool' | 'monochrome';
}

interface Point {
  x: number;
  y: number;
}

interface BourkeShape {
  id: number;
  iteration: number;
  center: Point;
  area: number;
  radius: number; // Bounding circle radius
  type: 'Circle' | 'Triangle' | 'Square';
  vertices: Point[]; // For polygons
  angle: number; // Rotation angle
  color: string;
  shadowVertices?: Point[]; // Shadow projection
  depth: number; // For 3D lighting effect
}

// Paul Bourke's Line Intersection Algorithm
const lineIntersect = (p1: Point, p2: Point, p3: Point, p4: Point): { intersects: boolean; point?: Point } => {
  const EPS = 1e-10;
  
  const denom = (p4.y - p3.y) * (p2.x - p1.x) - (p4.x - p3.x) * (p2.y - p1.y);
  const numera = (p4.x - p3.x) * (p1.y - p3.y) - (p4.y - p3.y) * (p1.x - p3.x);
  const numerb = (p2.x - p1.x) * (p1.y - p3.y) - (p2.y - p1.y) * (p1.x - p3.x);

  // Check for coincident lines
  if (Math.abs(numera) < EPS && Math.abs(numerb) < EPS && Math.abs(denom) < EPS) {
    return { intersects: true };
  }

  // Check for parallel lines
  if (Math.abs(denom) < EPS) {
    return { intersects: false };
  }

  const mua = numera / denom;
  const mub = numerb / denom;

  // Check if intersection is within line segments
  if (mua >= 0 && mua <= 1 && mub >= 0 && mub <= 1) {
    const point: Point = {
      x: p1.x + mua * (p2.x - p1.x),
      y: p1.y + mua * (p2.y - p1.y)
    };
    return { intersects: true, point };
  }

  return { intersects: false };
};

// Paul Bourke's Point-in-Polygon Algorithm (Angle Summation Method)
const pointInPolygon = (point: Point, polygon: Point[]): boolean => {
  let angleSum = 0;

  for (let i = 0; i < polygon.length; i++) {
    const p1 = {
      x: polygon[i].x - point.x,
      y: polygon[i].y - point.y
    };
    const p2 = {
      x: polygon[(i + 1) % polygon.length].x - point.x,
      y: polygon[(i + 1) % polygon.length].y - point.y
    };

    const angle = Math.atan2(p2.y, p2.x) - Math.atan2(p1.y, p1.x);
    
    // Normalize angle to [-π, π]
    let normalizedAngle = angle;
    if (normalizedAngle > Math.PI) normalizedAngle -= 2 * Math.PI;
    if (normalizedAngle < -Math.PI) normalizedAngle += 2 * Math.PI;
    
    angleSum += normalizedAngle;
  }

  return Math.abs(angleSum) > Math.PI;
};

// Riemann Zeta function removed (using direct maxArea instead)

// Generate shape based on Bourke's algorithm
const generateShape = (iteration: number, area: number, type: 'Circle' | 'Triangle' | 'Square', center: Point, angle: number): BourkeShape => {
  let vertices: Point[] = [];
  let radius: number;

  switch (type) {
    case 'Circle':
      radius = Math.sqrt(area / Math.PI);
      vertices = []; // Circle doesn't need vertices
      break;
      
    case 'Triangle':
      // Equilateral triangle
      const sideLength = Math.sqrt(4 * area / Math.sqrt(3));
      radius = sideLength / Math.sqrt(3); // Circumradius
      
      for (let i = 0; i < 3; i++) {
        const vertexAngle = angle + (i * 2 * Math.PI) / 3;
        vertices.push({
          x: center.x + radius * Math.cos(vertexAngle),
          y: center.y + radius * Math.sin(vertexAngle)
        });
      }
      break;
      
    case 'Square':
      const squareSide = Math.sqrt(area);
      radius = squareSide * Math.sqrt(2) / 2; // Circumradius
      
      for (let i = 0; i < 4; i++) {
        const vertexAngle = angle + (i * Math.PI) / 2 + Math.PI / 4; // Rotated 45°
        vertices.push({
          x: center.x + radius * Math.cos(vertexAngle),
          y: center.y + radius * Math.sin(vertexAngle)
        });
      }
      break;
  }

  return {
    id: iteration,
    iteration,
    center,
    area,
    radius,
    type,
    vertices,
    angle,
    color: '#4285f4', // Will be set by color scheme
    depth: Math.random() * 0.3 + 0.1 // Random depth for lighting
  };
};

// Check intersection between two shapes using Bourke's method
const shapesIntersect = (shape1: BourkeShape, shape2: BourkeShape): boolean => {
  // First check: bounding circle intersection
  const distance = Math.sqrt(
    Math.pow(shape1.center.x - shape2.center.x, 2) + 
    Math.pow(shape1.center.y - shape2.center.y, 2)
  );
  
  if (distance > shape1.radius + shape2.radius) {
    return false; // Too far apart
  }

  // For circles, bounding circle check is sufficient
  if (shape1.type === 'Circle' && shape2.type === 'Circle') {
    return distance < shape1.radius + shape2.radius;
  }

  // For polygons, detailed intersection check
  if (shape1.type !== 'Circle' && shape2.type !== 'Circle') {
    return polygonsIntersect(shape1.vertices, shape2.vertices);
  }

  // Circle-polygon intersection
  if (shape1.type === 'Circle') {
    return circlePolygonIntersect(shape1.center, shape1.radius, shape2.vertices);
  } else {
    return circlePolygonIntersect(shape2.center, shape2.radius, shape1.vertices);
  }
};

// Check if two polygons intersect
const polygonsIntersect = (poly1: Point[], poly2: Point[]): boolean => {
  // Check if any vertex of poly1 is inside poly2
  for (const vertex of poly1) {
    if (pointInPolygon(vertex, poly2)) {
      return true;
    }
  }
  
  // Check if any vertex of poly2 is inside poly1
  for (const vertex of poly2) {
    if (pointInPolygon(vertex, poly1)) {
      return true;
    }
  }
  
  // Check if any edges intersect
  for (let i = 0; i < poly1.length; i++) {
    const p1 = poly1[i];
    const p2 = poly1[(i + 1) % poly1.length];
    
    for (let j = 0; j < poly2.length; j++) {
      const p3 = poly2[j];
      const p4 = poly2[(j + 1) % poly2.length];
      
      if (lineIntersect(p1, p2, p3, p4).intersects) {
        return true;
      }
    }
  }
  
  return false;
};

// Check circle-polygon intersection
const circlePolygonIntersect = (center: Point, radius: number, polygon: Point[]): boolean => {
  // Check if circle center is inside polygon
  if (pointInPolygon(center, polygon)) {
    return true;
  }
  
  // Check if circle intersects any edge
  for (let i = 0; i < polygon.length; i++) {
    const p1 = polygon[i];
    const p2 = polygon[(i + 1) % polygon.length];
    
    if (circleLineIntersect(center, radius, p1, p2)) {
      return true;
    }
  }
  
  return false;
};

// Check circle-line segment intersection
const circleLineIntersect = (center: Point, radius: number, p1: Point, p2: Point): boolean => {
  const dx = p2.x - p1.x;
  const dy = p2.y - p1.y;
  const lengthSq = dx * dx + dy * dy;
  
  if (lengthSq === 0) {
    // Point case
    const dist = Math.sqrt((center.x - p1.x) ** 2 + (center.y - p1.y) ** 2);
    return dist <= radius;
  }
  
  const t = Math.max(0, Math.min(1, ((center.x - p1.x) * dx + (center.y - p1.y) * dy) / lengthSq));
  const projection = {
    x: p1.x + t * dx,
    y: p1.y + t * dy
  };
  
  const dist = Math.sqrt((center.x - projection.x) ** 2 + (center.y - projection.y) ** 2);
  return dist <= radius;
};


// Shadow and lighting functions removed (not used with black-only color scheme)

export const ZetaSpaceTilingPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  // Animation disabled
  const [params, setParams] = useState<BourkeParams>({
    c: 2.000, // Bourke's power law exponent
    planeSize: 20,
    maxIterations: 1000,
    maxArea: 10.0, // Maximum area for the largest shape
    shapeType: 'Mixed',
    enableShadows: false,
    lightAngle: 45,
    shadowOpacity: 0.3,
    shadowOffset: 2,
    animationSpeed: 50,
    colorScheme: 'spectrum'
  });

  const [shapes, setShapes] = useState<BourkeShape[]>([]);

  // Bourke's Random Tiling Algorithm Implementation
  const generateBourkeTiling = useCallback(() => {
    // Use user-defined maximum area for the largest shape
    const initialArea = params.maxArea;
    
    const newShapes: BourkeShape[] = [];
    const maxAttempts = 1000;
    
    for (let i = 0; i < params.maxIterations; i++) {
      // Bourke's decreasing function: g(i) = 1 / (i * c)
      const area = initialArea / Math.pow(i + 1, params.c);
      
      // Stop if area becomes too small
      if (area < 0.01) break;
      
      // Choose shape type
      let shapeType: 'Circle' | 'Triangle' | 'Square';
      if (params.shapeType === 'Mixed') {
        const shapeTypes: ('Circle' | 'Triangle' | 'Square')[] = ['Circle', 'Triangle', 'Square'];
        shapeType = shapeTypes[Math.floor(Math.random() * shapeTypes.length)];
      } else {
        shapeType = params.shapeType as 'Circle' | 'Triangle' | 'Square';
      }
      
      let placed = false;
      let attempts = 0;
      
      // Try to place shape following Bourke's algorithm
      while (!placed && attempts < maxAttempts) {
        // Random position in plane
        const center: Point = {
          x: (Math.random() - 0.5) * params.planeSize,
          y: (Math.random() - 0.5) * params.planeSize
        };
        
        // Random orientation
        const angle = Math.random() * 2 * Math.PI;
        
        // Generate shape
        const newShape = generateShape(i, area, shapeType, center, angle);
        
        // Set color to black
        newShape.color = '#000000';
        
        // Check for intersections with existing shapes
        let intersects = false;
        for (const existingShape of newShapes) {
          if (shapesIntersect(newShape, existingShape)) {
            intersects = true;
            break;
          }
        }
        
        // Check if shape is within bounds
        const withinBounds = Math.abs(center.x) + newShape.radius <= params.planeSize / 2 &&
                            Math.abs(center.y) + newShape.radius <= params.planeSize / 2;
        
        if (!intersects && withinBounds) {
          
          newShapes.push(newShape);
          placed = true;
        }
        
        attempts++;
      }
      
      if (!placed) {
        console.log(`Could not place shape ${i + 1} after ${maxAttempts} attempts`);
      }
    }
    
    setShapes(newShapes);
    // Animation disabled
  }, [params]);

  // Generate Plotly traces for visualization
  const getPlotlyTraces = useCallback(() => {
    const visibleShapes = shapes;
    const traces: any[] = [];
    
    // Shadows disabled
    
    // Add main shapes
    visibleShapes.forEach((shape, index) => {
      if (shape.type === 'Circle') {
        // Draw circle as a polygon to maintain consistent size across zoom levels
        const numPoints = 64;
        const circleX: number[] = [];
        const circleY: number[] = [];
        
        for (let i = 0; i <= numPoints; i++) {
          const angle = (i * 2 * Math.PI) / numPoints;
          circleX.push(shape.center.x + shape.radius * Math.cos(angle));
          circleY.push(shape.center.y + shape.radius * Math.sin(angle));
        }
        
        traces.push({
          type: 'scatter',
          mode: 'lines',
          x: circleX,
          y: circleY,
          fill: 'toself',
          fillcolor: shape.color,
          line: { color: 'rgba(0,0,0,0.3)', width: 1 },
          hovertemplate: `Circle ${index + 1}<br>Area: ${shape.area.toFixed(3)}<br>Iteration: ${shape.iteration + 1}<extra></extra>`,
          showlegend: false,
          name: `Circle ${index}`
        });
      } else {
        // Polygon shapes
        const x = [...shape.vertices.map(v => v.x), shape.vertices[0].x];
        const y = [...shape.vertices.map(v => v.y), shape.vertices[0].y];
        
        traces.push({
          type: 'scatter',
          mode: 'lines',
          x: x,
          y: y,
          fill: 'toself',
          fillcolor: shape.color,
          line: { color: 'rgba(0,0,0,0.3)', width: 1 },
          hovertemplate: `${shape.type} ${index + 1}<br>Area: ${shape.area.toFixed(3)}<br>Iteration: ${shape.iteration + 1}<extra></extra>`,
          showlegend: false,
          name: `${shape.type} ${index}`
        });
      }
    });
    
    return traces;
  }, [shapes]);

  // Animation and effects
  useEffect(() => {
    generateBourkeTiling();
  }, [generateBourkeTiling]);

  // Animation functions removed

  const handleParamChange = (key: keyof BourkeParams, value: number | string | boolean) => {
    setParams(prev => ({ ...prev, [key]: value }));
  };

  const resetSimulation = () => {
    generateBourkeTiling();
  };

  const plotlyData = getPlotlyTraces();

  return (
    <div className="page-container">
      <Typography variant="h3" component="h1" className="page-title">
        Bourke Random Tiling
      </Typography>
      <Typography variant="body1" className="page-description">
        Interactive implementation of Paul Bourke's random tiling algorithm with Plotly visualization, shadows, and lighting effects.
      </Typography>

      <Paper sx={{ p: 3, mb: 3, backgroundColor: 'background.paper' }}>
        <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
          <Tab label="Visualization" />
          <Tab label="Mathematics" />
        </Tabs>
        
        {activeTab === 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6" gutterBottom>
              Paul Bourke's Random Space Filling Algorithm
            </Typography>
            <Typography variant="body2">
              This visualization implements Paul Bourke's random tiling algorithm with real-time intersection 
              detection. Each shape follows the power law g(i) = 1/(i·c) with non-overlapping placement constraints.
            </Typography>
            <Typography variant="body2" sx={{ mt: 1 }}>
              Algorithm credit: <Link href="https://paulbourke.net/fractals/randomtile/" target="_blank" rel="noopener noreferrer">
                Paul Bourke's Random Tiling
              </Link>
            </Typography>
          </Box>
        )}
        
        {activeTab === 1 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6" gutterBottom>
              Bourke Algorithm Theory
            </Typography>
            <Typography variant="body2" sx={{ mb: 2 }}>
              The algorithm uses a decreasing function to determine object areas at each iteration:
            </Typography>
            <MathRenderer math="g(i) = \frac{1}{i \cdot c}, \quad c > 1" block />
            <Typography variant="body2" sx={{ mt: 2, mb: 2 }}>
              The initial area is calculated using Riemann zeta convergence:
            </Typography>
            <MathRenderer math="A_0 = \frac{\text{Plane Area}}{\zeta(c)}" block />
            <Typography variant="body2" sx={{ mt: 2 }}>
              Each shape's area: <MathRenderer math="A_i = A_0 \cdot g(i)" /> with comprehensive 
              intersection detection using line segment intersection and point-in-polygon tests.
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
                width: 700,
                height: 700,
                xaxis: {
                  title: { text: 'X Coordinate' },
                  range: [-params.planeSize/2, params.planeSize/2],
                  scaleanchor: 'y',
                  scaleratio: 1
                },
                yaxis: {
                  title: { text: 'Y Coordinate' },
                  range: [-params.planeSize/2, params.planeSize/2]
                },
                showlegend: false,
                margin: { l: 60, r: 60, t: 20, b: 60 },
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(255,255,255,1)',
                dragmode: 'pan'
              }}
              style={{ width: '100%', height: '700px' }}
              config={{
                displayModeBar: true,
                displaylogo: false,
                modeBarButtonsToRemove: ['select2d', 'lasso2d', 'autoScale2d']
              }}
            />
            <Typography variant="body2" sx={{ mt: 1, textAlign: 'center' }}>
              Shapes Placed: {shapes.length} | Interactive Plotly View
            </Typography>
          </Box>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Box className="controls-area">
            <Typography variant="h6" gutterBottom>
              Bourke Algorithm Parameters
            </Typography>

            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>Shape Type</InputLabel>
              <Select
                value={params.shapeType}
                label="Shape Type"
                onChange={(e) => handleParamChange('shapeType', e.target.value)}
              >
                <MenuItem value="Circle">Circles</MenuItem>
                <MenuItem value="Triangle">Triangles</MenuItem>
                <MenuItem value="Square">Squares</MenuItem>
                <MenuItem value="Mixed">Mixed Shapes</MenuItem>
              </Select>
            </FormControl>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Power Exponent (c): {params.c.toFixed(3)}</Typography>
              <Slider
                value={params.c}
                onChange={(_, value) => handleParamChange('c', value as number)}
                min={0.001}
                max={2.500}
                step={0.001}
                marks={[
                  { value: 0.500, label: '0.500' },
                  { value: 1.000, label: '1.000' },
                  { value: 1.500, label: '1.500' },
                  { value: 2.000, label: '2.000' },
                  { value: 2.500, label: '2.500' }
                ]}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Plane Size: {params.planeSize}</Typography>
              <Slider
                value={params.planeSize}
                onChange={(_, value) => handleParamChange('planeSize', value as number)}
                min={10}
                max={50}
                step={2}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Max Iterations: {params.maxIterations}</Typography>
              <Slider
                value={params.maxIterations}
                onChange={(_, value) => handleParamChange('maxIterations', value as number)}
                min={100}
                max={10000}
                step={100}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Maximum Shape Area: {params.maxArea.toFixed(1)}</Typography>
              <Slider
                value={params.maxArea}
                onChange={(_, value) => handleParamChange('maxArea', value as number)}
                min={1.0}
                max={50.0}
                step={0.5}
                marks={[
                  { value: 5.0, label: '5.0' },
                  { value: 10.0, label: '10.0' },
                  { value: 25.0, label: '25.0' },
                  { value: 50.0, label: '50.0' }
                ]}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ display: 'flex', gap: 1, flexDirection: 'column' }}>
              <Button
                variant="outlined"
                onClick={resetSimulation}
                startIcon={<Refresh />}
                fullWidth
              >
                Generate New Tiling
              </Button>

              <Button
                variant="outlined"
                onClick={() => {
                  setParams({
                    c: 2.000,
                    planeSize: 20,
                    maxIterations: 1000,
                    maxArea: 10.0,
                    shapeType: 'Mixed',
                    enableShadows: false,
                    lightAngle: 45,
                    shadowOpacity: 0.3,
                    shadowOffset: 2,
                    animationSpeed: 50,
                    colorScheme: 'spectrum'
                  });
                  // Animation disabled
                }}
                startIcon={<LightMode />}
                fullWidth
              >
                Reset to Defaults
              </Button>
            </Box>

          </Box>
        </Grid>
      </Grid>
      
      {/* Tiling Statistics moved to bottom */}
      <Paper sx={{ p: 3, mt: 3, backgroundColor: 'background.paper' }}>
        <Typography variant="h6" gutterBottom>
          Tiling Statistics
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Typography variant="body2">
              Max Shape Area: <strong>{params.maxArea.toFixed(1)}</strong>
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="body2">
              Shapes Placed: <strong>{shapes.length}</strong>
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="body2">
              Power Law: <strong>g(i) = 1/(i·{params.c.toFixed(3)})</strong>
            </Typography>
          </Grid>
        </Grid>
      </Paper>
    </div>
  );
};

export default ZetaSpaceTilingPage;

