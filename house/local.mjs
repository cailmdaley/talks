#!/usr/bin/env node
// Work on a deck from this machine: build it with its localhost pages live, serve it,
// and rebuild and reload the browser whenever a file of the deck or the house changes.
//
//   node house/local.mjs <deck-dir> [--port 8090]
//
// The deck's deck.json may list what its live pages need under "local":
//   "local": [{ "url": "http://localhost:5318/", "start": "lightcone-demo studio" }]
// Each `start` command runs when its `url` does not answer.

import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const HOUSE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.dirname(HOUSE);
const OUT = path.join(REPO, '_local');
const MIME = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.json': 'application/json', '.css': 'text/css',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.webp': 'image/webp', '.avif': 'image/avif',
  '.mp4': 'video/mp4', '.webm': 'video/webm', '.pdf': 'application/pdf',
};
const RELOAD = `<script>new EventSource('/__reload').onmessage = function () { location.reload(); };</script>`;

const args = process.argv.slice(2);
const pi = args.indexOf('--port');
const port = pi >= 0 ? +args.splice(pi, 2)[1] : 8090;
if (args.length !== 1) { console.error('usage: node house/local.mjs <deck-dir> [--port 8090]'); process.exit(2); }
const deckDir = path.resolve(args[0]);
const name = path.basename(deckDir);

const answers = url => fetch(url).then(() => true, () => false);
for (const { url, start } of JSON.parse(fs.readFileSync(path.join(deckDir, 'deck.json'), 'utf8')).local || []) {
  if (await answers(url)) { console.log(`${url} is up`); continue; }
  console.log(`${url} is down: ${start}`);
  spawn(start, { shell: true, stdio: 'inherit' });
}

const clients = new Set();
let building = false, again = false;
function build() {
  if (building) { again = true; return; }
  building = true;
  const t = Date.now();
  spawn(process.execPath, [path.join(HOUSE, 'build.mjs'), deckDir, '--out', OUT, '--local'], { stdio: ['ignore', 'ignore', 'inherit'] })
    .on('exit', code => {
      building = false;
      console.log(`${new Date().toLocaleTimeString()} ${code ? 'build failed' : `built in ${((Date.now() - t) / 1000).toFixed(1)} s`}`);
      if (!code) for (const res of clients) res.write('data: built\n\n');
      if (again) { again = false; build(); }
    });
}

let timer;
const changed = (_, file) => {
  if (!file || /(^|\/)(_check|__pycache__|\.DS_Store)(\/|$)/.test(file)) return;
  clearTimeout(timer);
  timer = setTimeout(build, 300);
};
fs.watch(deckDir, { recursive: true }, changed);
fs.watch(HOUSE, { recursive: true }, changed);

http.createServer((req, res) => {
  const url = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  if (url === '/__reload') {
    res.writeHead(200, { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-store' });
    res.write('\n');
    clients.add(res);
    req.on('close', () => clients.delete(res));
    return;
  }
  if (url === '/') { res.writeHead(302, { Location: `/${name}/` }).end(); return; }
  let file = path.join(OUT, url);
  if (!file.startsWith(OUT)) { res.writeHead(403).end(); return; }
  if (url.endsWith('/')) file = path.join(file, 'index.html');
  fs.readFile(file, (err, buf) => {
    if (err) { res.writeHead(404).end('not found'); return; }
    const type = MIME[path.extname(file)] || 'application/octet-stream';
    res.writeHead(200, { 'Content-Type': type, 'Cache-Control': 'no-store' });
    res.end(type.startsWith('text/html') ? buf.toString().replace('</body>', RELOAD + '</body>') : buf);
  });
}).on('error', e => { console.error(`port ${port}: ${e.message}`); process.exit(1); })
  .listen(port, '127.0.0.1', () => { console.log(`http://localhost:${port}/${name}/`); build(); });
