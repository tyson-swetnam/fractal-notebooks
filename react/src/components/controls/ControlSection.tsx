import React from 'react';
import { Box, Typography, Divider } from '@mui/material';

interface ControlSectionProps {
  title: string;
  /** Optional accent colour for the section heading underline. */
  accent?: string;
  children: React.ReactNode;
  /** Hide the top divider (used for the first section in a panel). */
  first?: boolean;
}

/**
 * A titled group of controls. Sections give every control panel the same
 * visual rhythm: a small caption heading, an accent rule, then the controls.
 */
export const ControlSection: React.FC<ControlSectionProps> = ({ title, accent, children, first = false }) => {
  return (
    <Box sx={{ mb: 3 }}>
      {!first && <Divider sx={{ mb: 2 }} />}
      <Typography
        variant="overline"
        sx={{
          display: 'block',
          fontWeight: 700,
          letterSpacing: 1,
          mb: 1.5,
          color: accent || 'text.secondary',
          borderLeft: accent ? `3px solid ${accent}` : 'none',
          pl: accent ? 1 : 0,
        }}
      >
        {title}
      </Typography>
      {children}
    </Box>
  );
};
