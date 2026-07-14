import React, { useState } from 'react';
import { Typography, Grid, Box, Paper, Tabs, Tab, Chip } from '@mui/material';

export interface InfoTab {
  label: string;
  content: React.ReactNode;
}

interface AppScaffoldProps {
  title: string;
  subtitle: string;
  /** Accent colour for the title underline and category chip. */
  accent?: string;
  /** Optional short category label rendered as a chip beside the title. */
  category?: string;
  /** Optional tabbed information panel (Overview / Mathematics / Biology …). */
  infoTabs?: InfoTab[];
  /** The main visualization (canvas, Plot, svg …). */
  visualization: React.ReactNode;
  /** Optional caption rendered under the visualization. */
  caption?: React.ReactNode;
  /** Background for the visualization area. Defaults to the themed paper colour. */
  vizBackground?: string;
  /** The control panel contents (sliders, selects, buttons). */
  controls: React.ReactNode;
}

/**
 * The shared page shell for every visualization app. It guarantees a consistent
 * layout: a centred title + subtitle, an optional tabbed info panel, and a
 * two-column body with the visualization on the left and controls on the right.
 */
export const AppScaffold: React.FC<AppScaffoldProps> = ({
  title,
  subtitle,
  accent = '#2e7d32',
  category,
  infoTabs,
  visualization,
  caption,
  vizBackground,
  controls,
}) => {
  const [tab, setTab] = useState(0);

  return (
    <div className="page-container">
      <Box sx={{ textAlign: 'center', mb: 1 }}>
        <Typography
          variant="h3"
          component="h1"
          sx={{
            fontWeight: 400,
            display: 'inline-block',
            borderBottom: `3px solid ${accent}`,
            pb: 0.5,
          }}
        >
          {title}
        </Typography>
      </Box>
      {category && (
        <Box sx={{ textAlign: 'center', mb: 1.5 }}>
          <Chip
            label={category}
            size="small"
            sx={{ backgroundColor: accent, color: '#fff', fontWeight: 600 }}
          />
        </Box>
      )}
      <Typography variant="body1" className="page-description">
        {subtitle}
      </Typography>

      {infoTabs && infoTabs.length > 0 && (
        <Paper sx={{ p: { xs: 2, md: 3 }, mb: 3 }}>
          <Tabs
            value={tab}
            onChange={(_, v) => setTab(v)}
            variant="scrollable"
            scrollButtons="auto"
            sx={{ mb: 1, borderBottom: 1, borderColor: 'divider' }}
          >
            {infoTabs.map((t) => (
              <Tab key={t.label} label={t.label} />
            ))}
          </Tabs>
          {infoTabs.map((t, i) => (
            <Box key={t.label} sx={{ mt: 2, display: tab === i ? 'block' : 'none' }}>
              {t.content}
            </Box>
          ))}
        </Paper>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <Box
            className="visualization-area"
            sx={{ p: { xs: 1, md: 2 }, background: vizBackground, overflow: 'hidden' }}
          >
            {visualization}
            {caption && (
              <Typography variant="body2" sx={{ mt: 1, textAlign: 'center', color: 'text.secondary' }}>
                {caption}
              </Typography>
            )}
          </Box>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Box className="controls-area" sx={{ p: { xs: 2, md: 2.5 } }}>
            {controls}
          </Box>
        </Grid>
      </Grid>
    </div>
  );
};
