// The star chart on the lightcone-research slide: the planisphere of Bayer's Uranometria (1603),
// as on the Lightcone Research homepage, cut out of its plate so that only the engraving is left:
// the image is the ink alone, in the deck's graphite, transparent wherever the plate is paper and
// outside the chart's outer circle. It is kept as the slide shows it, a disc that rises from the
// footer's rule and leaves the slide at its right edge, at twice its size on the slide; the
// script prints the box (data-at) the slide gives it.
//   node 2611_ICE_Barcelona/make_plate.mjs
import path from 'node:path'; import { fileURLToPath } from 'node:url';
import sharp from 'sharp';
const IMG = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'images');
const C = [1000, 807], R = 662, size = 2 * R;       // the chart's centre and outer radius in the plate, pixels
const AT = { cx: 1660, cy: 930, r: 380, foot: 988 };   // the disc on the slide, and where the rule cuts it
const box = { x: AT.cx - AT.r, y: AT.cy - AT.r, w: 1920 - (AT.cx - AT.r), h: AT.foot - (AT.cy - AT.r) };
const W = box.w * 2, H = box.h * 2, D = AT.r * 4, INK = [0x39, 0x34, 0x2E];
const grey = await sharp(path.join(IMG, 'lightcone_uranometria.webp')).flatten({ background: '#fff' })
  .extract({ left: C[0] - R, top: C[1] - R, width: size, height: size }).greyscale().linear(1.5, -85).resize(D).extract({ left: 0, top: 0, width: W, height: H }).toColourspace('b-w').raw().toBuffer();
// the disc, its last few pixels above the rule fading out
const disc = await sharp(Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}"><defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="${1 - 22 / H}" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>
  <mask id="m"><rect width="${W}" height="${H}" fill="url(#g)"/></mask></defs><rect width="${W}" height="${H}" fill="#000"/><circle cx="${D / 2}" cy="${D / 2}" r="${D / 2 - 4}" fill="#fff" mask="url(#m)"/></svg>`)).blur(1.5).extractChannel(0).raw().toBuffer();
const out = Buffer.alloc(W * H * 4);
for (let i = 0; i < W * H; i++) { out.set(INK, 4 * i); out[4 * i + 3] = Math.round((255 - grey[i]) * disc[i] / 255); }
await sharp(out, { raw: { width: W, height: H, channels: 4 } }).webp({ quality: 86, alphaQuality: 90 }).toFile(path.join(IMG, 'lightcone_planisphere.webp'));
console.log(`data-at="${box.x} ${box.y} ${box.w} ${box.h}"`);
// the lc banner: its near-white ground lifted to white, so that multiplied into the paper it leaves no box
const banner = path.join(IMG, 'lightcone_cli_banner.png');
await sharp(await sharp(banner).removeAlpha().linear(1.03, 0).png().toBuffer()).toFile(banner);
