import { createTheme, responsiveFontSizes } from '@mui/material/styles';

const rawLightTheme = createTheme({
  map: {
    style: 'mapbox://styles/mapbox/light-v10'
  },
  typography: {
    htmlFontSize: 10,
    fontFamily: 'system-ui, sans-serif',
  },
  palette: {
    mode: 'light',
    primary: {
      main: '#3b82f6', // --accent
    },
    secondary: {
      main: '#06b6d4', // --accent2
    },
    background: {
      default: '#f8fafc', // светлый фон
      paper: '#ffffff', // белый для поверхностей
    },
    text: {
      primary: '#1e293b', // тёмный текст
      secondary: '#64748b', // --muted
    },
    divider: '#e2e8f0', // светлая граница
    command: {
      main: '#3b82f6',
      light: '#60a5fa',
      dark: '#2563eb',
    }
  },
});

export const LightTheme = responsiveFontSizes(rawLightTheme);
