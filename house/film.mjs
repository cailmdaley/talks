#!/usr/bin/env node
// Film one slide of a deck, for looking at a drawing that moves without opening a browser:
// builds the deck, steps the slide's CSS animations frame by frame, and writes an MP4.
//
//   node house/film.mjs <deck-dir> <slide> [--seconds 36] [--fps 15] [--out slide.mp4]
//
// Needs ffmpeg. Frames are 1280×720.

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import puppeteer from 'puppeteer';

const HOUSE = path.dirname(fileURLToPath(import.meta.url));
const argv = process.argv.slice(2);
const flag = (n, d) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : d; };
const [deck, slide] = argv.filter((a, i) => !a.startsWith('--') && !argv[i - 1]?.startsWith('--'));
if (!deck || !slide) { console.error('usage: node house/film.mjs <deck-dir> <slide> [--seconds 36] [--fps 15] [--out slide.mp4]'); process.exit(2); }
const seconds = Number(flag('--seconds', 36)), fps = Number(flag('--fps', 15)), out = path.resolve(flag('--out', `${slide}.mp4`));

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'house-film-'));
execFileSync('node', [path.join(HOUSE, 'build.mjs'), deck, '--out', tmp], { stdio: 'ignore' });
const browser = await puppeteer.launch();
const page = await browser.newPage();
await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 2 / 3 });
await page.goto(`file://${path.join(tmp, path.basename(path.resolve(deck)), 'index.html')}#/${slide}`, { waitUntil: 'networkidle0' });
await new Promise(r => setTimeout(r, 1500));
const moving = await page.evaluate(() => { const a = document.getAnimations(); a.forEach(x => x.pause()); return a.length; });
for (let i = 0; i < seconds * fps; i++) {
  await page.evaluate(t => document.getAnimations().forEach(x => { x.currentTime = t; }), i * 1000 / fps);
  await page.screenshot({ path: path.join(tmp, `f${String(i).padStart(5, '0')}.jpg`), quality: 88 });
}
await browser.close();
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(fps), '-i', path.join(tmp, 'f%05d.jpg'), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '19', out]);
fs.rmSync(tmp, { recursive: true, force: true });
console.log(`${out}: ${seconds} s of ${slide}, ${moving} animation${moving === 1 ? '' : 's'}`);
