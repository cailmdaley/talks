import puppeteer from 'puppeteer';
const b = await puppeteer.launch({args:['--no-sandbox','--autoplay-policy=no-user-gesture-required']});
const p = await b.newPage();
await p.setViewport({width:1920,height:1080});
p.on('console', msg => console.log('BROWSER:', msg.type(), msg.text()));
p.on('pageerror', err => console.log('PAGEERR:', err.message));
await p.goto(process.argv[2], {waitUntil: 'networkidle0'});
await new Promise(r => setTimeout(r, 1500));
await p.evaluate(s => Reveal.slide(s), parseInt(process.argv[3]));
await new Promise(r => setTimeout(r, 1500));
const info = await p.evaluate(() => {
  const v = document.querySelector('video.obs-video');
  if (!v) return {found: false};
  const r = v.getBoundingClientRect();
  const cs = getComputedStyle(v);
  return {
    found: true,
    src: v.getAttribute('src'),
    rect: {x:Math.round(r.x), y:Math.round(r.y), w:Math.round(r.width), h:Math.round(r.height)},
    readyState: v.readyState,
    paused: v.paused,
    muted: v.muted,
    error: v.error ? v.error.code : null,
    naturalW: v.videoWidth,
    naturalH: v.videoHeight,
    display: cs.display, visibility: cs.visibility, opacity: cs.opacity,
    width: cs.width, height: cs.height, maxW: cs.maxWidth, maxH: cs.maxHeight,
    currentTime: v.currentTime,
  };
});
console.log(JSON.stringify(info, null, 2));
await b.close();
