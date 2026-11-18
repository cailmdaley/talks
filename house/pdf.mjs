// Backup PDF of a built house deck: one page per slide in its final build state, or with
// --steps one page per build step. Drives _site/<deck>/index.html in puppeteer and assembles
// the screenshots with pymupdf (uv). Usage:
//   node house/pdf.mjs <deck-dir> [--steps] [--only a,b] [--out file.pdf]
// --only takes slide names (deck.json) and keeps their order in the deck.
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { execFileSync } from 'node:child_process';
import puppeteer from 'puppeteer';

const args = process.argv.slice(2);
const deckDir = args.find(a => !a.startsWith('--') && args[args.indexOf(a) - 1] !== '--only' && args[args.indexOf(a) - 1] !== '--out');
const steps = args.includes('--steps');
const only = args.includes('--only') ? args[args.indexOf('--only') + 1].split(',') : null;
const name = path.basename(path.resolve(deckDir));
const out = args.includes('--out') ? args[args.indexOf('--out') + 1] : path.join('_site', name, `${name}${steps ? '-steps' : ''}.pdf`);
const html = path.resolve('_site', name, 'index.html');
if (!fs.existsSync(html)) throw new Error(`build the deck first: node house/build.mjs ${deckDir}`);

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'house-pdf-'));
const browser = await puppeteer.launch({ args: ['--no-sandbox', '--allow-file-access-from-files', '--font-render-hinting=none'] });
const page = await browser.newPage();
await page.setViewport({ width: 1920, height: 1080 });
await page.evaluateOnNewDocument(() => { window.HousePosterOnly = true; });
await page.goto('file://' + html, { waitUntil: 'networkidle0', timeout: 180000 });
await page.waitForFunction(() => window.Reveal && Reveal.isReady());
// every top-level section, backups included (Reveal.getSlides() leaves out uncounted ones)
const slides = await page.evaluate(() => [...document.querySelectorAll('.reveal .slides > section')].map(s => s.getAttribute('data-house-slide') || ''));

const shots = [];
const shoot = async () => {
  await page.evaluate(() => document.getAnimations().forEach(a => a.finish()));
  await new Promise(r => setTimeout(r, 150));
  const f = path.join(tmp, `${String(shots.length).padStart(4, '0')}.png`);
  await page.screenshot({ path: f, captureBeyondViewport: false });
  shots.push(f);
};
for (let i = 0; i < slides.length; i++) {
  if (only && !only.includes(slides[i])) continue;
  if (steps) {
    await page.evaluate(i => Reveal.slide(i, 0, -1), i);
    await shoot();
    while (await page.evaluate(() => Reveal.availableFragments().next)) {
      await page.evaluate(() => Reveal.nextFragment());
      await shoot();
    }
  } else {
    await page.evaluate(i => Reveal.slide(i, 0, 999), i);
    await shoot();
  }
}
await browser.close();

fs.mkdirSync(path.dirname(path.resolve(out)), { recursive: true });
const py = `import sys, pymupdf
doc = pymupdf.open()
for f in sys.argv[2:]:
    pg = doc.new_page(width=1920 * 0.375, height=1080 * 0.375)
    pix = pymupdf.Pixmap(f)
    pg.insert_image(pg.rect, stream=pix.tobytes("jpeg", jpg_quality=88))
doc.save(sys.argv[1], deflate=True)`;
execFileSync('uv', ['run', '-q', '--with', 'pymupdf', 'python', '-c', py, path.resolve(out), ...shots], { stdio: 'inherit' });
fs.rmSync(tmp, { recursive: true });
console.log(`${shots.length} pages → ${out}`);
