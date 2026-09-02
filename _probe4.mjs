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
  const cols = document.querySelector('#why-cant-we-do-astronomy-here .columns');
  const col1 = cols.children[0], col2 = cols.children[1];
  const cs = n=>{const s=getComputedStyle(n); return {display:s.display, flexDirection:s.flexDirection, alignItems:s.alignItems, width:s.width, height:s.height};};
  function dims(el){ const r=el.getBoundingClientRect(); return {x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height)};}
  return {colsStyle: cs(cols), colsRect: dims(cols), col1Style: cs(col1), col1Rect: dims(col1), col2Style: cs(col2), col2Rect: dims(col2)};
});
console.log(JSON.stringify(info,null,2));
await b.close();
