// The deck's drawings, a pencil underdrawing with watercolour laid in: the three instruments looking
// up a light cone of redshift slices to the CMB (the title), and the same scene cut down to each
// part's instruments (the section openers). Each is a full 1920×1080 frame on a transparent ground.
// node 2611_ICE_Barcelona/make_art.mjs → images/ice_art_{title,euclid-spt,unions}.png
import path from 'node:path'; import { fileURLToPath } from 'node:url';
import puppeteer from 'puppeteer';
const HERE = path.dirname(fileURLToPath(import.meta.url));
const S = { ground: '#F6F0E4', graphite: '#45403A', payne: '#3B4150', rose: '#E3A9A3', sage: '#A9C4A6', sky: '#9FBEDB', butter: '#EBD38A', lilac: '#C3B3DC' };

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
const W = { line: { w: 1.75, o: 0.94 }, fine: { w: 1.3, o: 0.75 }, ghost: { w: 1.05, o: 0.34 }, sight: { w: 1.15, o: 0.5 } };
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
// an ellipse traced in one movement: it starts anywhere, drifts a little outward and runs past where it began
function oval(cx, cy, rx, ry, deg = 0, wt = W.line, run = 0.1) {
  const t0 = rnd() * 2 * Math.PI, a = deg * Math.PI / 180, n = 48, drift = 0.012 + rnd() * 0.012, pts = [];
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
// the back of the dish turns about PIVOT, above the tower
const PIVOT = [72, -124];
function spt(x, y, tilt, k = 1) {
  hand(47);
  const bowl = 'M-120 0 Q0 98 120 0', cabin = [[130, -128], [174, -128], [168, -164], [124, -164]];
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
    <g transform="translate(${PIVOT[0]} ${PIVOT[1]}) rotate(${tilt}) translate(0 -49)">
      ${paper(bowl + 'Z')}${loose('url(#g-shade)', 'M-10 49 Q70 44 120 0 Q60 80 -10 49Z', 1, 2, 1.5)}
      ${paper(ell(0, 0, 120, 22))}${loose(S.sky, ell(0, 0, 120, 22), 0.4, -2.5, 1.5)}
      ${paper(cabin.map((p, i) => (i ? 'L' : 'M') + f(p)).join(' ') + 'Z')}
      ${pencil(stroke(bowl, W.line) + oval(0, 0, 120, 22, 0, W.line, 0.08)
        + ln(0, 49, -72, 13, W.fine, 0) + ln(0, 49, 0, 22, W.fine, 0) + ln(0, 49, 72, 13, W.fine, 0) + stroke('M-104 10 Q0 44 104 10', W.fine)
        + ln(120, 0, 152, -128, W.fine, 6) + ln(64, -19, 138, -128, W.fine, 6) + poly(cabin, W.line, 5))}
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
// The sky as a light cone: discs at growing redshift, each a wash whose pigment pools along the same
// web of structure. The web sharpens toward the observer (growth) and the last disc is the CMB.
const AX = { x: 1235, y: 740, ang: -62 * Math.PI / 180 };
const hex = (rgb) => '#' + rgb.map(v => Math.round(v).toString(16).padStart(2, '0')).join('');
const rgb = (h) => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
const deep = (h, k = 0.7) => hex(rgb(h).map(v => v * k));
const mix = (a, b, t) => hex(rgb(a).map((v, i) => v * (1 - t) + rgb(b)[i] * t));
const CMB = { d: 590, o: 0.00, col: S.butter, cmb: true };
// five redshifts, far to near: distance along the cone, sideways offset (in radii), contrast of the web, base tint
const DEPTHS = [
  { d: 470, o: -0.10, gain: 2.0, off: 0.72, tint: 0.42 },
  { d: 375, o: 0.12, gain: 2.7, off: 0.84, tint: 0.38 },
  { d: 290, o: -0.08, gain: 3.5, off: 0.98, tint: 0.34 },
  { d: 215, o: 0.14, gain: 4.6, off: 1.16, tint: 0.3 },
  { d: 150, o: -0.05, gain: 6, off: 1.4, tint: 0.26 },
];
const slices = (cols, cmb = true) => [...(cmb ? [CMB] : []), ...DEPTHS.map((s, i) => ({ ...s, col: cols[i] }))];
const sliceFilter = (i, s) => `<filter id="z${i}" x="-20%" y="-20%" width="140%" height="140%" color-interpolation-filters="sRGB">
  <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="2" seed="4" result="e"/>
  <feDisplacementMap in="SourceGraphic" in2="e" scale="4" xChannelSelector="R" yChannelSelector="G" result="disc"/>
  <feGaussianBlur in="disc" stdDeviation="0.9" result="mask"/>
  ${s.cmb ? `<feTurbulence type="fractalNoise" baseFrequency="0.11" numOctaves="2" seed="21" result="t"/>
  <feColorMatrix in="t" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  2.2 0 0 0 -0.8" result="a"/>`
  : `<feTurbulence type="turbulence" baseFrequency="0.02" numOctaves="4" seed="8" result="t"/>
  <feColorMatrix in="t" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  ${-s.gain} 0 0 0 ${s.off}" result="a"/>`}
  <feGaussianBlur in="a" stdDeviation="${s.cmb ? 0.5 : 0.8}" result="ab"/>
  <feFlood flood-color="${deep(s.col, s.cmb ? 0.93 : 0.8)}" result="c"/>
  <feComposite in="c" in2="ab" operator="in" result="web"/>
  <feComposite in="web" in2="mask" operator="in" result="webIn"/>
  <feComponentTransfer in="mask" result="base"><feFuncA type="linear" slope="${s.cmb ? 0.38 : s.tint * 0.7}"/></feComponentTransfer>
  <feMorphology in="mask" operator="erode" radius="1" result="er"/><feGaussianBlur in="er" stdDeviation="0.9" result="erb"/>
  <feComposite in="mask" in2="erb" operator="out" result="rim"/>
  <feFlood flood-color="${deep(s.col, 0.8)}" result="rc"/><feComposite in="rc" in2="rim" operator="in" result="rimC"/>
  <feComponentTransfer in="rimC" result="rimA"><feFuncA type="linear" slope="0.8"/></feComponentTransfer>
  <feMerge><feMergeNode in="base"/><feMergeNode in="webIn"/><feMergeNode in="rimA"/></feMerge></filter>`;
const K = 0.5, FLAT = 0.3, rot = AX.ang * 180 / Math.PI + 90;
const maj = [Math.cos(AX.ang + Math.PI / 2), Math.sin(AX.ang + Math.PI / 2)];
// a point on the cone at distance d and u radii sideways of the slice's own centre
const at = (s, u = 0) => { const r = s.d * K, w = (s.o + u) * r; return [AX.x + s.d * Math.cos(AX.ang) + w * maj[0], AX.y + s.d * Math.sin(AX.ang) + w * maj[1]]; };
const pos = (d) => [AX.x + d * Math.cos(AX.ang), AX.y + d * Math.sin(AX.ang)];
const EYE = pos(88);   // where the light meets: every instrument points here
const SPT = { x: 1070, y: 1012, k: 0.8 }, EUC = { x: 1040, y: 640, k: 0.6 }, MK = [1545, 800];
const deg = (from, to) => Math.atan2(to[0] - from[0], -(to[1] - from[1])) * 180 / Math.PI;   // clockwise from up
const piv = [SPT.x + PIVOT[0] * SPT.k, SPT.y + PIVOT[1] * SPT.k], tilt = deg(piv, EYE);
const dish = [piv[0] + 49 * SPT.k * Math.sin(tilt * Math.PI / 180), piv[1] - 49 * SPT.k * Math.cos(tilt * Math.PI / 180)];   // the centre of its aperture
const eRot = deg([EUC.x, EUC.y], EYE), eTip = [EUC.x + 150 * EUC.k * Math.sin(eRot * Math.PI / 180), EUC.y - 150 * EUC.k * Math.cos(eRot * Math.PI / 180)];
// a line of sight, laid in lightly from the instrument through the point where the light meets and a little beyond
const sight = (from) => { const L = Math.hypot(EYE[0] - from[0], EYE[1] - from[1]), e = 26 / L;
  return ln(from[0], from[1], EYE[0] + (EYE[0] - from[0]) * e, EYE[1] + (EYE[1] - from[1]) * e, W.sight, 0); };

// One frame: the slices of the cone, each traced in pencil and washed in, the light bent a little
// at each on its way to the observer, and the instruments named in `who`, each aimed at the point
// where the light meets.
function scene({ sky, who }) {
  hand(5);
  const cone = `<defs>${sky.map((s, i) => sliceFilter(i, s)).join('')}</defs>` + sky.map((s, i) => { const [cx, cy] = at(s), k = s.d * K / 100;
    return `<g style="mix-blend-mode:multiply" transform="translate(${cx.toFixed(1)} ${cy.toFixed(1)}) rotate(${rot.toFixed(1)}) scale(${k.toFixed(3)} ${(k * FLAT).toFixed(3)})"><circle r="100" fill="${s.col}" filter="url(#z${i})"/></g>`; }).join('');
  const rims = sky.map(s => { const [cx, cy] = at(s), r = s.d * K * (1.01 + jit(0.012));
    return oval(cx + jit(3), cy + jit(3), r, r * FLAT * (1 + jit(0.04)), rot + jit(1), W.fine, 0.06 + rnd() * 0.08); }).join('');
  const rays = [-0.62, -0.3, 0.02, 0.33, 0.6].map(u => stroke(through(ease([...sky.map(s => at(s, u)), EYE])), W.fine)).join('');
  const has = (n) => who.includes(n);
  return `<defs>${PENCIL}${GLAZE}</defs>
  ${cone}
  ${pencil(rims + rays)}
  ${pencil((has('spt') ? sight(dish) : '') + (has('unions') ? sight(MK) : '') + (has('euclid') ? sight(eTip) : ''))}
  ${has('unions') ? glaze('url(#g-far)', 'M1090 960 C1230 930 1420 820 1560 800 S1800 840 1920 870 L1920 960Z') + maunaKea(1330, 800, 0.68) : ''}
  ${has('spt') ? spt(SPT.x, SPT.y, tilt, SPT.k) : ''}
  ${has('euclid') ? euclid(EUC.x, EUC.y, eRot, EUC.k) : ''}`;
}

const ramp = (a, b) => [0, 0.25, 0.5, 0.75, 1].map(t => mix(a, b, t));
const ART = {
  // every instrument, five redshifts from sky blue through lilac to rose, and the CMB behind them
  title: scene({ sky: slices([S.sky, '#B1B8DE', S.lilac, '#D7AEC0', S.rose]), who: ['euclid', 'spt', 'unions'] }),
  // Euclid's galaxies in the part's sky blue, in front of the CMB that SPT maps
  'euclid-spt': scene({ sky: slices(ramp('#8FB2D6', '#B9D0E6')), who: ['euclid', 'spt'] }),
  // the northern sky from Mauna Kea, in the part's rose
  unions: scene({ sky: slices(ramp('#D9A0B4', '#E8B5A8'), false), who: ['unions'] }),
};

const b = await puppeteer.launch();
const p = await b.newPage(); await p.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 2 });
for (const [name, art] of Object.entries(ART)) {
  await p.setContent(`<body style="margin:0;background:transparent"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="1920" height="1080" style="display:block">${art}</svg>`);
  await p.screenshot({ path: path.join(HERE, 'images', `ice_art_${name}.png`), omitBackground: true });
}
await b.close();
