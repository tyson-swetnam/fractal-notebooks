import React from 'react';
import { HashRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';
import { createCustomTheme } from './utils/themes';
import { Navigation } from './components/layout/Navigation';
import { HomePage } from './pages/HomePage';
// 1D/2D/3D Fractals
import { MandelbrotPage } from './pages/fractals-1d-2d-3d/MandelbrotPage';
import { JuliaPage } from './pages/fractals-1d-2d-3d/JuliaPage';
import { BrownianMotionPage } from './pages/fractals-1d-2d-3d/BrownianMotionPage';
import { ConwayGameOfLifePage } from './pages/fractals-1d-2d-3d/ConwayGameOfLifePage';
import { NoisePage } from './pages/fractals-1d-2d-3d/NoisePage';
import { WavesPage } from './pages/fractals-1d-2d-3d/WavesPage';
// Branching Architectures
import { DLAPage } from './pages/branching-architectures/DLAPage';
import { FernPage } from './pages/branching-architectures/FernPage';
import { TreePage } from './pages/branching-architectures/TreePage';
import { PythagorasTreePage } from './pages/branching-architectures/PythagorasTreePage';
import { TreeRoots3DPage } from './pages/branching-architectures/TreeRoots3DPage';
// Riemann Zeta Functions
import { ZetaSpaceTilingPage } from './pages/riemann-zeta-functions/ZetaSpaceTilingPage';
import { Zeta3DVisualizationPage } from './pages/riemann-zeta-functions/Zeta3DVisualizationPage';
import './App.css';

const AppContent: React.FC = () => {
  const { effectiveTheme } = useTheme();
  const theme = createCustomTheme(effectiveTheme);

  // Set data attribute on body for theme-specific CSS
  React.useEffect(() => {
    document.body.setAttribute('data-theme', effectiveTheme);
  }, [effectiveTheme]);

  return (
    <MuiThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <div className="App">
          <Navigation />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<HomePage />} />
              {/* 1D/2D/3D Fractals */}
              <Route path="/mandelbrot" element={<MandelbrotPage />} />
              <Route path="/julia" element={<JuliaPage />} />
              <Route path="/brownian" element={<BrownianMotionPage />} />
              <Route path="/conway" element={<ConwayGameOfLifePage />} />
              <Route path="/noise" element={<NoisePage />} />
              <Route path="/waves" element={<WavesPage />} />
              {/* Branching Architectures */}
              <Route path="/dla" element={<DLAPage />} />
              <Route path="/ferns" element={<FernPage />} />
              <Route path="/trees" element={<TreePage />} />
              <Route path="/pythagoras" element={<PythagorasTreePage />} />
              <Route path="/tree-roots-3d" element={<TreeRoots3DPage />} />
              {/* Riemann Zeta Functions */}
              <Route path="/zeta-space-tiling" element={<ZetaSpaceTilingPage />} />
              <Route path="/zeta-3d-visualization" element={<Zeta3DVisualizationPage />} />
            </Routes>
          </main>
        </div>
      </Router>
    </MuiThemeProvider>
  );
};

function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

export default App;