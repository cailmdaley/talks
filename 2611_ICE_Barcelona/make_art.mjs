// The deck's drawings, in pen over watercolour: the three instruments looking up a light cone of
// redshift slices to the CMB (the title), and the same scene cut down to each part's instruments
// (the section openers). Each is a full 1920×1080 frame on a transparent ground.
// node 2611_ICE_Barcelona/make_art.mjs → images/ice_art_{title,euclid-spt,unions}.png
import path from 'node:path'; import { fileURLToPath } from 'node:url';
import puppeteer from 'puppeteer';
const HERE = path.dirname(fileURLToPath(import.meta.url));
const S = { ground: '#F6F0E4', ink: '#211C17', muted: '#675D4F', rose: '#E3A9A3', sage: '#A9C4A6', sky: '#9FBEDB', butter: '#EBD38A', lilac: '#C3B3DC' };

const defs = `<defs>
${[['wash', 0.006, 110, 3, 4, 4], ['wash-fine', 0.012, 36, 1.6, 2, 2.5]].map(([id, freq, scale, blur, erode, rim]) => `<filter id="${id}" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB">
<feTurbulence type="fractalNoise" baseFrequency="${freq}" numOctaves="4" seed="11" result="n"/>
<feDisplacementMap in="SourceGraphic" in2="n" scale="${scale}" xChannelSelector="R" yChannelSelector="G" result="d"/>
<feGaussianBlur in="d" stdDeviation="${blur}" result="soft"/>
<feMorphology in="soft" operator="erode" radius="${erode}" result="er"/><feGaussianBlur in="er" stdDeviation="${rim}" result="erb"/>
<feComposite in="soft" in2="erb" operator="out" result="edge"/>
<feTurbulence type="fractalNoise" baseFrequency="${freq * 2}" numOctaves="3" seed="5" result="pool"/>
<feColorMatrix in="pool" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  2.4 0 0 0 -0.75" result="poolA"/>
<feComposite in="soft" in2="poolA" operator="in" result="pooled"/>
<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="3" result="g"/>
<feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -0.9 1.25" result="ga"/>
<feComposite in="soft" in2="ga" operator="in" result="grain"/>
<feMerge><feMergeNode in="grain"/><feMergeNode in="pooled"/><feMergeNode in="edge"/></feMerge></filter>`).join('')}
<filter id="pen" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="2" seed="2" result="n"/>
<feDisplacementMap in="SourceGraphic" in2="n" scale="5" xChannelSelector="R" yChannelSelector="G"/></filter></defs>`;

// a glaze: a wash laid precisely to its shape, pigment gathering in a thin line at the edge
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
const ell = (cx, cy, rx, ry) => `M${cx - rx} ${cy} a${rx} ${ry} 0 1 0 ${2 * rx} 0 a${rx} ${ry} 0 1 0 ${-2 * rx} 0Z`;
const INK = `fill="none" stroke="${S.ink}" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round" filter="url(#pen)"`;
const FINE = `stroke-width="1.2"`;

// a dome on a drum, lit from the upper left, its slit open toward the sky on the left
const dome = (x, y, r) => { const t = y - r * 0.7;
  return `<path d="M${x - r} ${y} V${t} a${r} ${r} 0 0 1 ${2 * r} 0 V${y}Z" fill="${S.ground}"/>
  <path d="M${x + r * 0.15} ${t - r * 0.99} A${r} ${r} 0 0 1 ${x + r} ${t} V${y} H${x + r * 0.15}Z" fill="url(#g-shade)" stroke="none"/>
  <path d="M${x - r} ${t} h${2 * r}" ${FINE}/>
  <path d="M${x - r * 0.1} ${t - r} Q${x - r * 0.72} ${t - r * 0.86} ${x - r * 0.93} ${t - r * 0.3} L${x - r * 0.62} ${t - r * 0.2} Q${x - r * 0.5} ${t - r * 0.7} ${x + r * 0.12} ${t - r * 0.98}Z" fill="${S.ink}" fill-opacity="0.82" ${FINE}/>`; };
// a cylindrical enclosure (Subaru)
const drum = (x, y, w, h) => `<path d="M${x - w / 2} ${y} v${-h} q${w / 2} ${-w * 0.22} ${w} 0 v${h}Z" fill="${S.ground}"/>
  <path d="M${x + w * 0.1} ${y - h - w * 0.1} q${w * 0.25} ${-w * 0.02} ${w * 0.4} ${w * 0.1} v${h} h${-w * 0.4}Z" fill="url(#g-shade)" stroke="none"/>
  <path d="M${x - w / 2} ${y - h} q${w / 2} ${w * 0.16} ${w} 0" ${FINE}/><path d="M${x - w * 0.3} ${y - h + w * 0.05} v${h * 0.5} h${w * 0.2} v${-h * 0.48}Z" fill="${S.ink}" fill-opacity="0.82" ${FINE}/>`;

function maunaKea(x, y, k = 1) {   // the summit ridge with CFHT, Subaru, the Keck pair and two small domes
  const ridge = `M0 150 C90 140 150 96 230 84 S390 30 470 34 S600 44 660 70 S760 130 860 150`;
  return `<g transform="translate(${x} ${y}) scale(${k})">
    ${glaze('url(#g-mount)', ridge + ' L860 300 L0 300Z')}
    ${glaze('url(#g-shade)', 'M470 34 S600 44 660 70 S760 130 860 150 L700 190 C620 150 540 90 470 34Z', 0.8)}
    <g ${INK}>
      <path d="${ridge}"/>
      <path d="M140 156 C210 136 250 130 300 122 M520 100 C580 110 640 132 690 156 M330 158 C380 146 420 144 470 148 M250 190 C300 180 340 178 390 182" ${FINE} opacity="0.7"/>
      ${dome(196, 96, 20)}${dome(318, 62, 44)}${drum(430, 40, 56, 78)}${dome(528, 44, 30)}${dome(596, 54, 30)}${dome(690, 92, 18)}
    </g></g>`;
}

function spt(x, y, tilt, k = 1) {   // the 10 m off-axis dish, pointed tilt degrees from the zenith, beside the raised lab
  return `<g transform="translate(${x} ${y}) scale(${k})">
    ${glaze('url(#g-ice)', 'M-340 0 H360 L300 46 H-280Z')}
    <g ${INK}>
      <path d="M-330 0 H350"/>
      <path d="M-230 -34 h150 v-62 h-150Z" fill="${S.ground}"/><path d="M-120 -96 h40 v62 h-40Z" fill="url(#g-shade)" stroke="none"/>
      <path d="M-212 -34 v34 M-98 -34 v34 M-155 -34 v34 M-212 -17 h114" ${FINE}/>
      <path d="M-214 -80 h20 v16 h-20Z M-180 -80 h20 v16 h-20Z M-146 -80 h20 v16 h-20Z" ${FINE}/>
      <path d="M-80 -60 l36 60 M-80 -44 h10" ${FINE}/>
      <path d="M32 0 l16 -96 h48 l16 96Z" fill="${S.ground}"/><path d="M76 -96 h20 l16 96 h-30Z" fill="url(#g-shade)" stroke="none"/>
      <g transform="translate(72 -176) rotate(${tilt})">
        <path d="M-22 46 L-12 84 M22 46 L12 84"/>
        <path d="M-120 0 Q0 98 120 0Z" fill="${S.ground}"/><path d="M-10 49 Q70 44 120 0 Q60 80 -10 49Z" fill="url(#g-shade)" stroke="none"/>
        <path d="${ell(0, 0, 120, 22)}" fill="${S.ground}"/><path d="${ell(0, 0, 120, 22)}" fill="${S.sky}" fill-opacity="0.35" stroke="none"/>
        <path d="M0 49 L-72 13 M0 49 L0 22 M0 49 L72 13 M-104 10 Q0 44 104 10" ${FINE}/>
        <path d="M120 0 L152 -128 M64 -19 L138 -128" stroke-width="1.8"/><path d="M130 -128 h44 l-6 -36 h-44Z" fill="${S.ground}"/>
      </g>
    </g></g>`;
}

function euclid(x, y, rot, k = 1) { // the telescope tube on its service module, behind the sunshield; the aperture leads
  return `<g transform="translate(${x} ${y}) rotate(${rot}) scale(${k})">
    <g ${INK}>
      <path d="M-18 -140 h112 v190 h-112Z" fill="${S.ground}"/><path d="M50 -140 h44 v190 h-44Z" fill="url(#g-shade)" stroke="none"/>
      <path d="${ell(38, -140, 56, 15)}" fill="${S.ground}"/><path d="${ell(38, -140, 42, 10)}" fill="${S.ink}" fill-opacity="0.82" ${FINE}/>
      <path d="M-34 50 h144 l-12 74 h-120Z" fill="${S.ground}"/><path d="M50 50 h60 l-12 74 h-48Z" fill="url(#g-shade)" stroke="none"/><path d="M-26 86 h128" ${FINE}/>
      <path d="M38 124 v22 M12 150 q26 18 52 0 M12 150 q26 -10 52 0"/>
      <path d="M-96 -178 l64 -22 v326 l-64 22Z" fill="${S.ground}"/><path d="M-96 -178 l64 -22 v326 l-64 22Z" fill="url(#g-foil)" stroke="none"/>
      <path d="M-96 -96 l64 -22 M-96 -14 l64 -22 M-96 68 l64 -22 M-64 -189 v326" ${FINE}/>
    </g></g>`;
}

const sight = (x1, y1, x2, y2) => `<path d="M${x1} ${y1} L${x2} ${y2}"/>`;
// The sky as a light cone: discs at growing redshift, each a wash whose pigment pools along the same
// web of structure. The web sharpens toward the observer (growth) and the last disc is the CMB.
const AX = { x: 1235, y: 740, ang: -62 * Math.PI / 180 };
const hex = (rgb) => '#' + rgb.map(v => Math.round(v).toString(16).padStart(2, '0')).join('');
const rgb = (h) => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
const deep = (h, f = 0.7) => hex(rgb(h).map(v => v * f));
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
const dish = [SPT.x + 72 * SPT.k, SPT.y - 176 * SPT.k];
const deg = (from, to) => Math.atan2(to[0] - from[0], -(to[1] - from[1])) * 180 / Math.PI;   // clockwise from up
const eRot = deg([EUC.x, EUC.y], EYE), eTip = [EUC.x + 150 * EUC.k * Math.sin(eRot * Math.PI / 180), EUC.y - 150 * EUC.k * Math.cos(eRot * Math.PI / 180)];
const toward = (from, f = 0.97) => sight(from[0], from[1], from[0] + (EYE[0] - from[0]) * f, from[1] + (EYE[1] - from[1]) * f);

// One frame: the slices of the cone, the light bent a little at each on its way to the observer,
// and the instruments named in `who`, each aimed at the point where the light meets.
function scene({ sky, who }) {
  const cone = `<defs>${sky.map((s, i) => sliceFilter(i, s)).join('')}</defs>` + sky.map((s, i) => { const [cx, cy] = at(s), k = s.d * K / 100;
    return `<g style="mix-blend-mode:multiply" transform="translate(${cx.toFixed(1)} ${cy.toFixed(1)}) rotate(${rot.toFixed(1)}) scale(${k.toFixed(3)} ${(k * FLAT).toFixed(3)})"><circle r="100" fill="${s.col}" filter="url(#z${i})"/></g>`; }).join('');
  const rays = [-0.62, -0.3, 0.02, 0.33, 0.6].map(u => `<path d="M${sky.map(s => at(s, u).map(v => v.toFixed(1)).join(' ')).join(' L')} L${EYE.map(v => v.toFixed(1)).join(' ')}"/>`).join('');
  const has = (n) => who.includes(n);
  return `${defs}<defs>${GLAZE}</defs>
  ${cone}
  <g fill="none" stroke="${S.ink}" stroke-width="1.1" stroke-linejoin="round" opacity="0.5" filter="url(#pen)">${rays}</g>
  <g fill="none" stroke="${S.muted}" stroke-width="1.4" stroke-dasharray="3 9" opacity="0.75">
    ${has('spt') ? toward(dish) : ''}${has('unions') ? toward(MK) : ''}${has('euclid') ? toward(eTip) : ''}</g>
  ${has('unions') ? glaze('url(#g-far)', 'M1090 960 C1230 930 1420 820 1560 800 S1800 840 1920 870 L1920 960Z') + maunaKea(1330, 800, 0.68) : ''}
  ${has('spt') ? spt(SPT.x, SPT.y, deg(dish, EYE), SPT.k) : ''}
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
