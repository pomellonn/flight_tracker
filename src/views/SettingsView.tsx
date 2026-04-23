import React, { useContext } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  FormGroup,
  FormControl,
  FormControlLabel,
  InputLabel,
  Switch,
  Select,
  MenuItem,
} from '@mui/material';
import { AppContext, SettingKeys } from '../components/infrastructure/AppContextProvider.js';
import { ViewKeys } from './viewKeys.js';
import { ThemeKeys } from './../styles/index.js';

import type { SelectChangeEvent } from '@mui/material';
import type { INavigationElementProps } from '../navigation/navigationTypes.js';

interface ILocalProps {}
type Props = ILocalProps & INavigationElementProps;

const SettingsView: React.FC<Props> = () => {
  const contextName: string = ViewKeys.SettingsView;
  const appContext = useContext(AppContext);

  // Safe boolean getter — always returns a boolean, never undefined
  const getBoolSetting = (key: string): boolean => {
    const value = appContext.pullSetting(key);
    return typeof value === 'boolean' ? value : false;
  };

  const handleThemeChange = (e: SelectChangeEvent) => {
    appContext.changeTheme(e.target.value);
  };

  const handleSettingToggle = (e: React.ChangeEvent<HTMLInputElement>) => {
    appContext.pushSetting(e.target.name, e.target.checked);
  };

  return (
    <Box
      sx={{
        height: '100%',
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        gap: 1,
        p: 2,
        overflowY: 'auto',
      }}
    >
      {/* App settings */}
      <Card variant="outlined">
        <CardContent>
          <Typography variant="h6" gutterBottom>
            App settings
          </Typography>
          <FormGroup>
            <FormControl variant="outlined" size="small" sx={{ minWidth: 200, mt: 1 }}>
              <InputLabel id="theme-select-label">Theme</InputLabel>
              <Select
                labelId="theme-select-label"
                label="Theme"
                value={appContext.activeThemeName}
                onChange={handleThemeChange}
              >
                <MenuItem value={ThemeKeys.DarkTheme}>{ThemeKeys.DarkTheme}</MenuItem>
                <MenuItem value={ThemeKeys.LightTheme}>{ThemeKeys.LightTheme}</MenuItem>
              </Select>
            </FormControl>
          </FormGroup>
        </CardContent>
      </Card>

      {/* Map settings */}
      <Card variant="outlined">
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Map settings
          </Typography>
          <FormGroup>
  
            <FormControlLabel
              control={
                <Switch
                  name={SettingKeys.ShowDataOverlayOnMap}
                  checked={getBoolSetting(SettingKeys.ShowDataOverlayOnMap)}
                  onChange={handleSettingToggle}
                />
              }
              label="Show data overlay on map"
            />
          </FormGroup>
        </CardContent>
      </Card>
    </Box>
  );
};

export default SettingsView;