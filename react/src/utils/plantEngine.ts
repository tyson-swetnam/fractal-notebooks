/**
 * 3D turtle interpreter for L-system strings, plus helpers that convert the
 * resulting geometry into Plotly traces.
 *
 * The turtle carries an orthonormal frame (heading H, left Lft, up Up) and
 * walks the module string. Bracketed sub-strings push/pop the full state, which
 * is how branching arises. Optional tropism bends the heading toward a fixed
 * vector each step, modelling gravitropism (roots) or phototropism (shoots).
 *
 * Command alphabet (ABOP-style):
 *   F  draw a segment forward        f  move forward without drawing
 *   +  yaw left      -  yaw right     &  pitch down    ^  pitch up
 *   \  roll left     /  roll right    |  turn around (180° yaw)
 *   [  push state    ]  pop state
 *   !  scale width by widthFactor     >  scale length by lengthFactor
 *   <  scale length by 1/lengthFactor
 *   L  place an organ (leaf / lamina / apothecium …) at the current node
 */

import chroma from 'chroma-js';

type Vec3 = [number, number, number];

const add = (a: Vec3, b: Vec3): Vec3 => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const scaleV = (v: Vec3, s: number): Vec3 => [v[0] * s, v[1] * s, v[2] * s];
const dot = (a: Vec3, b: Vec3): number => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a: Vec3, b: Vec3): Vec3 => [
  a[1] * b[2] - a[2] * b[1],
  a[2] * b[0] - a[0] * b[2],
  a[0] * b[1] - a[1] * b[0],
];
const len = (v: Vec3): number => Math.sqrt(dot(v, v));
const norm = (v: Vec3): Vec3 => {
  const l = len(v);
  return l > 1e-9 ? [v[0] / l, v[1] / l, v[2] / l] : [0, 0, 1];
};

/** Rotate vector v about a unit axis k by angle theta (Rodrigues' formula). */
function rotate(v: Vec3, k: Vec3, theta: number): Vec3 {
  const c = Math.cos(theta);
  const s = Math.sin(theta);
  const d = dot(k, v);
  const cr = cross(k, v);
  return [
    v[0] * c + cr[0] * s + k[0] * d * (1 - c),
    v[1] * c + cr[1] * s + k[1] * d * (1 - c),
    v[2] * c + cr[2] * s + k[2] * d * (1 - c),
  ];
}

export type OrganKind = 'leaf' | 'lamina' | 'thallus' | 'apothecium' | 'flower' | 'none';

export interface Segment {
  p0: Vec3;
  p1: Vec3;
  width: number;
  order: number;
}

export interface Organ {
  pos: Vec3;
  order: number;
  size: number;
}

export interface PlantGeometry {
  segments: Segment[];
  organs: Organ[];
  maxOrder: number;
  bounds: { min: Vec3; max: Vec3 };
}

export interface TurtleParams {
  angle: number; // base turn/pitch angle (degrees)
  angleJitter: number; // random ± added to each rotation (degrees)
  rollAngle: number; // angle used by roll commands / and \ (degrees)
  step: number; // initial segment length
  lengthFactor: number; // '>' length multiplier (<1 shrinks)
  widthFactor: number; // '!' width multiplier
  initialWidth: number;
  tropism: Vec3; // direction the heading is pulled toward
  tropismStrength: number; // 0..1 susceptibility
  planar: boolean; // if true, pitch/roll are ignored (2D fan in the XY plane)
  organSize: number;
}

interface TurtleState {
  pos: Vec3;
  H: Vec3;
  Lft: Vec3;
  Up: Vec3;
  step: number;
  width: number;
  order: number;
}

const DEG = Math.PI / 180;

/** Interpret an L-system string into 3D geometry. */
export function interpret(str: string, params: TurtleParams, rng: () => number): PlantGeometry {
  const segments: Segment[] = [];
  const organs: Organ[] = [];

  // Initial frame: growing along +Z, or along +Y for planar plants.
  const start: TurtleState = params.planar
    ? { pos: [0, 0, 0], H: [0, 1, 0], Lft: [1, 0, 0], Up: [0, 0, 1], step: params.step, width: params.initialWidth, order: 0 }
    : { pos: [0, 0, 0], H: [0, 0, 1], Lft: [1, 0, 0], Up: [0, 1, 0], step: params.step, width: params.initialWidth, order: 0 };

  let state: TurtleState = { ...start };
  const stack: TurtleState[] = [];

  const min: Vec3 = [Infinity, Infinity, Infinity];
  const max: Vec3 = [-Infinity, -Infinity, -Infinity];
  const track = (p: Vec3) => {
    for (let i = 0; i < 3; i++) {
      if (p[i] < min[i]) min[i] = p[i];
      if (p[i] > max[i]) max[i] = p[i];
    }
  };
  track(start.pos);

  let maxOrder = 0;
  const jitter = () => (params.angleJitter > 0 ? (rng() * 2 - 1) * params.angleJitter * DEG : 0);

  // Rotate the whole frame about an axis (keeps H, Lft, Up orthonormal).
  const rotFrame = (axis: Vec3, theta: number) => {
    state.H = norm(rotate(state.H, axis, theta));
    state.Lft = norm(rotate(state.Lft, axis, theta));
    state.Up = norm(rotate(state.Up, axis, theta));
  };

  for (const cmd of str) {
    switch (cmd) {
      case 'F': {
        // Optional tropism: bend heading toward the tropism vector.
        if (params.tropismStrength > 0 && !params.planar) {
          const torque = cross(state.H, params.tropism);
          const m = len(torque);
          if (m > 1e-6) {
            rotFrame(scaleV(torque, 1 / m), params.tropismStrength * m * 0.5);
          }
        }
        const p1 = add(state.pos, scaleV(state.H, state.step));
        segments.push({ p0: state.pos, p1, width: state.width, order: state.order });
        track(p1);
        state.pos = p1;
        break;
      }
      case 'f': {
        state.pos = add(state.pos, scaleV(state.H, state.step));
        track(state.pos);
        break;
      }
      case '+':
        rotFrame(state.Up, params.angle * DEG + jitter());
        break;
      case '-':
        rotFrame(state.Up, -params.angle * DEG + jitter());
        break;
      case '&':
        if (!params.planar) rotFrame(state.Lft, params.angle * DEG + jitter());
        break;
      case '^':
        if (!params.planar) rotFrame(state.Lft, -params.angle * DEG + jitter());
        break;
      case '/':
        if (!params.planar) rotFrame(state.H, params.rollAngle * DEG);
        break;
      case '\\':
        if (!params.planar) rotFrame(state.H, -params.rollAngle * DEG);
        break;
      case '|':
        rotFrame(state.Up, Math.PI);
        break;
      case '!':
        state.width = Math.max(0.4, state.width * params.widthFactor);
        break;
      case '>':
        state.step *= params.lengthFactor;
        break;
      case '<':
        state.step /= params.lengthFactor;
        break;
      case 'L':
        organs.push({
          pos: state.pos,
          order: state.order,
          size: params.organSize * Math.max(0.35, Math.min(1, state.step / params.step)),
        });
        break;
      case '[':
        stack.push({ ...state });
        state = { ...state, order: state.order + 1 };
        if (state.order > maxOrder) maxOrder = state.order;
        break;
      case ']': {
        const popped = stack.pop();
        if (popped) state = popped;
        break;
      }
      default:
        break;
    }
  }

  if (!isFinite(min[0])) {
    min[0] = min[1] = min[2] = 0;
    max[0] = max[1] = max[2] = 1;
  }

  return { segments, organs, maxOrder, bounds: { min, max } };
}

export interface PlantStyle {
  barkColor: string; // colour at order 0 (trunk / base)
  tipColor: string; // colour at the highest order (tips)
  organColor: string;
  baseWidth: number; // line width (px) at order 0
}

/**
 * Convert geometry into Plotly traces. Segments are bucketed by branch order;
 * each order becomes one scatter3d line trace (segments separated by nulls) so
 * a whole plant is a handful of traces regardless of segment count. `maxVisible`
 * limits which orders are drawn, enabling a growth animation.
 */
export function buildPlotTraces(
  geo: PlantGeometry,
  style: PlantStyle,
  opts: { showOrgans?: boolean; maxVisibleOrder?: number } = {}
): unknown[] {
  const { showOrgans = true, maxVisibleOrder = Infinity } = opts;
  const traces: unknown[] = [];
  const orderCount = Math.max(1, geo.maxOrder);
  const scale = chroma.scale([style.barkColor, style.tipColor]).mode('lab');

  // Group segments by order.
  const byOrder = new Map<number, Segment[]>();
  for (const seg of geo.segments) {
    if (seg.order > maxVisibleOrder) continue;
    const arr = byOrder.get(seg.order) ?? [];
    arr.push(seg);
    byOrder.set(seg.order, arr);
  }

  const orders = Array.from(byOrder.keys()).sort((a, b) => a - b);
  for (const order of orders) {
    const segs = byOrder.get(order)!;
    const x: (number | null)[] = [];
    const y: (number | null)[] = [];
    const z: (number | null)[] = [];
    for (const s of segs) {
      x.push(s.p0[0], s.p1[0], null);
      y.push(s.p0[1], s.p1[1], null);
      z.push(s.p0[2], s.p1[2], null);
    }
    const t = order / orderCount;
    const width = Math.max(1, style.baseWidth * Math.pow(0.62, order));
    traces.push({
      type: 'scatter3d',
      mode: 'lines',
      x,
      y,
      z,
      line: { color: scale(t).hex(), width },
      hoverinfo: 'none',
      showlegend: false,
    });
  }

  if (showOrgans && geo.organs.length > 0) {
    const visible = geo.organs.filter((o) => o.order <= maxVisibleOrder);
    if (visible.length > 0) {
      const avgSize = visible.reduce((s, o) => s + o.size, 0) / visible.length;
      traces.push({
        type: 'scatter3d',
        mode: 'markers',
        x: visible.map((o) => o.pos[0]),
        y: visible.map((o) => o.pos[1]),
        z: visible.map((o) => o.pos[2]),
        marker: {
          color: style.organColor,
          size: Math.max(2, avgSize),
          opacity: 0.85,
          symbol: 'circle',
        },
        hoverinfo: 'none',
        showlegend: false,
      });
    }
  }

  return traces;
}
