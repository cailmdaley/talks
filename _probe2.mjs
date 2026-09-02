import puppeteer from 'puppeteer';
const b = await puppeteer.launch();
const p = await b.newPage();
await p.setViewport({width:1920,height:1080});
await p.goto(process.argv[2],{waitUntil:'networkidle0'});
await new Promise(r=>setTimeout(r,1000));
await p.evaluate(()=>{ Reveal.slide(1); });
await new Promise(r=>setTimeout(r,400));
for(let i=0;i<3;i++){ await p.evaluate(()=>{ Reveal.nextFragment(); }); await new Promise(r=>setTimeout(r,150)); }
const info = await p.evaluate(()=>{
  const col = document.querySelector('#why-cant-we-do-astronomy-here .column:nth-child(2)');
  const ul = document.querySelector('#why-cant-we-do-astronomy-here ul');
  const colR = col.getBoundingClientRect();
  const ulR = ul.getBoundingClientRect();
  const cs = getComputedStyle(col);
  const section = col.closest('section');
  const sR = section.getBoundingClientRect();
  return {colRect:colR, ulRect:ulR, colHeight:cs.height, colDisplay:cs.display, sectionRect:sR};
});
console.log(JSON.stringify(info,null,2));
await b.close();
