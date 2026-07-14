import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Typography, Box } from '@mui/material';
import { PlayArrow, Pause, ReplayCircleFilled } from '@mui/icons-material';
import { MathRenderer } from '../../components/math/MathRenderer';
// @ts-ignore
import Plot from 'react-plotly.js';
import { AppScaffold, ControlSection, ParameterSlider, ActionBar } from '../../components/controls';

const ACCENT = '#4c9a2a';
const DEG = Math.PI / 180;
const clamp = (v: number, a: number, b: number) => Math.max(a, Math.min(b, v));

interface FrondParams {
  rachisNodes: number;
  rachisLength: number;
  pinnaMax: number;
  pinnaAngle: number;
  baseCurl: number;
  pinnules: number;
}

type Seg = { x: [number, number]; z: [number, number] };

/**
 * Build a bipinnate fern frond at unfurl fraction `u` (0 = tight fiddlehead,
 * 1 = fully open). Curvature ramps along the rachis so the base opens first and
 * the tip stays coiled longest — the essence of circinate vernation.
 */
function buildFrond(p: FrondParams, u: number) {
  const rachis: Seg[] = [];
  const pinna: Seg[] = [];
  const pinnules: [number, number][] = [];

  let x = 0;
  let z = 0;
  let ang = 90 * DEG; // heading up in the (x, z) plane
  const N = p.rachisNodes;
  const stepLen = p.rachisLength / N;

  for (let i = 0; i < N; i++) {
    const s = i / (N - 1);
    const coil = clamp((s - u) / 0.18, 0, 1); // 0 where opened, 1 where still coiled
    const tighten = 1 + 3.2 * s; // spiral tightens toward the tip
    ang += p.baseCurl * DEG * coil * tighten;

    const nx = x + Math.cos(ang) * stepLen;
    const nz = z + Math.sin(ang) * stepLen;
    rachis.push({ x: [x, nx], z: [z, nz] });

    // Pinna length: peaks in the lower third of the frond, tucked while coiled.
    const profile = Math.sin(Math.PI * Math.pow(s, 0.75));
    const visible = 1 - coil * 0.85;
    const Lp = p.pinnaMax * Math.max(0, profile) * visible;

    if (Lp > 0.05 && s < 0.98) {
      for (const side of [1, -1]) {
        const pang = ang + side * p.pinnaAngle * DEG;
        let px = nx;
        let pz = nz;
        const M = p.pinnules;
        for (let j = 1; j <= M; j++) {
          const f = j / M;
          const qx = nx + Math.cos(pang) * Lp * f;
          const qz = nz + Math.sin(pang) * Lp * f;
          pinna.push({ x: [px, qx], z: [pz, qz] });
          pinnules.push([qx, qz]);
          px = qx;
          pz = qz;
        }
      }
    }
    x = nx;
    z = nz;
  }
  return { rachis, pinna, pinnules };
}

function segTrace(segs: Seg[], color: string, width: number) {
  const xs: (number | null)[] = [];
  const ys: (number | null)[] = [];
  const zs: (number | null)[] = [];
  for (const s of segs) {
    xs.push(s.x[0], s.x[1], null);
    ys.push(0, 0, null);
    zs.push(s.z[0], s.z[1], null);
  }
  return {
    type: 'scatter3d', mode: 'lines', x: xs, y: ys, z: zs,
    line: { color, width }, hoverinfo: 'none', showlegend: false,
  };
}

export const FernFrond3DPage: React.FC = () => {
  const [params, setParams] = useState<FrondParams>({
    rachisNodes: 46,
    rachisLength: 10,
    pinnaMax: 2.6,
    pinnaAngle: 55,
    baseCurl: 22,
    pinnules: 6,
  });
  const [u, setU] = useState(1);
  const [isAnimating, setIsAnimating] = useState(false);
  const animRef = useRef<number>();

  const frond = useMemo(() => buildFrond(params, u), [params, u]);

  const traces = useMemo(
    () => [
      segTrace(frond.rachis, '#6f5a2e', 6),
      segTrace(frond.pinna, '#4c9a2a', 2.5),
      {
        type: 'scatter3d', mode: 'markers',
        x: frond.pinnules.map((q) => q[0]),
        y: frond.pinnules.map(() => 0),
        z: frond.pinnules.map((q) => q[1]),
        marker: { color: '#77c043', size: 3, opacity: 0.9 },
        hoverinfo: 'none', showlegend: false,
      },
    ],
    [frond]
  );

  // Unfurl animation: ramp u from 0 to 1.
  useEffect(() => {
    if (!isAnimating) return;
    const tick = () => {
      setU((prev) => {
        const next = prev + 0.012;
        if (next >= 1) {
          setIsAnimating(false);
          return 1;
        }
        animRef.current = requestAnimationFrame(tick);
        return next;
      });
    };
    animRef.current = requestAnimationFrame(tick);
    return () => {
      if (animRef.current) cancelAnimationFrame(animRef.current);
    };
  }, [isAnimating]);

  const setParam = (k: keyof FrondParams, v: number) => setParams((p) => ({ ...p, [k]: v }));

  const unfurl = () => {
    if (isAnimating) {
      setIsAnimating(false);
    } else {
      setU(0);
      setIsAnimating(true);
    }
  };

  const coilUp = () => {
    setIsAnimating(false);
    setU(0);
  };

  const infoTabs = [
    {
      label: 'Overview',
      content: (
        <>
          <Typography variant="h6" gutterBottom>Circinate vernation</Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            Young fern fronds emerge tightly coiled as a "fiddlehead" (crozier) and unroll from the base
            upward — the tip is the last to open. Drag the <strong>Unfurl</strong> slider, or press the
            button, to watch a bipinnate frond open exactly this way.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            The rachis (main stalk) bears opposite pinnae, and each pinna carries a row of pinnules. Pinna
            length peaks in the lower third of the frond, giving the classic tapered lance-shaped outline.
          </Typography>
        </>
      ),
    },
    {
      label: 'Biology',
      content: (
        <>
          <Typography variant="h6" gutterBottom>Why ferns coil</Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            Circinate vernation protects the delicate, actively dividing tip inside the coil while the frond
            expands. It is a hallmark of ferns (Polypodiopsida) and a few cycads, and reflects differential
            growth: cells on the outer face of the coil elongate faster than those on the inner face.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            The self-similar rachis → pinna → pinnule division makes the frond a natural fractal, closely
            related to the Barnsley fern produced by an iterated function system.
          </Typography>
        </>
      ),
    },
    {
      label: 'Mathematics',
      content: (
        <>
          <Typography variant="h6" gutterBottom>Coil as a spiral</Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            The coiled tip approximates a logarithmic (equiangular) spiral, where the turning rate per unit
            length is constant:
          </Typography>
          <MathRenderer math="r(\theta) = a\, e^{b\theta}" block />
          <Typography variant="body2" sx={{ mt: 2 }}>
            Here each rachis node adds a bend proportional to its arc position <MathRenderer math="s" /> and a
            coil factor that switches off once the unfurl front <MathRenderer math="u" /> passes it:
          </Typography>
          <MathRenderer math="\Delta\phi(s) = \phi_0 \,(1 + 3.2\,s)\cdot \mathrm{clamp}\!\left(\tfrac{s-u}{0.18}\right)" block />
        </>
      ),
    },
  ];

  const controls = (
    <>
      <ControlSection title="Unfurling" accent={ACCENT} first>
        <ParameterSlider
          label="Unfurl" value={u} onChange={(v) => { setIsAnimating(false); setU(v); }}
          min={0} max={1} step={0.01} format={(v) => `${Math.round(v * 100)}%`}
          help="0% is a tight fiddlehead; 100% is a fully opened frond."
        />
      </ControlSection>

      <ControlSection title="Frond shape" accent={ACCENT}>
        <ParameterSlider label="Rachis length" value={params.rachisLength} onChange={(v) => setParam('rachisLength', v)} min={5} max={16} step={0.5} format={(v) => v.toFixed(1)} />
        <ParameterSlider label="Detail (nodes)" value={params.rachisNodes} onChange={(v) => setParam('rachisNodes', v)} min={20} max={70} step={1} help="Number of rachis segments — higher is smoother and denser." />
        <ParameterSlider label="Pinna length" value={params.pinnaMax} onChange={(v) => setParam('pinnaMax', v)} min={1} max={4.5} step={0.1} format={(v) => v.toFixed(1)} />
        <ParameterSlider label="Pinna angle" value={params.pinnaAngle} onChange={(v) => setParam('pinnaAngle', v)} min={20} max={80} step={1} unit="°" />
        <ParameterSlider label="Coil tightness" value={params.baseCurl} onChange={(v) => setParam('baseCurl', v)} min={10} max={36} step={1} unit="°" help="Bend added per node inside the coil — higher makes a tighter fiddlehead." />
        <ParameterSlider label="Pinnules / pinna" value={params.pinnules} onChange={(v) => setParam('pinnules', v)} min={3} max={12} step={1} />
      </ControlSection>

      <ControlSection title="Actions" accent={ACCENT}>
        <ActionBar
          actions={[
            { label: isAnimating ? 'Pause' : 'Unfurl fiddlehead', onClick: unfurl, icon: isAnimating ? <Pause /> : <PlayArrow />, variant: 'contained', color: ACCENT },
            { label: 'Coil up', onClick: coilUp, icon: <ReplayCircleFilled /> },
          ]}
        />
      </ControlSection>

      <ControlSection title="Statistics" accent={ACCENT}>
        <Typography variant="body2">Rachis nodes: <strong>{params.rachisNodes}</strong></Typography>
        <Typography variant="body2">Pinnules drawn: <strong>{frond.pinnules.length.toLocaleString()}</strong></Typography>
        <Typography variant="body2">Unfurled: <strong>{Math.round(u * 100)}%</strong></Typography>
        <Typography variant="body2">Fractal dimension: <strong>≈ 1.7</strong></Typography>
      </ControlSection>
    </>
  );

  return (
    <AppScaffold
      title="Fern Frond 3D"
      subtitle="Watch a bipinnate fern frond unroll from its coiled fiddlehead — circinate vernation, base to tip."
      accent={ACCENT}
      category="Branching Architectures"
      infoTabs={infoTabs}
      caption={`${frond.pinnules.length.toLocaleString()} pinnules · ${Math.round(u * 100)}% unfurled · drag to orbit`}
      visualization={
        <Plot
          data={traces as any}
          layout={{
            autosize: true,
            scene: {
              xaxis: { visible: false },
              yaxis: { visible: false },
              zaxis: { visible: false },
              aspectmode: 'data' as const,
              bgcolor: 'rgba(0,0,0,0)',
              camera: { eye: { x: 0.3, y: 2.2, z: 0.4 }, up: { x: 0, y: 0, z: 1 } },
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
