// Compare a deck built with baked media against the same deck with its filters live, slide by slide.
// node house/test/bake-compare.mjs <live index.html> <baked index.html> <out dir>
import puppeteer from 'puppeteer';
import sharp from 'sharp';
import fs from 'node:fs';
const [live, baked, out] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
const b = await puppeteer.launch({ headless: 'shell', args: ['--allow-file-access-from-files'] });
const shots = {};
let ids;
for (const [name, file] of [['baked', baked], ['live', live]]) {
  const p = await b.newPage(); await p.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
  await p.evaluateOnNewDocument(() => { window.HousePosterOnly = true; });
  await p.goto('file://' + file, { waitUntil: 'load', timeout: 120000 });
  await p.evaluate(async () => { await document.fonts.ready; });
  await p.addStyleTag({ content: '*, *::before, *::after { animation: none !important; transition: none !important; } .fragment { opacity: 1 !important; visibility: visible !important; }' });
  ids ||= await p.evaluate(() => [...document.querySelectorAll('section:has(image[data-asset])')].map(s => s.id));
  for (const id of ids) {
    await p.evaluate((id) => { const i = Reveal.getIndices(document.getElementById(id)); Reveal.slide(i.h, i.v); }, id);
    await new Promise(r => setTimeout(r, 400));
    (shots[id] ||= {})[name] = await p.screenshot();
  }
  await p.close();
}
await b.close();
for (const id of ids) {
  const [A, B] = await Promise.all(['live', 'baked'].map(n => sharp(shots[id][n]).removeAlpha().raw().toBuffer()));
  let sum = 0, big = 0;
  for (let k = 0; k < A.length; k++) { const d = Math.abs(A[k] - B[k]); sum += d; if (d > 24) big++; }
  console.log(id.padEnd(22), 'mean |Δ|', (sum / A.length).toFixed(3), ' values off by > 24:', big);
  fs.writeFileSync(`${out}/${id}-live.png`, shots[id].live); fs.writeFileSync(`${out}/${id}-baked.png`, shots[id].baked);
}
