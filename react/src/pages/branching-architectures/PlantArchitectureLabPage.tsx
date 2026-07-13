import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Typography, Box, Switch, FormControlLabel } from '@mui/material';
import { PlayArrow, Pause, Casino, Refresh, Park } from '@mui/icons-material';
// @ts-ignore
import Plot from 'react-plotly.js';
import { AppScaffold, ControlSection, ParameterSlider, ParameterSelect, ActionBar } from '../../components/controls';
import { useTheme } from '../../contexts/ThemeContext';
import { makeRng, rewrite } from '../../utils/lsystem';
import { interpret, buildPlotTraces, TurtleParams } from '../../utils/plantEngine';
import { PLANT_PRESETS, PRESET_GROUPS, getPreset } from '../../utils/plantPresets';

const ACCENT = '#2e7d32';

interface Overrides {
  iterations: number;
  angle: number;
  angleJitter: number;
  lengthFactor: number;
  widthFactor: number;
  tropismStrength: number;
}

function presetOverrides(key: string): Overrides {
  const p = getPreset(key);
  return {
    iterations: p.spec.iterations,
    angle: p.turtle.angle,
    angleJitter: p.turtle.angleJitter,
    lengthFactor: p.turtle.lengthFactor,
    widthFactor: p.turtle.widthFactor,
    tropismStrength: p.turtle.tropismStrength,
  };
}

export const PlantArchitectureLabPage: React.FC = () => {
  const { effectiveTheme } = useTheme();
  const [presetKey, setPresetKey] = useState('tree');
  const [ov, setOv] = useState<Overrides>(() => presetOverrides('tree'));
  const [showOrgans, setShowOrgans] = useState(true);
  const [seed, setSeed] = useState(1);

  const [isAnimating, setIsAnimating] = useState(false);
  const [visibleOrder, setVisibleOrder] = useState(Infinity);
  const animRef = useRef<ReturnType<typeof setTimeout>>();

  const preset = getPreset(presetKey);

  // Rebuild geometry whenever the grammar or a parameter changes.
  const geometry = useMemo(() => {
    const turtle: TurtleParams = {
      ...preset.turtle,
      angle: ov.angle,
      angleJitter: ov.angleJitter,
      lengthFactor: ov.lengthFactor,
      widthFactor: ov.widthFactor,
      tropismStrength: ov.tropismStrength,
    };
    const rng = makeRng(seed);
    const str = rewrite({ ...preset.spec, iterations: ov.iterations }, rng);
    return interpret(str, turtle, rng);
  }, [preset, ov, seed]);

  const traces = useMemo(
    () =>
      buildPlotTraces(geometry, preset.style, {
        showOrgans,
        maxVisibleOrder: isAnimating ? visibleOrder : Infinity,
      }),
    [geometry, preset.style, showOrgans, isAnimating, visibleOrder]
  );

  // Growth animation: reveal one branch order at a time.
  useEffect(() => {
    if (!isAnimating) return;
    if (visibleOrder >= geometry.maxOrder) {
      setIsAnimating(false);
      return;
    }
    animRef.current = setTimeout(() => setVisibleOrder((o) => (o === Infinity ? 0 : o + 1)), 380);
    return () => {
      if (animRef.current) clearTimeout(animRef.current);
    };
  }, [isAnimating, visibleOrder, geometry.maxOrder]);

  useEffect(() => () => { if (animRef.current) clearTimeout(animRef.current); }, []);

  const selectPreset = (key: string) => {
    setPresetKey(key);
    setOv(presetOverrides(key));
    setShowOrgans(getPreset(key).showOrgans);
    setSeed(1);
    setIsAnimating(false);
    setVisibleOrder(Infinity);
  };

  const setOverride = (k: keyof Overrides, v: number) => setOv((prev) => ({ ...prev, [k]: v }));

  const animateGrowth = () => {
    if (isAnimating) {
      setIsAnimating(false);
    } else {
      setVisibleOrder(0);
      setIsAnimating(true);
    }
  };

  const showFull = () => {
    setIsAnimating(false);
    setVisibleOrder(Infinity);
  };

  const options = useMemo(() => {
    const sorted = [...PLANT_PRESETS].sort(
      (a, b) => PRESET_GROUPS.indexOf(a.group) - PRESET_GROUPS.indexOf(b.group)
    );
    return sorted.map((p) => ({ value: p.key, label: p.label, hint: `${p.group} · ${p.tagline}` }));
  }, []);

  const axisTheme = effectiveTheme === 'dark'
    ? { bg: 'rgba(0,0,0,0)', grid: 'rgba(255,255,255,0.05)' }
    : { bg: 'rgba(0,0,0,0)', grid: 'rgba(0,0,0,0.06)' };

  const rulesText = Object.entries(preset.spec.rules)
    .map(([k, v]) => `${k} → ${typeof v === 'string' ? v : v.map((o) => o.successor).join(' | ')}`)
    .join('\n');

  const infoTabs = [
    {
      label: 'Overview',
      content: (
        <>
          <Typography variant="h6" gutterBottom>{preset.label}</Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>{preset.description}</Typography>
          <Typography variant="body2" color="text.secondary">
            This lab models plant form with L-systems (Lindenmayer systems): a short grammar is rewritten
            repeatedly, then a 3D "turtle" walks the resulting string, drawing a segment for every{' '}
            <code>F</code>, turning at brackets, and pushing/popping state to make branches. Every growth
            form on this page is the same engine driven by a different grammar.
          </Typography>
        </>
      ),
    },
    {
      label: 'Biology',
      content: (
        <>
          <Typography variant="h6" gutterBottom>Botanical background</Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>{preset.biology}</Typography>
          <Typography variant="body2" color="text.secondary">
            Estimated branching (box-counting) fractal dimension for this form: <strong>{preset.fractalDim}</strong>.
            Prostrate thalli approach 1, planar fronds sit near 1.7, and space-filling woody crowns exceed 2.
          </Typography>
        </>
      ),
    },
    {
      label: 'Grammar',
      content: (
        <>
          <Typography variant="h6" gutterBottom>Production rules</Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            Axiom <code>{preset.spec.axiom}</code>, rewritten {ov.iterations}× with these productions:
          </Typography>
          <Box
            component="pre"
            sx={{
              p: 2, borderRadius: 1, overflowX: 'auto', fontSize: 14,
              backgroundColor: effectiveTheme === 'dark' ? '#111' : '#f5f5f5',
              border: '1px solid', borderColor: 'divider',
            }}
          >
            {rulesText}
          </Box>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            Turtle symbols: <code>F</code> draw, <code>+ -</code> yaw, <code>&amp; ^</code> pitch,{' '}
            <code>/ \</code> roll, <code>[ ]</code> branch, <code>&gt;</code> shorten, <code>!</code> thin,{' '}
            <code>L</code> place an organ (leaf, lamina, or apothecium).
          </Typography>
        </>
      ),
    },
  ];

  const controls = (
    <>
      <ControlSection title="Growth form" accent={ACCENT} first>
        <ParameterSelect label="Plant / lichen" value={presetKey} options={options} onChange={selectPreset} />
      </ControlSection>

      <ControlSection title="Form parameters" accent={ACCENT}>
        <ParameterSlider
          label="Iterations" value={ov.iterations} onChange={(v) => setOverride('iterations', v)}
          min={preset.iterationRange[0]} max={preset.iterationRange[1]} step={1}
          help="How many times the grammar is rewritten. More iterations = more detail (and more segments)."
        />
        <ParameterSlider
          label="Branch angle" value={ov.angle} onChange={(v) => setOverride('angle', v)}
          min={5} max={90} step={1} unit="°"
          help="Divergence angle at each fork or turn."
        />
        <ParameterSlider
          label="Angle variation" value={ov.angleJitter} onChange={(v) => setOverride('angleJitter', v)}
          min={0} max={30} step={1} unit="°"
          help="Random jitter added to every turn, for a more natural, less mechanical look."
        />
        <ParameterSlider
          label="Length falloff" value={ov.lengthFactor} onChange={(v) => setOverride('lengthFactor', v)}
          min={0.6} max={1} step={0.01} format={(v) => v.toFixed(2)}
          help="Factor applied to segment length after each order (< 1 tapers the plant)."
        />
        <ParameterSlider
          label="Width falloff" value={ov.widthFactor} onChange={(v) => setOverride('widthFactor', v)}
          min={0.5} max={1} step={0.01} format={(v) => v.toFixed(2)}
          help="How quickly branch thickness thins toward the tips."
        />
        <ParameterSlider
          label="Tropism" value={ov.tropismStrength} onChange={(v) => setOverride('tropismStrength', v)}
          min={0} max={0.4} step={0.01} format={(v) => v.toFixed(2)}
          help="Upward pull on growing tips (phototropism / negative gravitropism)."
        />
      </ControlSection>

      <ControlSection title="Appearance" accent={ACCENT}>
        <FormControlLabel
          control={<Switch checked={showOrgans} onChange={(e) => setShowOrgans(e.target.checked)} />}
          label="Show leaves / organs"
        />
      </ControlSection>

      <ControlSection title="Actions" accent={ACCENT}>
        <ActionBar
          actions={[
            {
              label: isAnimating ? 'Pause growth' : 'Animate growth',
              onClick: animateGrowth,
              icon: isAnimating ? <Pause /> : <PlayArrow />,
              variant: 'contained',
              color: ACCENT,
            },
            { label: 'Show full plant', onClick: showFull, icon: <Park /> },
            { label: 'New variation', onClick: () => setSeed((s) => s + 1), icon: <Casino /> },
            { label: 'Reset to preset', onClick: () => selectPreset(presetKey), icon: <Refresh /> },
          ]}
        />
      </ControlSection>

      <ControlSection title="Statistics" accent={ACCENT}>
        <Typography variant="body2">Segments: <strong>{geometry.segments.length.toLocaleString()}</strong></Typography>
        <Typography variant="body2">Organs: <strong>{geometry.organs.length.toLocaleString()}</strong></Typography>
        <Typography variant="body2">Branch orders: <strong>{geometry.maxOrder}</strong></Typography>
        <Typography variant="body2">Fractal dimension: <strong>{preset.fractalDim}</strong></Typography>
      </ControlSection>
    </>
  );

  return (
    <AppScaffold
      title="Plant Architecture Lab"
      subtitle="Grow bryophytes, ferns, lichens, and vascular plants from L-systems — one 3D engine, nine botanically-informed growth forms."
      accent={ACCENT}
      category="Branching Architectures"
      infoTabs={infoTabs}
      caption={`${preset.label} — ${geometry.segments.length.toLocaleString()} segments · drag to orbit, scroll to zoom`}
      visualization={
        <Plot
          data={traces as any}
          layout={{
            autosize: true,
            scene: {
              xaxis: { visible: false, showgrid: false },
              yaxis: { visible: false, showgrid: false },
              zaxis: { visible: false, showgrid: false },
              aspectmode: 'data' as const,
              bgcolor: axisTheme.bg,
              camera: { eye: { x: 1.6, y: 1.6, z: 0.9 }, up: { x: 0, y: 0, z: 1 } },
            },
            showlegend: false,
            margin: { l: 0, r: 0, t: 0, b: 0 },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
          }}
          useResizeHandler
          style={{ width: '100%', height: '620px' }}
          config={{
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['pan2d', 'select2d', 'lasso2d', 'hoverClosestCartesian', 'hoverCompareCartesian'],
          }}
        />
      }
      controls={controls}
    />
  );
};
