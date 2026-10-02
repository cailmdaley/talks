#!/usr/bin/env node
// House deck check: lint every slide against the layouts, build the deck, render
// every slide (and every detail overlay) headless at 1920×1080 with all fragments
// shown, measure it, and save screenshots plus a contact sheet.
//
//   node house/check.mjs <deck-dir> [--steps] [--only name,name]
//
// Writes <deck-dir>/_check/: NN-name.png per slide, NN-name.detail-K.png per
// overlay, contact.png, and check.txt (the same report printed here).
// Exits 1 when any slide has an error.

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { loadDeck, parseSlide, buildDeck, BuildError, LAYOUTS } from './build.mjs';

const HOUSE = path.dirname(fileURLToPath(import.meta.url));
const MIN_PX = 24;
const MIN_CONTRAST = 4.5;
const MAX_WORDS = 60;

// ── Lint: source-level rules ──────────────────────────────────────────────

// What each layout may hold at its top level, after the headline.
// Each entry: [selector, min, max].
const SCHEMA = {
  title:         { head: 'h1', body: [['p.subtitle', 0, 1], ['p.byline', 0, 1], ['p.affil', 0, 2], ['p.venue', 0, 1], ['p.date', 0, 1], ['div.logos', 0, 1]] },
  section:       { head: 'h2', body: [['p', 0, 1]] },
  statement:     { head: 'h2', body: [['p', 0, 2]] },
  points:        { head: 'h2', body: [['ul', 0, 2], ['ol', 0, 2], ['p', 0, 4], ['div.eq', 0, 3], ['div.cols', 0, 1], ['pre', 0, 1], ['span.source', 0, 1], ['p.source', 0, 1]], need: 1 },
  figure:        { head: 'h2', body: [['figure', 1, 1]] },
  'figure-text': { head: 'h2', body: [['figure', 1, 1], ['div.text', 1, 1]] },
  compare:       { head: 'h2', body: [['figure', 2, 2]] },
  grid:          { head: 'h2', body: [['figure', 3, 6]] },
  number:        { head: 'h2', body: [['div.stat', 1, 3]] },
  bleed:         { head: 'h2?', body: [['figure', 1, 1]] },
  table:         { head: 'h2', body: [['table', 1, 1], ['span.source', 0, 1], ['p.source', 0, 1], ['p', 0, 1]] },
  quote:         { head: null, body: [['blockquote', 1, 1], ['span.source', 0, 1], ['p.source', 0, 1]] },
  closing:       { head: 'h2', body: [['ol', 0, 1], ['ul', 0, 1], ['p', 0, 2], ['p.contact', 0, 1]], need: 1 },
};

const REVEAL_CLASSES = ['fragment', 'fade-in', 'fade-out', 'fade-up', 'fade-down', 'fade-left', 'fade-right',
  'fade-in-then-out', 'fade-in-then-semi-out', 'semi-fade-out', 'current-visible', 'highlight-red', 'highlight-blue',
  'highlight-green', 'highlight-current-red', 'highlight-current-blue', 'highlight-current-green', 'grow', 'shrink',
  'strike', 'notes', 'detail', 'r-stack', 'r-hstack', 'r-vstack'];

function vocabulary(deck) {
  const files = [path.join(HOUSE, 'house.css'), ...fs.readdirSync(path.join(HOUSE, 'themes')).map(f => path.join(HOUSE, 'themes', f))];
  if (deck.meta.css) files.push(path.join(deck.dir, deck.meta.css));
  const words = new Set(REVEAL_CLASSES);
  for (const f of files) {
    if (!fs.existsSync(f)) continue;
    const css = fs.readFileSync(f, 'utf8').replace(/\/\*[\s\S]*?\*\//g, '').replace(/url\([^)]*\)/g, '');
    for (const m of css.matchAll(/\.([a-zA-Z][\w-]*)/g)) words.add(m[1]);
  }
  return words;
}

function matches(el, sel) {
  const [tag, cls] = sel.split('.');
  return el.localName === tag && (!cls || el.classList.contains(cls));
}

function describe(el) {
  return `<${el.localName}${el.classList.length ? ` class="${[...el.classList].join(' ')}"` : ''}>`;
}

function lintBlock(el, where, vocab, out, isDetail) {
  const layout = el.getAttribute('data-layout');
  if (!layout) { out.errors.push(`${where}: no data-layout (one of ${LAYOUTS.join(', ')})`); return; }
  const schema = SCHEMA[layout];
  if (!schema) { out.errors.push(`${where}: unknown layout "${layout}" (one of ${LAYOUTS.join(', ')})`); return; }
  if (isDetail && !el.getAttribute('data-label')) out.errors.push(`${where}: detail needs data-label (the chip text)`);
  if (el.hasAttribute('data-split') && !['50', '60', '70'].includes(el.getAttribute('data-split')))
    out.errors.push(`${where}: data-split must be 50, 60 or 70`);

  let kids = [...el.children].filter(c => !(c.localName === 'aside' && (c.classList.contains('notes') || c.classList.contains('detail'))));
  for (const n of el.childNodes)
    if (n.nodeType === 3 && n.textContent.trim()) out.errors.push(`${where}: bare text "${n.textContent.trim().slice(0, 40)}" at the top level; wrap it in an element`);

  const headSel = schema.head?.replace('?', '');
  if (headSel) {
    const optional = schema.head.endsWith('?');
    if (kids[0]?.localName === headSel) {
      const h = kids[0];
      if (h.querySelector('br')) out.warnings.push(`${where}: <br> in the headline; a headline is one line`);
      kids = kids.slice(1);
    } else if (!optional) out.errors.push(`${where}: a ${layout} slide starts with its <${headSel}>`);
  }
  const counts = schema.body.map(() => 0);
  for (const k of kids) {
    // most specific selector first: p.source before p
    const order = schema.body.map((b, i) => i).sort((a, b) => schema.body[b][0].length - schema.body[a][0].length);
    const i = order.find(i => matches(k, schema.body[i][0]));
    if (i === undefined) {
      out.errors.push(`${where}: ${describe(k)} is not allowed at the top of a ${layout} slide (allowed: ${schema.body.map(b => b[0]).join(', ')})`);
      continue;
    }
    counts[i]++;
  }
  schema.body.forEach(([sel, min, max], i) => {
    if (counts[i] < min) out.errors.push(`${where}: a ${layout} slide needs ${min === max ? min : `at least ${min}`} ${sel} (has ${counts[i]})`);
    if (counts[i] > max) out.errors.push(`${where}: a ${layout} slide allows at most ${max} ${sel} (has ${counts[i]}); split the slide`);
  });
  if (schema.need && !kids.length) out.errors.push(`${where}: a ${layout} slide needs a body`);

  for (const d of el.querySelectorAll('*')) {
    for (const c of d.classList)
      if (!vocab.has(c)) out.errors.push(`${where}: class "${c}" is not in the design system (house.css, themes, or the deck's css)`);
    const style = d.getAttribute('style');
    if (style) {
      if (/(font-size|line-height|zoom|transform\s*:\s*scale|font\s*:)/i.test(style))
        out.errors.push(`${where}: ${describe(d)} sets type size inline (${style.trim()}); sizes come from the scale, so cut words or split`);
      else out.warnings.push(`${where}: ${describe(d)} has an inline style (${style.trim()}); fine for a one-off`);
    }
    if (d.localName === 'section') out.errors.push(`${where}: nested <section>; decks are strictly linear (use an <aside class="detail">)`);
    if (d.localName === 'mark' && d.parentElement?.localName !== 'figure') out.errors.push(`${where}: <mark> highlights belong directly inside a <figure>`);
    if (d.localName === 'mark' && !d.hasAttribute('data-box')) out.errors.push(`${where}: <mark> needs data-box="x y w h"`);
    if (d.localName === 'img' && !d.hasAttribute('alt')) out.warnings.push(`${where}: <img src="${d.getAttribute('src')}"> has no alt text`);
    if (d.localName === 'font' || d.localName === 'center') out.errors.push(`${where}: <${d.localName}> is not allowed`);
  }
}

function lint(deck) {
  const vocab = vocabulary(deck);
  const per = new Map();
  for (const s of deck.slides) {
    const out = { errors: [], warnings: [] };
    per.set(s.name, out);
    const { top, section } = parseSlide(s.src);
    if (!section) { out.errors.push(`must hold exactly one top-level <section> (found ${top.map(describe).join(', ') || 'nothing'})`); continue; }
    lintBlock(section, 'slide', vocab, out, false);
    section.querySelectorAll(':scope > aside.detail').forEach((d, k) => lintBlock(d, `detail ${k + 1}`, vocab, out, true));
    const notes = section.querySelector(':scope > aside.notes');
    if (!notes || !notes.textContent.trim()) out.warnings.push('no speaker notes; the report shows notes as the slide\'s prose');
  }
  return per;
}

// ── Render and measure ────────────────────────────────────────────────────

// Runs in the page. Measures the visible frame of the current slide.
function measure({ MIN_PX, MIN_CONTRAST, MAX_WORDS }) {
  const errors = [], warnings = [];
  const section = Reveal.getCurrentSlide();
  const frame = section.querySelector(':scope > .slide.detail.open') || section.querySelector(':scope > .slide:not(.detail)');
  const layout = frame.getAttribute('data-layout');
  const F = frame.getBoundingClientRect();
  const scale = F.width / 1920;
  const cs = getComputedStyle(frame);
  const C = {
    left: F.left + parseFloat(cs.paddingLeft) * scale,
    right: F.right - parseFloat(cs.paddingRight) * scale,
    top: F.top + parseFloat(cs.paddingTop) * scale,
    bottom: F.bottom - parseFloat(cs.paddingBottom) * scale,
  };
  const px = v => Math.round(v / scale);
  const label = el => {
    let s = el.localName;
    if (el.id) s += `#${el.id}`;
    if (el.classList.length) s += '.' + [...el.classList].join('.');
    const t = (el.textContent || '').trim().replace(/\s+/g, ' ');
    return t ? `${s} "${t.slice(0, 36)}${t.length > 36 ? '…' : ''}"` : s;
  };
  const exempt = el => el.closest('.foot, .chips, mjx-container, .logos') ||
    (layout === 'bleed' && el.closest('figure')) || el.closest('svg') && el.localName !== 'svg';
  const visible = el => {
    const st = getComputedStyle(el);
    if (st.display === 'none' || st.visibility === 'hidden') return false;
    let o = 1;
    for (let e = el; e && e !== frame; e = e.parentElement) o *= parseFloat(getComputedStyle(e).opacity);
    return o > 0.05;
  };

  // colour helpers
  const parse = c => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const v = m[1].split(/[\s,/]+/).filter(Boolean).map(Number); return { r: v[0], g: v[1], b: v[2], a: v.length > 3 ? v[3] : 1 }; };
  const over = (top, bot) => ({ r: top.r * top.a + bot.r * (1 - top.a), g: top.g * top.a + bot.g * (1 - top.a), b: top.b * top.a + bot.b * (1 - top.a), a: 1 });
  const lum = c => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }; return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); };
  const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };
  const background = el => {
    const stack = [];
    for (let e = el; e; e = e.parentElement) {
      const c = parse(getComputedStyle(e).backgroundColor);
      if (c && c.a > 0) { stack.push(c); if (c.a >= 1) break; }
      if (e === frame) break;
    }
    let bg = { r: 255, g: 255, b: 255, a: 1 };
    for (const c of stack.reverse()) bg = over(c, bg);
    return bg;
  };

  const all = [...frame.querySelectorAll('*')];
  const flagged = new Set();
  let words = 0;
  for (const el of all) {
    if (!visible(el)) continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) continue;
    const ownText = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());

    // geometry
    if (!exempt(el)) {
      const out = { left: C.left - r.left, right: r.right - C.right, top: C.top - r.top, bottom: r.bottom - C.bottom };
      const worst = Object.entries(out).sort((a, b) => b[1] - a[1])[0];
      let ancestorFlagged = false;
      for (let e = el.parentElement; e && e !== frame; e = e.parentElement) if (flagged.has(e)) { ancestorFlagged = true; break; }
      if (worst[1] > 1.5 && !ancestorFlagged) {
        flagged.add(el);
        const offCanvas = r.left < F.left - 1 || r.right > F.right + 1 || r.top < F.top - 1 || r.bottom > F.bottom + 1;
        errors.push(`${label(el)} ${offCanvas ? 'is clipped by the canvas' : 'leaves the content box'} (${worst[0]} by ${px(worst[1])}px)`);
      }
      const st = getComputedStyle(el);
      if ((st.overflowX !== 'visible' || st.overflowY !== 'visible') && !el.matches('.slide, .frame, .cell') &&
          (el.scrollHeight > el.clientHeight + 2 || el.scrollWidth > el.clientWidth + 2))
        errors.push(`${label(el)} clips its content (${el.scrollWidth}×${el.scrollHeight} in ${el.clientWidth}×${el.clientHeight})`);
    }

    // type size and contrast, for elements that carry text themselves
    if (ownText && !el.closest('mjx-container')) {
      const st = getComputedStyle(el);
      let size = parseFloat(st.fontSize);
      if (el.closest('svg')) { const m = el.getScreenCTM?.(); if (m) size *= Math.hypot(m.a, m.b) / scale; }
      if (size < MIN_PX - 0.5) errors.push(`${label(el)} is set at ${size.toFixed(1)}px (minimum ${MIN_PX}px)`);
      if (!el.closest('svg') && !el.closest('.foot')) words += [...el.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join(' ').split(/\s+/).filter(w => /\w/.test(w)).length;
      const fg = parse(st.color);
      if (fg && !el.closest('svg')) {
        const bg = background(el);
        const c = ratio(over(fg, bg), bg);
        if (c < MIN_CONTRAST - 0.005) errors.push(`${label(el)} has contrast ${c.toFixed(2)}:1 (minimum ${MIN_CONTRAST}:1)`);
      }
    }
  }

  // headline: one line wanted, three is an error
  const h = frame.querySelector(':scope > h2');
  if (h && layout !== 'section') {
    const lh = parseFloat(getComputedStyle(h).lineHeight);
    const lines = Math.round((h.getBoundingClientRect().height / scale - (layout === 'bleed' ? 52 : 18)) / lh);
    if (lines >= 3) errors.push(`headline runs to ${lines} lines; tighten it or split the slide`);
    else if (lines === 2) warnings.push('headline wraps to two lines; a claim reads best on one');
  }

  // top-level body blocks must not overlap each other
  const body = frame.querySelector(':scope > .body');
  const blocks = body ? [...body.children].filter(visible).map(e => [e, e.getBoundingClientRect()]) : [];
  for (let i = 0; i < blocks.length; i++)
    for (let j = i + 1; j < blocks.length; j++) {
      const [a, ra] = blocks[i], [b, rb] = blocks[j];
      const ox = Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left);
      const oy = Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top);
      if (ox > 2 && oy > 2 && getComputedStyle(body).display !== 'contents') errors.push(`${label(a)} overlaps ${label(b)} (${px(ox)}×${px(oy)}px)`);
    }

  // images: present, decoded, and not drawn at zero size
  for (const img of frame.querySelectorAll('img')) {
    if (!img.complete || !img.naturalWidth) errors.push(`image ${img.getAttribute('data-src-path') || '(inline)'} did not load`);
    else if (visible(img) && img.getBoundingClientRect().height < 40 * scale && !img.closest('.logos')) errors.push(`image ${img.getAttribute('data-src-path')} is drawn ${px(img.getBoundingClientRect().height)}px tall`);
  }
  for (const ph of frame.querySelectorAll('.placeholder')) if (visible(ph)) warnings.push(`placeholder "${ph.textContent.trim().slice(0, 40)}" still on the slide`);

  if (words > MAX_WORDS) warnings.push(`${words} words on screen; above ${MAX_WORDS} the audience reads instead of listening`);
  return { errors, warnings, layout, words };
}

async function render(deck, built, outDir, { steps, only }) {
  const { default: puppeteer } = await import('puppeteer');
  const browser = await puppeteer.launch({ args: ['--no-sandbox', '--allow-file-access-from-files', '--font-render-hinting=none'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
  const pageErrors = [];
  page.on('pageerror', e => pageErrors.push(String(e)));
  // the deck must work offline: anything fetched from the network is an error
  page.on('request', r => { if (!/^(data:|file:|about:|blob:)/.test(r.url())) pageErrors.push(`network request to ${r.url().slice(0, 80)} (decks must be self-contained)`); });
  await page.goto(pathToFileURL(built.index).href, { waitUntil: 'load', timeout: 120000 });
  await page.evaluate(async () => { await document.fonts.ready; await new Promise(r => Reveal.isReady() ? r() : Reveal.on('ready', r)); });
  const results = new Map();
  const shots = [];
  const n = await page.evaluate(() => Reveal.getTotalSlides());
  for (let i = 0; i < n; i++) {
    const s = deck.slides[i];
    if (only && !only.includes(s.name)) continue;
    const tag = `${String(i + 1).padStart(2, '0')}-${s.name}`;
    const res = { errors: [], warnings: [] };
    results.set(s.name, res);
    if (steps) {
      const count = await page.evaluate(i => { Reveal.slide(i, 0, -1); return Reveal.getCurrentSlide().querySelectorAll('.fragment').length; }, i);
      for (let f = -1; f < count; f++) {
        await page.evaluate((i, f) => Reveal.slide(i, 0, f), i, f);
        await new Promise(r => setTimeout(r, 120));
        await page.screenshot({ path: path.join(outDir, `${tag}.step${f + 1}.png`) });
      }
    }
    await page.evaluate(i => Reveal.slide(i, 0, 999), i);
    await new Promise(r => setTimeout(r, 150));
    const m = await page.evaluate(measure, { MIN_PX, MIN_CONTRAST, MAX_WORDS });
    res.errors.push(...m.errors); res.warnings.push(...m.warnings);
    const file = path.join(outDir, `${tag}.png`);
    await page.screenshot({ path: file });
    shots.push({ file, tag, name: s.name, res });
    const nd = await page.evaluate(() => Reveal.getCurrentSlide().querySelectorAll(':scope > .slide.detail').length);
    for (let k = 0; k < nd; k++) {
      await page.evaluate(k => House.open(Reveal.getCurrentSlide(), String(k)), k);
      await new Promise(r => setTimeout(r, 150));
      const dm = await page.evaluate(measure, { MIN_PX, MIN_CONTRAST, MAX_WORDS });
      res.errors.push(...dm.errors.map(e => `detail ${k + 1}: ${e}`));
      res.warnings.push(...dm.warnings.map(e => `detail ${k + 1}: ${e}`));
      const dfile = path.join(outDir, `${tag}.detail-${k + 1}.png`);
      await page.screenshot({ path: dfile });
      shots.push({ file: dfile, tag: `${tag} · detail ${k + 1}`, name: s.name, res, detail: true });
      await page.evaluate(() => House.close());
    }
  }

  // contact sheet
  const cards = shots.map(s => {
    const bad = s.res.errors.length ? 'bad' : s.res.warnings.length ? 'warn' : '';
    return `<div class="card ${bad}"><img src="${path.basename(s.file)}"><p>${s.tag}${s.res.errors.length ? ` — ${s.res.errors.length} error${s.res.errors.length > 1 ? 's' : ''}` : ''}</p></div>`;
  }).join('');
  const sheet = path.join(outDir, 'contact.html');
  const cols = 4;
  fs.writeFileSync(sheet, `<!doctype html><meta charset="utf-8"><style>
body{margin:0;padding:24px;background:#2b2722;font:18px/1.3 system-ui;color:#ddd;width:${cols * 500 + 24 * 2}px}
.grid{display:grid;grid-template-columns:repeat(${cols},480px);gap:20px}
.card img{width:480px;height:270px;display:block;outline:1px solid #555}
.card.bad img{outline:4px solid #e0533f}.card.warn img{outline:2px solid #d9ae57}
.card p{margin:6px 0 0}h1{font-size:22px;margin:0 0 16px;font-weight:600}
</style><h1>${deck.meta.title} — ${deck.name} · ${shots.length} frames</h1><div class="grid">${cards}</div>`);
  const sp = await browser.newPage();
  await sp.setViewport({ width: cols * 500 + 48, height: 800 });
  await sp.goto(pathToFileURL(sheet).href, { waitUntil: 'load' });
  await sp.screenshot({ path: path.join(outDir, 'contact.png'), fullPage: true });
  await browser.close();
  return { results, pageErrors };
}

// ── Main ──────────────────────────────────────────────────────────────────

async function main(argv) {
  const dir = argv.find(a => !a.startsWith('--'));
  if (!dir) { console.error('usage: node house/check.mjs <deck-dir> [--steps] [--only a,b]'); return 2; }
  const oi = argv.indexOf('--only');
  const only = oi >= 0 ? argv[oi + 1].split(',') : null;
  const steps = argv.includes('--steps');
  let deck;
  try { deck = loadDeck(dir); }
  catch (e) { console.error(e instanceof BuildError ? `deck index:\n${e.message}` : e.stack); return 1; }

  const outDir = path.join(deck.dir, '_check');
  fs.rmSync(outDir, { recursive: true, force: true });
  fs.mkdirSync(outDir, { recursive: true });

  const linted = lint(deck);
  let built;
  try { built = await buildDeck(deck.dir, fs.mkdtempSync(path.join(os.tmpdir(), 'house-check-'))); }
  catch (e) {
    const lines = [`build failed:`, e instanceof BuildError ? e.message : e.stack];
    for (const [name, r] of linted) for (const m of r.errors) lines.push(`  slides/${name}.html: ${m}`);
    console.error(lines.join('\n'));
    fs.writeFileSync(path.join(outDir, 'check.txt'), lines.join('\n') + '\n');
    return 1;
  }
  const { results, pageErrors } = await render(deck, built, outDir, { steps, only });

  const lines = [];
  let nErr = 0, nWarn = 0;
  deck.slides.forEach((s, i) => {
    if (only && !only.includes(s.name)) return;
    const l = linted.get(s.name), r = results.get(s.name) || { errors: [], warnings: [] };
    const errors = [...l.errors, ...r.errors], warnings = [...l.warnings, ...r.warnings];
    nErr += errors.length; nWarn += warnings.length;
    const head = `${String(i + 1).padStart(2, '0')} ${s.name}`;
    lines.push(errors.length ? `✗ ${head}` : warnings.length ? `! ${head}` : `✓ ${head}`);
    for (const e of errors) lines.push(`    error: ${e}`);
    for (const w of warnings) lines.push(`    warn:  ${w}`);
  });
  for (const e of pageErrors) { lines.push(`✗ page error: ${e}`); nErr++; }
  lines.push('', `${nErr} error${nErr === 1 ? '' : 's'}, ${nWarn} warning${nWarn === 1 ? '' : 's'} · screenshots and contact.png in ${path.relative(process.cwd(), outDir)}/`);
  const text = lines.join('\n');
  console.log(text);
  fs.writeFileSync(path.join(outDir, 'check.txt'), text + '\n');
  return nErr ? 1 : 0;
}

main(process.argv.slice(2)).then(code => process.exit(code));
