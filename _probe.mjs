import puppeteer from 'puppeteer';
const b = await puppeteer.launch();
const p = await b.newPage();
await p.setViewport({width:1920,height:1080});
await p.goto(process.argv[2],{waitUntil:'networkidle0'});
await new Promise(r=>setTimeout(r,1200));
await p.evaluate(()=>{ Reveal.slide(1); });
await new Promise(r=>setTimeout(r,500));
for(let i=0;i<5;i++){ await p.evaluate(()=>{ Reveal.next(); }); await new Promise(r=>setTimeout(r,200)); }
const info = await p.evaluate(()=>{
  const li = document.querySelectorAll('#why-cant-we-do-astronomy-here li');
  return Array.from(li).map(e=>({t:e.textContent, vis:getComputedStyle(e).visibility, disp:getComputedStyle(e).display, op:getComputedStyle(e).opacity, classes:e.className}));
});
console.log(JSON.stringify(info,null,2));
await p.screenshot({path:'/tmp/aot_shots/paris_probe.png'});
await b.close();
