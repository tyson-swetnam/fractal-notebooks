/**
 * Botanically-informed L-system presets spanning the major land-plant and
 * lichen growth forms. Each preset pairs a rewriting grammar with turtle
 * parameters and a colour style, plus short overview / biology notes used by
 * the Plant Architecture Lab.
 *
 * The grammars follow the modelling tradition of Prusinkiewicz & Lindenmayer
 * ("The Algorithmic Beauty of Plants"), adapted to the characteristic
 * architecture of each group: dichotomous thalli (liverworts), erect leafy
 * shoots with spiral phyllotaxis (acrocarpous mosses), freely branched feathers
 * (pleurocarpous mosses), pinnate fronds (ferns), 3D dichotomous podetia
 * (fruticose lichens), monopodial herbaceous axes, and woody trees/shrubs.
 */

import type { LSystemSpec } from './lsystem';
import type { TurtleParams, PlantStyle } from './plantEngine';

export interface PlantPreset {
  key: string;
  label: string;
  group: 'Bryophytes' | 'Ferns' | 'Lichens' | 'Vascular (herbaceous)' | 'Woody';
  tagline: string;
  description: string;
  biology: string;
  fractalDim: string;
  spec: LSystemSpec;
  turtle: TurtleParams;
  style: PlantStyle;
  showOrgans: boolean;
  iterationRange: [number, number];
}

const GOLDEN = 137.5; // golden-angle phyllotaxis

export const PLANT_PRESETS: PlantPreset[] = [
  {
    key: 'liverwort',
    label: 'Thalloid liverwort',
    group: 'Bryophytes',
    tagline: 'Marchantia — flat, repeatedly forking thallus',
    description:
      'A thalloid liverwort grows as a flat ribbon that repeatedly forks in two (isotomous dichotomy). There is no true stem or leaf — the whole body is a single sheet of tissue that splits at each growing tip.',
    biology:
      'Liverworts (Marchantiophyta) are among the earliest-diverging land plants. Dichotomous branching of the thallus is their signature architecture; each fork is an equal division of the apical meristem.',
    fractalDim: '≈ 1.58',
    spec: { axiom: 'X', rules: { X: 'F[+X][-X]' }, iterations: 7 },
    turtle: {
      angle: 32, angleJitter: 6, rollAngle: 0, step: 1, lengthFactor: 0.85, widthFactor: 0.78,
      initialWidth: 7, tropism: [0, 0, 1], tropismStrength: 0, planar: true, organSize: 3,
    },
    style: { barkColor: '#3f7d3a', tipColor: '#9bd17a', organColor: '#8fce6a', baseWidth: 8 },
    showOrgans: false,
    iterationRange: [3, 9],
  },
  {
    key: 'hornwort',
    label: 'Hornwort',
    group: 'Bryophytes',
    tagline: 'Anthoceros — erect horn-like sporophytes',
    description:
      'A hornwort raises a tuft of slender, needle-like sporophytes ("horns") from a low thalloid gametophyte. Each horn grows continuously from a basal meristem rather than branching.',
    biology:
      'Hornworts (Anthocerotophyta) are the third bryophyte lineage. Their unbranched, upward-growing sporophyte is unique among land plants for its intercalary (basal) growth.',
    fractalDim: '≈ 1.05',
    spec: { axiom: 'A[&A][^A][+A][-A]', rules: { A: 'FA' }, iterations: 6 },
    turtle: {
      angle: 20, angleJitter: 8, rollAngle: 90, step: 0.7, lengthFactor: 1, widthFactor: 1,
      initialWidth: 3, tropism: [0, 0, 1], tropismStrength: 0.15, planar: false, organSize: 2,
    },
    style: { barkColor: '#3a6b4f', tipColor: '#7fbf8f', organColor: '#6fae7f', baseWidth: 4 },
    showOrgans: false,
    iterationRange: [3, 10],
  },
  {
    key: 'moss_acro',
    label: 'Acrocarpous moss',
    group: 'Bryophytes',
    tagline: 'Erect leafy shoot, spiral phyllotaxis',
    description:
      'An acrocarpous moss forms an unbranched (or sparsely branched) erect shoot with small leaves arranged in a tight spiral around the stem. The sporophyte, when present, terminates the main axis.',
    biology:
      'Acrocarpous mosses (e.g. Polytrichum, Bryum) grow upright in cushions. Leaves follow golden-angle (137.5°) phyllotaxis, packing maximally around the leafy gametophyte stem.',
    fractalDim: '≈ 1.12',
    spec: { axiom: 'A', rules: { A: 'F[&L][^L]/A' }, iterations: 16 },
    turtle: {
      angle: 58, angleJitter: 10, rollAngle: GOLDEN, step: 0.6, lengthFactor: 1, widthFactor: 1,
      initialWidth: 3, tropism: [0, 0, 1], tropismStrength: 0.08, planar: false, organSize: 2.4,
    },
    style: { barkColor: '#4c7a43', tipColor: '#8fc96a', organColor: '#79b94f', baseWidth: 3.5 },
    showOrgans: true,
    iterationRange: [6, 26],
  },
  {
    key: 'moss_pleuro',
    label: 'Pleurocarpous moss',
    group: 'Bryophytes',
    tagline: 'Freely branched feather moss',
    description:
      'A pleurocarpous moss spreads as a much-branched, feathery mat. A creeping main axis produces paired side branches, each of which bears its own smaller branchlets and leaves.',
    biology:
      'Pleurocarpous mosses (e.g. Hypnum, Thuidium) branch freely and bear sporophytes on short lateral shoots. Their plumose architecture maximises surface area for water capture.',
    fractalDim: '≈ 1.5',
    spec: { axiom: 'A', rules: { A: 'F[+B][-B]/A', B: 'F[+L][-L]>B' }, iterations: 6 },
    turtle: {
      angle: 40, angleJitter: 12, rollAngle: 65, step: 0.9, lengthFactor: 0.8, widthFactor: 0.72,
      initialWidth: 3.5, tropism: [0, 0, 1], tropismStrength: 0.05, planar: false, organSize: 2.2,
    },
    style: { barkColor: '#4f7a3e', tipColor: '#9ccf68', organColor: '#82be52', baseWidth: 4 },
    showOrgans: true,
    iterationRange: [4, 8],
  },
  {
    key: 'fern',
    label: 'Fern frond (bipinnate)',
    group: 'Ferns',
    tagline: 'Rachis → pinnae → pinnules',
    description:
      'A fern frond is a compound leaf: a central rachis bears opposite pinnae, and each pinna bears smaller pinnules. Older (basal) pinnae have had longer to develop, giving the frond its tapered outline.',
    biology:
      'Ferns (Polypodiopsida) are seedless vascular plants. Their fronds unroll from a coiled fiddlehead (circinate vernation) and show self-similar pinnate division across two or more orders.',
    fractalDim: '≈ 1.72',
    spec: { axiom: 'X', rules: { X: 'F[+P][-P]>X', P: 'F[+Q][-Q]>P', Q: 'FL' }, iterations: 8 },
    turtle: {
      angle: 42, angleJitter: 5, rollAngle: 0, step: 1.2, lengthFactor: 0.82, widthFactor: 0.72,
      initialWidth: 5, tropism: [0, 0, 1], tropismStrength: 0, planar: false, organSize: 2.4,
    },
    style: { barkColor: '#5f7d33', tipColor: '#a6cf63', organColor: '#7cb342', baseWidth: 5 },
    showOrgans: true,
    iterationRange: [4, 11],
  },
  {
    key: 'lichen_fruticose',
    label: 'Fruticose lichen',
    group: 'Lichens',
    tagline: 'Cladonia / Usnea — shrubby 3D dichotomy',
    description:
      'A fruticose lichen builds a miniature shrub of hollow, repeatedly dividing branches (podetia) in three dimensions. Reproductive cups or discs (apothecia) sit at the tips.',
    biology:
      'Lichens are symbioses of fungi with algae or cyanobacteria — not plants — but their fruticose thalli branch dichotomously in 3D, an architecture that maximises light and air exposure for the photobiont.',
    fractalDim: '≈ 2.1',
    spec: { axiom: 'X', rules: { X: 'F[&+>X][&->X][^/>X]' }, iterations: 6 },
    turtle: {
      angle: 26, angleJitter: 16, rollAngle: 90, step: 0.95, lengthFactor: 0.82, widthFactor: 0.72,
      initialWidth: 4, tropism: [0, 0, 1], tropismStrength: 0.06, planar: false, organSize: 2.8,
    },
    style: { barkColor: '#9fb0a0', tipColor: '#d4dcc9', organColor: '#8a5a3a', baseWidth: 4.5 },
    showOrgans: true,
    iterationRange: [3, 7],
  },
  {
    key: 'herbaceous',
    label: 'Herbaceous plant',
    group: 'Vascular (herbaceous)',
    tagline: 'Monopodial stem, spiral leaves',
    description:
      'A herbaceous seed plant grows a single dominant (monopodial) stem that lays down leaf-bearing lateral shoots in a golden-angle spiral. The main axis keeps the lead; laterals stay subordinate.',
    biology:
      'Herbaceous angiosperms concentrate growth at a single apical meristem (apical dominance). Spiral phyllotaxis at 137.5° minimises self-shading of successive leaves.',
    fractalDim: '≈ 1.5',
    spec: { axiom: 'A', rules: { A: 'F[&B]/A', B: 'F[+L][-L]' }, iterations: 12 },
    turtle: {
      angle: 55, angleJitter: 8, rollAngle: GOLDEN, step: 0.9, lengthFactor: 0.9, widthFactor: 0.85,
      initialWidth: 3.5, tropism: [0, 0, 1], tropismStrength: 0.12, planar: false, organSize: 3.2,
    },
    style: { barkColor: '#4a7c3f', tipColor: '#86c05a', organColor: '#6fb03c', baseWidth: 4 },
    showOrgans: true,
    iterationRange: [5, 18],
  },
  {
    key: 'shrub',
    label: 'Woody shrub',
    group: 'Woody',
    tagline: 'Multi-branched 3D bush',
    description:
      'A shrub branches profusely in three dimensions from near the base, with no single trunk dominating. Repeated tri-furcation with random variation fills a rounded crown volume.',
    biology:
      'Shrubs invest in many woody axes rather than one trunk. The bushy, space-filling crown (fractal dimension well above 2) is efficient for intercepting light in the understory.',
    fractalDim: '≈ 2.3',
    spec: { axiom: 'X', rules: { X: 'F[&+>X][&->X][/>X]' }, iterations: 6 },
    turtle: {
      angle: 24, angleJitter: 12, rollAngle: 100, step: 1.2, lengthFactor: 0.8, widthFactor: 0.7,
      initialWidth: 6, tropism: [0, 0, 1], tropismStrength: 0.08, planar: false, organSize: 2.6,
    },
    style: { barkColor: '#6b4a2f', tipColor: '#6faf4a', organColor: '#5ba03a', baseWidth: 6 },
    showOrgans: true,
    iterationRange: [3, 7],
  },
  {
    key: 'tree',
    label: 'Woody tree',
    group: 'Woody',
    tagline: 'Monopodial trunk with apical dominance',
    description:
      'A tree holds a dominant vertical leader (trunk) that sheds tapering lateral branches as it climbs. Branch radii thin at each order following da Vinci\'s rule, ending in a leafy canopy.',
    biology:
      'Trees combine apical dominance with secondary (girth) growth. Branch cross-sections roughly conserve area across a fork (r_parent² ≈ Σ r_child²), a scaling law linking form to hydraulic transport.',
    fractalDim: '≈ 2.5',
    spec: { axiom: 'X', rules: { X: 'F[&+X]/[&-X]/>X' }, iterations: 7 },
    turtle: {
      angle: 32, angleJitter: 8, rollAngle: 90, step: 1.6, lengthFactor: 0.82, widthFactor: 0.72,
      initialWidth: 10, tropism: [0, 0, 1], tropismStrength: 0.05, planar: false, organSize: 2.4,
    },
    style: { barkColor: '#6b4423', tipColor: '#4c9a3a', organColor: '#3f9a34', baseWidth: 9 },
    showOrgans: true,
    iterationRange: [4, 8],
  },
];

export const PRESET_GROUPS = ['Bryophytes', 'Ferns', 'Lichens', 'Vascular (herbaceous)', 'Woody'] as const;

export function getPreset(key: string): PlantPreset {
  return PLANT_PRESETS.find((p) => p.key === key) ?? PLANT_PRESETS[0];
}
