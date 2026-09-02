import puppeteer from 'puppeteer';
const b = await puppeteer.launch();
const p = await b.newPage();
await p.setViewport({width:1920,height:1080});
await p.goto(process.argv[2],{waitUntil:'networkidle0'});
await new Promise(r=>setTimeout(r,1000));
await p.evaluate(s=>{ Reveal.slide(s); }, parseInt(process.argv[3]));
await new Promise(r=>setTimeout(r,500));
const info = await p.evaluate(()=>{
  const img = document.querySelector('.mcmurdo-img');
  const r = img.getBoundingClientRect();
  const cs = getComputedStyle(img);
  return {rect:{x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height)}, h:cs.height, w:cs.width, maxH:cs.maxHeight, maxW:cs.maxWidth};
});
console.log(JSON.stringify(info,null,2));
await b.close();
