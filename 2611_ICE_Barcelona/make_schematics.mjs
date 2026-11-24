// The inline schematics whose lines are computed: each is written into its slide as the <svg> of
// the slide's <figure>, drawn in the house media (pencil, pen, glaze) so it recolours with the theme.
// Ink is what is measured, wash what is simulated or inferred, pencil the construction.
// node 2611_ICE_Barcelona/make_schematics.mjs [--only spiral,chain]
import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
const HERE = path.dirname(fileURLToPath(import.meta.url));

let state = 1;   // the hand is seeded, so every run draws the same lines
const hand = (s) => { state = s; };
const rnd = () => { state = (state + 0x6D2B79F5) | 0; let t = Math.imul(state ^ (state >>> 15), 1 | state);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
const jit = (a) => (rnd() * 2 - 1) * a;
const gauss = () => Math.sqrt(-2 * Math.log(rnd() + 1e-9)) * Math.cos(2 * Math.PI * rnd());
const n1 = (v) => (Math.round(v * 10) / 10).toString();
const f = ([x, y]) => `${n1(x)} ${n1(y)}`;
const line = (pts) => 'M' + pts.map(f).join(' L');
// a ribbon about a centreline: half-width h(i) at each point, closed
function ribbon(pts, h) {
  const nrm = pts.map((p, i) => { const a = pts[Math.max(i - 1, 0)], b = pts[Math.min(i + 1, pts.length - 1)], L = Math.hypot(b[0] - a[0], b[1] - a[1]); return [-(b[1] - a[1]) / L, (b[0] - a[0]) / L]; });
  const side = (s) => pts.map((p, i) => [p[0] + s * h(i / (pts.length - 1)) * nrm[i][0], p[1] + s * h(i / (pts.length - 1)) * nrm[i][1]]);
  return line([...side(1), ...side(-1).reverse()]) + 'Z';
}

// ── spiral ───────────────────────────────────────────────────────────────────────────────────
// Two arms wound inward onto the data. The pipeline is a line: pencil where it sets out, a pen's
// ink once it has been checked, heavier as it nears the data. The simulations are one stroke of
// wash, broad and pale butter where they are cheap, narrowing and deepening to lilac as they are
// made realistic (the track of the fidelity slide, wound up). The data is a small sky in ink.
function spiral() {
  hand(7);
  const C = [330, 330], R0 = 292, R1 = 70, TURNS = 1.75, N = 260;
  const arm = (a0) => Array.from({ length: N + 1 }, (_, i) => { const t = i / N, r = R1 + (R0 - R1) * Math.pow(1 - t, 1.12), a = a0 + 2 * Math.PI * TURNS * t;
    return [C[0] + r * Math.sin(a), C[1] - r * Math.cos(a)]; });
  const pipe = arm(0), sims = arm(Math.PI);
  // the brush lands, spreads, and is drawn out to a point
  const brush = (t) => (1.8 + 19 * Math.pow(1 - t, 0.85)) * Math.min(1, Math.sqrt(t / 0.035) * 0.75 + 0.25) * (1 + 0.07 * Math.sin(23 * t) + 0.05 * Math.sin(61 * t + 1));
  const wash = ribbon(sims, brush);
  // ink takes over from pencil a third of the way in, and bears down as it goes
  const k0 = Math.round(N * 0.22), inked = pipe.slice(k0);
  const ink = ribbon(inked, (t) => 0.6 + 2.2 * Math.pow(t, 0.7));
  // the data: galaxies' shapes as fine strokes of ink, as under the loupe of the UNIONS opener
  let ticks = ''; const placed = [];
  for (let k = 0; placed.length < 22 && k < 2000; k++) {
    const r = 56 * Math.sqrt(rnd()), a = rnd() * 2 * Math.PI, x = r * Math.cos(a), y = r * Math.sin(a);
    if ((Math.abs(y) < 24 && Math.abs(x) < 52) || placed.some(([u, v]) => Math.hypot(u - x, v - y) < 15)) continue;   // the word keeps the middle
    placed.push([x, y]);
    const th = a + Math.PI / 2 + jit(0.8), L = 2.5 + rnd() * 3.5;
    ticks += `M${f([C[0] + x - L * Math.cos(th), C[1] + y - L * Math.sin(th)])} L${f([C[0] + x + L * Math.cos(th), C[1] + y + L * Math.sin(th)])} `;
  }
  return `<svg viewBox="-10 -70 680 790" role="img" aria-label="Two arms spiralling inward together, pipeline and simulations, meeting at the data in the center">
      <defs>
        <radialGradient id="spiral-butter" gradientUnits="userSpaceOnUse" cx="${C[0]}" cy="${C[1]}" r="${R0 + 20}">
          <stop offset="0.38" class="stop-butter" stop-opacity="0"/><stop offset="0.66" class="stop-butter" stop-opacity="0.95"/><stop offset="1" class="stop-butter" stop-opacity="0.8"/>
        </radialGradient>
        <radialGradient id="spiral-lilac" gradientUnits="userSpaceOnUse" cx="${C[0]}" cy="${C[1]}" r="${R0 + 20}">
          <stop offset="0.22" class="stop-lilac" stop-opacity="1"/><stop offset="0.5" class="stop-lilac" stop-opacity="0.7"/><stop offset="0.72" class="stop-lilac" stop-opacity="0"/>
        </radialGradient>
      </defs>
      <!-- simulations: one stroke of wash, butter where they are cheap, lilac as they near the data -->
      <path d="${wash}" class="glaze" fill="url(#spiral-butter)"/>
      <path d="${wash}" class="glaze" fill="url(#spiral-lilac)"/>
      <!-- pipeline: set out in pencil, inked as it is checked -->
      <path d="${line(pipe)}" class="pencil fill-none stroke-ink" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="${ink}" class="pen fill-ink"/>
      <!-- the data: what is measured, in ink -->
      <circle cx="${C[0]}" cy="${C[1]}" r="${R1 - 4}" class="fill-ground"/>
      <circle cx="${C[0]}" cy="${C[1]}" r="${R1 - 4}" class="pen fill-none stroke-ink" stroke-width="3"/>
      <path d="${ticks.trim()}" class="fill-none stroke-ink" stroke-width="1.5" stroke-linecap="round"/>
      <text x="330" y="344" font-size="42" text-anchor="middle">data</text>
      <text x="330" y="-6" font-size="48" text-anchor="middle"><tspan font-weight="600">pipeline</tspan></text>
      <text x="330" y="702" font-size="48" text-anchor="middle"><tspan font-weight="600">simulations</tspan></text>
    </svg>`;
}

// ── chain ────────────────────────────────────────────────────────────────────────────────────
// A lensing analysis as five small drawings, each in the medium of what it is: the image as
// counts in a grid of pixels, a galaxy's shape as an ellipse with its axes, the catalogue as
// shapes inside a footprint with its masks, the data vector as points with their errors (all
// measured, so ink on a pencil construction), and the cosmology as a posterior in wash (inferred).
// Under them the mocks, one band of wash tied to every stage.
function chain() {
  hand(11);
  const X = [156, 508, 860, 1212, 1560], Y = 78, TILT = -28 * Math.PI / 180;
  const pen = (d, w = 2.2, extra = '') => `<path d="${d}" class="pen fill-none stroke-ink" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"${extra}/>`;
  const pencil = (d, w = 2.2) => `<path d="${d}" class="pencil fill-none stroke-ink" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/>`;
  const ellipse = (cx, cy, a, b, th, n = 40) => line(Array.from({ length: n }, (_, i) => { const t = 2 * Math.PI * i / n, x = a * Math.cos(t), y = b * Math.sin(t);
    return [cx + x * Math.cos(th) - y * Math.sin(th), cy + x * Math.sin(th) + y * Math.cos(th)]; })) + 'Z';

  // images: a galaxy and a star as counts on the detector
  const NP = 10, CELL = 13, x0 = X[0] - NP * CELL / 2, y0 = Y - NP * CELL / 2;
  let pixels = '', grid = '';
  for (let j = 0; j < NP; j++) for (let i = 0; i < NP; i++) {
    const u = (i + 0.5 - NP / 2) * CELL + 8, v = (j + 0.5 - NP / 2) * CELL - 6, a = u * Math.cos(TILT) + v * Math.sin(TILT), b = -u * Math.sin(TILT) + v * Math.cos(TILT);
    const gal = Math.exp(-0.5 * ((a / 27) ** 2 + (b / 13) ** 2)), star = 0.85 * Math.exp(-0.5 * (((u - 50) / 8) ** 2 + ((v - 36) / 8) ** 2));
    const val = Math.min(1, gal + star + 0.03 + 0.06 * rnd());
    pixels += `<rect x="${n1(x0 + i * CELL + 0.6)}" y="${n1(y0 + j * CELL + 0.6)}" width="${CELL - 1.2}" height="${CELL - 1.2}" opacity="${(0.82 * val ** 1.25).toFixed(2)}"/>`;
  }
  for (let k = 0; k <= NP; k++) grid += `M${n1(x0 + k * CELL)} ${n1(y0 - 2)} V${n1(y0 + NP * CELL + 2)} M${n1(x0 - 2)} ${n1(y0 + k * CELL)} H${n1(x0 + NP * CELL + 2)} `;
  const images = `<g class="fill-ink">${pixels}</g>${pencil(grid.trim(), 1.3)}`;

  // shapes: the galaxy as an ellipse, in pen, over its two axes
  const ax = (L, th) => `M${f([X[1] - L * Math.cos(th), Y - L * Math.sin(th)])} L${f([X[1] + L * Math.cos(th), Y + L * Math.sin(th)])}`;
  const shapes = pencil(`${ax(78, TILT)} ${ax(44, TILT + Math.PI / 2)}`, 2) + pen(ellipse(X[1], Y, 60, 28, TILT), 2.6);

  // catalog: every galaxy's shape as a stroke, inside the survey's footprint and around its masks
  const U = 16, tiles = [[-4, -2], [-3, -2], [-3, -3], [0, -3], [0, -4], [3, -4], [3, -3], [4, -3], [4, 1], [3, 1], [3, 3], [1, 3], [1, 4], [-3, 4], [-3, 2], [-4, 2]].map(([a, b]) => [a * U * 1.12, b * U]);
  const inside = (x, y) => tiles.reduce((c, [x1, y1], i) => { const [x2, y2] = tiles[(i + 1) % tiles.length]; return (y1 > y) !== (y2 > y) && x < x1 + (x2 - x1) * (y - y1) / (y2 - y1) ? !c : c; }, false);
  const masks = [[-22, -14, 10], [30, 16, 8], [-30, 34, 6]];
  const foot = line(tiles.map(([x, y]) => [X[2] + x, Y + y])) + 'Z';
  let sticks = ''; const placed = [];
  for (let k = 0; placed.length < 44 && k < 6000; k++) {
    const x = jit(74), y = jit(66);
    if (![[0, 0], [7, 0], [-7, 0], [0, 7], [0, -7]].every(([a, b]) => inside(x + a, y + b)) || masks.some(([u, v, r]) => Math.hypot(x - u, y - v) < r + 5) || placed.some(([u, v]) => Math.hypot(u - x, v - y) < 13)) continue;
    placed.push([x, y]);
    const th = TILT + jit(1.1), L = 2.5 + rnd() * 3.5;
    sticks += `M${f([X[2] + x - L * Math.cos(th), Y + y - L * Math.sin(th)])} L${f([X[2] + x + L * Math.cos(th), Y + y + L * Math.sin(th)])} `;
  }
  const catalog = pencil(masks.map(([u, v, r]) => ellipse(X[2] + u, Y + v, r, r, 0, 16)).join(' '), 1.8) + pen(foot, 2.4)
    + `<path d="${sticks.trim()}" class="fill-none stroke-ink" stroke-width="1.6" stroke-linecap="round"/>`;

  // data vectors: bandpowers with their errors, on pencil axes
  const axes = (cx) => pencil(`M${cx - 74} ${Y - 62} V${Y + 58} H${cx + 80}`, 2);
  let bars = '', dots = '';
  for (let i = 0; i < 7; i++) { const x = X[3] - 52 + i * 19.5, y = Y - 38 * Math.exp(-(((i - 1.2) / 3.4) ** 2)) + 22 + jit(3 + i * 0.9), e = 6 + i * 1.7;
    bars += `M${n1(x)} ${n1(y - e)} V${n1(y + e)} `; dots += `<circle cx="${n1(x)}" cy="${n1(y)}" r="4.4"/>`; }
  const vectors = axes(X[3]) + pen(bars.trim(), 2.2) + `<g class="fill-ink">${dots}</g>`;

  // cosmology: a posterior, two contours of one wash
  const cosmology = axes(X[4]) + `<path d="${ellipse(X[4] + 6, Y - 4, 56, 27, -0.6)}" class="glaze fill-lilac" opacity="0.6"/><path d="${ellipse(X[4] + 6, Y - 4, 32, 15, -0.6)}" class="glaze fill-lilac" opacity="0.95"/>`;

  const arrows = X.slice(0, -1).map((x, i) => `M${x + 112} ${Y} H${X[i + 1] - 112}`).map((d) => `<path d="${d}" marker-end="url(#chain-arrow)"/>`).join('');
  const label = (i, a, b) => `<text x="${X[i]}" y="212">${a}</text>\n        <text x="${X[i]}" y="258" font-size="32" font-weight="400" class="fill-muted">${b}</text>`;
  return `<svg viewBox="0 0 1712 720" role="img" aria-label="Images to shapes to catalog to data vectors to cosmology, with a band of mocks under every step, used to validate the pipeline and characterize systematics">
      <defs>
        <marker id="chain-arrow" viewBox="0 0 12 10" refX="11" refY="5" markerWidth="8" markerHeight="7" orient="auto">
          <path d="M0 0.5 Q6 3.5 12 5 Q6 6.5 0 9.5" class="fill-none stroke-ink" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
        </marker>
        <linearGradient id="chain-wash" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" class="stop-butter" stop-opacity="0.75"/><stop offset="1" class="stop-butter" stop-opacity="0.25"/>
        </linearGradient>
      </defs>
      <!-- the pipeline: each stage drawn as what it holds; measured in ink, inferred in wash, laid out in pencil -->
      <g transform="translate(${X[0]} ${Y}) scale(1.2) translate(${-X[0]} ${-Y})">${images}</g>
      <g transform="translate(${X[1]} ${Y}) scale(1.2) translate(${-X[1]} ${-Y})">${shapes}</g>
      <g transform="translate(${X[2]} ${Y}) scale(1.2) translate(${-X[2]} ${-Y})">${catalog}</g>
      <g transform="translate(${X[3]} ${Y}) scale(1.2) translate(${-X[3]} ${-Y})">${vectors}</g>
      <g transform="translate(${X[4]} ${Y}) scale(1.2) translate(${-X[4]} ${-Y})">${cosmology}</g>
      <g class="pencil fill-none stroke-ink" stroke-width="2.2" stroke-linecap="round">${arrows}</g>
      <g font-size="40" font-weight="600" text-anchor="middle">
        ${label(0, 'Images', 'PSF, astrometry')}
        ${label(1, 'Shapes', 'calibration m')}
        ${label(2, 'Catalog', 'masks, n(z)')}
        ${label(3, 'Data vectors', 'nulls, blinding')}
        ${label(4, 'Cosmology', 'likelihood')}
      </g>
      <!-- the mocks: a wash under the whole pipeline, tied to every stage -->
      <g class="fragment">
        <rect x="10" y="376" width="1692" height="124" rx="3" class="glaze" fill="url(#chain-wash)"/>
        <g class="pencil fill-none stroke-ink" stroke-width="2.2" stroke-linecap="round">${X.map((x) => `<path d="M${x} 366 V282" marker-end="url(#chain-arrow)"/>`).join('')}</g>
        <text x="856" y="436" font-size="40" font-weight="600" text-anchor="middle">Mocks with known inputs</text>
        <text x="856" y="482" font-size="32" text-anchor="middle" class="fill-muted">footprint, noise, PSF, redshift distributions, systematics</text>
      </g>
      <g class="fragment" font-size="40" text-anchor="middle">
        <text x="856" y="600">validate the pipeline at each step</text>
        <text x="856" y="660">characterize systematics</text>
      </g>
    </svg>`;
}

// ── unions-3x2pt ─────────────────────────────────────────────────────────────────────────────
// Lenses and sources along redshift. The source bins are broad and overlap, so four washes of rose
// rising from the axis, each a schematic n(z) whose mean falls on the pencil line under its label
// (the shapes follow the working n(z) of the cosmic-shear slide: the first three compact, the last
// with a long tail). The lens bins are cuts, so five blocks of one grey wash with a pen line at
// each edge, standing in front of the sources as the lenses do on the sky.
function unions3x2pt() {
  const x = (z) => 60 + z * 1326.67, BASE = 246, H = 160;
  // peak, width below it, width above it, height; the means come out at 0.29, 0.43, 0.58, 0.92
  const bins = [[0.281, 0.085, 0.1, 0.92], [0.404, 0.07, 0.1, 1], [0.611, 0.11, 0.075, 0.8], [0.82, 0.07, 0.2, 0.56]], means = [0.293, 0.428, 0.583, 0.924];
  const hump = ([zp, sl, sr, a]) => { const pts = []; for (let z = Math.max(0, zp - 3.2 * sl); z <= Math.min(1.245, zp + 3.2 * sr); z += 0.01) pts.push([x(z), BASE - H * a * Math.exp(-0.5 * ((z - zp) / (z < zp ? sl : sr)) ** 2)]);
    return line([[pts[0][0], BASE], ...pts, [pts[pts.length - 1][0], BASE]]) + 'Z'; };
  const tick = [0, 0.2, 0.4, 0.6, 0.8, 1, 1.2];
  return `<svg viewBox="0 30 1712 310" role="img" aria-label="Redshift axis from 0 to 1.2: five LSx lens bins between 0.05 and 0.55, and the four UNIONS source bins as broad overlapping distributions with mean redshifts 0.29, 0.43, 0.58 and 0.92">
      <defs>
        <linearGradient id="unions-3x2pt-tail" gradientUnits="userSpaceOnUse" x1="1480" y1="0" x2="1700" y2="0">
          <stop offset="0" class="stop-rose" stop-opacity="0.62"/><stop offset="1" class="stop-rose" stop-opacity="0"/>
        </linearGradient>
      </defs>
      <!-- the redshift axis, in pencil -->
      <g class="pencil fill-none stroke-ink" stroke-width="2.2" stroke-linecap="round">
        <path d="M60 246 H1652 ${tick.map((z) => `M${n1(x(z))} 246 V259`).join(' ')}"/>
      </g>
      <g font-size="34" text-anchor="middle" class="fill-muted">
        ${tick.map((z) => `<text x="${n1(x(z))}" y="300">${z}</text>`).join('')}
      </g>
      <!-- source bins: four washes of rose, broad and overlapping, each mean on a pencil line -->
      ${bins.map((b, i) => `<path d="${hump(b)}" class="glaze${i < 3 ? ' fill-rose' : ''}"${i < 3 ? ' opacity="0.62"' : ' fill="url(#unions-3x2pt-tail)"'}/>`).join('\n      ')}
      <path d="${means.map((z) => `M${n1(x(z))} 84 V${BASE}`).join(' ')}" class="pencil fill-none stroke-muted" stroke-width="1.8" stroke-linecap="round"/>
      <!-- lens bins: one grey wash over z 0.05–0.55, cut in pen at the bin edges, on paper kept clear of the sources behind -->
      <rect x="${n1(x(0.05))}" y="192" width="${n1(x(0.55) - x(0.05))}" height="46" class="fill-ground"/>
      <rect x="${n1(x(0.05))}" y="192" width="${n1(x(0.55) - x(0.05))}" height="46" rx="2" class="glaze" fill="#3B4150" opacity="0.2"/>
      <path d="${[0.05, 0.15, 0.25, 0.35, 0.45, 0.55].map((z) => `M${n1(x(z))} 190 V240`).join(' ')}" class="pen fill-none stroke-ink" stroke-width="2"/>
      <g font-size="36" font-weight="600" text-anchor="middle">
        ${[0.1, 0.2, 0.3, 0.4, 0.5].map((z, i) => `<text x="${n1(x(z))}" y="228">L${i + 1}</text>`).join('')}
        ${means.map((z, i) => `<text x="${n1(x(z))}" y="72" class="fill-accent">S${i + 1}</text>`).join('')}
      </g>
      <text x="${n1(x(0.583) + 18)}" y="228" font-size="36">LSx lens bins</text>
      <text x="60" y="72" font-size="36" class="fill-accent">UNIONS v2 sources</text>
      <text x="856" y="336" text-anchor="middle" font-size="34" class="fill-muted">redshift</text>
    </svg>`;
}

const SCHEMATICS = { spiral, chain, 'unions-3x2pt': unions3x2pt };
const only = (() => { const i = process.argv.indexOf('--only'); return i > 0 ? process.argv[i + 1].split(',') : null; })();
for (const [name, draw] of Object.entries(SCHEMATICS)) {
  if (only && !only.includes(name)) continue;
  const file = path.join(HERE, 'slides', `${name}.html`), html = fs.readFileSync(file, 'utf8');
  fs.writeFileSync(file, html.replace(/<svg[\s\S]*?<\/svg>/, () => draw()));
}
