import React from 'react';
import { FormControl, InputLabel, Select, MenuItem, Box, Typography } from '@mui/material';

interface Option {
  value: string;
  label: string;
  /** Optional one-line hint shown under the option label in the dropdown. */
  hint?: string;
}

interface ParameterSelectProps {
  label: string;
  value: string;
  options: Option[];
  onChange: (value: string) => void;
  disabled?: boolean;
}

/**
 * A themed dropdown used for discrete choices (plant type, render style, …).
 * Options may carry a short hint rendered beneath the label.
 */
export const ParameterSelect: React.FC<ParameterSelectProps> = ({
  label,
  value,
  options,
  onChange,
  disabled = false,
}) => {
  return (
    <FormControl fullWidth size="small" sx={{ mb: 2.5 }} disabled={disabled}>
      <InputLabel>{label}</InputLabel>
      <Select value={value} label={label} onChange={(e) => onChange(e.target.value)}>
        {options.map((opt) => (
          <MenuItem key={opt.value} value={opt.value}>
            <Box>
              <Typography variant="body2">{opt.label}</Typography>
              {opt.hint && (
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', lineHeight: 1.2 }}>
                  {opt.hint}
                </Typography>
              )}
            </Box>
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};
