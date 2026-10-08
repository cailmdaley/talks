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
  widemath: 'leaves the content box (right',
  cssurl: 'loads a file through url() in a style',
  longname: 'does not fit under its portrait in two lines',
  noface: 'a portrait is <figure><img',
  stackless: 'data-stack goes on a people slide with a div.text',
  loneprism: 'data-prism turns a stack',
  strayzoom: 'data-zoom goes on a later face of a <figure data-prism>',
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

const only = spawnSync(process.execPath, [CHECK, path.join(HERE, '..', 'demo'), '--only', 'nope'], { encoding: 'utf8' });
ok(only.status === 2 && only.stderr.includes('no slide named nope'), '--only with an unknown slide fails');

console.log(failed ? `\n${failed} failed` : '\nall passed');
process.exit(failed ? 1 : 0);
