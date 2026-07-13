import React from 'react';
import { Box, Typography, Slider, Tooltip, IconButton } from '@mui/material';
import { HelpOutline } from '@mui/icons-material';

interface ParameterSliderProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min: number;
  max: number;
  step?: number;
  /** Optional short unit appended to the displayed value, e.g. "°" or "ms". */
  unit?: string;
  /** Optional formatter for the displayed value (overrides `unit`). */
  format?: (value: number) => string;
  /** Optional explanatory tooltip shown behind a help icon. */
  help?: string;
  disabled?: boolean;
}

/**
 * A labelled slider with a live value read-out and optional help tooltip.
 * Used across every app so parameter controls look and behave identically.
 */
export const ParameterSlider: React.FC<ParameterSliderProps> = ({
  label,
  value,
  onChange,
  min,
  max,
  step = 1,
  unit = '',
  format,
  help,
  disabled = false,
}) => {
  const display = format ? format(value) : `${value}${unit}`;

  return (
    <Box sx={{ mb: 2.5 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 0.5 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <Typography variant="body2" sx={{ fontWeight: 500 }}>
            {label}
          </Typography>
          {help && (
            <Tooltip title={help} arrow enterTouchDelay={0}>
              <IconButton size="small" sx={{ p: 0.25 }} aria-label={`${label} help`}>
                <HelpOutline sx={{ fontSize: 15, opacity: 0.6 }} />
              </IconButton>
            </Tooltip>
          )}
        </Box>
        <Typography
          variant="body2"
          sx={{ fontFamily: 'monospace', color: 'primary.main', fontWeight: 600 }}
        >
          {display}
        </Typography>
      </Box>
      <Slider
        value={value}
        onChange={(_, v) => onChange(v as number)}
        min={min}
        max={max}
        step={step}
        disabled={disabled}
        valueLabelDisplay="auto"
        valueLabelFormat={(v) => (format ? format(v) : `${v}${unit}`)}
        size="small"
      />
    </Box>
  );
};
