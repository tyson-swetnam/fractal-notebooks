import React, { useState } from 'react';
import { Box, Typography, IconButton, useTheme, useMediaQuery } from '@mui/material';
import { ExpandMore, ExpandLess, Settings } from '@mui/icons-material';

interface CollapsiblePanelProps {
  title: string;
  children: React.ReactNode;
  defaultExpanded?: boolean;
  position: 'left' | 'right' | 'bottom';
  icon?: React.ReactNode;
}

export const CollapsiblePanel: React.FC<CollapsiblePanelProps> = ({
  title,
  children,
  defaultExpanded = false,
  position,
  icon = <Settings fontSize="small" />
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isTablet = useMediaQuery(theme.breakpoints.down('lg'));
  
  // On mobile, default to collapsed unless explicitly set
  const [expanded, setExpanded] = useState(isMobile ? false : defaultExpanded);

  const handleToggle = () => {
    setExpanded(!expanded);
  };

  // Mobile: Bottom overlay panel
  // Tablet: Side panels with smaller width
  // Desktop: Full side panels
  const getPanelStyles = () => {
    const baseStyles = {
      position: 'fixed' as const,
      backgroundColor: 'rgba(0,0,0,0.85)',
      backdropFilter: 'blur(10px)',
      borderRadius: isMobile ? '12px 12px 0 0' : 2,
      zIndex: 1000,
      color: 'white',
      transition: 'all 0.3s ease-in-out',
    };

    if (isMobile) {
      // Mobile: Bottom sheet
      return {
        ...baseStyles,
        bottom: 0,
        left: 0,
        right: 0,
        maxHeight: '70vh',
        transform: expanded ? 'translateY(0)' : 'translateY(calc(100% - 60px))',
        borderRadius: '12px 12px 0 0',
      };
    } else if (position === 'bottom') {
      // Tablet/Desktop bottom panel
      return {
        ...baseStyles,
        bottom: 20,
        left: 20,
        right: 20,
        maxHeight: expanded ? '40vh' : '60px',
        overflow: 'hidden',
      };
    } else {
      // Side panels
      const width = isTablet ? 280 : 320;
      return {
        ...baseStyles,
        top: 80,
        [position]: 20,
        width: expanded ? width : '60px',
        maxHeight: 'calc(100vh - 100px)',
        overflow: 'hidden',
      };
    }
  };

  const getContentStyles = () => {
    if (isMobile) {
      return {
        padding: expanded ? 3 : 0,
        maxHeight: expanded ? 'calc(70vh - 120px)' : 0,
        overflow: 'auto',
        transition: 'all 0.3s ease-in-out',
      };
    } else {
      return {
        padding: expanded ? 3 : 0,
        opacity: expanded ? 1 : 0,
        transition: 'all 0.3s ease-in-out',
        overflow: 'auto',
        maxHeight: '100%',
      };
    }
  };

  const getHeaderStyles = () => {
    if (isMobile) {
      return {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '16px 20px',
        borderBottom: expanded ? '1px solid rgba(255,255,255,0.1)' : 'none',
        minHeight: '60px',
      };
    } else {
      return {
        display: 'flex',
        alignItems: 'center',
        justifyContent: expanded ? 'space-between' : 'center',
        padding: expanded ? '16px 20px' : '16px 8px',
        borderBottom: expanded ? '1px solid rgba(255,255,255,0.1)' : 'none',
        minHeight: '60px',
      };
    }
  };

  return (
    <Box sx={getPanelStyles()}>
      {/* Header with toggle */}
      <Box sx={getHeaderStyles()}>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: 1,
          opacity: (expanded || isMobile) ? 1 : 0,
          transition: 'opacity 0.3s ease-in-out',
        }}>
          {icon}
          {(expanded || isMobile) && (
            <Typography variant="h6" sx={{ 
              fontSize: isMobile ? '1.1rem' : '1rem',
              fontWeight: 600,
            }}>
              {title}
            </Typography>
          )}
        </Box>
        
        <IconButton
          onClick={handleToggle}
          sx={{
            color: 'white',
            backgroundColor: expanded ? 'transparent' : 'rgba(255,255,255,0.1)',
            '&:hover': {
              backgroundColor: 'rgba(255,255,255,0.2)',
            },
            transition: 'all 0.3s ease-in-out',
          }}
          size={isMobile ? 'medium' : 'small'}
        >
          {isMobile ? (
            expanded ? <ExpandMore /> : <ExpandLess />
          ) : (
            expanded ? <ExpandLess /> : <ExpandMore />
          )}
        </IconButton>
      </Box>

      {/* Content */}
      <Box sx={getContentStyles()}>
        {expanded && children}
      </Box>
    </Box>
  );
};