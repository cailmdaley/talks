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
  const X = [156, 508, 860, 1250, 1580], Y = 72, YB = 574, YM = 373, SC = 1.05, TILT = -28 * Math.PI / 180;
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
  const axes = (cx) => pencil(`M${cx - 74} ${YM - 62} V${YM + 58} H${cx + 80}`, 2);
  let bars = '', dots = '';
  for (let i = 0; i < 7; i++) { const x = X[3] - 52 + i * 19.5, y = YM - 38 * Math.exp(-(((i - 1.2) / 3.4) ** 2)) + 22 + jit(3 + i * 0.9), e = 6 + i * 1.7;
    bars += `M${n1(x)} ${n1(y - e)} V${n1(y + e)} `; dots += `<circle cx="${n1(x)}" cy="${n1(y)}" r="4.4"/>`; }
  const vectors = axes(X[3]) + pen(bars.trim(), 2.2) + `<g class="fill-ink">${dots}</g>`;

  // cosmology: a posterior, two contours of one wash
  const cosmology = axes(X[4]) + `<path d="${ellipse(X[4] + 6, YM - 4, 56, 27, -0.6)}" class="glaze fill-lilac" opacity="0.6"/><path d="${ellipse(X[4] + 6, YM - 4, 32, 15, -0.6)}" class="glaze fill-lilac" opacity="0.95"/>`;

  // timestreams: what the detectors record as the telescope scans, one trace each, a glitch in one
  let traces = '';
  for (let d = 0; d < 4; d++) { let v = 0; const y = YB - 45 + d * 30;
    traces += line(Array.from({ length: 44 }, (_, i) => { v = 0.72 * v + gauss() * 3.6; return [X[0] - 72 + i * 144 / 43, y + v + 5 * Math.sin(i / 7 + d) - (d === 1 && i === 29 ? 20 : 0)]; })) + ' '; }
  const streams = pen(traces.trim(), 1.7);

  // maps: the temperature of a patch of sky, hot spots contoured in pen and cold ones in pencil
  const H = 62, NG = 36, K = 2 * Math.PI / 54;
  const waves = Array.from({ length: 12 }, () => { const th = rnd() * Math.PI, k = K * (0.75 + 0.5 * rnd()); return [k * Math.cos(th), k * Math.sin(th), rnd() * 2 * Math.PI]; });
  const T = (x, y) => waves.reduce((t, [kx, ky, ph]) => t + Math.cos(kx * x + ky * y + ph), 0) / Math.sqrt(waves.length / 2);
  const contour = (level) => { let d = ''; const g = (i) => -H + 2 * H * i / NG;
    for (let j = 0; j < NG; j++) for (let i = 0; i < NG; i++) {
      const c = [[g(i), g(j)], [g(i + 1), g(j)], [g(i + 1), g(j + 1)], [g(i), g(j + 1)]], v = c.map(([x, y]) => T(x, y) - level), cut = [];
      for (let e = 0; e < 4; e++) { const a = v[e], b = v[(e + 1) % 4]; if ((a > 0) !== (b > 0)) { const t = a / (a - b), [p, q] = [c[e], c[(e + 1) % 4]]; cut.push([X[1] + p[0] + t * (q[0] - p[0]), YB + p[1] + t * (q[1] - p[1])]); } }
      for (let e = 0; e + 1 < cut.length; e += 2) d += `M${f(cut[e])} L${f(cut[e + 1])} `;
    } return d.trim(); };
  const frame = (cx) => pencil(`M${cx - H} ${YB - H} H${cx + H} V${YB + H} H${cx - H}Z`, 2);
  const maps = frame(X[1]) + pencil(contour(-0.75), 1.5) + pen(contour(0.75), 1.9);

  // the lensing map: the mass in front of the CMB, inferred from its maps, so laid in wash
  const kappa = [[-24, -20, 26, 19, 0.5, 0.85], [22, 14, 30, 20, -0.4, 0.7], [-30, 30, 15, 12, 0.2, 0.55], [30, -34, 14, 11, 0.9, 0.5]]
    .map(([x, y, a, b, th, o]) => `<path d="${ellipse(X[2] + x, YB + y, a, b, th, 24)}" class="wash-fine fill-sky" opacity="${o}"/>`).join('') + frame(X[2]);

  const at = (i, y, g) => `<g transform="translate(${X[i]} ${y}) scale(${SC}) translate(${-X[i]} ${-y})">${g}</g>`;
  const arrow = (d) => `<path d="${d}" marker-end="url(#chain-arrow)"/>`;
  const row = (y) => [0, 1].map((i) => arrow(`M${X[i] + 106} ${y} H${X[i + 1] - 106}`)).join('');
  // each probe's last stage bends to the data vectors, which both share
  const join = (y, s) => arrow(`M${X[2] + 106} ${y} C${X[2] + 205} ${y} ${X[3] - 195} ${YM + s * 34} ${X[3] - 106} ${YM + s * 34}`);
  const label = (i, y, a, b) => `<text x="${X[i]}" y="${y}">${a}</text>\n        <text x="${X[i]}" y="${y + 44}" font-size="32" font-weight="400" class="fill-muted">${b}</text>`;
  return `<svg viewBox="0 0 1712 760" role="img" aria-label="Two rows meet at shared data vectors and cosmology: galaxy images to shapes to catalog above, CMB timestreams to maps to lensing map below, and a band of mocks between them tied to every stage, used to validate the pipeline and characterize systematics">
      <defs>
        <marker id="chain-arrow" viewBox="0 0 12 10" refX="11" refY="5" markerWidth="8" markerHeight="7" orient="auto">
          <path d="M0 0.5 Q6 3.5 12 5 Q6 6.5 0 9.5" class="fill-none stroke-ink" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
        </marker>
        <linearGradient id="chain-wash" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" class="stop-butter" stop-opacity="0.75"/><stop offset="1" class="stop-butter" stop-opacity="0.25"/>
        </linearGradient>
      </defs>
      <!-- two probes, one measurement: each stage drawn as what it holds; measured in ink, inferred in wash, laid out in pencil -->
      ${at(0, Y, images)}
      ${at(1, Y, shapes)}
      ${at(2, Y, catalog)}
      ${at(0, YB, streams)}
      ${at(1, YB, maps)}
      ${at(2, YB, kappa)}
      ${at(3, YM, vectors)}
      ${at(4, YM, cosmology)}
      <g class="pencil fill-none stroke-ink" stroke-width="2.2" stroke-linecap="round">${row(Y)}${row(YB)}${join(Y, -1)}${join(YB, 1)}${arrow(`M${X[3] + 112} ${YM} H${X[4] - 112}`)}</g>
      <g font-size="40" font-weight="600" text-anchor="middle">
        ${label(0, Y + 118, 'Images', 'PSF, astrometry')}
        ${label(1, Y + 118, 'Shapes', 'calibration m')}
        ${label(2, Y + 118, 'Catalog', 'masks, n(z)')}
        ${label(0, YB + 118, 'Timestreams', 'noise, filtering')}
        ${label(1, YB + 118, 'Maps', 'beam, calibration')}
        ${label(2, YB + 118, 'Lensing map', 'foregrounds, normalization')}
        ${label(3, YM + 118, 'Data vectors', 'nulls, blinding')}
        ${label(4, YM + 118, 'Cosmology', 'likelihood')}
      </g>
      <!-- the mocks: a wash between the two probes, tied to every stage and run to the same data vectors -->
      <g class="fragment">
        <rect x="10" y="${YM - 55}" width="1020" height="110" rx="3" class="glaze" fill="url(#chain-wash)"/>
        <g class="pencil fill-none stroke-ink" stroke-width="2.2" stroke-linecap="round">${X.slice(0, 3).map((x) => arrow(`M${x} ${YM - 65} V${Y + 178}`) + arrow(`M${x} ${YM + 65} V${YB - 78}`)).join('')}${arrow(`M1042 ${YM} H${X[3] - 106}`)}</g>
        <text x="520" y="${YM - 6}" font-size="40" font-weight="600" text-anchor="middle">Mocks with known inputs</text>
        <text x="520" y="${YM + 36}" font-size="32" text-anchor="middle" class="fill-muted">sky signals, footprint, noise, PSF, redshift distributions, systematics</text>
      </g>
      <g class="fragment" font-size="40" text-anchor="middle">
        <text x="1415" y="${YB + 86}">validate the pipeline at each step</text>
        <text x="1415" y="${YB + 146}">characterize systematics</text>
      </g>
    </svg>`;
}

// ── unions-3x2pt ─────────────────────────────────────────────────────────────────────────────
// The lens bins in front of the sources they lens. The six SPHEREx bins are the LSx curves of Calum
// Murray's figure (images/lsx_nz_desy6.svg, a matplotlib SVG: axes from z = 0 at 38.55 pt to 1.4 at
// 460.925 pt, baseline at 122.796 pt), narrow washes of rose under a pen line. Behind them rises the
// source n(z) of the first UNIONS release, a broad wash of sky under pencil, deepest under the ridge
// and thinning to the axis, with the jagged ridge of its histogram kept. Every curve is scaled to a
// peak of one, as Calum drew his.
//
// UNIONS_NZ is the published n(z) of ShapePipe v1.4.6.3 (nz_SP_v1.4.6.3_B.txt, sha256 e09a917b…,
// the SOM-weighted histogram of Z_B in blind_nz_shapepipe_v1.4.6.3.fits): its value in each bin of
// width 0.025 from z = 0 to 1.6, over its peak (1.405 at z = 0.4625).
const UNIONS_NZ = [0.006, 0.056, 0.147, 0.209, 0.301, 0.462, 0.497, 0.629, 0.817, 0.876, 0.856, 0.972, 0.765, 0.848, 0.977, 0.909,
  0.957, 0.973, 1.000, 0.921, 0.956, 0.988, 0.949, 0.846, 0.855, 0.763, 0.660, 0.638, 0.560, 0.561, 0.512, 0.479,
  0.471, 0.448, 0.398, 0.411, 0.365, 0.303, 0.315, 0.336, 0.279, 0.256, 0.194, 0.204, 0.206, 0.170, 0.194, 0.164,
  0.164, 0.168, 0.146, 0.120, 0.118, 0.090, 0.064, 0.097, 0.051, 0.057, 0.085, 0.035, 0.042, 0.067, 0.035, 0.047];
function unions3x2pt() {
  const src = fs.readFileSync(path.join(HERE, 'images', 'lsx_nz_desy6.svg'), 'utf8');
  const lsx = [...src.matchAll(/<g id="line2d_\d+">\s*<path d="([^"]+)"[^>]*style="([^"]+)"/g)]
    .filter(([, , style]) => /#b9573a/.test(style))
    .map(([, d]) => ({ pts: [...d.matchAll(/[ML] ([\d.]+) ([\d.]+)/g)].map(([, px, py]) => [(px - 38.55) / (460.925 - 38.55) * 1.4, 122.796 - py]) }))
    .filter((c) => c.pts.length > 20);
  const ZMAX = 1.6, x = (z) => 60 + z * 1592 / ZMAX, BASE = 300, H = 204;
  // each lens bin is kept from where it leaves the axis to where it returns, so the lines do not pile up along it
  for (const c of lsx) { const top = Math.max(...c.pts.map((p) => p[1])), on = c.pts.map((p) => p[1] > 0.006 * top);
    const i0 = Math.max(0, on.indexOf(true) - 1), i1 = Math.min(c.pts.length - 1, on.lastIndexOf(true) + 1);
    c.xy = c.pts.slice(i0, i1 + 1).map(([z, v]) => [x(z), BASE - H * v / top]); }
  const sources = [[x(0), BASE], ...UNIONS_NZ.map((v, i) => [x(0.025 * (i + 0.5)), BASE - H * v])];
  const area = (xy) => line([[xy[0][0], BASE], ...xy, [xy[xy.length - 1][0], BASE]]) + 'Z';
  const tick = [0, 0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4, 1.6];
  return `<svg viewBox="0 24 1712 386" role="img" aria-label="Redshift distributions between redshift 0 and 1.6, each scaled to a peak of one: six narrow bins of the SPHEREx all-sky lens sample LSx v0.9 between redshift 0 and 0.55, in front of the source galaxies of the first UNIONS release, whose distribution rises to a broad peak near 0.5 and falls away to 1.6">
      <!-- the axes, in pencil -->
      <g class="pencil fill-none stroke-ink" stroke-width="2.2" stroke-linecap="round">
        <path d="M60 ${BASE} H1652 ${tick.map((z) => `M${n1(x(z))} ${BASE} V${BASE + 13}`).join(' ')}"/>
      </g>
      <g font-size="35" text-anchor="middle" class="fill-muted">
        ${tick.map((z) => `<text x="${n1(x(z))}" y="${BASE + 54}">${z}</text>`).join('')}
        <text x="856" y="${BASE + 94}">redshift</text>
        <text x="1652" y="${BASE + 94}" text-anchor="end" font-style="italic">lens bins preliminary, from Calum Murray</text>
      </g>
      <defs>
        <linearGradient id="nz-sky" gradientUnits="userSpaceOnUse" x1="0" y1="${BASE - H}" x2="0" y2="${BASE}">
          <stop offset="0" class="stop-sky" stop-opacity="0.95"/><stop offset="0.55" class="stop-sky" stop-opacity="0.5"/><stop offset="1" class="stop-sky" stop-opacity="0.14"/>
        </linearGradient>
      </defs>
      <!-- the UNIONS sources: one broad wash of sky under pencil, behind, the pigment gathered under the ridge and thinning to the axis -->
      <path d="${area(sources)}" class="glaze" fill="url(#nz-sky)"/>
      <g class="pencil fill-none stroke-ink" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round">
        <path d="${line(sources)}"/>
      </g>
      <!-- LSx lens bins: narrow washes of rose under a pen line, in front -->
      ${lsx.map((c) => `<path d="${area(c.xy)}" class="glaze fill-rose" opacity="0.62"/>`).join('\n      ')}
      <g class="pen fill-none stroke-accent" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round">
        ${lsx.map((c) => `<path d="${line(c.xy)}"/>`).join('\n        ')}
      </g>
      <text x="${n1(x(0.82))}" y="74" font-size="36" font-weight="600" class="fill-accent">SPHEREx all-sky lenses (v0.9), 6 bins</text>
      <text x="${n1(x(0.82))}" y="124" font-size="36" font-weight="600">UNIONS sources, first release</text>
    </svg>`;
}

// ── unions-next ──────────────────────────────────────────────────────────────────────────────
// The shear calibration of the slide's three bullets as measurements on one axis of m: a pencil
// line at zero, each estimate an ink point with its error bar in pen. The first release sits far
// to the left; the two v2 estimates straddle zero.
function shearcal() {
  const x = (m) => 96 + (m + 7) / 9.4 * 720, rows = [['first release', -5.7, 0.47, 150], ['v2 · ShapePipe', -0.6, 0.4, 262], ['v2 · AnaCal', 0.3, 0.8, 374]];
  const tick = [-6, -4, -2, 0, 2];
  return `<svg viewBox="0 40 860 520" role="img" aria-label="Multiplicative shear bias m in percent on one axis: the first release at minus 5.7, and the two v2 estimates, ShapePipe at minus 0.6 plus or minus 0.4 and AnaCal at plus 0.3 plus or minus 0.8, both consistent with zero">
      <!-- zero, and the axis, in pencil -->
      <g class="pencil fill-none stroke-ink" stroke-linecap="round">
        <path d="M${n1(x(-7))} 452 H${n1(x(2.4))} ${tick.map((m) => `M${n1(x(m))} 452 V465`).join(' ')}" stroke-width="2.2"/>
        <path d="M${n1(x(0))} 96 V452" stroke-width="1.8" stroke-dasharray="3 9"/>
      </g>
      <g font-size="35" text-anchor="middle" class="fill-muted">
        ${tick.map((m) => `<text x="${n1(x(m))}" y="506">${m > 0 ? '+' : m < 0 ? '−' : ''}${Math.abs(m)}</text>`).join('')}
        <text x="${n1(x(-2.3))}" y="550">shear bias <tspan font-style="italic">m</tspan>, percent</text>
      </g>
      <!-- the three estimates: error bars in pen, points in ink -->
      <g class="pen fill-none stroke-ink" stroke-width="2.6" stroke-linecap="round">
        ${rows.map(([, m, e, y]) => `<path d="M${n1(x(m - e))} ${y} H${n1(x(m + e))} M${n1(x(m - e))} ${y - 11} V${y + 11} M${n1(x(m + e))} ${y - 11} V${y + 11}"/>`).join('\n        ')}
      </g>
      ${rows.map(([, m, , y]) => `<circle cx="${n1(x(m))}" cy="${y}" r="9" class="fill-ink"/>`).join('')}
      <g font-size="36">
        ${rows.map(([name, m, e, y], i) => i ? `<text x="${n1(x(m - e) - 26)}" y="${y + 12}" text-anchor="end">${name}</text>` : `<text x="${n1(x(m + e) + 26)}" y="${y + 12}">${name}</text>`).join('\n        ')}
      </g>
    </svg>`;
}

const SCHEMATICS = { spiral, chain, 'unions-3x2pt': unions3x2pt, 'unions-next': shearcal };
const only = (() => { const i = process.argv.indexOf('--only'); return i > 0 ? process.argv[i + 1].split(',') : null; })();
for (const [name, draw] of Object.entries(SCHEMATICS)) {
  if (only && !only.includes(name)) continue;
  const file = path.join(HERE, 'slides', `${name}.html`), html = fs.readFileSync(file, 'utf8');
  fs.writeFileSync(file, html.replace(/<svg[\s\S]*?<\/svg>/, () => draw()));
}
