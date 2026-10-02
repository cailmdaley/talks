#!/usr/bin/env node
// House deck build: a deck directory (deck.json + slides/*.html + figures) becomes
// one self-contained index.html (reveal, fonts, figures and math inlined) and a
// report.html that lays the same slides out as a scrolling document with their notes.
//
//   node house/build.mjs <deck-dir>... [--out _site]   build named decks
//   node house/build.mjs --all [--out _site]           build every deck with a deck.json
//   node house/build.mjs --listing <file.yml>          write Quarto listing items for house decks

import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { parseHTML } from 'linkedom';
import { imageSize } from 'image-size';

const HOUSE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.dirname(HOUSE);
const NM = path.join(REPO, 'node_modules');
const CACHE = path.join(NM, '.cache', 'house');

export const LAYOUTS = [
  'title', 'section', 'statement', 'points', 'figure', 'figure-text',
  'compare', 'grid', 'number', 'bleed', 'table', 'quote', 'closing',
];

const MIME = {
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif',
  '.svg': 'image/svg+xml', '.webp': 'image/webp', '.avif': 'image/avif',
};

export class BuildError extends Error {
  constructor(problems) {
    super(problems.map(p => `  ${p}`).join('\n'));
    this.problems = problems;
  }
}

const read = p => fs.readFileSync(p, 'utf8');
const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

// ── Deck index ────────────────────────────────────────────────────────────

export function loadDeck(dir) {
  dir = path.resolve(dir);
  const file = path.join(dir, 'deck.json');
  if (!fs.existsSync(file)) throw new BuildError([`${dir}: no deck.json`]);
  let meta;
  try { meta = JSON.parse(read(file)); }
  catch (e) { throw new BuildError([`deck.json: ${e.message}`]); }
  const problems = [];
  for (const k of ['title', 'author', 'date', 'footer', 'sections'])
    if (meta[k] === undefined) problems.push(`deck.json: missing "${k}"`);
  if (!Array.isArray(meta.sections)) problems.push('deck.json: "sections" must be a list');
  const slides = [];
  const seen = new Set();
  for (const [i, sec] of (meta.sections ?? []).entries()) {
    if (!sec.title) problems.push(`deck.json: section ${i + 1} has no "title"`);
    if (!sec.outline) problems.push(`deck.json: section "${sec.title ?? i + 1}" has no one-sentence "outline"`);
    if (!Array.isArray(sec.slides) || !sec.slides.length) { problems.push(`deck.json: section "${sec.title ?? i + 1}" lists no slides`); continue; }
    for (const name of sec.slides) {
      if (seen.has(name)) problems.push(`deck.json: slide "${name}" listed twice`);
      seen.add(name);
      const src = path.join(dir, 'slides', `${name}.html`);
      if (!fs.existsSync(src)) problems.push(`deck.json: slides/${name}.html does not exist`);
      slides.push({ name, src, section: sec });
    }
  }
  const slideDir = path.join(dir, 'slides');
  if (fs.existsSync(slideDir))
    for (const f of fs.readdirSync(slideDir))
      if (f.endsWith('.html') && !seen.has(f.slice(0, -5)))
        problems.push(`slides/${f} is not listed in deck.json (list it, e.g. in a Backup section, or delete it)`);
  if (problems.length) throw new BuildError(problems);
  return { dir, name: path.basename(dir), meta, slides };
}

// ── Assets ────────────────────────────────────────────────────────────────

function pdfToPng(pdf) {
  const st = fs.statSync(pdf);
  const key = crypto.createHash('sha1').update(`${path.resolve(pdf)}:${st.size}:${st.mtimeMs}`).digest('hex').slice(0, 16);
  fs.mkdirSync(CACHE, { recursive: true });
  const base = path.join(CACHE, key);
  if (!fs.existsSync(`${base}.png`))
    execFileSync('pdftocairo', ['-png', '-singlefile', '-scale-to', '3200', '-f', '1', '-l', '1', pdf, base]);
  return `${base}.png`;
}

function loadImage(file) {
  let ext = path.extname(file).toLowerCase();
  if (ext === '.pdf') { file = pdfToPng(file); ext = '.png'; }
  const mime = MIME[ext];
  if (!mime) throw new Error(`unsupported image type ${ext}`);
  const buf = fs.readFileSync(file);
  let w, h;
  try { ({ width: w, height: h } = imageSize(buf)); } catch { /* sizes unknown */ }
  return { uri: `data:${mime};base64,${buf.toString('base64')}`, w, h };
}

function fontFaces() {
  const g = path.join(NM, '@fontsource-variable/eb-garamond/files');
  const m = path.join(NM, '@fontsource/ibm-plex-mono/files');
  const face = (family, file, weight, style, range) => {
    const b64 = fs.readFileSync(file).toString('base64');
    return `@font-face{font-family:'${family}';font-style:${style};font-weight:${weight};font-display:block;src:url(data:font/woff2;base64,${b64}) format('woff2');unicode-range:${range};}`;
  };
  const LATIN = 'U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD';
  const LATIN_EXT = 'U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF';
  const GREEK = 'U+0370-0377,U+037A-037F,U+0384-038A,U+038C,U+038E-03A1,U+03A3-03FF';
  const out = [];
  for (const style of ['normal', 'italic']) {
    out.push(face('EB Garamond', `${g}/eb-garamond-latin-wght-${style}.woff2`, '400 800', style, LATIN));
    out.push(face('EB Garamond', `${g}/eb-garamond-latin-ext-wght-${style}.woff2`, '400 800', style, LATIN_EXT));
    out.push(face('EB Garamond', `${g}/eb-garamond-greek-wght-${style}.woff2`, '400 800', style, GREEK));
  }
  for (const w of [400, 500])
    out.push(face('IBM Plex Mono', `${m}/ibm-plex-mono-latin-${w}-normal.woff2`, w, 'normal', LATIN));
  return out.join('\n');
}

// ── Math: TeX pre-rendered to SVG at build time ───────────────────────────

let MJ;
async function loadMathJax() {
  if (MJ) return MJ;
  const { mathjax } = await import('mathjax-full/js/mathjax.js');
  const { TeX } = await import('mathjax-full/js/input/tex.js');
  const { SVG } = await import('mathjax-full/js/output/svg.js');
  const { liteAdaptor } = await import('mathjax-full/js/adaptors/liteAdaptor.js');
  const { RegisterHTMLHandler } = await import('mathjax-full/js/handlers/html.js');
  const { AllPackages } = await import('mathjax-full/js/input/tex/AllPackages.js');
  const adaptor = liteAdaptor();
  RegisterHTMLHandler(adaptor);
  MJ = { mathjax, TeX, SVG, adaptor, AllPackages };
  return MJ;
}

async function renderMath(bodyHTML, macros = {}) {
  const { mathjax, TeX, SVG, adaptor, AllPackages } = await loadMathJax();
  const errors = [];
  const tex = new TeX({
    formatError: (jax, err) => { errors.push(`TeX error in $${jax.latex}$: ${err.message}`); return jax.formatError(err); },
    packages: AllPackages.filter(p => !['bussproofs', 'autoload', 'require', 'noundefined'].includes(p)),
    inlineMath: [['$', '$'], ['\\(', '\\)']],
    displayMath: [['$$', '$$'], ['\\[', '\\]']],
    processEscapes: true,
    macros,
  });
  const svg = new SVG({ fontCache: 'local' });
  const doc = mathjax.document(`<html><head></head><body>${bodyHTML}</body></html>`, {
    InputJax: tex, OutputJax: svg,
    compileError: (d, math, err) => { errors.push(`TeX error in $${math.math}$: ${err.message}`); d.compileError(math, err); },
  });
  doc.render();
  if (errors.length) throw new BuildError(errors);
  const body = adaptor.innerHTML(adaptor.body(doc.document));
  const css = body.includes('<mjx-container') ? adaptor.textContent(svg.styleSheet(doc)) : '';
  return { body, css };
}

// ── Slides ────────────────────────────────────────────────────────────────

function parseFragment(html) {
  const { document } = parseHTML(`<!doctype html><html><head></head><body>${html}</body></html>`);
  return document;
}

export function parseSlide(src) {
  const document = parseFragment(read(src));
  const top = [...document.body.children];
  return { document, top, section: top.length === 1 && top[0].localName === 'section' ? top[0] : null };
}

function wrapInFrame(fig, el, ar) {
  const doc = fig.ownerDocument;
  const box = doc.createElement('span');
  box.className = 'frame';
  if (ar) box.setAttribute('style', `--ar:${ar.toFixed(5)}`);
  const cell = doc.createElement('div');
  cell.className = 'cell';
  fig.insertBefore(cell, el);
  cell.appendChild(box);
  box.appendChild(el);
  // a source line sits directly under the figure, inside the cell
  const src = fig.querySelector(':scope > .source');
  if (src) cell.appendChild(src);
  return box;
}

function moveMarks(fig, box, problems, where) {
  for (const mark of [...fig.querySelectorAll(':scope > mark')]) {
    const nums = (mark.getAttribute('data-box') || '').trim().split(/[\s,]+/).map(Number);
    if (nums.length !== 4 || nums.some(n => !Number.isFinite(n) || n < 0 || n > 100))
      problems.push(`${where}: <mark> needs data-box="x y w h" in percent of the image`);
    else mark.setAttribute('style', `--x:${nums[0]};--y:${nums[1]};--w:${nums[2]};--h:${nums[3]}`);
    box.appendChild(mark);
  }
}

function frameFigures(frame, deckDir, problems, where) {
  // inline SVG schematics: sized by their viewBox, coloured by theme tokens
  for (const svg of [...frame.querySelectorAll('figure > svg')]) {
    const vb = (svg.getAttribute('viewBox') || '').trim().split(/[\s,]+/).map(Number);
    if (vb.length !== 4 || !(vb[2] > 0 && vb[3] > 0)) { problems.push(`${where}: an inline <svg> in a figure needs a viewBox`); continue; }
    svg.removeAttribute('width'); svg.removeAttribute('height');
    const fig = svg.parentElement;
    moveMarks(fig, wrapInFrame(fig, svg, vb[2] / vb[3]), problems, where);
  }
  for (const img of [...frame.querySelectorAll('img')]) {
    const src = img.getAttribute('src') || '';
    if (/^(data:|https?:)/.test(src)) { if (src.startsWith('http')) problems.push(`${where}: remote image ${src} (copy it into images/)`); continue; }
    const file = path.resolve(deckDir, src);
    if (!fs.existsSync(file)) { problems.push(`${where}: missing image ${src}`); continue; }
    let im;
    try { im = loadImage(file); } catch (e) { problems.push(`${where}: ${src}: ${e.message}`); continue; }
    img.setAttribute('src', im.uri);
    img.setAttribute('data-src-path', src);
    if (!img.hasAttribute('alt')) img.setAttribute('alt', '');
    const fig = img.parentElement;
    if (fig?.localName !== 'figure') continue;
    moveMarks(fig, wrapInFrame(fig, img, im.w && im.h ? im.w / im.h : null), problems, where);
  }
}

// Build one .slide frame from an authored element (a <section> or an <aside class="detail">).
function makeFrame(el, { deckDir, problems, where, footer, number, isDetail }) {
  const doc = el.ownerDocument;
  const layout = el.getAttribute('data-layout');
  const frame = doc.createElement('div');
  frame.className = isDetail ? 'slide detail' : 'slide';
  if (layout) frame.setAttribute('data-layout', layout);
  for (const a of ['data-split', 'data-flip']) if (el.hasAttribute(a)) frame.setAttribute(a, el.getAttribute(a));
  for (const c of el.classList) if (c !== 'detail') frame.classList.add(c);
  const style = el.getAttribute('style');
  if (style && !isDetail) frame.setAttribute('style', style);

  const kids = [...el.childNodes].filter(n => !(n.nodeType === 1 && n.localName === 'aside' && (n.classList.contains('notes') || n.classList.contains('detail'))));
  const head = kids.find(n => n.nodeType === 1);
  const body = doc.createElement('div');
  body.className = 'body';
  if (head && /^h[12]$/.test(head.localName) && layout !== 'title') frame.appendChild(head);
  for (const n of kids) if (n !== head || layout === 'title' || !/^h[12]$/.test(head.localName)) body.appendChild(n);
  frame.appendChild(body);
  if (layout === 'grid') frame.setAttribute('data-count', String(body.querySelectorAll(':scope > figure').length));

  frameFigures(frame, deckDir, problems, where);

  if (layout !== 'title') {
    const foot = doc.createElement('div');
    foot.className = 'foot';
    foot.innerHTML = isDetail
      ? `<span>${esc(el.getAttribute('data-label') || 'Detail')}</span><button class="close" type="button">back to slide ${number}</button>`
      : `<span>${footer}</span><span class="num">${number}</span>`;
    frame.appendChild(foot);
  }
  return frame;
}

function buildSlides(deck) {
  const problems = [];
  const out = [];
  deck.slides.forEach((s, i) => {
    const where = `slides/${s.name}.html`;
    const { section } = parseSlide(s.src);
    if (!section) { problems.push(`${where}: must hold exactly one top-level <section>`); return; }
    const number = i + 1;
    const footer = esc(deck.meta.footer);
    const frame = makeFrame(section, { deckDir: deck.dir, problems, where, footer, number });
    const notes = [...section.querySelectorAll(':scope > aside.notes')];
    const details = [...section.querySelectorAll(':scope > aside.detail')].map((d, k) => {
      const f = makeFrame(d, { deckDir: deck.dir, problems, where: `${where} detail ${k + 1}`, footer, number, isDetail: true });
      f.setAttribute('data-detail', String(k));
      return { frame: f, label: d.getAttribute('data-label') || `Detail ${k + 1}` };
    });
    if (details.length) {
      const chips = section.ownerDocument.createElement('div');
      chips.className = 'chips';
      chips.innerHTML = details.map((d, k) => `<button class="chip" type="button" data-open="${k}">${esc(d.label)}</button>`).join('');
      frame.appendChild(chips);
    }
    const attrs = [...section.attributes]
      .filter(a => !['data-layout', 'data-split', 'data-flip', 'class', 'style', 'id'].includes(a.name))
      .map(a => ` ${a.name}="${esc(a.value)}"`).join('');
    out.push({
      ...s, number,
      sectionAttrs: `id="${esc(s.name)}" data-house-slide="${esc(s.name)}"${attrs}`,
      frame: frame.outerHTML,
      notes: notes.map(n => n.innerHTML).join('\n'),
      details: details.map(d => ({ label: d.label, frame: d.frame.outerHTML })),
    });
  });
  if (problems.length) throw new BuildError(problems);
  return out;
}

// Math is rendered once over all frames and notes, then split back out.
async function typeset(slides, macros) {
  const SEP = '<hr data-house-sep="">';
  const parts = [];
  for (const s of slides) parts.push(s.frame, s.notes, ...s.details.map(d => d.frame));
  const { body, css } = await renderMath(parts.join(SEP), macros);
  const back = body.split(/<hr data-house-sep="?"?\s*\/?>/);
  if (back.length !== parts.length) throw new Error('math pass lost slide boundaries');
  let k = 0;
  for (const s of slides) {
    s.frame = back[k++]; s.notes = back[k++];
    for (const d of s.details) d.frame = back[k++];
  }
  return css;
}

// ── Output ────────────────────────────────────────────────────────────────

// A theme is a token set (plus any furniture, such as a logo) in themes/<name>.css;
// url(...) references in it are inlined relative to the themes directory.
export function themeNames() {
  return fs.readdirSync(path.join(HOUSE, 'themes')).filter(f => f.endsWith('.css')).map(f => f.slice(0, -4));
}

function themeCss(deck) {
  const name = deck.meta.theme || 'house';
  const file = path.join(HOUSE, 'themes', `${name}.css`);
  if (!fs.existsSync(file)) throw new BuildError([`deck.json: unknown theme "${name}" (one of ${themeNames().join(', ')})`]);
  return read(file).replace(/url\(\s*["']?([^"')]+)["']?\s*\)/g, (m, ref) => {
    if (/^(data:|https?:|#)/.test(ref)) return m;
    const im = loadImage(path.resolve(path.dirname(file), ref));
    return `url("${im.uri}")`;
  });
}

function deckCss(deck) {
  const extra = deck.meta.css ? path.join(deck.dir, deck.meta.css) : null;
  return extra && fs.existsSync(extra) ? read(extra) : '';
}

function deckHTML(deck, slides, mathCss, theme) {
  const sections = slides.map(s => `<section ${s.sectionAttrs}>
${s.frame}
${s.details.map(d => d.frame).join('\n')}
${s.notes.trim() ? `<aside class="notes">${s.notes}</aside>` : ''}
</section>`).join('\n');
  return `<!doctype html>
<html lang="en" class="theme-${esc(deck.meta.theme || 'house')}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(deck.meta.title)}</title>
<meta name="description" content="${esc(deck.meta.description || '')}">
<style>${fontFaces()}</style>
<style>${read(path.join(NM, 'reveal.js/dist/reveal.css'))}</style>
<style>${read(path.join(HOUSE, 'house.css'))}</style>
<style>${theme}</style>
<style>${mathCss}</style>
${deckCss(deck) ? `<style>${deckCss(deck)}</style>` : ''}
</head>
<body>
<div class="reveal"><div class="slides">
${sections}
</div></div>
<script>${read(path.join(NM, 'reveal.js/dist/reveal.js'))}</script>
<script>${read(path.join(NM, 'reveal.js/dist/plugin/notes.js'))}</script>
<script>${read(path.join(HOUSE, 'runtime.js'))}</script>
</body>
</html>
`;
}

function reportHTML(deck, slides, mathCss, theme) {
  const m = deck.meta;
  const toc = m.sections.map((sec, i) => `<li><a href="#part-${i + 1}">${esc(sec.title)}</a> <span class="outline">— ${esc(sec.outline)}</span></li>`).join('');
  let body = '';
  let current = null;
  m.sections.forEach((sec, i) => { sec._id = `part-${i + 1}`; });
  for (const s of slides) {
    if (s.section !== current) {
      current = s.section;
      body += `<h2 class="part" id="${current._id}">${esc(current.title)}</h2><p class="part-outline">${esc(current.outline)}</p>`;
    }
    body += `<article id="${esc(s.name)}">
<div class="viewport">${s.frame}</div>
${s.notes.trim() ? `<div class="prose">${s.notes}</div>` : ''}
${s.details.map(d => `<div class="detail-copy"><p class="label">${esc(d.label)}</p><div class="viewport">${d.frame.replace('class="slide detail"', 'class="slide detail open"')}</div></div>`).join('\n')}
</article>`;
  }
  return `<!doctype html>
<html lang="en" class="theme-${esc(m.theme || 'house')}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(m.title)} — report</title>
<style>${fontFaces()}</style>
<style>${read(path.join(HOUSE, 'house.css'))}</style>
<style>${theme}</style>
<style>${mathCss}</style>
${deckCss(deck) ? `<style>${deckCss(deck)}</style>` : ''}
</head>
<body class="report">
<main>
<header class="deck">
<h1>${esc(m.title)}</h1>
<p>${esc(m.author)}${m.venue ? ` · ${esc(m.venue)}` : ''} · ${esc(m.date)}</p>
<nav class="toc"><ol>${toc}</ol></nav>
</header>
${body}
</main>
<script>
(function () {
  function fit() {
    document.querySelectorAll('.viewport').forEach(function (v) {
      var s = v.clientWidth / 1920;
      v.firstElementChild.style.transform = 'scale(' + s + ')';
    });
  }
  window.addEventListener('resize', fit);
  fit();
})();
</script>
</body>
</html>
`;
}

export async function buildDeck(dir, outRoot) {
  const deck = loadDeck(dir);
  const slides = buildSlides(deck);
  const theme = themeCss(deck);
  const mathCss = await typeset(slides, deck.meta.macros || {});
  const out = path.join(outRoot, deck.name);
  fs.mkdirSync(out, { recursive: true });
  const index = path.join(out, 'index.html');
  const report = path.join(out, 'report.html');
  fs.writeFileSync(index, deckHTML(deck, slides, mathCss, theme));
  fs.writeFileSync(report, reportHTML(deck, slides, mathCss, theme));
  return { deck, slides, index, report };
}

export function houseDecks() {
  return fs.readdirSync(REPO)
    .filter(d => fs.existsSync(path.join(REPO, d, 'deck.json')))
    .map(d => path.join(REPO, d));
}

function listing(file) {
  const items = houseDecks().map(dir => {
    const m = JSON.parse(read(path.join(dir, 'deck.json')));
    if (m.draft) return null;
    const name = path.basename(dir);
    return [
      `- title: ${JSON.stringify(m.title)}`,
      `  path: ${name}/index.html`,
      `  date: ${JSON.stringify(m.date)}`,
      `  description: ${JSON.stringify(m.description || m.venue || '')}`,
    ].join('\n');
  }).filter(Boolean);
  fs.writeFileSync(file, items.length ? items.join('\n') + '\n' : '[]\n');
  console.log(`wrote ${file} (${items.length} decks)`);
}

async function main(argv) {
  const args = [...argv];
  let out = path.join(REPO, '_site');
  const oi = args.indexOf('--out');
  if (oi >= 0) { out = path.resolve(args[oi + 1]); args.splice(oi, 2); }
  const li = args.indexOf('--listing');
  if (li >= 0) { listing(path.resolve(args[li + 1])); return 0; }
  const all = args.includes('--all');
  const dirs = all ? houseDecks() : args.filter(a => !a.startsWith('--'));
  if (all && !dirs.length) { console.log('no house decks to build'); return 0; }
  if (!dirs.length) { console.error('usage: node house/build.mjs <deck-dir>... | --all [--out DIR] | --listing FILE'); return 2; }
  let failed = 0;
  for (const d of dirs) {
    try {
      const r = await buildDeck(d, out);
      const kb = f => `${Math.round(fs.statSync(f).size / 1024)} kB`;
      console.log(`${r.deck.name}: ${r.slides.length} slides → ${path.relative(process.cwd(), r.index)} (${kb(r.index)}), report.html (${kb(r.report)})`);
    } catch (e) {
      failed++;
      console.error(`${path.basename(path.resolve(d))}: build failed\n${e instanceof BuildError ? e.message : e.stack}`);
    }
  }
  return failed ? 1 : 0;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url))
  main(process.argv.slice(2)).then(code => process.exit(code));
