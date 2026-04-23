import { createTheme, responsiveFontSizes } from '@mui/material/styles';

const rawDarkTheme = createTheme({
  map: {
    style: 'mapbox://styles/mapbox/dark-v10'
  },
  typography: {
    htmlFontSize: 10,
    fontFamily: 'system-ui, sans-serif',
  },
  palette: {
    mode: 'dark',
    primary: {
      main: '#3b82f6', // --accent
    },
    secondary: {
      main: '#06b6d4', // --accent2
    },
    background: {
      default: '#0f172a', // --bg
      paper: '#1e293b', // --surface
    },
    text: {
      primary: '#e2e8f0', // --text
      secondary: '#64748b', // --muted
    },
    divider: '#334155', // --border
    command: {
      main: '#3b82f6',
      light: '#60a5fa',
      dark: '#2563eb',
    }
  },
});

export const DarkTheme = responsiveFontSizes(rawDarkTheme);
