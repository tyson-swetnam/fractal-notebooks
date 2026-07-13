import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Typography, Box } from '@mui/material';
import { MathRenderer } from '../../components/math/MathRenderer';
import { PlayArrow, Pause, Refresh, Park } from '@mui/icons-material';
import { AppScaffold, ControlSection, ParameterSlider, ParameterSelect, ActionBar } from '../../components/controls';
import { useTheme } from '../../contexts/ThemeContext';

const ACCENT = '#2e7d32';

interface FernParams {
  numPoints: number;
  animationSpeed: number;
  fernType: 'barnsley' | 'thelypteridaceae' | 'culcita' | 'fishbone';
}

const FERN_TYPES = {
  barnsley: [
    { a: 0, b: 0, c: 0, d: 0.16, e: 0, f: 0, p: 0.01 },
    { a: 0.85, b: 0.04, c: -0.04, d: 0.85, e: 0, f: 1.6, p: 0.85 },
    { a: 0.2, b: -0.26, c: 0.23, d: 0.22, e: 0, f: 1.6, p: 0.07 },
    { a: -0.15, b: 0.28, c: 0.26, d: 0.24, e: 0, f: 0.44, p: 0.07 },
  ],
  thelypteridaceae: [
    { a: 0, b: 0, c: 0, d: 0.25, e: 0, f: -0.4, p: 0.02 },
    { a: 0.95, b: 0.005, c: -0.005, d: 0.93, e: -0.002, f: 0.5, p: 0.84 },
    { a: 0.035, b: -0.2, c: 0.16, d: 0.04, e: -0.09, f: 0.02, p: 0.07 },
    { a: -0.04, b: 0.2, c: 0.16, d: 0.04, e: 0.083, f: 0.12, p: 0.07 },
  ],
  culcita: [
    { a: 0, b: 0, c: 0, d: 0.16, e: 0, f: 0, p: 0.01 },
    { a: 0.85, b: 0.04, c: -0.04, d: 0.85, e: 0, f: 1.6, p: 0.85 },
    { a: 0.2, b: -0.26, c: 0.23, d: 0.22, e: 0, f: 1.6, p: 0.07 },
    { a: -0.15, b: 0.28, c: 0.26, d: 0.24, e: 0, f: 0.44, p: 0.07 },
  ],
  fishbone: [
    { a: 0, b: 0, c: 0, d: 0.25, e: 0, f: -0.14, p: 0.02 },
    { a: 0.85, b: 0.02, c: -0.02, d: 0.83, e: 0, f: 1, p: 0.84 },
    { a: 0.09, b: -0.28, c: 0.3, d: 0.11, e: 0, f: 0.6, p: 0.07 },
    { a: -0.09, b: 0.28, c: 0.3, d: 0.09, e: 0, f: 0.7, p: 0.07 },
  ],
};

const FERN_LABELS: Record<FernParams['fernType'], string> = {
  barnsley: 'Barnsley Fern',
  thelypteridaceae: 'Thelypteridaceae',
  culcita: 'Culcita',
  fishbone: 'Fishbone Fern',
};

export const FernPage: React.FC = () => {
  const { effectiveTheme } = useTheme();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const [isAnimating, setIsAnimating] = useState(false);
  const [currentPoint, setCurrentPoint] = useState(0);
  const [params, setParams] = useState<FernParams>({
    numPoints: 50000,
    animationSpeed: 100,
    fernType: 'barnsley',
  });

  const [points, setPoints] = useState<{ x: number; y: number }[]>([]);

  const generateFern = useCallback(() => {
    const transforms = FERN_TYPES[params.fernType];
    const newPoints: { x: number; y: number }[] = [];

    let x = 0;
    let y = 0;

    for (let i = 0; i < params.numPoints; i++) {
      const rand = Math.random();
      let cumulativeP = 0;
      let selectedTransform = transforms[0];

      for (const transform of transforms) {
        cumulativeP += transform.p;
        if (rand <= cumulativeP) {
          selectedTransform = transform;
          break;
        }
      }

      const newX = selectedTransform.a * x + selectedTransform.b * y + selectedTransform.e;
      const newY = selectedTransform.c * x + selectedTransform.d * y + selectedTransform.f;

      x = newX;
      y = newY;

      newPoints.push({ x, y });
    }

    setPoints(newPoints);
    setCurrentPoint(0);
  }, [params.fernType, params.numPoints]);

  const drawFern = useCallback(() => {
    if (!canvasRef.current || points.length === 0) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const visiblePoints = points.slice(0, currentPoint + 1);
    if (visiblePoints.length === 0) return;

    const minX = Math.min(...points.map((p) => p.x));
    const maxX = Math.max(...points.map((p) => p.x));
    const minY = Math.min(...points.map((p) => p.y));
    const maxY = Math.max(...points.map((p) => p.y));

    const padding = 50;
    const scaleX = (canvas.width - 2 * padding) / (maxX - minX || 1);
    const scaleY = (canvas.height - 2 * padding) / (maxY - minY || 1);
    const scale = Math.min(scaleX, scaleY);

    const offsetX = canvas.width / 2 - ((minX + maxX) / 2) * scale;
    const offsetY = padding - minY * scale;

    const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
    gradient.addColorStop(0, '#90EE90');
    gradient.addColorStop(0.3, '#228B22');
    gradient.addColorStop(1, '#006400');

    ctx.fillStyle = gradient;

    visiblePoints.forEach((point, index) => {
      const px = point.x * scale + offsetX;
      const py = point.y * scale + offsetY;

      const alpha = Math.min(1, 0.1 + (index / visiblePoints.length) * 0.9);
      const size = 1 + (point.y - minY) / (maxY - minY || 1);

      ctx.globalAlpha = alpha;
      ctx.beginPath();
      ctx.arc(px, py, size, 0, 2 * Math.PI);
      ctx.fill();
    });

    ctx.globalAlpha = 1;
  }, [points, currentPoint]);

  const animate = useCallback(() => {
    if (currentPoint < points.length - 1) {
      setCurrentPoint((prev) => Math.min(prev + Math.ceil(params.animationSpeed / 10), points.length - 1));
      animationRef.current = requestAnimationFrame(animate);
    } else {
      setIsAnimating(false);
    }
  }, [currentPoint, points.length, params.animationSpeed]);

  useEffect(() => {
    drawFern();
  }, [drawFern]);

  useEffect(() => {
    generateFern();
  }, [generateFern]);

  useEffect(() => {
    if (isAnimating) {
      animate();
    }
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isAnimating, animate]);

  const handleParamChange = (key: keyof FernParams, value: number | string) => {
    setParams((prev) => ({ ...prev, [key]: value }));
  };

  const toggleAnimation = () => {
    if (isAnimating) {
      setIsAnimating(false);
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    } else {
      setCurrentPoint(0);
      setIsAnimating(true);
    }
  };

  const showFullFern = () => {
    setCurrentPoint(points.length - 1);
    setIsAnimating(false);
  };

  const resetFern = () => {
    setCurrentPoint(0);
    setIsAnimating(false);
  };

  const infoTabs = [
    {
      label: 'Overview',
      content: (
        <>
          <Typography variant="h6" gutterBottom>Iterated function system (IFS)</Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            A Barnsley fern is drawn one point at a time by the "chaos game": starting from a point, one of four
            affine maps is chosen at random (weighted by probability) and applied, and the result is plotted. Over
            tens of thousands of iterations the points converge on the fern's self-similar attractor.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            The four maps encode the stem, the successively smaller leaflets, and the left/right sub-fronds — a
            compact recipe for a strikingly lifelike frond.
          </Typography>
        </>
      ),
    },
    {
      label: 'Mathematics',
      content: (
        <>
          <Typography variant="h6" gutterBottom>Affine transformations</Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            Each iteration applies one affine map selected with probability <MathRenderer math="p_i" />:
          </Typography>
          <MathRenderer
            math="\begin{pmatrix} x_{n+1} \\ y_{n+1} \end{pmatrix} = \begin{pmatrix} a & b \\ c & d \end{pmatrix} \begin{pmatrix} x_n \\ y_n \end{pmatrix} + \begin{pmatrix} e \\ f \end{pmatrix}"
            block
          />
          <Typography variant="body2" sx={{ mt: 2 }}>
            The classic Barnsley fern uses four such maps. Different coefficient sets yield distinct fern species —
            try Thelypteridaceae, Culcita, or a fishbone fern from the selector.
          </Typography>
        </>
      ),
    },
    {
      label: 'Biology',
      content: (
        <>
          <Typography variant="h6" gutterBottom>Ferns as natural fractals</Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            Real fern fronds are compound leaves whose pinnae repeat the shape of the whole frond at smaller scale.
            This self-similarity is exactly what the IFS captures, which is why so few numbers reproduce the form
            so convincingly.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            For a developmental view of the same organ — the frond unrolling from its fiddlehead — see the
            <strong> Fern Frond 3D</strong> app.
          </Typography>
        </>
      ),
    },
  ];

  const controls = (
    <>
      <ControlSection title="Fern species" accent={ACCENT} first>
        <ParameterSelect
          label="Fern type"
          value={params.fernType}
          onChange={(v) => handleParamChange('fernType', v)}
          options={[
            { value: 'barnsley', label: 'Barnsley Fern', hint: 'The classic 4-map fern' },
            { value: 'thelypteridaceae', label: 'Thelypteridaceae', hint: 'Marsh / maiden ferns' },
            { value: 'culcita', label: 'Culcita', hint: 'Soft tree-fern relative' },
            { value: 'fishbone', label: 'Fishbone Fern', hint: 'Narrow, ladder-like pinnae' },
          ]}
        />
      </ControlSection>

      <ControlSection title="Rendering" accent={ACCENT}>
        <ParameterSlider
          label="Number of points"
          value={params.numPoints}
          onChange={(v) => handleParamChange('numPoints', v)}
          min={5000}
          max={100000}
          step={5000}
          format={(v) => `${(v / 1000).toFixed(0)}k`}
          help="More points fill in the fern's fine detail but take longer to draw."
        />
        <ParameterSlider
          label="Animation speed"
          value={params.animationSpeed}
          onChange={(v) => handleParamChange('animationSpeed', v)}
          min={10}
          max={500}
          step={10}
          help="Points revealed per frame while animating growth."
        />
      </ControlSection>

      <ControlSection title="Actions" accent={ACCENT}>
        <ActionBar
          actions={[
            {
              label: isAnimating ? 'Pause growth' : 'Animate growth',
              onClick: toggleAnimation,
              icon: isAnimating ? <Pause /> : <PlayArrow />,
              variant: 'contained',
              color: ACCENT,
            },
            { label: 'Show complete fern', onClick: showFullFern, icon: <Park /> },
            { label: 'Reset', onClick: resetFern, icon: <Refresh /> },
          ]}
        />
      </ControlSection>

      <ControlSection title="Statistics" accent={ACCENT}>
        <Typography variant="body2">Species: <strong>{FERN_LABELS[params.fernType]}</strong></Typography>
        <Typography variant="body2">Points drawn: <strong>{(currentPoint + 1).toLocaleString()} / {points.length.toLocaleString()}</strong></Typography>
        <Typography variant="body2">Transforms: <strong>{FERN_TYPES[params.fernType].length}</strong></Typography>
        <Typography variant="body2">Fractal dimension: <strong>≈ 1.66</strong></Typography>
      </ControlSection>
    </>
  );

  return (
    <AppScaffold
      title="Barnsley Ferns"
      subtitle="Grow lifelike fern fronds from a four-map iterated function system — the chaos game in action."
      accent={ACCENT}
      category="Branching Architectures"
      infoTabs={infoTabs}
      caption={`${FERN_LABELS[params.fernType]} — ${(currentPoint + 1).toLocaleString()} of ${points.length.toLocaleString()} points`}
      visualization={
        <Box sx={{ display: 'flex', justifyContent: 'center' }}>
          <canvas
            ref={canvasRef}
            width={800}
            height={600}
            style={{
              width: '100%',
              maxWidth: 800,
              height: 'auto',
              borderRadius: 8,
              backgroundColor: effectiveTheme === 'dark' ? '#0b0f0b' : '#eef3ec',
            }}
          />
        </Box>
      }
      controls={controls}
    />
  );
};
