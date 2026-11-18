#!/usr/bin/env node
// Tests for the checker itself: the demo deck must pass, and every slide of the
// broken fixture must fail for the reason it was written to exhibit.
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const CHECK = path.join(HERE, '..', 'check.mjs');
const run = dir => spawnSync(process.execPath, [CHECK, dir], { encoding: 'utf8' });

const EXPECT = {
  overflow: 'clipped by the canvas (bottom',
  tiny: 'is set at 18.0px',
  unknown: 'class "sparkle" is not in the design system',
  contrast: 'has contrast 1.36:1',
  layoutless: 'unknown layout "carousel"',
  toomany: 'allows at most 2 figure',
  overlap: 'overlaps div.text',
  offcanvas: 'p.wide "wide" is clipped by the canvas (right',
  stepfade: 'at step 0 of 2: p.fragment.fade-out "gone later" is clipped by the canvas',
  svgtext: 'text.fill-ground "same colour as its box" has contrast 1.00:1',
  faint: 'p "barely there" has contrast',
  headline: 'overlaps the headline',
  nested: 'p "first paragraph here" overlaps p "second paragraph"',
  shrunk: 'the slide frame is scaled or transformed',
  emptyfig: 'a <figure> holds exactly one',
  loosestack: 'or a stack of <img>s whose later ones are fragments (has 2)',
  widemath: '(right by',
  cssurl: 'loads a file through url() in a style',
  longname: 'does not fit under its portrait in two lines',
  noface: 'a portrait is <figure><img',
  stackless: 'data-stack goes on a people or figure-text slide with a div.text',
  loneprism: 'data-prism turns a stack',
  strayzoom: 'data-zoom goes on a later face of a <figure data-prism>',
  loosepage: 'a <iframe> belongs directly inside a <figure>',
};
const SVG_OFF = 'text "far right" is clipped by the canvas';

let failed = 0;
const ok = (cond, msg) => { console.log(`${cond ? '✓' : '✗'} ${msg}`); if (!cond) failed++; };

const demo = run(path.join(HERE, '..', 'demo'));
ok(demo.status === 0, `demo deck passes (${demo.stdout.trim().split('\n').pop()})`);

const broken = run(path.join(HERE, 'broken'));
ok(broken.status === 1, 'broken fixture exits 1');
const blocks = {};
let cur = null;
for (const line of broken.stdout.split('\n')) {
  const m = line.match(/^[✗!✓] \d+ (\S+)/);
  if (m) { cur = m[1]; blocks[cur] = []; continue; }
  if (cur && line.startsWith('    error:')) blocks[cur].push(line);
}
for (const [slide, needle] of Object.entries(EXPECT))
  ok((blocks[slide] || []).some(l => l.includes(needle)), `${slide}: reports "${needle}"`);

ok((blocks.svgtext || []).some(l => l.includes(SVG_OFF)), `svgtext: reports "${SVG_OFF}"`);
ok(broken.stdout.includes('failed to load file:///tmp/missing.png'), 'a failed file load is reported');

const fail = run(path.join(HERE, 'buildfail'));
ok(fail.status === 1, 'build-failure fixture exits 1');
for (const needle of [
  'slides/missing.html: missing image images/does_not_exist.png',
  'slides/badbox.html: <mark> needs data-box="x y w h" in percent of the image, inside it',
  'slides/stray.html: text outside the <section> ("LOST TEXT")',
  'slides/badtex.html: TeX error in $\\frac{1}{$',
  'slides/badzoom.html: images/napoli_footprint_2_planck.png: data-zoom needs "x y w h"',
  'slides/badapp.html: missing app script private/nowhere.js',
  'slides/badalt.html: images/napoli_footprint_1_dr1.png: data-alt needs "variants" in deck.json',
  'slides/noposter.html: <video src="images/house_test_video.mp4"> needs a poster image',
  'slides/missingvideo.html: missing video images/no_such_video.mp4',
  'slides/badvideo.html: images/house_test_video.jpg: unsupported video type (mp4 or webm)',
  'slides/pageposter.html: <iframe> needs a data-poster image',
]) ok(fail.stderr.includes(needle), `build refuses: ${needle}`);

// Variants: the deck passes the checker, and in a browser the control swaps the image,
// disables the variant with no image, shows each variant's text, and stays off slides
// without variants; the report shows the default variant and no control.
const vdir = path.join(HERE, 'variants');
const vcheck = run(vdir);
ok(vcheck.status === 0, `variants fixture passes (${vcheck.stdout.trim().split('\n').pop()})`);
{
  const fs = await import('node:fs');
  const os = await import('node:os');
  const out = fs.mkdtempSync(path.join(os.tmpdir(), 'house-variants-'));
  const b = spawnSync(process.execPath, [path.join(HERE, '..', 'build.mjs'), vdir, '--out', out], { encoding: 'utf8' });
  ok(b.status === 0, 'variants fixture builds');
  const { default: puppeteer } = await import('puppeteer');
  const browser = await puppeteer.launch({ args: ['--no-sandbox', '--allow-file-access-from-files'] });
  try {
    const page = await browser.newPage();
    await page.goto('file://' + path.join(out, 'variants', 'index.html'));
    await page.waitForFunction(() => window.Reveal && Reveal.isReady() && document.querySelector('.slide > .variants'));
    const state = () => page.evaluate(() => {
      const s = document.querySelector('#toggled .slide');
      const btn = o => s.querySelector(`.variants button[data-option="${o}"]`);
      const shown = [...s.querySelectorAll('.source [data-variant]')].filter(e => !e.hasAttribute('data-hide')).map(e => e.textContent);
      return { src: s.querySelector('figure img').getAttribute('src'), on: [...s.querySelectorAll('.variants button.on')].map(x => x.dataset.option),
        disabled: ['a', 'b', 'c'].filter(o => btn(o).disabled), shown, plain: !!document.querySelector('#plain .slide > .variants') };
    });
    const s0 = await state();
    ok(s0.on.join() === 'a' && s0.disabled.join() === 'c', `control: a on, c disabled (on ${s0.on}, disabled ${s0.disabled})`);
    ok(s0.shown.join() === 'map A', 'default text shown, the others hidden');
    ok(!s0.plain, 'no control on a slide without variants');
    await page.evaluate(() => document.querySelector('#toggled .variants button[data-option="b"]').click());
    const s1 = await state();
    ok(s1.src !== s0.src && s1.on.join() === 'b', 'clicking b swaps the image');
    ok(s1.shown.join() === 'another map', "b's text shown");
    ok(await page.evaluate(() => House.variant()) === 'b', 'the choice is the deck\'s');
    const report = fs.readFileSync(path.join(out, 'variants', 'report.html'), 'utf8');
    ok(!report.includes('class="variants"') && /<span[^>]*data-hide[^>]*>another map/.test(report) && !/<span[^>]*data-hide[^>]*>map A/.test(report),
      'the report shows the default variant, with no control');
  } finally { await browser.close(); }
}

// Variant axes: a slide that names only some axes (data-variant-axes) shows the
// others faded and inert, still showing the deck's choice, which it leaves alone.
const adir = path.join(HERE, 'axes');
const acheck = run(adir);
ok(acheck.status === 0, `axes fixture passes (${acheck.stdout.trim().split('\n').pop()})`);
{
  const fs = await import('node:fs');
  const os = await import('node:os');
  const out = fs.mkdtempSync(path.join(os.tmpdir(), 'house-axes-'));
  const b = spawnSync(process.execPath, [path.join(HERE, '..', 'build.mjs'), adir, '--out', out], { encoding: 'utf8' });
  ok(b.status === 0, 'axes fixture builds');
  const { default: puppeteer } = await import('puppeteer');
  const browser = await puppeteer.launch({ args: ['--no-sandbox', '--allow-file-access-from-files'] });
  try {
    const page = await browser.newPage();
    await page.goto('file://' + path.join(out, 'axes', 'index.html'));
    await page.waitForFunction(() => window.Reveal && Reveal.isReady() && document.querySelectorAll('.slide > .variants').length === 2);
    const seg = (slide, axis) => page.evaluate((sl, ax) => {
      const g = document.querySelector(`#${sl} .variants .seg[data-axis="${ax}"]`);
      return { idle: g.classList.contains('idle'), on: [...g.querySelectorAll('button.on')].map(x => x.dataset.option),
        disabled: [...g.querySelectorAll('button')].filter(x => x.disabled).map(x => x.dataset.option) };
    }, slide, axis);
    ok(!(await seg('both', 'shear')).idle && !(await seg('both', 'cmb')).idle, 'both axes live on a slide that uses both');
    const c0 = await seg('cmbonly', 'shear');
    ok(c0.idle && c0.disabled.join() === 'x,y' && c0.on.join() === 'x', `shear idle and inert on the CMB-only slide (on ${c0.on}, disabled ${c0.disabled})`);
    ok(!(await seg('cmbonly', 'cmb')).idle, 'the CMB axis stays live there');
    await page.evaluate(() => House.setVariant('shear', 'y'));
    const c1 = await seg('cmbonly', 'shear');
    ok(c1.on.join() === 'y', "the idle segment shows the deck's choice");
    const src = () => page.evaluate(() => document.querySelector('#cmbonly figure img').getAttribute('src'));
    const s0 = await src();
    await page.evaluate(() => document.querySelector('#cmbonly .variants button[data-option="b"]').click());
    ok(await page.evaluate(() => House.variant()) === 'y|b', 'a click on the live axis keeps the idle axis\'s choice');
    ok(await src() !== s0, 'the CMB-only slide shows b with its idle axis at the default (it has x|b only)');
  } finally { await browser.close(); }
}

// Video assets work offline and on the web; the report and checker show posters.
const videoDir = path.join(HERE, 'video');
const videoCheck = run(videoDir);
ok(videoCheck.status === 0, `video fixture passes (${videoCheck.stdout.trim().split('\n').pop()})`);
{
  const fs = await import('node:fs');
  const os = await import('node:os');
  const { buildDeck } = await import('../build.mjs');
  const { default: puppeteer } = await import('puppeteer');
  const browser = await puppeteer.launch({ args: ['--no-sandbox', '--allow-file-access-from-files'] });
  const out = fs.mkdtempSync(path.join(os.tmpdir(), 'house-video-'));
  try {
    for (const web of [false, true]) {
      const built = await buildDeck(videoDir, out, { web });
      const page = await browser.newPage();
      await page.goto('file://' + built.index);
      await page.waitForFunction(() => window.Reveal && Reveal.isReady());
      const assets = await page.evaluate(() => {
        const [loop, once] = document.querySelectorAll('video');
        return { src: loop.getAttribute('src'), poster: loop.getAttribute('poster'),
          loop: loop.loop, once: once.loop, muted: loop.muted,
          ar: loop.parentElement.style.getPropertyValue('--ar'),
          unique: Object.keys(HouseAssets).length };
      });
      ok(assets.src.startsWith(web ? 'a/' : 'data:video/mp4;base64,'), `video asset resolves (${web ? 'web' : 'offline'})`);
      ok(assets.poster.startsWith(web ? 'a/' : 'data:image/jpeg;base64,') && assets.ar === '1.77778', 'poster resolves and sizes the frame');
      ok(assets.loop && !assets.once && assets.muted && assets.unique === 3, 'clips are muted, loop unless data-once, and share assets');
      const bytes = url => web ? fs.readFileSync(path.join(path.dirname(built.index), url)) : Buffer.from(url.split(',')[1], 'base64');
      ok(bytes(assets.poster).equals(fs.readFileSync(path.join(videoDir, 'images/house_test_video.jpg'))) &&
        bytes(assets.src).equals(fs.readFileSync(path.join(videoDir, 'images/house_test_video.mp4'))), 'video and poster keep their original bytes, without ground blending');
      await page.evaluate(() => Reveal.slide(1));
      await page.waitForFunction(() => {
        const video = document.querySelectorAll('video')[1];
        return !video.paused && video.currentTime > 0;
      });
      ok(true, 'WebM decodes and plays on entry');
      await page.evaluate(() => Reveal.slide(2));
      ok(await page.evaluate(() => [...document.querySelectorAll('video')].every(v => v.paused)), 'real playback pauses on leaving the slide');
      // Stub media playback so restart calls are tested even in browsers without H.264.
      await page.evaluate(() => {
        for (const video of document.querySelectorAll('video')) {
          video.pause();
          video.play = function () { this.dataset.played = Number(this.dataset.played || 0) + 1; return Promise.resolve(); };
          video.pause = function () { this.dataset.paused = 'yes'; };
        }
        Reveal.slide(2);
        Reveal.slide(0);
      });
      ok(await page.evaluate(() => {
        const [loop, once] = document.querySelectorAll('video');
        return loop.dataset.played === '1' && loop.currentTime === 0 && once.dataset.paused === 'yes';
      }), 'entering a slide restarts its clip and pauses the others');
      await page.evaluate(() => Reveal.slide(1));
      ok(await page.evaluate(() => {
        const [loop, once] = document.querySelectorAll('video');
        return loop.dataset.paused === 'yes' && once.dataset.played === '1';
      }), 'leaving a slide pauses its clip');
      await page.goto('file://' + built.report);
      ok(await page.evaluate(web => !document.querySelector('video') && document.querySelector('figure img').src.includes(web ? '/a/' : 'data:image/jpeg;base64,'), web), 'report shows a poster, not a video');
      const report = fs.readFileSync(built.report, 'utf8');
      ok(!report.includes('video/mp4') && !report.includes('.mp4'), 'report carries no clip assets');
      await page.close();
    }
  } finally {
    await browser.close();
    fs.rmSync(out, { recursive: true, force: true });
  }
}

// Live pages never load in static outputs, and load only once in the live deck.
const pageDir = path.join(HERE, 'page');
const pageCheck = run(pageDir);
ok(pageCheck.status === 0, `live page fixture passes (${pageCheck.stdout.trim().split('\n').pop()})`);
{
  const fs = await import('node:fs');
  const os = await import('node:os');
  const { buildDeck } = await import('../build.mjs');
  const { default: puppeteer } = await import('puppeteer');
  const out = fs.mkdtempSync(path.join(os.tmpdir(), 'house-page-'));
  const built = await buildDeck(pageDir, out);
  const browser = await puppeteer.launch({ args: ['--no-sandbox', '--allow-file-access-from-files'] });
  try {
    for (const mode of ['live', 'checker', 'print', 'print-media', 'report']) {
      const page = await browser.newPage();
      let requests = 0;
      await page.setRequestInterception(true);
      page.on('request', request => {
        if (request.url().startsWith('https:')) {
          requests++;
          request.respond({ status: 200, contentType: 'text/html', body: '<h1>Live app</h1>' });
        } else request.continue();
      });
      if (mode === 'checker') await page.evaluateOnNewDocument(() => { window.HousePosterOnly = true; });
      if (mode === 'print-media') await page.emulateMediaType('print');
      await page.goto('file://' + (mode === 'report' ? built.report : built.index) + (mode === 'print' ? '?print-pdf' : ''));
      if (mode !== 'report') await page.waitForFunction(() => Reveal.isReady());
      ok(requests === 0, `${mode}: no page request on opening`);
      if (mode === 'live') {
        ok(await page.evaluate(() => {
          const iframe = document.querySelector('iframe');
          return !iframe.hasAttribute('src') && getComputedStyle(iframe).display === 'none' &&
            iframe.parentElement.style.getPropertyValue('--ar') === '1.77778' &&
            iframe.previousElementSibling.src.startsWith('data:image/jpeg;base64,');
        }), 'live page starts behind an inlined, poster-sized frame');
        await page.evaluate(() => Reveal.slide(1));
        await page.waitForFunction(() => document.querySelector('iframe').getAttribute('src') === 'https://example.invalid/');
        await new Promise(r => setTimeout(r, 300));
        ok(requests === 2, 'visiting the slide probes the host, then loads the live page once');
        await page.evaluate(() => { Reveal.slide(0); Reveal.slide(1); });
        await new Promise(r => setTimeout(r, 300));
        ok(requests === 2 && await page.evaluate(() => document.querySelector('iframe').getAttribute('src') === 'https://example.invalid/'), 'the page stays loaded across visits');
      } else {
        if (mode !== 'report') await page.evaluate(() => Reveal.slide(1));
        ok(requests === 0 && await page.evaluate(() => [...document.querySelectorAll('iframe')].every(f => !f.hasAttribute('src'))), `${mode}: visiting the page slide keeps the network unloaded`);
        ok(await page.evaluate(() => !!document.querySelector('figure img[src^="data:image/jpeg"]')), `${mode}: the poster is present`);
      }
      await page.close();
    }
    // an unreachable host leaves the poster up rather than an error page
    const page = await browser.newPage();
    await page.setRequestInterception(true);
    page.on('request', request => request.url().startsWith('https:') ? request.abort('namenotresolved') : request.continue());
    await page.goto('file://' + built.index);
    await page.waitForFunction(() => Reveal.isReady());
    await page.evaluate(() => Reveal.slide(1));
    await new Promise(r => setTimeout(r, 500));
    ok(await page.evaluate(() => { const f = document.querySelector('iframe'); return !f.hasAttribute('src') && getComputedStyle(f).display === 'none'; }), 'live: an unreachable host keeps the poster');
    await page.close();
  } finally {
    await browser.close();
    fs.rmSync(out, { recursive: true, force: true });
  }
}

const only = spawnSync(process.execPath, [CHECK, path.join(HERE, '..', 'demo'), '--only', 'nope'], { encoding: 'utf8' });
ok(only.status === 2 && only.stderr.includes('no slide named nope'), '--only with an unknown slide fails');

console.log(failed ? `\n${failed} failed` : '\nall passed');
process.exit(failed ? 1 : 0);
