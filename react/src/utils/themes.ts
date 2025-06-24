import { createTheme, Theme } from '@mui/material/styles';

export const createCustomTheme = (mode: 'light' | 'dark'): Theme => {
  return createTheme({
    palette: {
      mode,
      primary: {
        main: mode === 'dark' ? '#007acc' : '#1976d2',
        light: mode === 'dark' ? '#4da6ff' : '#42a5f5',
        dark: mode === 'dark' ? '#005a9e' : '#1565c0',
      },
      secondary: {
        main: mode === 'dark' ? '#ff6b6b' : '#dc004e',
        light: mode === 'dark' ? '#ff9999' : '#ff5983',
        dark: mode === 'dark' ? '#cc5555' : '#9a0036',
      },
      background: {
        default: mode === 'dark' ? '#0a0a0a' : '#f5f5f5',
        paper: mode === 'dark' ? '#1a1a1a' : '#ffffff',
      },
      text: {
        primary: mode === 'dark' ? '#ffffff' : '#1a1a1a',
        secondary: mode === 'dark' ? '#cccccc' : '#666666',
      },
      divider: mode === 'dark' ? '#333333' : '#e0e0e0',
      action: {
        hover: mode === 'dark' ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.04)',
        selected: mode === 'dark' ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.08)',
      }
    },
    typography: {
      fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
      h1: {
        fontWeight: 300,
        color: mode === 'dark' ? '#ffffff' : '#1a1a1a',
      },
      h2: {
        fontWeight: 300,
        color: mode === 'dark' ? '#ffffff' : '#1a1a1a',
      },
      h3: {
        fontWeight: 400,
        color: mode === 'dark' ? '#ffffff' : '#1a1a1a',
      },
      body1: {
        color: mode === 'dark' ? '#cccccc' : '#666666',
      },
    },
    components: {
      MuiCssBaseline: {
        styleOverrides: {
          body: {
            backgroundColor: mode === 'dark' ? '#0a0a0a' : '#f5f5f5',
            color: mode === 'dark' ? '#ffffff' : '#1a1a1a',
            transition: 'background-color 0.3s ease, color 0.3s ease',
          },
        },
      },
      MuiAppBar: {
        styleOverrides: {
          root: {
            backgroundColor: mode === 'dark' ? '#1a1a1a' : '#1976d2',
            borderBottom: `1px solid ${mode === 'dark' ? '#333333' : '#e0e0e0'}`,
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundColor: mode === 'dark' ? '#1a1a1a' : '#ffffff',
            border: `1px solid ${mode === 'dark' ? '#333333' : '#e0e0e0'}`,
            transition: 'background-color 0.3s ease, border-color 0.3s ease',
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            backgroundColor: mode === 'dark' ? '#1a1a1a' : '#ffffff',
            border: `1px solid ${mode === 'dark' ? '#333333' : '#e0e0e0'}`,
            transition: 'all 0.3s ease',
            '&:hover': {
              borderColor: mode === 'dark' ? '#007acc' : '#1976d2',
              transform: 'translateY(-2px)',
              boxShadow: mode === 'dark' 
                ? '0 4px 12px rgba(0, 122, 204, 0.2)' 
                : '0 4px 12px rgba(25, 118, 210, 0.2)',
            },
          },
        },
      },
      MuiSlider: {
        styleOverrides: {
          root: {
            color: mode === 'dark' ? '#007acc' : '#1976d2',
          },
          track: {
            backgroundColor: mode === 'dark' ? '#007acc' : '#1976d2',
          },
          thumb: {
            backgroundColor: mode === 'dark' ? '#007acc' : '#1976d2',
            '&:hover': {
              boxShadow: mode === 'dark' 
                ? '0 0 0 8px rgba(0, 122, 204, 0.16)' 
                : '0 0 0 8px rgba(25, 118, 210, 0.16)',
            },
          },
        },
      },
      MuiTextField: {
        styleOverrides: {
          root: {
            '& .MuiOutlinedInput-root': {
              backgroundColor: mode === 'dark' ? '#333333' : '#ffffff',
              '& fieldset': {
                borderColor: mode === 'dark' ? '#555555' : '#e0e0e0',
              },
              '&:hover fieldset': {
                borderColor: mode === 'dark' ? '#007acc' : '#1976d2',
              },
              '&.Mui-focused fieldset': {
                borderColor: mode === 'dark' ? '#007acc' : '#1976d2',
              },
            },
            '& .MuiInputLabel-root': {
              color: mode === 'dark' ? '#cccccc' : '#666666',
            },
            '& .MuiOutlinedInput-input': {
              color: mode === 'dark' ? '#ffffff' : '#1a1a1a',
            },
          },
        },
      },
    },
  });
};