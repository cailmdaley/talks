// Cross-browser robustness check for the dv-vector slide (Chromium, Firefox, WebKit),
// with Playwright. For each browser: forward and back through the steps, entering
// from the next slide, rapid key presses mid-flight, hash jumps to each step,
// a resize mid-zoom, an iframe, reveal's overview, the print view and the report;
// each lands exactly on its rest state (the app's data-rest equals the number of
// fragments shown, on the right slide). Mid-pan and mid-zoom frames at 25/50/75 %,
// hover and a detail card are screenshotted.
//
//   node house/build.mjs 2610_Napoli_CMBX --out <site>
//   node check_dv_vector_browsers.cjs chromium <out> <site>/2610_Napoli_CMBX
//
// On Leonardo the login node (RHEL 8, glibc 2.28) runs only Chromium; Firefox and
// WebKit run inside the cmbx apptainer container (Debian 12) from Playwright's
// Debian builds, with their GTK/GStreamer/Mesa libraries unpacked from Debian
// packages into a private sysroot on LD_LIBRARY_PATH (no change to the container):
// see /leonardo_work/EUHPC_E07_074/cdaley00/pw-debian (env.sh, fetch.sh, fetch2.sh).
const pw = require('playwright');
const fs = require('fs');
const path = require('path');
const [NAME, OUT, SITE] = process.argv.slice(2);
const DECK = 'file://' + path.join(SITE, 'index.html');
const wait = ms => new Promise(r => setTimeout(r, ms));
const results = [];
const errors = [];

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await pw[NAME].launch();
  const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();
  page.on('pageerror', e => errors.push(String(e)));
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });

  const ready = async (p) => p.evaluate(async () => {
    await document.fonts.ready;
    await new Promise(r => (window.Reveal && Reveal.isReady()) ? r() : Reveal.on('ready', r));
  });
  const H = async (p) => p.evaluate(() => Reveal.getIndices(document.getElementById('dv-vector')).h);
  // the app at rest on the step its fragments say?
  const probe = (p) => p.evaluate(() => {
    const s = document.getElementById('dv-vector');
    const fig = s.querySelector('figure');
    const svg = s.querySelector('svg.app-view');
    return {
      current: Reveal.getCurrentSlide() === s,
      visible: fig.querySelectorAll('.fragment.visible').length,
      rest: svg ? svg.getAttribute('data-rest') : 'no-svg',
      cam: svg ? svg.querySelector(':scope > g').getAttribute('transform') : null,
    };
  });
  const check = async (p, name, expect, shot = true, target = page) => {
    const s = await probe(p);
    const ok = s.current && s.rest === String(s.visible) && (expect == null || s.visible === expect);
    results.push({ name, ok, ...s, expect });
    if (shot) await target.screenshot({ path: path.join(OUT, `${NAME}-${name}.png`) });
  };
  const key = async (k, ms = 0) => { await page.keyboard.press(k); if (ms) await wait(ms); };

  await page.goto(DECK + '#/dv-vector', { waitUntil: 'load', timeout: 180000 });
  await ready(page);
  const h = await H(page);
  await page.evaluate(h => Reveal.slide(h, 0, -1), h);
  await wait(400);

  // forward and backward through the steps, with real key presses
  await check(page, 'fwd-0', 0);
  await key('ArrowRight', 1300); await check(page, 'fwd-1', 1);
  await key('ArrowRight', 2000); await check(page, 'fwd-2', 2);
  await key('ArrowLeft', 2000); await check(page, 'back-1', 1);
  await key('ArrowLeft', 1300); await check(page, 'back-0', 0);

  // entering backwards from the next slide lands on the last step
  await page.evaluate(h => Reveal.slide(h + 1, 0), h); await wait(400);
  await key('ArrowLeft', 800); await check(page, 'enter-from-next', 2);

  // rapid presses, mid-animation
  await page.evaluate(h => Reveal.slide(h, 0, -1), h); await wait(300);
  // two fragments: from step 0, R R L R L R lands on step 2, every press mid-flight
  for (const [k, ms] of [['ArrowRight', 150], ['ArrowRight', 120], ['ArrowLeft', 90], ['ArrowRight', 70], ['ArrowLeft', 60], ['ArrowRight', 40]])
    await key(k, ms);
  await wait(2200); await check(page, 'rapid', 2);
  // and back down, as fast
  for (const [k, ms] of [['ArrowLeft', 100], ['ArrowLeft', 60], ['ArrowRight', 50], ['ArrowLeft', 40]]) await key(k, ms);
  await wait(2200); await check(page, 'rapid-back', 0);

  // mid-pan and mid-zoom frames: pause the step's clock at 25/50/75 %
  const midframes = async (label, from) => {
    for (const f of [0.25, 0.5, 0.75]) {
      await page.evaluate(([h, from]) => { Reveal.slide(h, 0, from); document.getAnimations().forEach(a => a.finish()); }, [h, from]);
      await wait(250);
      await key('ArrowRight');
      await page.evaluate(f => document.getAnimations().forEach(a => {
        const d = a.effect && a.effect.getComputedTiming().duration;
        if (d === 900 || d === 1500) { a.pause(); a.currentTime = f * d; }
      }), f);
      await wait(250);
      await page.screenshot({ path: path.join(OUT, `${NAME}-${label}-${Math.round(f * 100)}.png`) });
      await page.evaluate(() => document.getAnimations().forEach(a => a.finish()));
      await wait(150);
    }
  };
  await midframes('pan', -1);
  await midframes('zoom', 0);

  // hover and a detail card, by pointer
  await page.evaluate(h => { Reveal.slide(h, 0, 1); document.getAnimations().forEach(a => a.finish()); }, h);
  await wait(300);
  const hit = await page.evaluate(() => {
    const r = document.querySelectorAll('#dv-vector .dvv-hit')[86].getBoundingClientRect();   // delta_5 x delta_5
    return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
  });
  await page.mouse.move(hit.x, hit.y); await wait(150);
  await page.screenshot({ path: path.join(OUT, `${NAME}-hover.png`) });
  const t0 = Date.now();
  await page.mouse.click(hit.x, hit.y);
  await page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
  const openMs = Date.now() - t0;
  await wait(300);
  await page.screenshot({ path: path.join(OUT, `${NAME}-card.png`) });
  const before = await page.evaluate(() => JSON.stringify(Reveal.getIndices()));
  await key('ArrowRight', 300);
  const stayed = before === await page.evaluate(() => JSON.stringify(Reveal.getIndices()));
  await key('Escape', 300);
  const closed = await page.evaluate(() => !document.querySelector('#dv-vector .dvv-card'));
  results.push({ name: 'card', ok: stayed && closed, openMs, keysHeldWhileOpen: stayed, escCloses: closed });

  // overview mode (Esc in reveal) and back
  await key('Escape', 800);
  const overview = await page.evaluate(() => Reveal.isOverview());
  await page.screenshot({ path: path.join(OUT, `${NAME}-overview.png`) });
  await key('Escape', 800);
  results.push({ name: 'overview', ok: overview, overview });
  await check(page, 'after-overview', 2);

  // resize mid-zoom
  await page.evaluate(h => { Reveal.slide(h, 0, 0); document.getAnimations().forEach(a => a.finish()); }, h);
  await wait(300);
  await key('ArrowRight', 400);
  await page.setViewportSize({ width: 1280, height: 720 });
  await wait(2000); await check(page, 'resize', 2);
  await page.setViewportSize({ width: 1920, height: 1080 });
  await wait(500);

  // hash jumps straight to each step, in a fresh page
  for (const f of [-1, 0, 1]) {
    const p = await ctx.newPage();
    p.on('pageerror', e => errors.push(String(e)));
    await p.goto(DECK + `#/dv-vector/0/${f}`, { waitUntil: 'load', timeout: 180000 });
    await ready(p); await wait(500);
    await check(p, `hash-${f + 1}`, f + 1, true, p);
    await p.close();
  }

  // inside an iframe
  fs.writeFileSync(path.join(SITE, 'iframe.html'), `<!doctype html><body style="margin:0;background:#888"><iframe src="index.html#/dv-vector" style="width:1200px;height:675px;border:0;margin:40px"></iframe></body>`);
  {
    const p = await ctx.newPage();
    p.on('pageerror', e => errors.push(String(e)));
    await p.goto('file://' + path.join(SITE, 'iframe.html'), { waitUntil: 'load', timeout: 180000 });
    await wait(500);
    const fr = p.frames()[1];
    await ready(fr);
    await fr.evaluate(() => { const i = Reveal.getIndices(document.getElementById('dv-vector')); Reveal.slide(i.h, 0, -1); });
    await wait(400);
    for (const k of [1, 2]) { await fr.evaluate(() => Reveal.next()); await wait(k === 1 ? 1300 : 2000); await check(fr, `iframe-${k}`, k, true, p); }
    await p.close();
  }

  // print view: every fragment state is its own page
  {
    const p = await ctx.newPage();
    p.on('pageerror', e => errors.push(String(e)));
    await p.goto(DECK.replace('index.html', 'index.html?print-pdf') + '#/dv-vector', { waitUntil: 'load', timeout: 180000 });
    await ready(p); await wait(1500);
    const pages = await p.evaluate(() => [...document.querySelectorAll('section#dv-vector, section[id="dv-vector"]')].map((s, i) => {
      const svg = s.querySelector('svg.app-view');
      return { i, visible: s.querySelectorAll('figure .fragment.visible').length, rest: svg ? svg.getAttribute('data-rest') : 'no-svg' };
    }));
    const els = await p.$$('section#dv-vector');
    for (let i = 0; i < els.length; i++) {
      const pg = await els[i].evaluateHandle(e => e.closest('.pdf-page') || e);
      await pg.asElement().screenshot({ path: path.join(OUT, `${NAME}-print-${i}.png`) });
    }
    results.push({ name: 'print', ok: pages.length >= 1 && pages.every(x => x.rest === String(x.visible)), pages });
    await p.close();
  }

  // the report shows the fallback stack's last frame
  {
    const p = await ctx.newPage();
    await p.setViewportSize({ width: 1200, height: 900 });
    await p.goto('file://' + path.join(SITE, 'report.html'), { waitUntil: 'load', timeout: 180000 });
    await wait(800);
    const v = await p.$('#dv-vector .viewport');
    await v.scrollIntoViewIfNeeded();
    await v.screenshot({ path: path.join(OUT, `${NAME}-report.png`) });
    results.push({ name: 'report', ok: !(await p.evaluate(() => !!document.querySelector('#dv-vector svg.app-view'))) });
    await p.close();
  }

  await browser.close();
  const summary = { browser: NAME, version: browser.version ? browser.version() : '', passed: results.filter(r => r.ok).length, of: results.length, errors, results };
  fs.writeFileSync(path.join(OUT, `${NAME}-summary.json`), JSON.stringify(summary, null, 1));
  console.log(`${NAME}: ${summary.passed}/${summary.of} passed, ${errors.length} page errors`);
  results.filter(r => !r.ok).forEach(r => console.log('  FAIL', JSON.stringify(r)));
  errors.slice(0, 5).forEach(e => console.log('  ERR', e.slice(0, 200)));
})().catch(e => { console.error(NAME, 'harness crashed:', e); process.exit(1); });
