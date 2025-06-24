import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  Typography, 
  Slider, 
  Button, 
  Box, 
  Paper, 
  IconButton, 
  Drawer,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Fab,
  Collapse,
  Alert,
  Chip,
  Tabs,
  Tab,
  Link
} from '@mui/material';
import { 
  Settings, 
  Info, 
  Close, 
  ZoomIn, 
  ZoomOut, 
  CenterFocusStrong,
  Speed,
  ExpandMore,
  ExpandLess
} from '@mui/icons-material';
import { MandelbrotWebGLGenerator } from '../../utils/mandelbrotWebGL';
import { MathRenderer } from '../../components/math/MathRenderer';

interface MandelbrotParams {
  centerX: number;
  centerY: number;
  zoom: number;
  maxIterations: number;
  colorScheme: 'classic' | 'fire' | 'ocean' | 'psychedelic' | 'grayscale';
}

interface PresetLocation {
  name: string;
  centerX: number;
  centerY: number;
  zoom: number;
  description: string;
}

const interestingLocations: PresetLocation[] = [
  { name: 'Main Set', centerX: -0.5, centerY: 0, zoom: 1, description: 'The classic Mandelbrot set view' },
  { name: 'Seahorse Valley', centerX: -0.7269, centerY: 0.1889, zoom: 100, description: 'Intricate seahorse-like patterns' },
  { name: 'Lightning', centerX: -1.8, centerY: 0, zoom: 50, description: 'Lightning-like fractal structures' },
  { name: 'Spiral', centerX: -0.7453, centerY: 0.11307, zoom: 500, description: 'Beautiful spiral formations' },
  { name: 'Mini Mandelbrot', centerX: -0.16, centerY: 1.0405, zoom: 1000, description: 'Tiny copy of the main set' },
  { name: 'Feather', centerX: -0.7463, centerY: 0.11102, zoom: 2000, description: 'Delicate feather-like structures' }
];

export const MandelbrotPage: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const generatorRef = useRef<MandelbrotWebGLGenerator | null>(null);
  const animationFrameRef = useRef<number>();
  
  // UI State
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [infoOpen, setInfoOpen] = useState(false);
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [isCalculating, setIsCalculating] = useState(false);
  const [webGLSupported, setWebGLSupported] = useState(true);
  const [performanceMode, setPerformanceMode] = useState(false);
  const [isPanning, setIsPanning] = useState(false);
  const [lastMousePos, setLastMousePos] = useState({ x: 0, y: 0 });
  const [infoTabValue, setInfoTabValue] = useState(0);
  
  // Fractal Parameters
  const [params, setParams] = useState<MandelbrotParams>({
    centerX: -0.5,
    centerY: 0,
    zoom: 1,
    maxIterations: 100,
    colorScheme: 'classic'
  });

  // Window dimensions
  const [dimensions, setDimensions] = useState({
    width: window.innerWidth,
    height: window.innerHeight
  });

  // Initialize WebGL renderer
  const initializeWebGL = useCallback(() => {
    if (!canvasRef.current) return;

    try {
      const generator = new MandelbrotWebGLGenerator(canvasRef.current, {
        ...params,
        width: dimensions.width,
        height: dimensions.height
      });
      generatorRef.current = generator;
      setWebGLSupported(true);
    } catch (error) {
      console.error('WebGL initialization failed:', error);
      setWebGLSupported(false);
    }
  }, [params, dimensions]);

  // Render fractal
  const renderFractal = useCallback(() => {
    if (!generatorRef.current) return;

    setIsCalculating(true);
    
    const render = () => {
      if (generatorRef.current) {
        generatorRef.current.updateParams({
          ...params,
          width: dimensions.width,
          height: dimensions.height
        });
        generatorRef.current.render();
      }
      setIsCalculating(false);
    };

    if (performanceMode) {
      // Immediate render for performance mode
      render();
    } else {
      // Slight delay for smooth transitions
      animationFrameRef.current = requestAnimationFrame(render);
    }
  }, [params, dimensions, performanceMode]);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      setDimensions({
        width: window.innerWidth,
        height: window.innerHeight
      });
    };

    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  // Initialize and render
  useEffect(() => {
    initializeWebGL();
  }, [initializeWebGL]);

  useEffect(() => {
    renderFractal();
  }, [renderFractal]);

  // Cleanup
  useEffect(() => {
    return () => {
      if (generatorRef.current) {
        generatorRef.current.dispose();
      }
    };
  }, []);

  const handleParamChange = (key: keyof MandelbrotParams, value: number | string) => {
    setParams(prev => ({ ...prev, [key]: value }));
  };

  const handleCanvasClick = (event: React.MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current || !generatorRef.current || isPanning) return;
    
    const rect = canvasRef.current.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    const complex = generatorRef.current.screenToComplex(x, y);
    
    setParams(prev => ({
      ...prev,
      centerX: complex.x,
      centerY: complex.y,
      zoom: prev.zoom * (event.shiftKey ? 0.5 : 2) // Shift+click to zoom out
    }));
  };

  const handleMouseDown = (event: React.MouseEvent<HTMLCanvasElement>) => {
    if (event.button === 0) { // Left mouse button
      setIsPanning(true);
      setLastMousePos({ x: event.clientX, y: event.clientY });
    }
  };

  const handleMouseMove = (event: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isPanning || !canvasRef.current || !generatorRef.current) return;

    const deltaX = event.clientX - lastMousePos.x;
    const deltaY = event.clientY - lastMousePos.y;
    
    // Convert pixel movement to complex plane movement
    const scale = 4.0 / params.zoom;
    const complexDeltaX = -deltaX * scale / dimensions.width;
    const complexDeltaY = deltaY * scale / dimensions.height;

    setParams(prev => ({
      ...prev,
      centerX: prev.centerX + complexDeltaX,
      centerY: prev.centerY + complexDeltaY
    }));

    setLastMousePos({ x: event.clientX, y: event.clientY });
  };

  const handleMouseUp = () => {
    setIsPanning(false);
  };

  const handleWheel = (event: React.WheelEvent<HTMLCanvasElement>) => {
    event.preventDefault();
    
    if (!canvasRef.current || !generatorRef.current) return;

    const rect = canvasRef.current.getBoundingClientRect();
    const mouseX = event.clientX - rect.left;
    const mouseY = event.clientY - rect.top;
    
    // Get the complex coordinate under the mouse
    const mouseComplex = generatorRef.current.screenToComplex(mouseX, mouseY);
    
    // Zoom factor - negative deltaY means zoom in
    const zoomFactor = event.deltaY > 0 ? 0.8 : 1.25;
    const newZoom = params.zoom * zoomFactor;
    
    // Calculate new center to keep the mouse position fixed
    const zoomRatio = newZoom / params.zoom;
    const newCenterX = mouseComplex.x + (params.centerX - mouseComplex.x) / zoomRatio;
    const newCenterY = mouseComplex.y + (params.centerY - mouseComplex.y) / zoomRatio;
    
    setParams(prev => ({
      ...prev,
      centerX: newCenterX,
      centerY: newCenterY,
      zoom: newZoom
    }));
  };

  const handleKeyPress = useCallback((event: KeyboardEvent) => {
    switch (event.key) {
      case '=':
      case '+':
        setParams(prev => ({ ...prev, zoom: prev.zoom * 1.5 }));
        break;
      case '-':
        setParams(prev => ({ ...prev, zoom: prev.zoom / 1.5 }));
        break;
      case 'r':
        setParams({
          centerX: -0.5,
          centerY: 0,
          zoom: 1,
          maxIterations: 100,
          colorScheme: 'classic'
        });
        break;
      case 'p':
        setPerformanceMode(!performanceMode);
        break;
    }
  }, [performanceMode]);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [handleKeyPress]);

  const goToLocation = (location: PresetLocation) => {
    setParams(prev => ({
      ...prev,
      centerX: location.centerX,
      centerY: location.centerY,
      zoom: location.zoom
    }));
    setSettingsOpen(false);
  };

  if (!webGLSupported) {
    return (
      <Box
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100vw',
          height: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#000',
          color: '#fff'
        }}
      >
        <Alert severity="error" sx={{ maxWidth: 400 }}>
          <Typography variant="h6" gutterBottom>
            WebGL Not Supported
          </Typography>
          <Typography variant="body2">
            This Mandelbrot explorer requires WebGL support. Please use a modern browser 
            or enable WebGL in your browser settings.
          </Typography>
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ position: 'relative', width: '100vw', height: '100vh', overflow: 'hidden' }}>
      {/* Full-screen Canvas */}
      <canvas
        ref={canvasRef}
        width={dimensions.width}
        height={dimensions.height}
        onClick={handleCanvasClick}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          cursor: isCalculating ? 'wait' : isPanning ? 'grabbing' : 'grab',
          backgroundColor: '#000'
        }}
      />

      {/* Floating Title */}
      <Paper
        elevation={8}
        sx={{
          position: 'absolute',
          top: 20,
          left: 20,
          p: 2,
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          borderRadius: 2,
          maxWidth: 400
        }}
      >
        <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold', color: '#1976d2' }}>
          Mandelbrot Set Explorer
        </Typography>
        <Typography variant="body2" color="text.secondary">
          WebGL-Accelerated Real-time Fractal Visualization
        </Typography>
        
        {/* Quick Stats */}
        <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Chip 
            size="small" 
            label={`Zoom: ${params.zoom.toExponential(2)}`} 
            variant="outlined" 
          />
          <Chip 
            size="small" 
            label={`Iterations: ${params.maxIterations}`} 
            variant="outlined" 
          />
          <Chip 
            size="small" 
            label={params.colorScheme} 
            variant="outlined" 
          />
          {performanceMode && (
            <Chip 
              size="small" 
              label="Performance Mode" 
              color="success" 
              variant="outlined" 
            />
          )}
        </Box>
      </Paper>

      {/* Quick Controls */}
      <Paper
        elevation={8}
        sx={{
          position: 'absolute',
          top: 20,
          right: 20,
          p: 1,
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          borderRadius: 2,
          display: 'flex',
          flexDirection: 'column',
          gap: 1
        }}
      >
        <IconButton 
          onClick={() => setParams(prev => ({ ...prev, zoom: prev.zoom * 2 }))}
          size="small"
          title="Zoom In (+)"
        >
          <ZoomIn />
        </IconButton>
        <IconButton 
          onClick={() => setParams(prev => ({ ...prev, zoom: prev.zoom / 2 }))}
          size="small"
          title="Zoom Out (-)"
        >
          <ZoomOut />
        </IconButton>
        <IconButton 
          onClick={() => setParams({
            centerX: -0.5,
            centerY: 0,
            zoom: 1,
            maxIterations: 100,
            colorScheme: 'classic'
          })}
          size="small"
          title="Reset (R)"
        >
          <CenterFocusStrong />
        </IconButton>
      </Paper>

      {/* Floating Action Buttons */}
      <Fab
        color="primary"
        sx={{ position: 'absolute', bottom: 80, right: 20 }}
        onClick={() => setSettingsOpen(true)}
      >
        <Settings />
      </Fab>

      <Fab
        color="secondary"
        sx={{ position: 'absolute', bottom: 80, right: 100 }}
        onClick={() => setInfoOpen(true)}
      >
        <Info />
      </Fab>

      {/* Controls Drawer */}
      <Drawer
        anchor="left"
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        PaperProps={{
          sx: { 
            width: 400, 
            backgroundColor: 'rgba(255, 255, 255, 0.98)',
            backdropFilter: 'blur(10px)'
          }
        }}
      >
        <Box sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6">Fractal Controls</Typography>
            <IconButton onClick={() => setSettingsOpen(false)}>
              <Close />
            </IconButton>
          </Box>

          {/* Location Presets */}
          <Typography variant="h6" gutterBottom>
            Interesting Locations
          </Typography>
          <Box sx={{ mb: 3 }}>
            {interestingLocations.map((location) => (
              <Button
                key={location.name}
                variant="outlined"
                size="small"
                onClick={() => goToLocation(location)}
                sx={{ mr: 1, mb: 1 }}
              >
                {location.name}
              </Button>
            ))}
          </Box>

          {/* Color Scheme */}
          <FormControl fullWidth sx={{ mb: 3 }}>
            <InputLabel>Color Scheme</InputLabel>
            <Select
              value={params.colorScheme}
              label="Color Scheme"
              onChange={(e) => handleParamChange('colorScheme', e.target.value)}
            >
              <MenuItem value="classic">Classic Rainbow</MenuItem>
              <MenuItem value="fire">Fire</MenuItem>
              <MenuItem value="ocean">Ocean</MenuItem>
              <MenuItem value="psychedelic">Psychedelic</MenuItem>
              <MenuItem value="grayscale">Grayscale</MenuItem>
            </Select>
          </FormControl>

          {/* Basic Controls */}
          <Box sx={{ mb: 3 }}>
            <Typography gutterBottom>Max Iterations: {params.maxIterations}</Typography>
            <Slider
              value={params.maxIterations}
              onChange={(_, value) => handleParamChange('maxIterations', value as number)}
              min={50}
              max={1000}
              step={10}
              marks={[
                { value: 100, label: '100' },
                { value: 500, label: '500' },
                { value: 1000, label: '1000' }
              ]}
            />
          </Box>

          {/* Advanced Controls */}
          <Button
            variant="text"
            onClick={() => setAdvancedOpen(!advancedOpen)}
            startIcon={advancedOpen ? <ExpandLess /> : <ExpandMore />}
            sx={{ mb: 2 }}
          >
            Advanced Controls
          </Button>

          <Collapse in={advancedOpen}>
            <Box sx={{ pl: 2 }}>
              <Box sx={{ mb: 3 }}>
                <Typography gutterBottom>Center X: {params.centerX.toFixed(8)}</Typography>
                <Slider
                  value={params.centerX}
                  onChange={(_, value) => handleParamChange('centerX', value as number)}
                  min={-2}
                  max={1}
                  step={0.000001}
                  valueLabelDisplay="auto"
                  valueLabelFormat={(value) => value.toFixed(6)}
                />
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography gutterBottom>Center Y: {params.centerY.toFixed(8)}</Typography>
                <Slider
                  value={params.centerY}
                  onChange={(_, value) => handleParamChange('centerY', value as number)}
                  min={-1.5}
                  max={1.5}
                  step={0.000001}
                  valueLabelDisplay="auto"
                  valueLabelFormat={(value) => value.toFixed(6)}
                />
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography gutterBottom>Zoom: {params.zoom.toExponential(2)}</Typography>
                <Slider
                  value={Math.log10(params.zoom)}
                  onChange={(_, value) => handleParamChange('zoom', Math.pow(10, value as number))}
                  min={0}
                  max={12}
                  step={0.1}
                  marks={[
                    { value: 0, label: '1' },
                    { value: 3, label: '1K' },
                    { value: 6, label: '1M' },
                    { value: 9, label: '1B' },
                    { value: 12, label: '1T' }
                  ]}
                  valueLabelDisplay="auto"
                  valueLabelFormat={(value) => `10^${value.toFixed(1)}`}
                />
              </Box>
            </Box>
          </Collapse>

          {/* Performance Settings */}
          <Button
            variant={performanceMode ? "contained" : "outlined"}
            onClick={() => setPerformanceMode(!performanceMode)}
            startIcon={<Speed />}
            fullWidth
            sx={{ mb: 2 }}
          >
            Performance Mode
          </Button>

          {/* Instructions */}
          <Alert severity="info" sx={{ mt: 2 }}>
            <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
              Mouse Controls:
            </Typography>
            <Typography variant="body2">
              • Mouse wheel to zoom in/out<br/>
              • Click and drag to pan<br/>
              • Click to zoom in and center<br/>
              • Shift+Click to zoom out
            </Typography>
            <Typography variant="body2" sx={{ fontWeight: 'bold', mt: 1 }}>
              Keyboard Shortcuts:
            </Typography>
            <Typography variant="body2">
              • +/- keys to zoom<br/>
              • R key to reset<br/>
              • P key for performance mode
            </Typography>
          </Alert>
        </Box>
      </Drawer>

      {/* Info Drawer */}
      <Drawer
        anchor="right"
        open={infoOpen}
        onClose={() => setInfoOpen(false)}
        PaperProps={{
          sx: { 
            width: 500, 
            backgroundColor: 'rgba(255, 255, 255, 0.98)',
            backdropFilter: 'blur(10px)'
          }
        }}
      >
        <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', p: 3, pb: 0 }}>
            <Typography variant="h6">Mandelbrot Explorer</Typography>
            <IconButton onClick={() => setInfoOpen(false)}>
              <Close />
            </IconButton>
          </Box>

          <Tabs 
            value={infoTabValue} 
            onChange={(_, newValue) => setInfoTabValue(newValue)}
            sx={{ borderBottom: 1, borderColor: 'divider', px: 3 }}
          >
            <Tab label="Mathematics" />
            <Tab label="Technical Info" />
            <Tab label="Performance" />
          </Tabs>

          <Box sx={{ flex: 1, overflow: 'auto', p: 3 }}>
            {infoTabValue === 0 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  The Mandelbrot Set
                </Typography>
                <Typography variant="body2" sx={{ mb: 2 }}>
                  The Mandelbrot set is defined as the set of complex numbers <MathRenderer math="c" /> for which the sequence:
                </Typography>
                <MathRenderer math="z_0 = 0, \quad z_{n+1} = z_n^2 + c" block />
                <Typography variant="body2" sx={{ mt: 2, mb: 3 }}>
                  remains bounded as <MathRenderer math="n \to \infty" />. Points where <MathRenderer math="|z_n| > 2" /> 
                  for some <MathRenderer math="n" /> escape to infinity and are colored based on the iteration count.
                </Typography>

                <Typography variant="h6" gutterBottom>
                  Mathematical Properties
                </Typography>
                <Typography variant="body2" sx={{ mb: 2 }}>
                  • The set is connected and has fractal dimension approximately 2<br/>
                  • It exhibits self-similarity at different scales<br/>
                  • The boundary has infinite length but encloses finite area<br/>
                  • Contains infinitely many miniature copies of itself
                </Typography>

                <Typography variant="h6" gutterBottom>
                  Complex Dynamics
                </Typography>
                <Typography variant="body2">
                  The iteration formula <MathRenderer math="z_{n+1} = z_n^2 + c" /> represents a quadratic polynomial in the complex plane. 
                  The behavior of this dynamical system determines whether a point belongs to the Mandelbrot set.
                </Typography>
              </Box>
            )}

            {infoTabValue === 1 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  WebGL Implementation
                </Typography>
                <Typography variant="body2" sx={{ mb: 3 }}>
                  This implementation uses WebGL shaders to compute the Mandelbrot set in parallel on your GPU, 
                  enabling real-time exploration of the fractal at high resolutions and zoom levels.
                </Typography>

                <Typography variant="h6" gutterBottom>
                  Current Location
                </Typography>
                <Box sx={{ 
                  backgroundColor: 'rgba(0, 0, 0, 0.05)', 
                  p: 2, 
                  borderRadius: 1, 
                  fontFamily: 'monospace',
                  mb: 3
                }}>
                  <Typography variant="body2">
                    Center: {params.centerX.toFixed(10)} + {params.centerY.toFixed(10)}i<br/>
                    Zoom: {params.zoom.toExponential(3)}<br/>
                    Iterations: {params.maxIterations}<br/>
                    Resolution: {dimensions.width} × {dimensions.height}<br/>
                    Color Scheme: {params.colorScheme}
                  </Typography>
                </Box>

                <Typography variant="h6" gutterBottom>
                  Technical Details
                </Typography>
                <Typography variant="body2">
                  • GPU-accelerated fragment shaders for parallel computation<br/>
                  • Real-time parameter updates without recompilation<br/>
                  • High-precision floating point calculations<br/>
                  • Optimized for interactive exploration up to extreme zoom levels
                </Typography>
              </Box>
            )}

            {infoTabValue === 2 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Performance Optimization
                </Typography>
                <Typography variant="body2" sx={{ mb: 3 }}>
                  • Performance Mode reduces visual effects for faster rendering<br/>
                  • Lower iteration counts render faster but with less detail<br/>
                  • WebGL utilizes your graphics card for parallel computation<br/>
                  • Real-time rendering at 60fps for smooth exploration
                </Typography>

                <Typography variant="h6" gutterBottom>
                  Rendering Statistics
                </Typography>
                <Box sx={{ 
                  backgroundColor: 'rgba(0, 0, 0, 0.05)', 
                  p: 2, 
                  borderRadius: 1, 
                  fontFamily: 'monospace',
                  mb: 3
                }}>
                  <Typography variant="body2">
                    Pixel Count: {(dimensions.width * dimensions.height).toLocaleString()}<br/>
                    GPU Threads: ~{Math.floor((dimensions.width * dimensions.height) / 64).toLocaleString()} warps<br/>
                    Max Iterations: {params.maxIterations}<br/>
                    Performance Mode: {performanceMode ? 'Enabled' : 'Disabled'}
                  </Typography>
                </Box>

                <Typography variant="h6" gutterBottom>
                  Tips for Better Performance
                </Typography>
                <Typography variant="body2">
                  • Enable Performance Mode for older graphics cards<br/>
                  • Reduce iteration count for faster initial exploration<br/>
                  • Close other GPU-intensive applications<br/>
                  • Use keyboard shortcuts for rapid navigation
                </Typography>
              </Box>
            )}
          </Box>

          {/* WebGL Code Reference Footer */}
          <Box sx={{ 
            p: 2, 
            borderTop: 1, 
            borderColor: 'divider', 
            backgroundColor: 'rgba(0, 0, 0, 0.02)' 
          }}>
            <Typography variant="caption" color="text.secondary">
              WebGL implementation inspired by{' '}
              <Link 
                href="https://webglfundamentals.org/webgl/lessons/webgl-fundamentals.html" 
                target="_blank" 
                rel="noopener noreferrer"
                color="primary"
              >
                WebGL Fundamentals
              </Link>
              {' '}and optimized for real-time fractal exploration.
            </Typography>
          </Box>
        </Box>
      </Drawer>

      {/* Loading Indicator */}
      {isCalculating && (
        <Box
          sx={{
            position: 'absolute',
            bottom: 20,
            left: 20,
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            color: 'white',
            px: 2,
            py: 1,
            borderRadius: 1
          }}
        >
          <Typography variant="body2">Rendering...</Typography>
        </Box>
      )}
    </Box>
  );
};