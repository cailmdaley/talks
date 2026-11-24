// film a slide of the built deck by stepping its animations: node _film.mjs <index.html> <slide> <frames-dir> <seconds> [fps]
import fs from 'node:fs'; import puppeteer from 'puppeteer';
const [,, file, hash, dir, secs, fps = 15] = process.argv;
fs.mkdirSync(dir, { recursive: true });
const b = await puppeteer.launch();
const p = await b.newPage(); await p.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 2 / 3 });
await p.goto('file://' + file + '#/' + hash, { waitUntil: 'networkidle0' });
await new Promise(r => setTimeout(r, 1500));
const n = await p.evaluate(() => { const a = document.getAnimations(); a.forEach(x => x.pause()); return a.length; });
console.log(n, 'animations');
for (let i = 0; i < secs * fps; i++) {
  await p.evaluate((t) => document.getAnimations().forEach(x => { x.currentTime = t; }), i * 1000 / fps);
  await p.screenshot({ path: `${dir}/f${String(i).padStart(4, '0')}.jpg`, quality: 88 });
}
await b.close();
