import React, { useState, useEffect, useCallback } from 'react';
import { Typography, Grid, Slider, Button, Box, Paper, FormControl, InputLabel, Select, MenuItem, Tab, Tabs } from '@mui/material';
import { MathRenderer } from '../../components/math/MathRenderer';
import { PlayArrow, Pause, Refresh } from '@mui/icons-material';
// @ts-ignore
import Plot from 'react-plotly.js';

interface TreeParams {
  maxDepth: number;
  branchAngle: number;
  angleVariation: number;
  lengthScale: number;
  branchingFactor: number;
  animationSpeed: number;
  treeStyle: 'classic' | 'natural' | 'winter' | 'abstract';
}

interface Branch {
  x: [number, number];
  y: [number, number];
  z?: [number, number];
  angle: number;
  length: number;
  depth: number;
  thickness: number;
  color: string;
}

export const TreePage: React.FC = () => {
  const animationRef = React.useRef<NodeJS.Timeout>();
  const [activeTab, setActiveTab] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);
  const [currentDepth, setCurrentDepth] = useState(0);
  const [params, setParams] = useState<TreeParams>({
    maxDepth: 9,
    branchAngle: 30,
    angleVariation: 15,
    lengthScale: 0.7,
    branchingFactor: 2,
    animationSpeed: 500,
    treeStyle: 'classic'
  });

  const [branches, setBranches] = useState<Branch[]>([]);

  const createChildBranch = useCallback((parent: Branch, angle: number): Branch | null => {
    const length = parent.length * params.lengthScale;
    const thickness = Math.max(1, parent.thickness * 0.7);
    
    const angleRad = (angle * Math.PI) / 180;
    const startX = parent.x[1];
    const startY = parent.y[1];
    const endX = startX + length * Math.cos(angleRad);
    const endY = startY + length * Math.sin(angleRad);
    
    return {
      x: [startX, endX],
      y: [startY, endY],
      angle,
      length,
      depth: parent.depth + 1,
      thickness,
      color: ''
    };
  }, [params.lengthScale]);

  const getBranchColor = useCallback((depth: number, maxDepth: number): string => {
    switch (params.treeStyle) {
      case 'classic':
        return depth === 0 ? '#8B4513' : '#228B22';
      
      case 'natural':
        if (depth <= 2) return '#654321'; // Brown trunk/main branches
        return `hsl(${120 + depth * 10}, 60%, ${40 + depth * 5}%)`; // Green leaves
      
      case 'winter':
        return depth === 0 ? '#4A4A4A' : '#E0E0E0';
      
      case 'abstract':
        const hue = (depth * 60) % 360;
        return `hsl(${hue}, 70%, 50%)`;
      
      default:
        return '#8B4513';
    }
  }, [params.treeStyle]);

  const generateTree = useCallback(() => {
    const newBranches: Branch[] = [];
    
    // Start with the trunk
    const trunkLength = 120;
    const trunk: Branch = {
      x: [0, 0],
      y: [0, trunkLength],
      angle: 90, // Pointing up
      length: trunkLength,
      depth: 0,
      thickness: 8,
      color: getBranchColor(0, params.maxDepth)
    };
    
    newBranches.push(trunk);
    
    // Queue for breadth-first generation
    const queue: Branch[] = [trunk];
    
    while (queue.length > 0) {
      const current = queue.shift()!;
      
      if (current.depth >= params.maxDepth) continue;
      
      // Create child branches
      const numBranches = params.branchingFactor;
      const baseAngle = current.angle;
      
      for (let i = 0; i < numBranches; i++) {
        // Calculate angle for this branch
        let branchAngle;
        if (numBranches === 1) {
          branchAngle = baseAngle + (Math.random() - 0.5) * params.angleVariation;
        } else {
          const angleStep = (params.branchAngle * 2) / (numBranches - 1);
          branchAngle = baseAngle - params.branchAngle + i * angleStep;
          branchAngle += (Math.random() - 0.5) * params.angleVariation;
        }
        
        const childBranch = createChildBranch(current, branchAngle);
        if (childBranch) {
          childBranch.color = getBranchColor(childBranch.depth, params.maxDepth);
          newBranches.push(childBranch);
          queue.push(childBranch);
        }
      }
    }
    
    setBranches(newBranches);
  }, [params.maxDepth, params.branchAngle, params.angleVariation, params.branchingFactor, createChildBranch, getBranchColor]);

  // Prepare Plotly data from branches
  const getPlotlyData = useCallback(() => {
    const visibleBranches = branches.filter(branch => branch.depth <= currentDepth);
    
    const traceData: any[] = visibleBranches.map((branch, index) => ({
      type: 'scatter',
      x: branch.x,
      y: branch.y,
      mode: 'lines',
      line: {
        color: branch.color,
        width: Math.max(1, branch.thickness)
      },
      hoverinfo: 'none',
      showlegend: false,
      name: `Branch ${index}`
    }));
    
    // Add leaves for terminal branches
    const leafBranches = visibleBranches.filter(branch => 
      branch.depth >= params.maxDepth - 2 && 
      (params.treeStyle === 'natural' || params.treeStyle === 'classic')
    );
    
    if (leafBranches.length > 0) {
      const leafTrace = {
        type: 'scatter',
        x: leafBranches.map(branch => branch.x[1]),
        y: leafBranches.map(branch => branch.y[1]),
        mode: 'markers',
        marker: {
          color: params.treeStyle === 'natural' ? '#32CD32' : '#228B22',
          size: leafBranches.map(branch => Math.max(4, branch.thickness * 2))
        },
        hoverinfo: 'none',
        showlegend: false,
        name: 'Leaves'
      };
      traceData.push(leafTrace);
    }
    
    return traceData;
  }, [branches, currentDepth, params.maxDepth, params.treeStyle]);

  // Get background color based on tree style
  const getBackgroundColor = () => {
    switch (params.treeStyle) {
      case 'winter':
        return 'linear-gradient(to bottom, #87CEEB, #F0F8FF)';
      case 'natural':
        return 'linear-gradient(to bottom, #87CEEB, #90EE90)';
      default:
        return 'linear-gradient(to bottom, #191970, #000)';
    }
  };

  const animate = useCallback(() => {
    if (currentDepth < params.maxDepth) {
      setCurrentDepth(prev => prev + 1);
      animationRef.current = setTimeout(() => {
        animate();
      }, params.animationSpeed);
    } else {
      setIsAnimating(false);
    }
  }, [currentDepth, params.maxDepth, params.animationSpeed]);

  const plotlyData = getPlotlyData();

  useEffect(() => {
    generateTree();
    setCurrentDepth(0);
  }, [generateTree]);

  useEffect(() => {
    if (isAnimating && currentDepth < params.maxDepth) {
      animate();
    }
    return () => {
      if (animationRef.current) {
        clearTimeout(animationRef.current);
      }
    };
  }, [isAnimating, animate, currentDepth, params.maxDepth]);

  const handleParamChange = (key: keyof TreeParams, value: number | string) => {
    setParams(prev => ({ ...prev, [key]: value }));
  };

  const toggleAnimation = () => {
    if (isAnimating) {
      setIsAnimating(false);
      if (animationRef.current) {
        clearTimeout(animationRef.current);
      }
    } else {
      setCurrentDepth(0);
      setIsAnimating(true);
    }
  };

  const showFullTree = () => {
    setCurrentDepth(params.maxDepth);
    setIsAnimating(false);
  };

  const resetTree = () => {
    setCurrentDepth(0);
    setIsAnimating(false);
  };

  return (
    <div className="page-container">
      <Typography variant="h3" component="h1" className="page-title">
        Fractal Trees
      </Typography>
      <Typography variant="body1" className="page-description">
        Generate beautiful fractal trees using recursive branching algorithms.
      </Typography>

      <Paper sx={{ p: 3, mb: 3, backgroundColor: 'background.paper' }}>
        <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
          <Tab label="Visualization" />
          <Tab label="Mathematics" />
        </Tabs>
        
        {activeTab === 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6" gutterBottom>
              Interactive Fractal Tree Visualization
            </Typography>
            <Typography variant="body2">
              Generate beautiful fractal trees using recursive branching algorithms with customizable parameters 
              for natural, winter, and abstract tree styles. Watch the tree grow with animated depth progression.
            </Typography>
          </Box>
        )}
        
        {activeTab === 1 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recursive Tree Generation
            </Typography>
            <Typography variant="body2" sx={{ mb: 2 }}>
              Fractal trees are generated using recursive algorithms where each branch spawns multiple child branches. 
              The relationship between generations follows:
            </Typography>
            <MathRenderer 
              math="L_{n+1} = L_n \cdot s, \quad \theta_{n+1} = \theta_n \pm \alpha \pm \delta" 
              block 
            />
            <Typography variant="body2" sx={{ mt: 2 }}>
              where <MathRenderer math="L_n" /> is branch length, <MathRenderer math="s" /> is the scaling factor, 
              <MathRenderer math="\theta_n" /> is the branch angle, <MathRenderer math="\alpha" /> is the branching angle, 
              and <MathRenderer math="\delta" /> is random variation for natural appearance.
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
                xaxis: {
                  visible: false,
                  range: [-200, 200]
                },
                yaxis: {
                  visible: false,
                  range: [-50, 300]
                },
                showlegend: false,
                margin: { l: 0, r: 0, t: 0, b: 0 },
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                dragmode: 'pan'
              }}
              style={{ width: '100%', height: '600px', background: getBackgroundColor() }}
              config={{
                displayModeBar: true,
                displaylogo: false,
                modeBarButtonsToRemove: ['select2d', 'lasso2d', 'autoScale2d']
              }}
            />
            <Typography variant="body2" sx={{ mt: 1, textAlign: 'center' }}>
              Growth Depth: {currentDepth} / {params.maxDepth} | 
              Branches: {branches.filter(b => b.depth <= currentDepth).length} | Interactive Plotly View
            </Typography>
          </Box>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Box className="controls-area">
            <Typography variant="h6" gutterBottom>
              Tree Parameters
            </Typography>

            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>Tree Style</InputLabel>
              <Select
                value={params.treeStyle}
                label="Tree Style"
                onChange={(e) => handleParamChange('treeStyle', e.target.value)}
              >
                <MenuItem value="classic">Classic</MenuItem>
                <MenuItem value="natural">Natural</MenuItem>
                <MenuItem value="winter">Winter</MenuItem>
                <MenuItem value="abstract">Abstract</MenuItem>
              </Select>
            </FormControl>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Max Depth: {params.maxDepth}</Typography>
              <Slider
                value={params.maxDepth}
                onChange={(_, value) => handleParamChange('maxDepth', value as number)}
                min={3}
                max={12}
                step={1}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Branch Angle: {params.branchAngle}°</Typography>
              <Slider
                value={params.branchAngle}
                onChange={(_, value) => handleParamChange('branchAngle', value as number)}
                min={10}
                max={90}
                step={5}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Angle Variation: ±{params.angleVariation}°</Typography>
              <Slider
                value={params.angleVariation}
                onChange={(_, value) => handleParamChange('angleVariation', value as number)}
                min={0}
                max={45}
                step={1}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Length Scale: {params.lengthScale.toFixed(2)}</Typography>
              <Slider
                value={params.lengthScale}
                onChange={(_, value) => handleParamChange('lengthScale', value as number)}
                min={0.4}
                max={0.9}
                step={0.05}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Branching Factor: {params.branchingFactor}</Typography>
              <Slider
                value={params.branchingFactor}
                onChange={(_, value) => handleParamChange('branchingFactor', value as number)}
                min={2}
                max={4}
                step={1}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Animation Speed: {params.animationSpeed}ms</Typography>
              <Slider
                value={params.animationSpeed}
                onChange={(_, value) => handleParamChange('animationSpeed', value as number)}
                min={100}
                max={1000}
                step={50}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ display: 'flex', gap: 1, flexDirection: 'column' }}>
              <Button
                variant="contained"
                onClick={toggleAnimation}
                startIcon={isAnimating ? <Pause /> : <PlayArrow />}
                fullWidth
                sx={{ backgroundColor: '#228B22' }}
              >
                {isAnimating ? 'Pause' : 'Animate'} Growth
              </Button>

              <Button
                variant="outlined"
                onClick={showFullTree}
                fullWidth
              >
                Show Full Tree
              </Button>

              <Button
                variant="outlined"
                onClick={resetTree}
                startIcon={<Refresh />}
                fullWidth
              >
                Reset Tree
              </Button>
            </Box>

            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" gutterBottom>
                Tree Statistics
              </Typography>
              <Typography variant="body2">
                Total Branches: <strong>{branches.length}</strong>
              </Typography>
              <Typography variant="body2">
                Visible Branches: <strong>{branches.filter(b => b.depth <= currentDepth).length}</strong>
              </Typography>
              <Typography variant="body2">
                Fractal Dimension: <strong>≈ {(1.2 + params.branchingFactor * 0.2).toFixed(2)}</strong>
              </Typography>
            </Box>
          </Box>
        </Grid>
      </Grid>
    </div>
  );
};