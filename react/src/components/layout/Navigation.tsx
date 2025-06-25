import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  useMediaQuery,
  useTheme,
  Menu,
  MenuItem,
} from '@mui/material';
import { ExpandMore } from '@mui/icons-material';
import { Link, useLocation } from 'react-router-dom';
import { ThemeToggle } from './ThemeToggle';

type NavItem = 
  | { path: string; label: string }
  | { label: string; items: { path: string; label: string }[] };

const navItems: NavItem[] = [
  { path: '/', label: 'Home' },
  { 
    label: '1D/2D/3D Fractals',
    items: [
      { path: '/mandelbrot', label: 'Mandelbrot Set' },
      { path: '/julia', label: 'Julia Sets' },
      { path: '/brownian', label: 'Brownian Motion' },
      { path: '/conway', label: 'Conway\'s Game of Life' },
      { path: '/noise', label: 'Noise Patterns' },
      { path: '/waves', label: 'Wave Dynamics' },
      { path: '/dla', label: 'Diffusion-Limited Aggregation' },
    ]
  },
  { 
    label: 'Riemann Zeta Functions',
    items: [
      { path: '/zeta-space-tiling', label: 'Zeta Space Tiling' },
      { path: '/zeta-3d-visualization', label: '3D Zeta Visualization' },
    ]
  },
  { 
    label: 'Branching Architectures',
    items: [
      { path: '/ferns', label: 'Barnsley Ferns' },
      { path: '/trees', label: 'Fractal Trees' },
      { path: '/pythagoras', label: 'Pythagoras Tree' },
      { path: '/tree-roots-3d', label: '3D Tree with Roots' },
    ]
  }
];

export const Navigation: React.FC = () => {
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [anchorEls, setAnchorEls] = useState<{ [key: string]: HTMLElement | null }>({});

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, label: string) => {
    setAnchorEls(prev => ({ ...prev, [label]: event.currentTarget }));
  };

  const handleMenuClose = (label: string) => {
    setAnchorEls(prev => ({ ...prev, [label]: null }));
  };

  const isMenuOpen = (label: string) => Boolean(anchorEls[label]);

  const isPathActive = (path: string) => location.pathname === path;
  
  const isCategoryActive = (items: { path: string; label: string }[]) => 
    items.some(item => location.pathname === item.path);

  return (
    <AppBar position="fixed" sx={{ zIndex: 1201 }}>
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Fractal Notebooks
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {!isMobile && navItems.map((item) => {
            if ('path' in item) {
              // Single item
              return (
                <Button
                  key={item.path}
                  component={Link}
                  to={item.path}
                  color="inherit"
                  variant={isPathActive(item.path) ? 'outlined' : 'text'}
                  size="small"
                >
                  {item.label}
                </Button>
              );
            } else {
              // Dropdown menu
              const menuLabel = item.label;
              return (
                <React.Fragment key={menuLabel}>
                  <Button
                    color="inherit"
                    variant={isCategoryActive(item.items) ? 'outlined' : 'text'}
                    size="small"
                    endIcon={<ExpandMore />}
                    onClick={(e) => handleMenuOpen(e, menuLabel)}
                    aria-controls={isMenuOpen(menuLabel) ? `${menuLabel}-menu` : undefined}
                    aria-haspopup="true"
                  >
                    {menuLabel}
                  </Button>
                  <Menu
                    id={`${menuLabel}-menu`}
                    anchorEl={anchorEls[menuLabel]}
                    open={isMenuOpen(menuLabel)}
                    onClose={() => handleMenuClose(menuLabel)}
                    MenuListProps={{
                      'aria-labelledby': `${menuLabel}-button`,
                    }}
                  >
                    {item.items.map((subItem) => (
                      <MenuItem
                        key={subItem.path}
                        component={Link}
                        to={subItem.path}
                        onClick={() => handleMenuClose(menuLabel)}
                        selected={isPathActive(subItem.path)}
                      >
                        {subItem.label}
                      </MenuItem>
                    ))}
                  </Menu>
                </React.Fragment>
              );
            }
          })}
          <ThemeToggle />
        </Box>
      </Toolbar>
    </AppBar>
  );
};