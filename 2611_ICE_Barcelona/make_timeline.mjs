// Writes the inline SVG of slides/timeline.html from timelines.json: for each survey, a wash over the
// observing that went into its cosmology releases, and for each release an arc from its last night
// of data to its headline cosmology paper, a dot when that paper reached arXiv.
// Rerun after changing the data: node 2611_ICE_Barcelona/make_timeline.mjs
import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
const HERE = path.dirname(fileURLToPath(import.meta.url));
const SLIDE = path.join(HERE, 'slides', 'timeline.html');
const data = JSON.parse(fs.readFileSync(path.join(HERE, 'timelines.json'), 'utf8'));

// a date as a decimal year: a day as given, a month at its middle, a bare year at its start
// (or its end, for the last night of data)
const yr = (d, end) => { const [y, m, dd] = d.split('-').map(Number); return m ? y + (m - 1) / 12 + (dd ? dd - 1 : 14) / 365 : y + (end ? 1 : 0); };
const f = (v) => (Math.round(v * 10) / 10).toString();

const ORDER = ['CFHTLenS', 'KiDS', 'DES', 'HSC SSP', 'UNIONS', 'Planck', 'ACT', 'SPT'];
const NAME = { 'HSC SSP': 'HSC' };
// each release's label under its paper; CFHTLenS's two papers, a few months apart, go unlabelled
const LABEL = {
  'KiDS-450': '450', 'KiDS+VIKING-450': 'KV450', 'KiDS-1000': '1000', 'KiDS-Legacy': 'Legacy', 'UNIONS-3500': '3500',
  'DR6 lensing': 'DR6 κ', 'DR6 power spectra': 'DR6',
  'SPT-SZ 2008-09 (Keisler+11)': 'SZ', 'SPT-SZ full (Story+12)': 'SZ', 'SPTpol 500d (Henning+18)': 'pol',
  'SPT-3G 2018 (Dutcher+21, Balkenhol+23)': '3G', 'SPT-3G D1 2019-20 (Camphuis+25)': '3G D1',
};
const label = (r) => r.name in LABEL ? LABEL[r.name] : /^(2D|tomography)/.test(r.name) ? '' : r.name.replace(/\s*\(.*\)/, '');

// the frame is the figure's box at 1:1: the body's width and the height it gives the figure
const W = 1712, H = 760, T0 = 2003, T1 = 2027, X0 = 236, X1 = 1680;
const x = (t) => X0 + (X1 - X0) * (t - T0) / (T1 - T0);
const Y0 = 40, P = 86, AXIS = H - 12;
// arcs stay low enough to pass under the labels of the row above
const lift = (gap) => Math.min(26, 5 + 3 * gap);
const arc = (a, b, y, h) => `M${f(a)} ${y - 9} C${f(a)} ${f(y - 9 - 1.3 * h)} ${f(b)} ${f(y - 9 - 1.3 * h)} ${f(b)} ${y - 8}`;
const band = (a, b, y, wash) => `<rect x="${f(a)}" y="${y - 50}" width="${f(b - a)}" height="100" class="fill-none"/><rect x="${f(a)}" y="${y - 9}" width="${f(b - a)}" height="18" rx="9" class="${wash}"/>`;

// the legend, in the empty years before most galaxy surveys began; the caveat, in the empty top right
const lx = +f(x(2004.4)), ly = Y0 + 2 * P - 14, row = 46, tx = lx + 92, LH = 3 * row + 40;
let grid = '', washes = '', ticks = '', arcs = '', dots = '', names = '', labels = '';
for (let t = 2004; t <= 2026; t += 2) {
  const gx = f(x(t)), top = t < 2014 ? 0 : Y0 + 24;
  grid += t < 2011 ? `<path d="M${gx} ${top} V${ly - 40} M${gx} ${ly + LH + 20} V${AXIS - 40}"/>` : `<path d="M${gx} ${top} V${AXIS - 40}"/>`;
  labels += `<text x="${gx}" y="${AXIS}" class="fill-muted">${t}</text>`;
}
ORDER.forEach((name, i) => {
  const s = data.surveys.find(v => v.name === name), y = Y0 + i * P, R = s.releases;
  const a = Math.min(...R.map(r => yr(r.data_start.date))), b = Math.max(...R.map(r => yr(r.data_end.date, true)));
  washes += band(x(a), x(b), y, s.kind === 'cmb' ? 'fill-butter' : 'fill-sage');
  names += `<text x="0" y="${y + 14}"><tspan font-weight="600">${NAME[name] || name}</tspan></text>`;
  for (const r of R) {
    const e = yr(r.data_end.date, true), p = yr(r.paper_date.date);
    ticks += `M${f(x(e))} ${y - 9} v18 `;
    arcs += `<path d="${arc(x(e), x(p), y, lift(p - e))}"/>`;
    dots += `<circle cx="${f(x(p))}" cy="${y}" r="7"/>`;
    if (label(r)) labels += `<text x="${f(x(p))}" y="${y + 36}">${label(r)}</text>`;
  }
  console.log(name.padEnd(9), R.map(r => `${label(r) || r.name}: ${(yr(r.paper_date.date) - yr(r.data_end.date, true)).toFixed(1)} yr`).join(', '));
});

const legend = {
  washes: band(lx, lx + 70, ly, 'fill-sage') + band(lx, lx + 70, ly + row, 'fill-butter'),
  ink: `<path d="M${lx + 6} ${ly + 2 * row + 9} v18"/>`,
  arcs: `<path d="${arc(lx + 6, lx + 70, ly + 2 * row + 18, 20)}"/>`,
  dots: `<circle cx="${lx + 70}" cy="${ly + 2 * row + 18}" r="7"/>`,
  text: `<text x="${tx}" y="${ly + 11}">galaxy-survey observing</text>
        <text x="${tx}" y="${ly + row + 11}">CMB observing</text>
        <text x="${tx}" y="${ly + 2 * row + 29}">last night of data to</text>
        <text x="${tx}" y="${ly + 3 * row + 29}">the paper on arXiv</text>
        <text x="${X1}" y="${Y0 + 4}" text-anchor="end" font-style="italic" class="fill-muted">representative releases; dates to within a year</text>`,
};

const svg = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="For eight surveys, the observing behind their cosmology releases and an arc from each release's last night of data to its cosmology paper on arXiv, 2003 to 2026">
      <g class="stroke-muted" stroke-width="1.2" stroke-dasharray="2 10" opacity="0.6">${grid}</g>
      <g class="wash-fine" opacity="0.85">${washes}${legend.washes}</g>
      <g class="stroke-ink" stroke-width="2"><path d="${ticks}"/>${legend.ink}</g>
      <g class="fill-none stroke-ink pen" stroke-width="2.2">${arcs}${legend.arcs}</g>
      <g class="fill-ink">${dots}${legend.dots}</g>
      <g font-size="40">${names}</g>
      <g font-size="32" text-anchor="middle">${labels}</g>
      <g font-size="32">${legend.text}</g>
    </svg>`;
const html = fs.readFileSync(SLIDE, 'utf8');
fs.writeFileSync(SLIDE, html.replace(/<svg[\s\S]*?<\/svg>/, svg));
