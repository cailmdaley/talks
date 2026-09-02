import puppeteer from 'puppeteer';
const b = await puppeteer.launch();
const p = await b.newPage();
await p.setViewport({width:1920,height:1080});
await p.goto(process.argv[2],{waitUntil:'networkidle0'});
await new Promise(r=>setTimeout(r,1000));
await p.evaluate(s=>{ Reveal.slide(s); }, parseInt(process.argv[4]));
await new Promise(r=>setTimeout(r,400));
const frags = parseInt(process.argv[5]||0);
for(let i=0;i<frags;i++){ await p.evaluate(()=>{ Reveal.nextFragment(); }); await new Promise(r=>setTimeout(r,200)); }
await new Promise(r=>setTimeout(r,400));
await p.screenshot({path:process.argv[3]});
await b.close();
