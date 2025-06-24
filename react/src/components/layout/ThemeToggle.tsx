import React from 'react';
import {
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Tooltip,
} from '@mui/material';
import {
  Brightness4,
  Brightness7,
  SettingsBrightness,
  Check,
} from '@mui/icons-material';
import { useTheme, ThemeMode } from '../../contexts/ThemeContext';

export const ThemeToggle: React.FC = () => {
  const { themeMode, setThemeMode } = useTheme();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleThemeChange = (mode: ThemeMode) => {
    setThemeMode(mode);
    handleClose();
  };

  const getIcon = () => {
    switch (themeMode) {
      case 'light':
        return <Brightness7 />;
      case 'dark':
        return <Brightness4 />;
      case 'system':
        return <SettingsBrightness />;
      default:
        return <SettingsBrightness />;
    }
  };

  const getTooltipText = () => {
    switch (themeMode) {
      case 'light':
        return 'Light theme';
      case 'dark':
        return 'Dark theme';
      case 'system':
        return 'System theme';
      default:
        return 'Theme settings';
    }
  };

  return (
    <>
      <Tooltip title={getTooltipText()}>
        <IconButton
          color="inherit"
          onClick={handleClick}
          aria-controls={open ? 'theme-menu' : undefined}
          aria-haspopup="true"
          aria-expanded={open ? 'true' : undefined}
        >
          {getIcon()}
        </IconButton>
      </Tooltip>
      <Menu
        id="theme-menu"
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        MenuListProps={{
          'aria-labelledby': 'theme-button',
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem onClick={() => handleThemeChange('light')}>
          <ListItemIcon>
            <Brightness7 fontSize="small" />
          </ListItemIcon>
          <ListItemText>Light</ListItemText>
          {themeMode === 'light' && (
            <ListItemIcon>
              <Check fontSize="small" />
            </ListItemIcon>
          )}
        </MenuItem>
        <MenuItem onClick={() => handleThemeChange('dark')}>
          <ListItemIcon>
            <Brightness4 fontSize="small" />
          </ListItemIcon>
          <ListItemText>Dark</ListItemText>
          {themeMode === 'dark' && (
            <ListItemIcon>
              <Check fontSize="small" />
            </ListItemIcon>
          )}
        </MenuItem>
        <MenuItem onClick={() => handleThemeChange('system')}>
          <ListItemIcon>
            <SettingsBrightness fontSize="small" />
          </ListItemIcon>
          <ListItemText>System</ListItemText>
          {themeMode === 'system' && (
            <ListItemIcon>
              <Check fontSize="small" />
            </ListItemIcon>
          )}
        </MenuItem>
      </Menu>
    </>
  );
};