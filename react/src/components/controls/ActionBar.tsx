import React from 'react';
import { Box, Button } from '@mui/material';

export interface ActionButton {
  label: string;
  onClick: () => void;
  icon?: React.ReactNode;
  variant?: 'contained' | 'outlined';
  /** Optional colour override for a primary (contained) action. */
  color?: string;
  disabled?: boolean;
}

interface ActionBarProps {
  actions: ActionButton[];
}

/**
 * A vertical stack of full-width action buttons. Keeps the primary/secondary
 * button treatment identical across every app.
 */
export const ActionBar: React.FC<ActionBarProps> = ({ actions }) => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
      {actions.map((action) => (
        <Button
          key={action.label}
          variant={action.variant ?? 'outlined'}
          onClick={action.onClick}
          startIcon={action.icon}
          disabled={action.disabled}
          fullWidth
          sx={
            action.variant === 'contained' && action.color
              ? {
                  backgroundColor: action.color,
                  '&:hover': { backgroundColor: action.color, filter: 'brightness(0.92)' },
                }
              : undefined
          }
        >
          {action.label}
        </Button>
      ))}
    </Box>
  );
};
