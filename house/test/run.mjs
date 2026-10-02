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
};

let fail = 0;
const ok = (cond, msg) => { console.log(`${cond ? '✓' : '✗'} ${msg}`); if (!cond) fail++; };

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

const missing = run(path.join(HERE, 'missing'));
ok(missing.status === 1 && missing.stderr.includes('missing image images/does_not_exist.png'), 'missing image fails the build');

console.log(fail ? `\n${fail} failed` : '\nall passed');
process.exit(fail ? 1 : 0);
