import puppeteer from 'puppeteer';
const file = process.argv[2];
const b = await puppeteer.launch({args:['--no-sandbox']});
const p = await b.newPage();
await p.setViewport({width:1920,height:1080,deviceScaleFactor:1});
await p.goto("file://"+file,{waitUntil:'networkidle0'});
await new Promise(r=>setTimeout(r,1000));
const info = await p.evaluate(()=>{
  const sec = document.querySelector('.reveal .slides section');
  const bar = document.querySelector('.logo-bar');
  const cnrs = document.querySelector('.logo-cnrs');
  const r = el => el ? (()=>{const b=el.getBoundingClientRect();return {x:Math.round(b.x),y:Math.round(b.y),w:Math.round(b.width),h:Math.round(b.height),bottom:Math.round(b.bottom)};})() : null;
  const cs = el => el ? getComputedStyle(el) : null;
  return {
    secId: sec?.id,
    secRect: r(sec),
    secHeight: cs(sec)?.height,
    secPosition: cs(sec)?.position,
    barRect: r(bar),
    barPosition: cs(bar)?.position,
    barBottom: cs(bar)?.bottom,
    cnrsRect: r(cnrs),
    cnrsHeight: cs(cnrs)?.height,
    viewport: {w: window.innerWidth, h: window.innerHeight}
  };
});
console.log(JSON.stringify(info,null,2));
await b.close();
