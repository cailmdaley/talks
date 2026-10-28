// Static frames of a dv-vector slide (fallback stack): the live SVG at each rest
// state, on white at twice the displayed size, cut from a page screenshot clipped
// to the svg.app-view box (element screenshots grab the wrong region on the
// cineca headless shell).
//
//   node house/build.mjs 2610_SPT_CMBX --out $TMPDIR/site
//   node 2610_Napoli_CMBX/private/snapshot_dv_vector_clip.cjs $TMPDIR/site/2610_SPT_CMBX/index.html dv_vector_spt
const path = require('path');
const TALKS = path.resolve(__dirname, '..', '..');
const puppeteer = require(require.resolve('puppeteer', { paths: [TALKS] }));
const deck = path.resolve(process.argv[2]);
const stem = process.argv[3] || 'dv_vector';
(async () => {
  const b = await puppeteer.launch({ args: ['--no-sandbox', '--allow-file-access-from-files', '--font-render-hinting=none'] });
  const p = await b.newPage();
  await p.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 2 });
  await p.goto('file://' + deck + '#/dv-vector', { waitUntil: 'load', timeout: 180000 });
  await p.evaluate(async () => { await document.fonts.ready; await new Promise(r => Reveal.isReady() ? r() : Reveal.on('ready', r)); });
  await p.waitForSelector('figure.app-live svg.app-view', { timeout: 120000 });
  await p.addStyleTag({ content: 'html, body, .reveal, .reveal .slides, .reveal section, .slide { background: #FFFFFF !important; } .slide > .variants { display: none !important; }' });
  for (let k = 0; k < 3; k++) {
    await p.evaluate(k => {
      const i = Reveal.getIndices(document.getElementById('dv-vector'));
      Reveal.slide(i.h, 0, k - 1);
      document.getAnimations().forEach(a => a.finish());
    }, k);
    await new Promise(r => setTimeout(r, 1200));
    const box = await p.evaluate(() => {
      const r = document.querySelector('#dv-vector figure.app-live svg.app-view').getBoundingClientRect();
      return { x: r.x, y: r.y, width: r.width, height: r.height };
    });
    const out = path.join(__dirname, `${stem}_${k + 1}.png`);
    await p.screenshot({ path: out, clip: box });
    console.log('wrote', out, JSON.stringify(box));
  }
  await b.close();
})();
