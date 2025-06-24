import React, { useState, useEffect, useCallback } from 'react';
import { Typography, Grid, Slider, Button, Box, Paper, Tab, Tabs } from '@mui/material';
import { MathRenderer } from '../../components/math/MathRenderer';
import { PlayArrow } from '@mui/icons-material';
// @ts-ignore
import Plot from 'react-plotly.js';

interface TreeParams {
  // Crown parameters
  crownLevels: number;
  crownLength: number;
  crownRadius: number;
  crownTaper: number;
  crownAngle: number;
  crownLengthReduction: number;
  crownBranches: number;
  
  // Root parameters
  rootLevels: number;
  rootLength: number;
  rootRadius: number;
  rootTaper: number;
  rootAngle: number;
  rootLengthReduction: number;
  rootBranches: number;
}

interface TreeElement {
  x: number[];
  y: number[];
  z: number[];
  faces: number[][];
  color: string;
}

// Vector operations
const vectorLength = (v: number[]): number => Math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
const normalize = (v: number[]): number[] => {
  const len = vectorLength(v);
  return len > 0 ? [v[0] / len, v[1] / len, v[2] / len] : [0, 0, 0];
};
const add = (a: number[], b: number[]): number[] => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const scale = (v: number[], s: number): number[] => [v[0] * s, v[1] * s, v[2] * s];
const cross = (a: number[], b: number[]): number[] => [
  a[1] * b[2] - a[2] * b[1],
  a[2] * b[0] - a[0] * b[2],
  a[0] * b[1] - a[1] * b[0]
];
const dot = (a: number[], b: number[]): number => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];

// Rotation using Rodrigues' rotation formula (same as Streamlit version)
const rotateVector = (v: number[], k: number[], theta: number): number[] => {
  const cosTheta = Math.cos(theta);
  const sinTheta = Math.sin(theta);
  const dotProduct = k[0] * v[0] + k[1] * v[1] + k[2] * v[2];
  const crossProduct = cross(k, v);
  
  return [
    v[0] * cosTheta + crossProduct[0] * sinTheta + k[0] * dotProduct * (1 - cosTheta),
    v[1] * cosTheta + crossProduct[1] * sinTheta + k[1] * dotProduct * (1 - cosTheta),
    v[2] * cosTheta + crossProduct[2] * sinTheta + k[2] * dotProduct * (1 - cosTheta)
  ];
};

export const TreeRoots3DPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [params, setParams] = useState<TreeParams>({
    crownLevels: 5,
    crownLength: 7.0,
    crownRadius: 0.5,
    crownTaper: 0.7,
    crownAngle: 30,
    crownLengthReduction: 0.7,
    crownBranches: 3,
    
    rootLevels: 4,
    rootLength: 5.0,
    rootRadius: 0.4,
    rootTaper: 0.7,
    rootAngle: 45,
    rootLengthReduction: 0.8,
    rootBranches: 2
  });

  const [treeElements, setTreeElements] = useState<TreeElement[]>([]);

  const generateCylinder = useCallback((p0: number[], p1: number[], radiusBase: number, radiusTop: number, sections: number = 8): TreeElement | null => {
    const v = [p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]];
    const length = vectorLength(v);
    
    if (length === 0) return null;
    
    const vNorm = normalize(v);
    let notV = [1, 0, 0];
    if (Math.abs(dot(vNorm, notV)) > 0.99) {
      notV = [0, 1, 0];
    }
    
    const n1 = normalize(cross(vNorm, notV));
    const n2 = cross(vNorm, n1);
    
    const t = Array.from({ length: sections }, (_, i) => (i * 2 * Math.PI) / sections);
    
    // Base circle vertices
    const baseCircle = t.map(angle => {
      const circlePoint = [
        n1[0] * Math.cos(angle) + n2[0] * Math.sin(angle),
        n1[1] * Math.cos(angle) + n2[1] * Math.sin(angle),
        n1[2] * Math.cos(angle) + n2[2] * Math.sin(angle)
      ];
      return add(p0, scale(circlePoint, radiusBase));
    });
    
    // Top circle vertices
    const topCircle = t.map(angle => {
      const circlePoint = [
        n1[0] * Math.cos(angle) + n2[0] * Math.sin(angle),
        n1[1] * Math.cos(angle) + n2[1] * Math.sin(angle),
        n1[2] * Math.cos(angle) + n2[2] * Math.sin(angle)
      ];
      return add(p1, scale(circlePoint, radiusTop));
    });
    
    // Combine all vertices
    const allVertices = [...baseCircle, ...topCircle];
    const x = allVertices.map(v => v[0]);
    const y = allVertices.map(v => v[1]);
    const z = allVertices.map(v => v[2]);
    
    // Generate faces (side faces only, no caps)
    const faces: number[][] = [];
    const n = sections;
    for (let i = 0; i < n; i++) {
      const nextI = (i + 1) % n;
      // Two triangles per quad
      faces.push([i, nextI, n + nextI]);
      faces.push([i, n + nextI, n + i]);
    }
    
    return { x, y, z, faces, color: 'saddlebrown' };
  }, []);

  const growTree = useCallback((
    p0: number[],
    direction: number[],
    length: number,
    radiusBase: number,
    taperRatio: number,
    levels: number,
    angle: number,
    lengthReduction: number,
    branchesPerLevel: number,
    elements: TreeElement[],
    isRoot: boolean = false
  ): void => {
    if (levels === 0 || radiusBase < 0.01 || length < 0.01) return;
    
    let p1 = add(p0, scale(direction, length));
    if (isRoot && p1[2] > 0) {
      p1[2] = 0;
    }
    
    const radiusTop = radiusBase * taperRatio;
    const cylinder = generateCylinder(p0, p1, radiusBase, radiusTop);
    
    if (cylinder) {
      cylinder.color = isRoot ? 'sienna' : 'saddlebrown';
      elements.push(cylinder);
    }
    
    const N = branchesPerLevel;
    const radiusBaseChild = N > 0 ? radiusTop / Math.sqrt(N) : 0;
    const lengthChild = length * lengthReduction;
    
    for (let i = 0; i < N; i++) {
      let theta: number;
      if (isRoot) {
        const minTheta = Math.PI / 2;
        const maxTheta = Math.PI / 2 + (angle * Math.PI) / 180;
        theta = minTheta + Math.random() * (maxTheta - minTheta);
      } else {
        const minTheta = 0;
        const maxTheta = (angle * Math.PI) / 180;
        theta = minTheta + Math.random() * (maxTheta - minTheta);
      }
      
      theta += (Math.random() - 0.5) * (10 * Math.PI) / 180;
      const phi = Math.random() * 2 * Math.PI;
      
      if (isRoot) {
        theta = Math.max(Math.PI / 2, Math.min(Math.PI, theta));
      } else {
        theta = Math.max(0, Math.min(Math.PI / 2, theta));
      }
      
      // Create new direction in spherical coordinates
      let newDirection = [
        Math.sin(theta) * Math.cos(phi),
        Math.sin(theta) * Math.sin(phi),
        Math.cos(theta)
      ];
      
      // Rotate new direction to align with current branch direction
      const rotationAxis = cross([0, 0, 1], direction);
      const rotationAngle = Math.acos(Math.max(-1, Math.min(1, dot(direction, [0, 0, 1]))));
      
      if (vectorLength(rotationAxis) > 1e-6) {
        const normalizedAxis = normalize(rotationAxis);
        newDirection = rotateVector(newDirection, normalizedAxis, rotationAngle);
      }
      
      growTree(
        p1,
        newDirection,
        lengthChild,
        radiusBaseChild,
        taperRatio,
        levels - 1,
        angle,
        lengthReduction,
        branchesPerLevel,
        elements,
        isRoot
      );
    }
  }, [generateCylinder]);

  const generateTree = useCallback(() => {
    const elements: TreeElement[] = [];
    const p0 = [0, 0, 0];
    
    // Generate crown (upward)
    const direction = [0, 0, 1];
    growTree(
      p0,
      direction,
      params.crownLength,
      params.crownRadius,
      params.crownTaper,
      params.crownLevels,
      params.crownAngle,
      params.crownLengthReduction,
      params.crownBranches,
      elements,
      false
    );
    
    // Generate roots (downward)
    const directionRoot = [0, 0, -1];
    growTree(
      p0,
      directionRoot,
      params.rootLength,
      params.rootRadius,
      params.rootTaper,
      params.rootLevels,
      params.rootAngle,
      params.rootLengthReduction,
      params.rootBranches,
      elements,
      true
    );
    
    setTreeElements(elements);
  }, [params, growTree]);

  // Prepare Plotly data from tree elements
  const plotlyData = treeElements.map((elem, index) => ({
    type: 'mesh3d' as const,
    x: elem.x,
    y: elem.y,
    z: elem.z,
    i: elem.faces.map(face => face[0]),
    j: elem.faces.map(face => face[1]),
    k: elem.faces.map(face => face[2]),
    color: elem.color,
    flatshading: true,
    lighting: {
      ambient: 0.5,
      diffuse: 0.8,
      roughness: 0.9
    },
    showscale: false,
    name: `Tree Part ${index + 1}`
  })) as any;

  useEffect(() => {
    generateTree();
  }, [generateTree]);

  const handleParamChange = (key: keyof TreeParams, value: number) => {
    setParams(prev => ({ ...prev, [key]: value }));
  };

  const regenerateTree = () => {
    generateTree();
  };

  return (
    <div className="page-container">
      <Typography variant="h3" component="h1" className="page-title">
        3D Tree with Roots Visualization
      </Typography>
      <Typography variant="body1" className="page-description">
        Interactive 3D fractal tree generation with customizable crown and root systems using recursive branching algorithms.
      </Typography>

      <Paper sx={{ p: 3, mb: 3, backgroundColor: 'background.paper' }}>
        <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
          <Tab label="Visualization" />
          <Tab label="Mathematics" />
        </Tabs>
        
        {activeTab === 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6" gutterBottom>
              3D Fractal Tree with Root System
            </Typography>
            <Typography variant="body2">
              This visualization generates a complete tree structure with both crown (above ground) and root system (below ground) 
              using recursive fractal algorithms. Each branch and root is modeled as a tapered cylinder with realistic branching patterns.
            </Typography>
          </Box>
        )}
        
        {activeTab === 1 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6" gutterBottom>
              Mathematical Foundation
            </Typography>
            <Typography variant="body2" sx={{ mb: 2 }}>
              The tree generation follows recursive branching rules with geometric constraints:
            </Typography>
            <MathRenderer 
              math="r_{child} = \frac{r_{parent} \cdot t}{\sqrt{N}}" 
              block 
            />
            <Typography variant="body2" sx={{ mt: 2, mb: 2 }}>
              Where the length reduction follows:
            </Typography>
            <MathRenderer 
              math="l_{child} = l_{parent} \cdot \lambda" 
              block 
            />
            <Typography variant="body2" sx={{ mt: 2 }}>
              Branch directions are determined by spherical coordinates with angular constraints, 
              creating realistic 3D tree architectures that follow botanical scaling laws.
            </Typography>
          </Box>
        )}
      </Paper>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <Box className="visualization-area">
            <Plot
              data={plotlyData}
              layout={{
                scene: {
                  xaxis: { visible: false },
                  yaxis: { visible: false },
                  zaxis: { visible: false },
                  aspectmode: 'data' as const
                },
                showlegend: false,
                margin: { l: 0, r: 0, t: 0, b: 0 },
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)'
              }}
              style={{ width: '100%', height: '600px' }}
              config={{
                displayModeBar: true,
                displaylogo: false,
                modeBarButtonsToRemove: ['pan2d', 'select2d', 'lasso2d', 'autoScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian']
              }}
            />
            <Typography variant="body2" sx={{ mt: 1, textAlign: 'center' }}>
              Tree Elements: {treeElements.length} | Interactive 3D Plotly View
            </Typography>
          </Box>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Box className="controls-area">
            <Typography variant="h6" gutterBottom>
              Crown Parameters
            </Typography>

            <Box sx={{ mb: 2 }}>
              <Typography gutterBottom>Crown Levels: {params.crownLevels}</Typography>
              <Slider
                value={params.crownLevels}
                onChange={(_, value) => handleParamChange('crownLevels', value as number)}
                min={1}
                max={8}
                step={1}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography gutterBottom>Crown Length: {params.crownLength}</Typography>
              <Slider
                value={params.crownLength}
                onChange={(_, value) => handleParamChange('crownLength', value as number)}
                min={1.0}
                max={15.0}
                step={0.5}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography gutterBottom>Crown Radius: {params.crownRadius}</Typography>
              <Slider
                value={params.crownRadius}
                onChange={(_, value) => handleParamChange('crownRadius', value as number)}
                min={0.1}
                max={1.5}
                step={0.1}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography gutterBottom>Crown Taper: {params.crownTaper}</Typography>
              <Slider
                value={params.crownTaper}
                onChange={(_, value) => handleParamChange('crownTaper', value as number)}
                min={0.5}
                max={1.0}
                step={0.05}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography gutterBottom>Crown Angle: {params.crownAngle}°</Typography>
              <Slider
                value={params.crownAngle}
                onChange={(_, value) => handleParamChange('crownAngle', value as number)}
                min={10}
                max={80}
                step={5}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography gutterBottom>Crown Length Reduction: {params.crownLengthReduction}</Typography>
              <Slider
                value={params.crownLengthReduction}
                onChange={(_, value) => handleParamChange('crownLengthReduction', value as number)}
                min={0.5}
                max={1.0}
                step={0.05}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Crown Branches: {params.crownBranches}</Typography>
              <Slider
                value={params.crownBranches}
                onChange={(_, value) => handleParamChange('crownBranches', value as number)}
                min={0}
                max={8}
                step={1}
                valueLabelDisplay="auto"
              />
            </Box>

            <Typography variant="h6" gutterBottom>
              Root Parameters
            </Typography>

            <Box sx={{ mb: 2 }}>
              <Typography gutterBottom>Root Levels: {params.rootLevels}</Typography>
              <Slider
                value={params.rootLevels}
                onChange={(_, value) => handleParamChange('rootLevels', value as number)}
                min={1}
                max={8}
                step={1}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography gutterBottom>Root Length: {params.rootLength}</Typography>
              <Slider
                value={params.rootLength}
                onChange={(_, value) => handleParamChange('rootLength', value as number)}
                min={1.0}
                max={15.0}
                step={0.5}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography gutterBottom>Root Radius: {params.rootRadius}</Typography>
              <Slider
                value={params.rootRadius}
                onChange={(_, value) => handleParamChange('rootRadius', value as number)}
                min={0.1}
                max={1.5}
                step={0.1}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography gutterBottom>Root Angle: {params.rootAngle}°</Typography>
              <Slider
                value={params.rootAngle}
                onChange={(_, value) => handleParamChange('rootAngle', value as number)}
                min={10}
                max={80}
                step={5}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Root Branches: {params.rootBranches}</Typography>
              <Slider
                value={params.rootBranches}
                onChange={(_, value) => handleParamChange('rootBranches', value as number)}
                min={0}
                max={8}
                step={1}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ display: 'flex', gap: 1, flexDirection: 'column' }}>
              <Button
                variant="contained"
                onClick={regenerateTree}
                startIcon={<PlayArrow />}
                fullWidth
                sx={{ backgroundColor: '#228B22' }}
              >
                Regenerate Tree
              </Button>
            </Box>
          </Box>
        </Grid>
      </Grid>
    </div>
  );
};