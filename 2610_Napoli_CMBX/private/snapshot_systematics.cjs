// Static frames of the systematics-triangle slide, for its fallback stack (the report, a
// render without JS): the live SVG at each rest state, on white at twice the
// displayed size. White multiplies into any theme's ground, and an opaque frame
// hides the one under it, as a stack needs. The click hint and the toggles are
// left out: the frames do not respond to clicks.
//
//   node house/build.mjs 2610_Napoli_CMBX --out /tmp/site
//   node 2610_Napoli_CMBX/private/snapshot_systematics.cjs /tmp/site/2610_Napoli_CMBX/index.html
//   node house/build.mjs 2610_Napoli_CMBX                  # again, with the new frames
const path = require('path');
const TALKS = path.resolve(__dirname, '..', '..');
const puppeteer = require(require.resolve('puppeteer', { paths: [TALKS] }));
const deck = path.resolve(process.argv[2]);
(async () => {
  const b = await puppeteer.launch({ args: ['--no-sandbox', '--allow-file-access-from-files', '--font-render-hinting=none'] });
  const p = await b.newPage();
  await p.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 2 });
  await p.goto('file://' + deck + '#/systematics-triangle', { waitUntil: 'load' });
  await p.evaluate(async () => { await document.fonts.ready; await new Promise(r => Reveal.isReady() ? r() : Reveal.on('ready', r)); });
  await p.addStyleTag({ content: 'html, body, .reveal, .reveal .slides, .reveal section, .slide { background: #FFFFFF !important; } .slide > .variants, .app-choice { display: none !important; }' });
  for (let k = 0; k < 3; k++) {
    await p.evaluate(k => {
      const i = Reveal.getIndices(document.getElementById("systematics-triangle"));
      Reveal.slide(i.h, 0, k - 1);
      document.getAnimations().forEach(a => a.finish());
    }, k);
    await new Promise(r => setTimeout(r, 300));
    const svg = await p.$('#systematics-triangle svg.app-view');
    const out = path.join(__dirname, `systematics_${k + 1}.png`);
    await svg.screenshot({ path: out });
    console.log('wrote', out);
  }
  await b.close();
})();
