import React from 'react';
import { Box, Typography, Link, Divider } from '@mui/material';
import GitHubIcon from '@mui/icons-material/GitHub';
import type { INavigationElementProps } from '../navigation/navigationTypes.js';
import { ViewKeys } from './viewKeys.js';

interface ILocalProps {}
type Props = ILocalProps & INavigationElementProps;

interface Contributor {
  name: string;
  github: string;
}

const contributors: Contributor[] = [
  {
    name: 'Melania Aristakesian',
    github: 'https://github.com/pomellonn',
  },
    {
    name: 'Tristan Tate',
    github: 'https://github.com/deviceking',
  },
   {
    name: 'Antonova Aleksandra',
    github: 'https://github.com/dtwrx',
  },
   {
    name: 'Elovskikh Anastasiia',
    github: 'https://github.com/Elovskikh',
  },


];

const AboutView: React.FC<Props> = () => {
  const contextName: string = ViewKeys.AboutView;

  return (
    <Box
      sx={{
        height: '100%',
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        px: 3,
      }}
    >
      <Box sx={{ maxWidth: 480, width: '100%' }}>

        {/* Project title */}
        <Typography
          variant="h5"
          sx={{ fontWeight: 600, letterSpacing: '-0.5px', mb: 0.5 }}
        >
          Flight Tracker
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          
          <Link
            href="https://github.com/pomellonn/flight_tracker"
            target="_blank"
            rel="noopener noreferrer"
            underline="hover"
            sx={{ display: 'inline-flex', alignItems: 'center', gap: 0.4 }}
          >
            <GitHubIcon sx={{ fontSize: 14 }} />
            pomellonn/flight_tracker
          </Link>
        </Typography>

        <Divider sx={{ mb: 3 }} />

        {/* Contributors */}
        <Typography
          variant="overline"
          color="text.secondary"
          sx={{ letterSpacing: 1.5, fontSize: 11 }}
        >
          Contributors
        </Typography>

        <Box sx={{ mt: 1.5, display: 'flex', flexDirection: 'column', gap: 1.5 }}>
          {contributors.map((c) => (
            <Box
              key={c.github}
              sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
            >
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                  {c.name}
                </Typography>
         
              </Box>
              <Link
                href={c.github}
                target="_blank"
                rel="noopener noreferrer"
                underline="hover"
                color="text.secondary"
                sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontSize: 13 }}
              >
                <GitHubIcon sx={{ fontSize: 15 }} />
                GitHub
              </Link>
            </Box>
          ))}
        </Box>

        <Divider sx={{ my: 3 }} />

        {/* Stack */}
        <Typography
          variant="overline"
          color="text.secondary"
          sx={{ letterSpacing: 1.5, fontSize: 11 }}
        >
          Built with
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.75 }}>
          React · TypeScript · MUI · FastAPI · OpenSky Network API
        </Typography>

      </Box>
    </Box>
  );
};

export default AboutView;