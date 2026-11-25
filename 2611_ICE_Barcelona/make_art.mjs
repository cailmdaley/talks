// The deck's drawings, a pencil underdrawing with watercolour laid in. The title: the three
// instruments look up into a light cone of redshift sheets that ends at the CMB; the first two
// openers are the same scene cut down to each part's instruments, and the third is Lightcone's
// mark with that sky in its past cone; the other slides' drawings take their
// motifs from it (the cone, a sheet of sky, the mock globe). ART at the bottom maps each slide to its
// drawing. A drawing is a stack of layers drawn in the 1920×1080 frame, so that its washes and
// instruments can move a little; each is saved as the part of the frame it covers, with its place.
// node 2611_ICE_Barcelona/make_art.mjs [--only title,unions] [--out dir]
//   → images/ice_art/<drawing>-<layer>.png, and the <figure class="art"> of slides/<drawing>.html
import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
import puppeteer from 'puppeteer';
import sharp from 'sharp';
const HERE = path.dirname(fileURLToPath(import.meta.url));
const S = { ground: '#F6F0E4', graphite: '#39342E', payne: '#3B4150', rose: '#E3A9A3', sage: '#A9C4A6', sky: '#9FBEDB', butter: '#EBD38A', lilac: '#C3B3DC' };

// ── the pencil ───────────────────────────────────────────────────────────────────────────────
// Graphite: a fine line with a steady hand's drift, its pressure rising and falling along the
// stroke, broken a little by the tooth of the paper. Widths are screen pixels whatever the scale.
const PENCIL = `<filter id="pencil" x="-20%" y="-20%" width="140%" height="140%" color-interpolation-filters="sRGB">
  <feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="2" seed="9" result="w"/>
  <feDisplacementMap in="SourceGraphic" in2="w" scale="2.2" xChannelSelector="R" yChannelSelector="G" result="d"/>
  <feTurbulence type="fractalNoise" baseFrequency="0.011" numOctaves="3" seed="17" result="p"/>
  <feColorMatrix in="p" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1.7 -0.08" result="pa"/>
  <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="1" seed="3" result="g"/>
  <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2.4 2.05" result="ga"/>
  <feComposite in="d" in2="pa" operator="in" result="dp"/>
  <feComposite in="dp" in2="ga" operator="in"/></filter>`;

let state = 1;   // the hand is seeded, so every build draws the same lines
const hand = (s) => { state = s; };
const rnd = () => { state = (state + 0x6D2B79F5) | 0; let t = Math.imul(state ^ (state >>> 15), 1 | state);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
const jit = (a) => (rnd() * 2 - 1) * a;
const f = ([x, y]) => `${x.toFixed(1)} ${y.toFixed(1)}`;
// weights: a contour, a detail, a construction line
const W = { line: { w: 2.3, o: 0.96 }, fine: { w: 1.65, o: 0.82 }, ghost: { w: 1.25, o: 0.42 }, sight: { w: 1.45, o: 0.6 } };
const stroke = (d, { w, o }) => `<path d="${d}" stroke-width="${w}" opacity="${(o * (0.85 + rnd() * 0.15)).toFixed(2)}" vector-effect="non-scaling-stroke"/>`;
const pencil = (s) => `<g fill="none" stroke="${S.graphite}" stroke-linecap="round" stroke-linejoin="round" filter="url(#pencil)">${s}</g>`;

// a straight line drawn freehand: a faint bow, and it may run on a little past its ends
function ln(x1, y1, x2, y2, wt = W.line, over = 4) {
  const L = Math.hypot(x2 - x1, y2 - y1), ux = (x2 - x1) / L, uy = (y2 - y1) / L;
  const a = rnd() < 0.5 ? rnd() * over : 0, b = rnd() < 0.5 ? rnd() * over : 0;
  const s = [x1 - ux * a, y1 - uy * a], e = [x2 + ux * b, y2 + uy * b], bow = jit(Math.min(L * 0.01, 2.5));
  return stroke(`M${f(s)} Q${f([(s[0] + e[0]) / 2 - uy * bow, (s[1] + e[1]) / 2 + ux * bow])} ${f(e)}`, wt);
}
const poly = (pts, wt, over, closed = true) => (closed ? [...pts, pts[0]] : pts).slice(1).map((p, i, a) => { const q = i ? a[i - 1] : pts[0]; return ln(q[0], q[1], p[0], p[1], wt, over); }).join('');
const box = (x, y, w, h, wt, over) => poly([[x, y], [x + w, y], [x + w, y + h], [x, y + h]], wt, over);
// a smooth curve through points (Catmull-Rom as cubic Béziers)
function through(p, tension = 1) {
  let d = `M${f(p[0])}`;
  for (let i = 0; i < p.length - 1; i++) {
    const p0 = p[Math.max(i - 1, 0)], p1 = p[i], p2 = p[i + 1], p3 = p[Math.min(i + 2, p.length - 1)], k = tension / 6;
    d += ` C${f([p1[0] + (p2[0] - p0[0]) * k, p1[1] + (p2[1] - p0[1]) * k])} ${f([p2[0] - (p3[0] - p1[0]) * k, p2[1] - (p3[1] - p1[1]) * k])} ${f(p2)}`;
  }
  return d;
}
// a path eased: each inner point drawn halfway toward its neighbours, so kinks become bends
const ease = (p, n = 1) => n ? ease(p.map((q, i) => i && i < p.length - 1 ? [(p[i - 1][0] + 2 * q[0] + p[i + 1][0]) / 4, (p[i - 1][1] + 2 * q[1] + p[i + 1][1]) / 4] : q), n - 1) : p;
// an ellipse traced in one movement: it starts anywhere (or at the angle `from`), drifts a little outward and
// runs past where it began (or, with a negative run, stops short of it)
function oval(cx, cy, rx, ry, deg = 0, wt = W.line, run = 0.1, from = null) {
  const t0 = from ?? rnd() * 2 * Math.PI, a = deg * Math.PI / 180, n = 48, drift = 0.012 + rnd() * 0.012, pts = [];
  for (let i = 0; i <= n; i++) {
    const s = i / n, t = t0 + s * 2 * Math.PI * (1 + run), g = 1 + drift * (s - 0.5) + 0.004 * Math.sin(3 * t + t0);
    const x = rx * g * Math.cos(t), y = ry * g * Math.sin(t);
    pts.push([cx + x * Math.cos(a) - y * Math.sin(a), cy + x * Math.sin(a) + y * Math.cos(a)]);
  }
  return stroke(through(pts), wt);
}

// ── the watercolour ─────────────────────────────────────────────────────────────────────────
// a glaze: a wash laid to its shape, pigment gathering in a thin line at the edge
const GLAZE = `<filter id="glaze" x="-8%" y="-8%" width="116%" height="116%" color-interpolation-filters="sRGB">
  <feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="3" seed="11" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="6" xChannelSelector="R" yChannelSelector="G" result="d"/>
  <feGaussianBlur in="d" stdDeviation="0.7" result="soft"/>
  <feMorphology in="soft" operator="erode" radius="1.4" result="er"/><feGaussianBlur in="er" stdDeviation="1.3" result="erb"/>
  <feComposite in="soft" in2="erb" operator="out" result="edge"/>
  <feTurbulence type="fractalNoise" baseFrequency="0.7" numOctaves="2" seed="3" result="g"/>
  <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -0.45 1.12" result="ga"/>
  <feComposite in="soft" in2="ga" operator="in" result="grain"/>
  <feMerge><feMergeNode in="grain"/><feMergeNode in="edge"/></feMerge></filter>
  <linearGradient id="g-mount" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${S.rose}" stop-opacity="0.85"/><stop offset="0.45" stop-color="${S.butter}" stop-opacity="0.6"/><stop offset="1" stop-color="${S.butter}" stop-opacity="0"/></linearGradient>
  <linearGradient id="g-shade" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${S.lilac}" stop-opacity="0.15"/><stop offset="1" stop-color="${S.lilac}" stop-opacity="0.75"/></linearGradient>
  <linearGradient id="g-ice" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${S.sky}" stop-opacity="0.75"/><stop offset="1" stop-color="${S.sky}" stop-opacity="0"/></linearGradient>
  <linearGradient id="g-far" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${S.sky}" stop-opacity="0.5"/><stop offset="1" stop-color="${S.lilac}" stop-opacity="0"/></linearGradient>
  <linearGradient id="g-foil" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${S.butter}" stop-opacity="0.9"/><stop offset="1" stop-color="${S.butter}" stop-opacity="0.45"/></linearGradient>`;
const glaze = (fill, d, o = 1) => `<path d="${d}" fill="${fill}" opacity="${o}" filter="url(#glaze)"/>`;
// a wash laid freely, a little off the drawing
const loose = (fill, d, o = 1, dx = 1.5, dy = 1) => `<path d="${d}" transform="translate(${dx} ${dy})" fill="${fill}" opacity="${o}" filter="url(#glaze)"/>`;
const paper = (d) => `<path d="${d}" fill="${S.ground}"/>`;   // the white of the paper, kept clear of what lies behind
const dark = (d) => glaze(S.payne, d, 0.78);                     // an opening, in a dark wash
const ell = (cx, cy, rx, ry) => `M${cx - rx} ${cy} a${rx} ${ry} 0 1 0 ${2 * rx} 0 a${rx} ${ry} 0 1 0 ${-2 * rx} 0Z`;

// ── the instruments ─────────────────────────────────────────────────────────────────────────
// a dome on a drum, lit from the upper left, its slit open toward the sky on the left
function dome(x, y, r) {
  const t = y - r * 0.7, slit = `M${x - r * 0.1} ${t - r} Q${x - r * 0.72} ${t - r * 0.86} ${x - r * 0.93} ${t - r * 0.3} L${x - r * 0.62} ${t - r * 0.2} Q${x - r * 0.5} ${t - r * 0.7} ${x + r * 0.12} ${t - r * 0.98}Z`;
  return paper(`M${x - r} ${y} V${t} a${r} ${r} 0 0 1 ${2 * r} 0 V${y}Z`)
    + loose('url(#g-shade)', `M${x + r * 0.15} ${t - r * 0.99} A${r} ${r} 0 0 1 ${x + r} ${t} V${y} H${x + r * 0.15}Z`, 1, 1.2, 0.8)
    + dark(slit)
    + pencil(ln(x - r, y + 2, x - r, t) + ln(x + r, y + 2, x + r, t) + stroke(`M${x - r} ${t + 1} A${r} ${r} 0 0 1 ${x + r} ${t}`, W.line)
      + ln(x - r, t, x + r, t, W.fine, 5) + stroke(slit, W.fine));
}
// a cylindrical enclosure (Subaru)
function drum(x, y, w, h) {
  const door = `M${x - w * 0.3} ${y - h + w * 0.05} v${h * 0.5} h${w * 0.2} v${-h * 0.48}Z`;
  return paper(`M${x - w / 2} ${y} v${-h} q${w / 2} ${-w * 0.22} ${w} 0 v${h}Z`)
    + loose('url(#g-shade)', `M${x + w * 0.1} ${y - h - w * 0.1} q${w * 0.25} ${-w * 0.02} ${w * 0.4} ${w * 0.1} v${h} h${-w * 0.4}Z`, 1, 1.2, 0.8)
    + dark(door)
    + pencil(ln(x - w / 2, y + 2, x - w / 2, y - h) + ln(x + w / 2, y + 2, x + w / 2, y - h)
      + stroke(`M${x - w / 2} ${y - h} q${w / 2} ${-w * 0.22} ${w} 0`, W.line) + stroke(`M${x - w / 2} ${y - h} q${w / 2} ${w * 0.16} ${w} 0`, W.fine) + stroke(door, W.fine));
}

function maunaKea(x, y, k = 1) {   // the summit ridge with CFHT, Subaru, the Keck pair and two small domes
  hand(31);
  const ridge = `M0 150 C90 140 150 96 230 84 S390 30 470 34 S600 44 660 70 S760 130 860 150`;
  return `<g transform="translate(${x} ${y}) scale(${k})">
    <defs><linearGradient id="mk-fade" gradientUnits="userSpaceOnUse" x1="-90" y1="0" x2="150" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff"/></linearGradient>
      <mask id="mk-foot" maskUnits="userSpaceOnUse" x="-200" y="-100" width="1300" height="500"><rect x="-200" y="-100" width="1300" height="500" fill="url(#mk-fade)"/></mask></defs>
    <g mask="url(#mk-foot)">${glaze('url(#g-mount)', 'M-90 168 C-50 162 -20 156 0 150' + ridge.slice(6) + ' L860 300 L-90 300Z')}</g>
    ${glaze('url(#g-shade)', 'M470 34 S600 44 660 70 S760 130 860 150 L700 190 C620 150 540 90 470 34Z', 0.8)}
    ${pencil(stroke(ridge, W.line) + stroke('M4 154 C92 142 150 100 232 88 S390 36 468 38', W.ghost) + stroke('M-30 156 C40 150 70 146 110 140', W.ghost) + stroke('M830 146 C860 151 890 156 930 166', W.ghost)
      + stroke('M140 156 C210 136 250 130 300 122', W.fine) + stroke('M520 100 C580 110 640 132 690 156', W.fine)
      + stroke('M330 158 C380 146 420 144 470 148', W.ghost) + stroke('M250 190 C300 180 340 178 390 182', W.ghost))}
    ${dome(196, 96, 20)}${dome(318, 62, 44)}${drum(430, 40, 56, 78)}${dome(528, 44, 30)}${dome(596, 54, 30)}${dome(690, 92, 18)}
  </g>`;
}

// the 10 m off-axis dish on its fork, pointed tilt degrees from the zenith, beside the raised lab;
// the back of the dish turns about PIVOT, above the tower, so the dish is drawn apart from its base
const PIVOT = [72, -124];
const BOWL = 'M-120 0 Q0 98 120 0', CABIN = [[130, -128], [174, -128], [168, -164], [124, -164]];
function sptBase(x, y, k = 1) {   // the ice, the raised lab and the tower
  hand(47);
  return `<g transform="translate(${x} ${y}) scale(${k})">
    ${glaze('url(#g-ice)', 'M-340 0 H360 L300 46 H-280Z')}
    ${paper('M-230 -34 h150 v-62 h-150Z')}${loose('url(#g-shade)', 'M-120 -96 h40 v62 h-40Z')}
    ${paper('M32 0 l16 -96 h48 l16 96Z')}${loose('url(#g-shade)', 'M76 -96 h20 l16 96 h-30Z')}
    ${pencil(ln(-360, 0, 380, 0, W.line, 0) + ln(-300, 6, -190, 6, W.ghost, 0)
      + box(-230, -96, 150, 62, W.line, 6)
      + ln(-212, -34, -212, 0, W.fine) + ln(-98, -34, -98, 0, W.fine) + ln(-155, -34, -155, 0, W.fine) + ln(-212, -17, -98, -17, W.fine)
      + box(-214, -80, 20, 16, W.fine, 0) + box(-180, -80, 20, 16, W.fine, 0) + box(-146, -80, 20, 16, W.fine, 0)
      + ln(-80, -60, -44, 0, W.fine) + ln(-80, -44, -70, -44, W.fine)
      + poly([[32, 0], [48, -96], [96, -96], [112, 0]], W.line, 6, false) + ln(58, -96, 61, -132, W.line, 0) + ln(86, -96, 83, -132, W.line, 0))}
  </g>`;
}
function sptDish(x, y, tilt, k = 1) {   // the dish, its struts and the receiver cabin
  hand(48);
  return `<g transform="translate(${x} ${y}) scale(${k})"><g transform="translate(${PIVOT[0]} ${PIVOT[1]}) rotate(${tilt}) translate(0 -49)">
      ${paper(BOWL + 'Z')}${loose('url(#g-shade)', 'M-10 49 Q70 44 120 0 Q60 80 -10 49Z', 1, 2, 1.5)}
      ${paper(ell(0, 0, 120, 22))}${loose(S.sky, ell(0, 0, 120, 22), 0.4, -2.5, 1.5)}
      ${paper(CABIN.map((p, i) => (i ? 'L' : 'M') + f(p)).join(' ') + 'Z')}
      ${pencil(stroke(BOWL, W.line) + oval(0, 0, 120, 22, 0, W.line, 0.08)
        + ln(0, 49, -72, 13, W.fine, 0) + ln(0, 49, 0, 22, W.fine, 0) + ln(0, 49, 72, 13, W.fine, 0) + stroke('M-104 10 Q0 44 104 10', W.fine)
        + ln(120, 0, 152, -128, W.fine, 6) + ln(64, -19, 138, -128, W.fine, 6) + poly(CABIN, W.line, 5))}
    </g></g>`;
}

function euclid(x, y, rot, k = 1) { // the telescope tube on its service module, behind the sunshield; the aperture leads
  hand(53);
  const shield = [[-96, -178], [-32, -200], [-32, 126], [-96, 148]];
  return `<g transform="translate(${x} ${y}) rotate(${rot}) scale(${k})">
    ${paper('M-18 -140 h112 v190 h-112Z')}${loose('url(#g-shade)', 'M50 -140 h44 v190 h-44Z')}
    ${paper(ell(38, -140, 56, 15))}${dark(ell(38, -140, 42, 10))}
    ${paper('M-34 50 h144 l-12 74 h-120Z')}${loose('url(#g-shade)', 'M50 50 h60 l-12 74 h-48Z')}
    ${glaze('url(#g-foil)', 'M-96 -178 l64 -22 v326 l-64 22Z')}
    ${pencil(ln(-18, -140, -18, 50, W.line, 8) + ln(94, -140, 94, 50, W.line, 8) + oval(38, -140, 56, 15, 0, W.line, 0.12) + oval(38, -140, 42, 10, 0, W.fine, 0.05)
      + poly([[-34, 50], [110, 50], [98, 124], [-22, 124]], W.line, 6) + ln(-26, 86, 102, 86, W.fine)
      + ln(38, 124, 38, 146, W.fine, 0) + stroke('M12 150 q26 18 52 0 q-26 -10 -52 0', W.fine)
      + poly(shield, W.line, 7) + ln(-96, -96, -32, -118, W.fine) + ln(-96, -14, -32, -36, W.fine) + ln(-96, 68, -32, 46, W.fine) + ln(-64, -189, -64, 137, W.fine))}
  </g>`;
}

// ── the sky ─────────────────────────────────────────────────────────────────────────────────
// The sky as a light cone, wide enough at its mouth to hold every observer: sheets at growing
// redshift, each a wash whose pigment pools along the same web of structure. The web sharpens
// toward the observer (growth) and the last sheet is the CMB. Light leaves a patch of the far sky
// and reaches each instrument, bent a little at every sheet it crosses.
const SKY = { base: [1395, 930], ang: -101 * Math.PI / 180, r0: 100, k: 0.7, flat: 0.2 };
const AXV = [Math.cos(SKY.ang), Math.sin(SKY.ang)], MAJ = [Math.cos(SKY.ang + Math.PI / 2), Math.sin(SKY.ang + Math.PI / 2)];
const TILT = SKY.ang * 180 / Math.PI + 90;
const rad = (d) => SKY.r0 + SKY.k * d;
// a point on the sheet at distance d, u radii sideways of the sheet's own centre
const at = (s, u = 0) => { const w = (s.o + u) * rad(s.d); return [SKY.base[0] + s.d * AXV[0] + w * MAJ[0], SKY.base[1] + s.d * AXV[1] + w * MAJ[1]]; };
const along = (p) => (p[0] - SKY.base[0]) * AXV[0] + (p[1] - SKY.base[1]) * AXV[1];   // how far up the cone a point lies
const hex = (rgb) => '#' + rgb.map(v => Math.round(v).toString(16).padStart(2, '0')).join('');
const rgb = (h) => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
const deep = (h, k = 0.7) => hex(rgb(h).map(v => v * k));
const mix = (a, b, t) => hex(rgb(a).map((v, i) => v * (1 - t) + rgb(b)[i] * t));
const CMB = { d: 815, o: 0.00, col: S.butter, cmb: true };
// five redshifts, far to near: distance up the cone, sideways offset (in radii), contrast of the web, base tint
const DEPTHS = [
  { d: 690, o: -0.09, gain: 2.0, off: 0.72, tint: 0.42 },
  { d: 572, o: 0.10, gain: 2.7, off: 0.84, tint: 0.38 },
  { d: 462, o: -0.08, gain: 3.5, off: 0.98, tint: 0.34 },
  { d: 358, o: 0.11, gain: 4.6, off: 1.16, tint: 0.3 },
  { d: 262, o: -0.05, gain: 6, off: 1.4, tint: 0.26 },
];
const slices = (cols, cmb = true) => [...(cmb ? [CMB] : []), ...DEPTHS.map((s, i) => ({ ...s, col: cols[i] }))];
const sliceFilter = (id, s, face = false) => `<filter id="${id}" x="-20%" y="-20%" width="140%" height="140%" color-interpolation-filters="sRGB">
  <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="2" seed="4" result="e"/>
  <feDisplacementMap in="SourceGraphic" in2="e" scale="3" xChannelSelector="R" yChannelSelector="G" result="disc"/>
  <feGaussianBlur in="disc" stdDeviation="0.5" result="mask"/>
  ${s.cmb ? `<feTurbulence type="fractalNoise" baseFrequency="${face ? '0.22' : '0.3 0.17'}" numOctaves="2" seed="${s.seed || 21}" result="t"/>
  <feColorMatrix in="t" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  2.2 0 0 0 -0.8" result="a"/>`
  : `<feTurbulence type="turbulence" baseFrequency="${face ? '0.019' : '0.026 0.014'}" numOctaves="4" seed="${s.seed || 8}" result="t"/>
  <feColorMatrix in="t" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  ${-s.gain} 0 0 0 ${s.off}" result="a"/>`}
  <feGaussianBlur in="a" stdDeviation="${s.cmb ? 0.3 : 0.45}" result="ab"/>
  <feFlood flood-color="${deep(s.col, s.cmb ? 0.93 : 0.8)}" result="c"/>
  <feComposite in="c" in2="ab" operator="in" result="web"/>
  <feComposite in="web" in2="mask" operator="in" result="webIn"/>
  <feComponentTransfer in="mask" result="base"><feFuncA type="linear" slope="${s.cmb ? 0.38 : s.tint * 0.7}"/></feComponentTransfer>
  <feMorphology in="mask" operator="erode" radius="0.5" result="er"/><feGaussianBlur in="er" stdDeviation="0.45" result="erb"/>
  <feComposite in="mask" in2="erb" operator="out" result="rim"/>
  <feFlood flood-color="${deep(s.col, 0.8)}" result="rc"/><feComposite in="rc" in2="rim" operator="in" result="rimC"/>
  <feComponentTransfer in="rimC" result="rimA"><feFuncA type="linear" slope="0.8"/></feComponentTransfer>
  <feMerge><feMergeNode in="base"/><feMergeNode in="webIn"/><feMergeNode in="rimA"/></feMerge></filter>`;

// where each instrument stands, and the point its light arrives at
const SPT = { x: 1040, y: 1012, k: 0.8 }, EUC = { x: 1752, y: 600, k: 0.56 }, MKP = { x: 1330, y: 800, k: 0.68 }, MK = [1540, 792];
const SPT_PIVOT = [SPT.x + PIVOT[0] * SPT.k, SPT.y + PIVOT[1] * SPT.k];   // the dish turns here; Euclid turns about its middle, Mauna Kea's view about MK
const LOOK = { spt: -0.22, euclid: 0.3, unions: 0.04 };   // where on the far sky each looks, in radii from the axis
const deg = (from, to) => Math.atan2(to[0] - from[0], -(to[1] - from[1])) * 180 / Math.PI;   // clockwise from up
const off = (p, len, a) => [p[0] + len * Math.sin(a * Math.PI / 180), p[1] - len * Math.cos(a * Math.PI / 180)];

// washes laid lighter where the words are (left of words[0]), coming to full strength by words[1]:
// mask="url(#lift)"
const lifting = (words, lifted) => `<defs><linearGradient id="lift-g" gradientUnits="userSpaceOnUse" x1="${words[0]}" y1="0" x2="${words[1]}" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="${lifted}"/><stop offset="1" stop-color="#fff"/></linearGradient>
  <mask id="lift" maskUnits="userSpaceOnUse" x="0" y="-200" width="2200" height="1500"><rect x="0" y="-200" width="2200" height="1500" fill="url(#lift-g)"/></mask></defs>`;
const MEDIA = `<defs>${PENCIL}${GLAZE}</defs>`;

// One drawing, as layers from the back: each sheet of the cone washed in (far to near), their rims
// traced in pencil, what stands on the ground, and each instrument named in `who`, aimed at
// a patch of the farthest sheet it sees.
function scene({ sky, who, soft = 0.8, lifted = 0.42, words = [760, 1380], spt = SPT }) {   // spt: where the South Pole Telescope stands (above a footer, on an opener)
  hand(5);
  const has = (n) => who.includes(n), media = `<defs>${PENCIL}${GLAZE}</defs>`;
  // the farthest sheet each instrument sees: SPT the CMB, Euclid the deepest galaxies, UNIONS one sheet nearer
  const cmb = sky[0].cmb ? 1 : 0, src = { spt: { ...sky[0], o: 0 }, euclid: { ...sky[cmb], o: 0 }, unions: { ...sky[cmb + 1], o: 0 } };
  const lift = lifting(words, lifted);
  const sheets = sky.map((s, i) => { const [cx, cy] = at(s), k = rad(s.d) / 100;
    return { id: `sheet${i}`, cls: `wash breathe t${sky.length - 1 - i}`, dpr: 1, svg: `<defs>${sliceFilter('z', s)}</defs>${lift}<g mask="url(#lift)" opacity="${soft}">
      <g transform="translate(${cx.toFixed(1)} ${cy.toFixed(1)}) rotate(${TILT.toFixed(1)}) scale(${k.toFixed(3)} ${(k * SKY.flat).toFixed(3)})"><circle r="100" fill="${s.col}" filter="url(#z)"/></g></g>` }; });
  const rims = sky.map(s => { const [cx, cy] = at(s), r = rad(s.d) * (1.008 + jit(0.008));
    return oval(cx + jit(3), cy + jit(3), r, r * SKY.flat * (1 + jit(0.03)), TILT + jit(0.6), W.fine, 0.05 + rnd() * 0.07); }).join('');
  const tilt = deg([spt.x + PIVOT[0] * spt.k, spt.y + PIVOT[1] * spt.k], at(src.spt, LOOK.spt));
  const eRot = deg([EUC.x, EUC.y], at(src.euclid, LOOK.euclid));
  return [...sheets,
    { id: 'rims', svg: `${media}${lift}<g mask="url(#lift)">${pencil(rims)}</g>` },
    { id: 'ground', svg: media + (has('unions') ? glaze('url(#g-far)', 'M1090 960 C1230 930 1420 820 1560 800 S1800 840 1920 870 L1920 960Z') + maunaKea(MKP.x, MKP.y, MKP.k) : '') + (has('spt') ? sptBase(spt.x, spt.y, spt.k) : '') },
    has('spt') && { id: 'spt', cls: 'sweep about-spt', svg: media + sptDish(spt.x, spt.y, tilt, spt.k) },
    has('euclid') && { id: 'euclid', cls: 'sweep about-euclid', svg: media + euclid(EUC.x, EUC.y, eRot, EUC.k) },
  ].filter(Boolean);
}

// Looking straight up the cone from where the instruments stand: each sheet is a ring around the
// opening to the next, the nearest outermost with the coarsest web, and the CMB closes the far end.
// The rings drift a little off centre, as a cone seen slightly from the side, and no wash lies over another.
const RING = [1, 0.83, 0.67, 0.52, 0.38, 0.25];   // each sheet's radius in the mouth's, near to far
const ringAt = ({ cx, cy, R }) => (i) => [cx - (1 - RING[i]) * 0.146 * R, cy - (1 - RING[i]) * 0.108 * R, R * RING[i]];   // centre and radius of sheet i
function upTheCone({ cols, cx = 1690, cy = 630, R = 315 }) {
  hand(11);
  const sky = [...DEPTHS.map((s, i) => ({ ...s, col: cols[i], seed: 8 + 3 * i })).reverse(), { ...CMB, seed: 21 }];   // near to far
  const at = ringAt({ cx, cy, R });
  const sheets = sky.map((s, i) => { const [x, y, r] = at(i), k = r / 100;
    const hole = i < sky.length - 1 ? (([u, v, q]) => ` ${ell((u - x) / k, (v - y) / k, q / k, q / k)}`)(at(i + 1)) : '';
    return { id: `sheet${i}`, cls: `wash breathe t${i}`, dpr: 1, svg: `<defs>${sliceFilter('z', s, true)}</defs><g opacity="0.9" transform="translate(${x.toFixed(1)} ${y.toFixed(1)}) scale(${k.toFixed(3)})"><path d="${ell(0, 0, 100, 100)}${hole}" fill-rule="evenodd" fill="${s.col}" filter="url(#z)"/></g>` }; });
  const rims = sky.map((_, i) => { const [x, y, r] = at(i); return oval(x + jit(1), y + jit(1), r * 1.004, r * (1.004 + jit(0.006)), jit(20), i < 2 ? W.line : W.fine, 0.04 + rnd() * 0.05); }).join('');
  // the cone's walls, ruled from the mouth toward the far end
  const wall = (a) => { const [x0, y0, r0] = at(0), [x1, y1, r1] = at(5); return ln(x0 + r0 * Math.cos(a), y0 + r0 * Math.sin(a), x1 + r1 * Math.cos(a), y1 + r1 * Math.sin(a), W.ghost, 0); };
  return [...sheets.reverse(), { id: 'rims', svg: `${MEDIA}${pencil(rims + [2.5, 3.9, 5.3].map(wall).join(''))}` }];
}

// The third opener: Lightcone's mark, a light cone drawn by hand about its time and space axes, in
// the deck's pencil. Its past cone holds the talk's sky: the redshift sheets washed in, rose
// nearest the apex out to sky blue, and the CMB closing the mouth. The future cone is pencil alone.
function markCone({ cols, A = [1560, 505], H = 345, R = 215, flat = 0.26 }) {
  hand(23);
  const T = [0.8, 0.68, 0.56, 0.44, 0.32];   // how far down the past cone each sheet lies, far to near
  const sky = [{ ...CMB, t: 1 }, ...DEPTHS.map((s, i) => ({ ...s, col: cols[i], t: T[i], seed: 8 + 3 * i }))];
  const sheets = sky.map((s, i) => { const k = R * s.t / 100;
    return { id: `sheet${i}`, cls: `wash breathe t${sky.length - 1 - i}`, dpr: 1, svg: `<defs>${sliceFilter('z', s)}</defs><g opacity="0.88" transform="translate(${A[0]} ${(A[1] + H * s.t).toFixed(1)}) scale(${k.toFixed(3)} ${(k * flat).toFixed(3)})"><circle r="100" fill="${s.col}" filter="url(#z)"/></g>` }; });
  const ring = (t, up, wt) => oval(A[0] + jit(1.5), A[1] + (up ? -1 : 1) * H * t + jit(1.5), R * t * 1.006, R * t * flat * (1 + jit(0.03)), jit(1.2), wt, 0.04 + rnd() * 0.06);
  const lines = sky.map((s) => ring(s.t, false, s.cmb ? W.line : W.fine)).join('') + ring(1, true, W.line) + ring(0.6, true, W.ghost) + ring(0.32, true, W.ghost)
    // the cone's two walls cross at here and now; time runs up the page, space across it
    + ln(A[0] - R, A[1] - H, A[0] + R, A[1] + H, W.line, 10) + ln(A[0] + R, A[1] - H, A[0] - R, A[1] + H, W.line, 10)
    + ln(A[0] + 5, A[1] - H - 92, A[0] - 4, A[1] + H + 92, W.fine, 8) + ln(A[0] - 318, A[1] + 15, A[0] + 318, A[1] - 17, W.fine, 8);
  return [...sheets, { id: 'rims', svg: MEDIA + pencil(lines) }];
}

// a standing figure as a sketcher sets one into a landscape for scale: a contour in pencil down the
// lit side and around the head, then one muted wash for the figure (shoulders, a waist, two legs or
// a long coat), a darker touch for the head and the shaded side, and a shadow on the ground.
// `look` turns the head (1 toward the right), `arm` raises one toward the sky (1 the right arm),
// `step` sets one foot out to that side, the weight on the other.
function person(x, y, h, col, { lean = 0, look = 1, arm = 0, coat = false, w = 1, step = 0 } = {}) {
  const P = (u, v) => [x + (u * w + lean * v) * h, y - v * h];
  const side = (k) => [P(k * 0.105, 0.795), P(k * 0.094, 0.62), P(k * 0.076, 0.525), P(k * 0.088, 0.45)];
  const R = side(1), L = side(-1);
  const legs = coat ? [P(0.092, 0.16), P(0.05, 0.15), P(0.052, 0), P(0.012, 0), P(0.01, 0.15), P(-0.01, 0.15), P(-0.012, 0), P(-0.052, 0), P(-0.05, 0.15), P(-0.092, 0.16)]
    : [P(0.064 + step * 0.035, 0), P(0.02 + step * 0.035, 0), P(0.004, 0.4), P(-0.004, 0.4), P(-0.02 + step * 0.012, 0.012 * Math.abs(step)), P(-0.064 + step * 0.012, 0.012 * Math.abs(step))];
  const body = `M${f(L[0])} Q${f(P(-0.07, 0.842))} ${f(P(0, 0.842))} Q${f(P(0.07, 0.842))} ${f(R[0])} L${[...R.slice(1), ...legs, ...L.slice(1).reverse()].map(f).join(' L')}Z`;
  const shade = `M${f(P(0.03, 0.84))} Q${f(P(0.075, 0.84))} ${f(R[0])} L${[...R.slice(1), ...(coat ? [P(0.092, 0.16), P(0.03, 0.16)] : [P(0.064, 0), P(0.04, 0)]), P(0.03, 0.45)].map(f).join(' L')}Z`;
  const hc = P(look * 0.014, 0.915), dark = mix(col, S.payne, 0.35);
  const up = arm ? `M${f(P(arm * 0.085, 0.8))} L${f(P(arm * 0.105, 0.74))} L${f(P(arm * 0.232, 0.985))} L${f(P(arm * 0.212, 1.0))}Z` : '';
  return {
    lines: stroke(through([P(-0.108, 0.8), P(-0.097, 0.62), P(-0.079, 0.525), P(-0.091, 0.45), coat ? P(-0.095, 0.16) : P(-0.067, 0.02)]), W.fine) + oval(hc[0] - 0.6, hc[1] - 0.4, h * 0.047, h * 0.059, look * 8, W.ghost, -0.25),
    wash: `<ellipse cx="${(x + h * 0.12).toFixed(1)}" cy="${y + 2}" rx="${(h * 0.2).toFixed(1)}" ry="2.6" fill="${S.payne}" opacity="0.24" filter="url(#glaze)"/>`
      + glaze(col, body + up, 0.86) + glaze(S.payne, shade, 0.17) + glaze(dark, ell(hc[0], hc[1], h * 0.044, h * 0.056), 0.9),
  };
}

// What lies ahead: the cone again, with people where the instruments stood, looking up into it
// together. Its four sheets fade with distance from them, the third all but gone: we do not see
// far into the future.
function ahead() {
  hand(23);
  const base = [1602, 960], ang = -86 * Math.PI / 180, ax = [Math.cos(ang), Math.sin(ang)], mj = [Math.cos(ang + Math.PI / 2), Math.sin(ang + Math.PI / 2)], tilt = -86 + 90, flat = 0.3;
  const r = (d) => 62 + 0.44 * d, c = (d, o = 0) => [base[0] + d * ax[0] + o * r(d) * mj[0], base[1] + d * ax[1] + o * r(d) * mj[1]];
  const ds = [150, 232, 318, 405], os = [-0.06, 0.08, -0.05, 0.06];
  // four sheets, near to far: how much of each wash and of each pencil rim is left
  const sky = [{ ...DEPTHS[4], col: S.lilac }, { ...DEPTHS[3], col: '#D7AEC0' }, { ...DEPTHS[2], col: S.rose }, { ...DEPTHS[1], col: S.rose }];
  const FADE = [0.9, 0.42, 0.1, 0.035], wts = [W.line, { w: 1.6, o: 0.5 }, { w: 1.2, o: 0.17 }, { w: 1.1, o: 0.07 }];
  const washes = [3, 2, 1, 0].map(i => { const [x, y] = c(ds[i], os[i]), k = r(ds[i]) / 100;
    return { id: `sheet${i}`, cls: `wash breathe t${i}`, dpr: 1, svg: `<defs>${sliceFilter('z', sky[i])}</defs><g opacity="${FADE[i]}" transform="translate(${x.toFixed(1)} ${y.toFixed(1)}) rotate(${tilt}) scale(${k.toFixed(3)} ${(k * flat).toFixed(3)})"><circle r="100" fill="${sky[i].col}" filter="url(#z)"/></g>` }; });
  const rims = ds.map((d, i) => { const [x, y] = c(d, os[i]); return oval(x, y, r(d), r(d) * flat, tilt, wts[i], [0.07, 0.03, 0.02, 0.02][i]); }).join('');
  // the cone's sides fade with the sheets they pass
  const side = (u) => { const p = [c(u < 0 ? 125 : 85, u), c(ds[1] + 16, u), c(ds[2] + 10, u), c(ds[3], u)];
    return ln(p[0][0], p[0][1], p[1][0], p[1][1], W.sight, 0) + ln(p[1][0], p[1][1], p[2][0], p[2][1], { w: 1.2, o: 0.2 }, 0) + ln(p[2][0], p[2][1], p[3][0], p[3][1], { w: 1.1, o: 0.07 }, 0); };
  const tone = (c, k = 0.42) => mix(c, S.payne, k);
  // the people stand at the foot of the cone and under its nearest sheet: a pair in talk, a group
  // (one pointing up), three more under the cone. x, height, wash, how each stands
  const G = 962, crowd = [
    [1322, 102, tone(S.sky), { lean: 0.04, look: 1, step: 0.6 }], [1351, 91, tone(S.rose), { lean: -0.04, look: -1, coat: true }],
    [1440, 105, tone(S.lilac), { lean: 0.03, look: 1, arm: 1, step: -0.8 }], [1469, 93, tone('#DDB96F', 0.3), { lean: 0.045, look: 1, step: 0.5 }], [1501, 101, tone(S.rose, 0.5), { lean: -0.015, look: 1, coat: true }],
    [1586, 99, tone(S.sky, 0.5), { lean: 0.02, look: 0.5, step: -0.6 }], [1616, 89, tone(S.lilac), { lean: -0.03, look: -0.6, coat: true }], [1676, 101, tone(S.rose), { lean: -0.045, look: -1, step: 0.7 }]];
  const people = crowd.map(([x, h, col, how]) => person(x, G, h, col, how));
  return [
    ...washes,
    { id: 'lines', svg: MEDIA + pencil(rims + side(-1) + side(1)) },
    { id: 'people', svg: MEDIA + `<defs><linearGradient id="g-floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${S.lilac}" stop-opacity="0.5"/><stop offset="1" stop-color="${S.lilac}" stop-opacity="0"/></linearGradient></defs>`
      + glaze('url(#g-floor)', `M1250 ${G} H1790 L1745 ${G + 26} H1300Z`) + pencil(ln(1228, G, 1806, G, W.fine, 0) + ln(1270, G + 6, 1400, G + 6, W.ghost, 0) + people.map(p => p.lines).join(''))
      + people.map(p => p.wash).join('') },
  ];
}

// a sheet of sky as one wash: a disc of radius r at (cx, cy), seen face-on (flat 1) or tilted
const sheet = (s, cx, cy, r, { flat = 1, tilt = 0, o = 1, id = 'z' } = {}) => `<defs>${sliceFilter(id, s, flat === 1)}</defs><g opacity="${o}" transform="translate(${cx.toFixed(1)} ${cy.toFixed(1)}) rotate(${tilt}) scale(${(r / 100).toFixed(3)} ${(r / 100 * flat).toFixed(3)})"><circle r="100" fill="${s.col}" filter="url(#${id})"/></g>`;

// A simulated sky: a full-sky mock as a globe, one wash of butter with its web, over a graticule
// in pencil (the construction it is laid in).
const mockSky = (cx, cy, r, id = 'z') => sheet({ gain: 5.2, off: 1.22, tint: 0.34, col: S.butter, seed: 14 }, cx, cy, r, { id });
const graticule = (cx, cy, r, inc = 0.3) => oval(cx, cy, r * 1.005, r * 1.005, 0, W.line, 0.06)
  + [-60, -30, 0, 30, 60].map(lat => { const a = lat * Math.PI / 180; return oval(cx, cy - r * Math.sin(a) * Math.cos(inc), r * Math.cos(a), r * Math.cos(a) * Math.sin(inc), 0, W.ghost, 0.02); }).join('')
  + [25, 55, 90].map(lon => oval(cx, cy, r * Math.sin(lon * Math.PI / 180), r, 4, W.ghost, 0.02)).join('');
// ink: what is measured, in a pen's dark line
const INK = `<filter id="ink" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="2" seed="2" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="1.6" xChannelSelector="R" yChannelSelector="G"/></filter>`;
const ink = (s) => `<g fill="none" stroke="#211C17" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" filter="url(#ink)">${s}</g>`;

// A mock's input is known: the input spectrum in pencil, the sky simulated from it in wash, and
// what the pipeline measures on that sky in ink, lying on the pencil curve it came from.
function knownInput() {
  hand(83);
  const y0 = 905, H = 250, Wd = 440, shape = (t) => Math.pow(t, 0.55) * Math.exp(-1.7 * t) / 0.44;
  const curve = (x0) => Array.from({ length: 40 }, (_, i) => { const t = 0.03 + 1.75 * i / 39; return [x0 + 26 + (Wd - 40) * i / 39, y0 - 22 - (H - 60) * shape(t)]; });
  const axes = (x0) => ln(x0, y0, x0 + Wd, y0, W.fine, 6) + ln(x0, y0, x0, y0 - H, W.fine, 6);
  const xa = 170, xb = 1310, gx = 960, gy = 770, gr = 138;
  const truth = (x0, wt) => stroke(through(curve(x0)), wt);
  const pts = [2, 6, 10, 14, 18, 22, 26, 30, 34, 37].map((i, j) => { const [x, y] = curve(xb)[i], e = 9 + j * 2.1, d = jit(e * 0.75);
    return `<path d="M${x.toFixed(1)} ${(y + d - e).toFixed(1)} V${(y + d + e).toFixed(1)}"/><circle cx="${x.toFixed(1)}" cy="${(y + d).toFixed(1)}" r="5.2" fill="#211C17"/>`; }).join('');
  const arrow = (x1, x2, y) => ln(x1, y, x2, y, W.fine, 0) + stroke(`M${x2 - 12} ${y - 7} L${x2} ${y} L${x2 - 12} ${y + 7}`, W.fine);
  return [
    { id: 'wash', cls: 'wash', dpr: 1, svg: mockSky(gx, gy, gr) },
    { id: 'lines', svg: MEDIA + `<defs>${INK}</defs>` + pencil(axes(xa) + truth(xa, W.line) + graticule(gx, gy, gr) + axes(xb) + truth(xb, W.line) + arrow(660, 780, gy) + arrow(1140, 1260, gy)) + ink(pts) },
  ];
}

// What unites the three projects: one simulated sky, a full-sky mock as a globe, its graticule in
// pencil (the construction) under a wash (what is simulated), and a brace gathering the three lines.
function oneSky() {
  hand(61);
  const cx = 1640, cy = 335, r = 150;
  const globe = mockSky(cx, cy, r);
  const lines = graticule(cx, cy, r);
  const x = 1378, y1 = 222, y2 = 452, ym = (y1 + y2) / 2;
  const brace = stroke(`M${x} ${y1} q18 2 18 24 L${x + 18} ${ym - 26} q0 20 20 26 q-20 6 -20 26 L${x + 18} ${y2 - 24} q0 22 -18 24`, W.line);
  return [
    { id: 'wash', cls: 'wash late', dpr: 1, svg: globe },
    { id: 'lines', cls: 'late', svg: MEDIA + pencil(lines + brace + ln(x + 46, ym, cx - r - 14, ym, W.fine, 0)) },
  ];
}

// The shape catalogue under a loupe, drawn out from a spot on the nearest sheet: each galaxy's
// ellipticity as a fine stroke of ink (what is measured), longer where it is more elongated, turned
// around the mass in wash beneath it (what is inferred from them).
function shapeCatalogue({ cx = 676, cy = 800, R = 168, spot = [1150, 693] } = {}) {
  hand(97);
  const peaks = [[-58, -38, 1, 50], [72, 44, 0.8, 44], [-18, 104, 0.5, 34]];   // dx, dy, mass, core radius
  const deepRose = deep(S.rose, 0.72);
  const wash = `<defs><radialGradient id="mass"><stop offset="0" stop-color="${deepRose}" stop-opacity="0.95"/><stop offset="0.4" stop-color="${deepRose}" stop-opacity="0.45"/><stop offset="1" stop-color="${deepRose}" stop-opacity="0"/></radialGradient>
      <filter id="bleed" x="-30%" y="-30%" width="160%" height="160%"><feTurbulence type="fractalNoise" baseFrequency="0.018" numOctaves="3" seed="6" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="34" xChannelSelector="R" yChannelSelector="G" result="d"/><feGaussianBlur in="d" stdDeviation="1.2"/></filter>
      <clipPath id="lens"><circle cx="${cx}" cy="${cy}" r="${R - 2}"/></clipPath>${GLAZE}</defs>
    ${glaze(S.rose, ell(cx, cy, R - 1, R - 1), 0.3)}
    <g clip-path="url(#lens)"><g filter="url(#bleed)">
      <path d="M${cx + peaks[0][0]} ${cy + peaks[0][1]} Q${cx + 20} ${cy - 30} ${cx + peaks[1][0]} ${cy + peaks[1][1]} T${cx + 150} ${cy + 96}" fill="none" stroke="${deepRose}" stroke-width="15" opacity="0.3" stroke-linecap="round"/>
      <path d="M${cx + peaks[0][0]} ${cy + peaks[0][1]} Q${cx - 60} ${cy + 40} ${cx + peaks[2][0]} ${cy + peaks[2][1]}" fill="none" stroke="${deepRose}" stroke-width="12" opacity="0.26" stroke-linecap="round"/>
      ${peaks.map(([dx, dy, m, rc]) => `<circle cx="${cx + dx}" cy="${cy + dy}" r="${(rc * 1.9).toFixed(1)}" fill="url(#mass)" opacity="${(0.5 + 0.5 * m).toFixed(2)}"/>`).join('')}</g></g>`;
  // galaxies scattered evenly (no two closer than 28 px), each with an ellipticity of its own, sheared tangentially around the peaks
  const pts = [];
  for (let n = 0; n < 6000 && pts.length < 100; n++) { const a = rnd() * 2 * Math.PI, rr = Math.sqrt(rnd()) * (R - 15), q = [rr * Math.cos(a), rr * Math.sin(a)];
    if (pts.every(o => Math.hypot(o[0] - q[0], o[1] - q[1]) > 28)) pts.push(q); }
  const gal = pts.map(([x, y]) => { const ei = 0.06 + rnd() * 0.15, al = rnd() * Math.PI; let e1 = ei * Math.cos(2 * al), e2 = ei * Math.sin(2 * al);
    for (const [dx, dy, m, rc] of peaks) { const u = Math.hypot(x - dx, y - dy) / rc, g = 0.64 * m * 2 * u / (1 + u * u), ph = Math.atan2(y - dy, x - dx); e1 -= g * Math.cos(2 * ph); e2 -= g * Math.sin(2 * ph); }
    const e = Math.min(Math.hypot(e1, e2), 0.58), th = 0.5 * Math.atan2(e2, e1) * 180 / Math.PI, size = 4.4 + rnd() * rnd() * 5.5, k = Math.sqrt((1 + e) / (1 - e));
    const L = size * (0.55 + 2.4 * e), c = Math.cos(th * Math.PI / 180), sn = Math.sin(th * Math.PI / 180);
    return `<path d="M${(cx + x - L * c).toFixed(1)} ${(cy + y - L * sn).toFixed(1)} L${(cx + x + L * c).toFixed(1)} ${(cy + y + L * sn).toFixed(1)}"/>`; }).join('');
  // the loupe: its rim, the spot it is drawn out from, and the two lines that join them
  const d = Math.hypot(spot[0] - cx, spot[1] - cy), u = [(spot[0] - cx) / d, (spot[1] - cy) / d], nrm = [-u[1], u[0]], rs = 30;
  const tie = (sg) => ln(cx + sg * R * nrm[0] + u[0] * 6, cy + sg * R * nrm[1] + u[1] * 6, spot[0] + sg * rs * nrm[0] * 0.3, spot[1] + sg * rs * nrm[1] * 0.3, W.sight, 0);
  return [
    { id: 'mass', cls: 'wash', dpr: 1, svg: wash },
    { id: 'shapes', svg: MEDIA + `<defs>${INK}</defs>` + pencil(oval(cx, cy, R, R, 0, W.line, 0.07) + oval(cx + 1, cy + 1, R + 7, R + 6, 0, W.ghost, 0.04) + oval(spot[0], spot[1], rs, rs * 0.24, TILT, W.fine, 0.08) + tie(1) + tie(-1))
      + `<g fill="none" stroke="#211C17" stroke-width="1.9" stroke-linecap="round" filter="url(#ink)">${gal}</g>` },
  ];
}

// Simulation-based inference: the mock sky simulated again and again along a parameter, its web
// growing clumpier; the one that looks like the data is ringed in ink, and the posterior is a wash
// laid on the axis under it.
function inference() {
  hand(113);
  const y = 792, r = 56, ax = 936, xs = [0, 1, 2, 3, 4, 5, 6].map(i => 372 + i * 196), hit = 4;
  const globes = xs.map((x, i) => { const gain = 1.2 * 1.42 ** i; return sheet({ gain, off: 0.34 + 0.175 * gain, tint: 0.3, col: S.butter, seed: 14 }, x, y, r, { id: 'g' + i }); }).join('');
  const bump = (t) => Math.exp(-0.5 * ((t - xs[hit] - 14) / (t < xs[hit] + 14 ? 120 : 150)) ** 2);
  const top = Array.from({ length: 61 }, (_, i) => { const x = xs[hit] - 380 + i * 14; return [x, ax - 3 - 66 * bump(x)]; });
  const post = `<defs>${GLAZE}<linearGradient id="g-post" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${deep(S.lilac, 0.86)}" stop-opacity="0.95"/><stop offset="1" stop-color="${S.lilac}" stop-opacity="0.45"/></linearGradient></defs>`
    + glaze('url(#g-post)', through(top) + ` L${top[60][0]} ${ax} L${top[0][0]} ${ax}Z`);
  // each globe traced lightly: its rim, three parallels and a meridian
  const globe = (x, rim) => (rim ? oval(x, y, r * 1.005, r * 1.005, 0, W.fine, 0.06) : '')
    + [-40, 0, 40].map(lat => { const a = lat * Math.PI / 180; return oval(x, y - r * Math.sin(a) * Math.cos(0.3), r * Math.cos(a), r * Math.cos(a) * Math.sin(0.3), 0, W.ghost, 0.02); }).join('')
    + oval(x, y, r * 0.5, r, 4, W.ghost, 0.02);
  const lines = xs.map((x, i) => globe(x, i !== hit)).join('')
    + ln(250, ax, 1700, ax, W.line, 0) + stroke(`M1688 ${ax - 7} L1700 ${ax} L1688 ${ax + 7}`, W.line)
    + xs.map(x => ln(x, ax - 8, x, ax + 8, W.line, 0)).join('') + stroke(through(top), W.fine);
  return [
    { id: 'wash', cls: 'wash', dpr: 1, svg: globes + post },
    { id: 'lines', svg: MEDIA + `<defs>${INK}</defs>` + pencil(lines) + ink(`<circle cx="${xs[hit]}" cy="${y}" r="${r + 2}"/>`) },
  ];
}

// The three tensions, as a cosmologist sketches them: two posteriors of the expansion rate that stand
// apart; the clustering amplitude from lensing below the one the CMB predicts; and the dark-energy
// contour lying off the point where ΛCDM sits. Every posterior is a wash, since it is inferred;
// the CMB's is butter, as on the title.
function tensions() {
  hand(131);
  const y0 = 940, top = 752;
  const two = (fill, d, o = 1) => glaze(fill, d, 0.42 * o);
  // a tilted ellipse and its inner contour
  const contour = (col, cx, cy, a, b, deg, o = 1) => { const t = `rotate(${deg} ${cx} ${cy})`;
    return `<g transform="${t}">${two(col, ell(cx, cy, a, b), o)}${two(deep(col, 0.9), ell(cx, cy, a * 0.58, b * 0.58), o * 1.25)}</g>`; };
  const hump = (cx, w, h) => { const pts = Array.from({ length: 41 }, (_, i) => { const x = cx - 3 * w + i * 6 * w / 40; return [x, y0 - 2 - h * Math.exp(-0.5 * ((x - cx) / w) ** 2)]; }); return through(pts); };
  const area = (cx, w, h) => hump(cx, w, h) + ` L${cx + 3 * w} ${y0} L${cx - 3 * w} ${y0}Z`;
  const axes = (x) => ln(x, y0, x + 330, y0, W.line, 6) + ln(x, y0, x, top, W.line, 6);
  const xa = 300, xb = 795, xc = 1290;
  const wash = `<defs>${GLAZE}</defs>`
    + two(S.butter, area(xa + 112, 15, 160), 1.5) + two(S.rose, area(xa + 232, 27, 104), 1.5)
    + contour(S.sky, xb + 158, y0 - 74, 112, 36, -9) + contour(S.butter, xb + 232, y0 - 136, 38, 17, -30, 1.5)
    + contour(S.lilac, xc + 212, y0 - 68, 92, 30, 38, 1.35);
  const lcdm = [xc + 118, y0 - 128];
  const lines = ln(xa - 6, y0, xa + 336, y0, W.line, 0) + stroke(hump(xa + 112, 15, 160), W.fine) + stroke(hump(xa + 232, 27, 104), W.fine)
    + axes(xb) + axes(xc)
    + ln(lcdm[0], top + 10, lcdm[0], y0 - 8, W.sight, 0) + ln(xc + 8, lcdm[1], xc + 322, lcdm[1], W.sight, 0)
    + stroke(`M${lcdm[0] - 7} ${lcdm[1] - 7} l14 14 M${lcdm[0] + 7} ${lcdm[1] - 7} l-14 14`, W.line);
  return [{ id: 'wash', cls: 'wash early', dpr: 1, svg: wash }, { id: 'lines', cls: 'early', svg: MEDIA + pencil(lines) }];   // both arrive with the bullet that names the tensions
}

// The mock's own mark: the simulated sky as a small globe in the corner of the slide that tests the pipeline on it.
function mockMark() {
  hand(61);
  const cx = 1716, cy = 122, r = 82;
  return [
    { id: 'wash', cls: 'wash', dpr: 1, svg: mockSky(cx, cy, r) },
    { id: 'lines', svg: MEDIA + pencil(graticule(cx, cy, r)) },
  ];
}

// Computing changed astronomy in layers: sheets laid one over another, the oldest at the bottom.
// Three are finished, each a wash with what it carries: the sky a survey takes, as specks of ink;
// a simulated sky, as the web in wash; a grid of tests, ticked in ink. The fourth, agentic
// research, is still construction: its outline in pencil and the first of its wash, which spreads
// across the sheet when the slide's last line arrives.
function layers() {
  hand(149);
  const cx = 1500, a = 300, b = 84, th = 13, cys = [836, 660, 484, 308], cols = [S.butter, S.sky, S.rose, S.lilac];
  const P = (cy, u, v) => [cx + a * (u - v) / 2, cy + b * (u + v) / 2];                   // a point of a sheet, u and v in −1…1
  const corners = (cy) => [P(cy, -1, -1), P(cy, 1, -1), P(cy, 1, 1), P(cy, -1, 1)];        // far, right, near, left
  const shape = (pts) => `M${pts.map(f).join(' L')}Z`;
  const down = ([x, y]) => [x, y + th];
  const slabWash = (cy, col) => { const [, R, N, L] = corners(cy);
    return glaze(deep(col, 0.86), shape([L, N, down(N), down(L)]), 0.8) + glaze(deep(col, 0.78), shape([N, R, down(R), down(N)]), 0.8); };
  const slabLines = (cy) => { const c = corners(cy), [, R, N, L] = c;
    return poly(c, W.line, 3) + [L, N, R].map(q => ln(q[0], q[1], q[0], q[1] + th, W.fine, 0)).join('')
      + ln(...down(L), ...down(N), W.fine, 2) + ln(...down(N), ...down(R), W.fine, 2); };
  // the ties between one sheet and the next, at the left and right corners
  const ties = (lo, hi) => [3, 1].map(k => { const p = corners(lo)[k], q = corners(hi)[k]; return ln(p[0], p[1] - 6, q[0], q[1] + th + 8, W.ghost, 0); }).join('');
  const plane = (cy) => `matrix(${a / 200} ${b / 200} ${-a / 200} ${b / 200} ${cx} ${cy})`;
  // the survey's sky: galaxies as specks of ink, a few of them elongated
  const specks = Array.from({ length: 130 }, () => { const u = jit(0.9), v = jit(0.9), [x, y] = P(cys[0], u, v), r = 0.9 + rnd() * rnd() * 2.1, e = rnd() < 0.25 ? 1.5 + rnd() * 0.7 : 1;
    return `<ellipse cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" rx="${(r * e).toFixed(1)}" ry="${(r * 0.7).toFixed(1)}" transform="rotate(${(rnd() * 180).toFixed(0)} ${x.toFixed(1)} ${y.toFixed(1)})" fill="#211C17" stroke="none"/>`; }).join('');
  // the tests: a grid ruled in pencil, a tick of ink in each cell but the two still running
  const rule = [-0.5, 0, 0.5].map(t => ln(...P(cys[2], t, -0.94), ...P(cys[2], t, 0.94), W.ghost, 0) + ln(...P(cys[2], -0.94, t), ...P(cys[2], 0.94, t), W.ghost, 0)).join('');
  const cells = [-0.75, -0.25, 0.25, 0.75];
  const ticks = cells.flatMap((u, i) => cells.map((v, j) => { if ((i === 3 && j === 2) || (i === 2 && j === 3)) return ''; const [x, y] = P(cys[2], u, v);
    return `<path d="M${(x - 9).toFixed(1)} ${(y + 0.5).toFixed(1)} l6 6.5 l11 -14.5"/>`; })).join('');
  const web = `<defs>${sliceFilter('sim', { gain: 5.2, off: 1.22, tint: 0.5, col: deep(S.sky, 0.92), seed: 14 }, true)}</defs><g transform="${plane(cys[1])}"><rect x="-98" y="-98" width="196" height="196" fill="${S.sky}" filter="url(#sim)"/></g>`;
  // the sheet being laid: its outline and construction, and the wash begun at its near corner
  const top = cys[3], begun = shape([P(top, -1, 1), P(top, -1, 0.05), P(top, -0.45, 0.2), P(top, -0.1, 0.62), P(top, 0.12, 1)]);
  const construction = poly(corners(top), W.fine, 5) + ln(...P(top, -1, -1), ...P(top, 1, 1), W.ghost, 0) + ln(...P(top, -1, 1), ...P(top, 1, -1), W.ghost, 0)
    + ln(...P(top, 0, -1), ...P(top, 0, 1), W.ghost, 0) + ln(...P(top, -1, 0), ...P(top, 1, 0), W.ghost, 0);
  return [
    { id: 'wash', cls: 'wash', dpr: 1, svg: `<defs>${GLAZE}</defs>` + glaze(S.butter, shape(corners(cys[0])), 0.62) + slabWash(cys[0], S.butter) + web + slabWash(cys[1], S.sky)
        + glaze(S.rose, shape(corners(cys[2])), 0.5) + slabWash(cys[2], S.rose) },
    { id: 'lines', svg: MEDIA + `<defs>${INK}</defs>` + pencil(cys.slice(0, 3).map(slabLines).join('') + rule + ties(cys[0], cys[1]) + ties(cys[1], cys[2])) + ink(specks + ticks) },
    { id: 'begun', cls: 'wash early', dpr: 1, svg: `<defs>${GLAZE}</defs>` + loose(S.lilac, begun, 0.7) },
    { id: 'next', cls: 'early', svg: MEDIA + pencil(construction + ties(cys[2], top)) },
    { id: 'spread', cls: 'wash late', dpr: 1, svg: `<defs>${GLAZE}</defs>` + glaze(S.lilac, shape(corners(top)), 0.5) },
  ];
}

// Lightcone: the specification of an analysis as a sheet, one choice marked in each of its rows; the
// analyses run from it, as boxes; the results they give, as small figures. A thread ties every
// result back through its analysis to the choices it came from.
function lineage() {
  hand(167);
  const sx = 670, sy = 664, sw = 270, sh = 282, rows = [0, 1, 2, 3].map(i => sy + 62 + i * 58), pick = [1, 0, 2, 1];
  const optX = (k) => sx + 152 + k * 38, nx = 1140, nw = 150, nh = 56, rx = 1540, rw = 220, rh = 84, ys = [706, 806, 906];
  const thread = (x1, y1, x2, y2) => stroke(`M${x1} ${y1} C${x1 + (x2 - x1) * 0.5} ${y1} ${x2 - (x2 - x1) * 0.5} ${y2} ${x2} ${y2}`, W.fine);
  const sheet = poly([[sx, sy], [sx + sw - 34, sy], [sx + sw, sy + 34], [sx + sw, sy + sh], [sx, sy + sh]], W.line, 4)
    + ln(sx + sw - 34, sy, sx + sw - 34, sy + 34, W.fine, 0) + ln(sx + sw - 34, sy + 34, sx + sw, sy + 34, W.fine, 0)
    + rows.map((y, i) => ln(sx + 26, y, sx + 100 + (i % 2) * 16, y, W.fine, 0) + [0, 1, 2].map(k => oval(optX(k), y, 9, 9, 0, W.fine, 0.06)).join('')).join('');
  const chosen = rows.map((y, i) => `<circle cx="${optX(pick[i])}" cy="${y}" r="5.2" fill="#211C17" stroke="none"/>`).join('');
  const nodes = ys.map(y => box(nx, y - nh / 2, nw, nh, W.line, 4) + ln(nx + 18, y, nx + nw - 18 - rnd() * 30, y, W.ghost, 0)).join('');
  const frames = ys.map(y => ln(rx, y + rh / 2, rx + rw, y + rh / 2, W.fine, 4) + ln(rx, y + rh / 2, rx, y - rh / 2, W.fine, 4)).join('');
  // the three results: bandpowers on their curve, a posterior, a histogram
  const curve = Array.from({ length: 24 }, (_, i) => { const t = 0.05 + 1.7 * i / 23; return [rx + 16 + (rw - 30) * i / 23, ys[0] + rh / 2 - 8 - (rh - 22) * Math.pow(t, 0.55) * Math.exp(-1.7 * t) / 0.44]; });
  const points = [2, 5, 8, 11, 14, 17, 20, 22].map((i, j) => { const [x, y] = curve[i], e = 5 + j * 0.9, d = jit(e * 0.6);
    return `<path d="M${x.toFixed(1)} ${(y + d - e).toFixed(1)} V${(y + d + e).toFixed(1)}"/><circle cx="${x.toFixed(1)}" cy="${(y + d).toFixed(1)}" r="3.6" fill="#211C17"/>`; }).join('');
  const cx = rx + rw * 0.52, cy = ys[1] - 2, post = `<g transform="rotate(-24 ${cx} ${cy})">${glaze(S.lilac, ell(cx, cy, 70, 24), 0.55)}${glaze(deep(S.lilac, 0.86), ell(cx, cy, 40, 13), 0.7)}</g>`;
  const bars = [0.25, 0.5, 0.85, 1, 0.7, 0.4, 0.18].map((h, i) => [rx + 22 + i * 26, ys[2] + rh / 2 - h * (rh - 16), 22, h * (rh - 16)]);
  const wash = `<defs>${GLAZE}</defs>` + glaze(S.butter, `M${sx} ${sy} H${sx + sw - 34} L${sx + sw} ${sy + 34} V${sy + sh} H${sx}Z`, 0.3)
    + ys.map((y, i) => glaze([S.sky, S.rose, S.lilac][i], `M${nx} ${y - nh / 2} h${nw} v${nh} h${-nw}Z`, 0.55)).join('') + post
    + bars.map(([x, y, w, h]) => glaze(S.rose, `M${x} ${y} h${w} v${h} h${-w}Z`, 0.6)).join('');
  const ties = [[0, 0], [1, 0], [1, 1], [2, 1], [2, 2], [3, 2]].map(([r, n]) => thread(sx + sw + 6, rows[r], nx - 6, ys[n])).join('')
    + [[0, 0], [1, 0], [1, 1], [1, 2], [2, 2]].map(([n, r]) => thread(nx + nw + 6, ys[n], rx - 12, ys[r])).join('');
  return [
    { id: 'wash', cls: 'wash', dpr: 1, svg: wash },
    { id: 'lines', svg: MEDIA + `<defs>${INK}</defs>` + pencil(sheet + nodes + frames + ties + stroke(through(curve), W.fine) + bars.map(([x, y, w, h]) => box(x, y, w, h, W.fine, 0)).join('')
        + oval(cx, cy, 70, 24, -24, W.fine, 0.05)) + ink(chosen + points) },
  ];
}

const ramp = (a, b) => [0, 0.25, 0.5, 0.75, 1].map(t => mix(a, b, t));
const ART = {
  // every instrument, five redshifts from sky blue through lilac to rose, and the CMB behind them
  title: () => scene({ sky: slices([S.sky, '#B1B8DE', S.lilac, '#D7AEC0', S.rose]), who: ['euclid', 'spt', 'unions'] }),
  // Euclid's galaxies in the part's sky blue, in front of the CMB that SPT maps
  'euclid-spt': () => scene({ sky: slices(ramp('#8FB2D6', '#B9D0E6')), who: ['euclid', 'spt'], lifted: 0.14, words: [1020, 1440], spt: { x: 930, y: 952, k: 0.74 } }),
  // the turn to how the work is done: Lightcone's own mark, with the talk's sky in its past cone
  exciting: () => markCone({ cols: [S.sky, '#B1B8DE', S.lilac, '#D7AEC0', S.rose] }),
  questions: () => ahead(),
  // the whole sky again to close: looking straight up the cone, every redshift at once
  summary: () => upTheCone({ cols: [S.sky, '#B1B8DE', S.lilac, '#D7AEC0', S.rose], cx: 1640, cy: 700, R: 255 }),
  overview: () => oneSky(),
  mocks: () => mockMark(),
  tensions: () => tensions(),
  agents: () => knownInput(),
  agentic: () => layers(),
  'lightcone-research': () => lineage(),
  sbi: () => inference(),
  // the northern sky from Mauna Kea, in the part's rose, and the shape catalogue under a loupe
  unions: () => [...scene({ sky: slices(ramp('#D9A0B4', '#E8B5A8'), false), who: ['unions'], lifted: 0.14, words: [1020, 1440] }), ...shapeCatalogue()],
};

const ALT = {
  title: 'Pencil and watercolour drawing: the South Pole Telescope, the Mauna Kea domes and Euclid look up into a cone of redshift sheets that ends at the CMB',
  'euclid-spt': 'Euclid and the South Pole Telescope look up into a cone of blue redshift sheets that ends at the CMB',
  unions: 'The Mauna Kea domes look up into a cone of rose redshift sheets; a loupe drawn out from the nearest sheet shows galaxy shapes in ink, turned around the mass in wash beneath them',
  summary: 'Pencil and watercolour: the light cone seen from below, its redshift sheets as rings of wash, one inside the other, around the CMB at the far end',
  questions: 'Pencil and watercolour: a small group of people stand at the foot of a light cone and look up into it; its four sheets fade with distance, the nearest painted, the third almost gone',
  tensions: 'Three sketches in pencil and wash: two posteriors of the expansion rate standing apart, the lensing contour of clustering amplitude below the one from the CMB, and the dark-energy contour lying off the point where ΛCDM sits',
  mocks: 'A simulated sky as a small globe in pencil and wash',
  overview: 'A brace gathers the three projects and points to one simulated sky, a globe in pencil and wash',
  sbi: 'Seven mock skies along a parameter axis, their structure growing clumpier; the one that matches the data is ringed in ink and the posterior is a lilac wash on the axis beneath it',
  agentic: 'Four sheets drawn one above another in pencil and wash: a survey sky of ink specks, a simulated cosmic web, a grid of ticked tests, and on top a sheet still in construction lines with its wash only begun',
  'lightcone-research': 'A specification sheet in pencil with one choice marked in each row; threads run from its rows to three analyses, drawn as washed boxes, and on to three small results: bandpowers on a curve, a posterior, a histogram',
  agents: 'A known input spectrum in pencil, the sky simulated from it as a washed globe, and the measured bandpowers in ink lying on the same pencil curve',
  exciting: 'Pencil and watercolour: a light cone drawn about its time and space axes, as in the Lightcone logo; the past cone holds the redshift sheets as washes, down to the CMB at its mouth, and the future cone is bare pencil',
};

const flag = (n) => { const i = process.argv.indexOf(n); return i > 0 ? process.argv[i + 1] : null; };
const only = flag('--only')?.split(','), OUT = flag('--out') || path.join(HERE, 'images', 'ice_art');
fs.mkdirSync(OUT, { recursive: true });
const b = await puppeteer.launch();
const pages = {};
for (const dpr of [1, 2]) { pages[dpr] = await b.newPage(); await pages[dpr].setViewport({ width: 1920, height: 1080, deviceScaleFactor: dpr }); }
for (const [name, art] of Object.entries(ART)) {
  if (only && !only.includes(name)) continue;
  // layers that neither move nor differ in how they are laid (same classes, same resolution) are one image
  const layers = art().reduce((out, l) => { const last = out[out.length - 1];
    if (last && !l.cls && !last.cls && (l.dpr || 2) === (last.dpr || 2)) last.svg += l.svg; else out.push({ ...l });
    return out; }, []);
  for (const f of fs.readdirSync(OUT)) if (f.startsWith(`${name}-`)) fs.rmSync(path.join(OUT, f));
  for (const l of layers) { const dpr = l.dpr || 2, p = pages[dpr];
    await p.setContent(`<body style="margin:0;background:transparent"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="1920" height="1080" style="display:block">${l.svg}</svg>`);
    // each layer is kept as the part of the frame it draws on, with its place in the frame (data-at)
    const { data, info } = await sharp(await p.screenshot({ omitBackground: true })).raw().toBuffer({ resolveWithObject: true });
    let x0 = info.width, y0 = info.height, x1 = 0, y1 = 0;
    for (let y = 0; y < info.height; y++) for (let x = 0; x < info.width; x++) if (data[(y * info.width + x) * 4 + 3] > 2) { if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y; }
    const pad = 4 * dpr, snap = (v, up) => Math[up ? 'ceil' : 'floor'](v / dpr) * dpr;   // whole frame pixels, so a layer sits where it was drawn
    x0 = Math.max(0, snap(x0 - pad)); y0 = Math.max(0, snap(y0 - pad)); x1 = Math.min(info.width, snap(x1 + 1 + pad, true)); y1 = Math.min(info.height, snap(y1 + 1 + pad, true));
    await sharp(data, { raw: info }).extract({ left: x0, top: y0, width: x1 - x0, height: y1 - y0 }).png({ compressionLevel: 9 }).toFile(path.join(OUT, `${name}-${l.id}.png`));
    l.at = [x0, y0, x1 - x0, y1 - y0].map(v => v / dpr).join(' '); }
  // the slide of the same name carries the drawing: its <figure class="art"> is written here
  const figure = `  <figure class="art">\n${layers.map((l, i) => `    <img src="images/ice_art/${name}-${l.id}.png"${l.cls ? ` class="${l.cls}"` : ''} data-at="${l.at}" alt="${i ? '' : ALT[name]}">`).join('\n')}\n  </figure>\n`;
  const file = path.join(HERE, 'slides', `${name}.html`), html = fs.readFileSync(file, 'utf8');
  const next = /  <figure class="art">[\s\S]*?<\/figure>\n/.test(html) ? html.replace(/  <figure class="art">[\s\S]*?<\/figure>\n/, figure) : html.replace('  <aside class="notes">', figure + '  <aside class="notes">');
  if (next !== html && !flag('--out')) fs.writeFileSync(file, next);
}
await b.close();
