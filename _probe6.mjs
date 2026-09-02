import puppeteer from 'puppeteer';
const b = await puppeteer.launch();
const p = await b.newPage();
await p.setViewport({width:1920,height:1080});
await p.goto(process.argv[2],{waitUntil:'networkidle0'});
await new Promise(r=>setTimeout(r,1000));
await p.evaluate(()=>{ Reveal.slide(3); });
await new Promise(r=>setTimeout(r,500));
const info = await p.evaluate(()=>{
  const wrap = document.querySelector('.sky-plot-wrap');
  const img = document.querySelector('.opacity-plot');
  const box = document.querySelector('.cmb-box');
  const d = el => { const r = el.getBoundingClientRect(); return {x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height)}; };
  return {wrap: d(wrap), img: d(img), box: d(box)};
});
console.log(JSON.stringify(info, null, 2));
await b.close();
