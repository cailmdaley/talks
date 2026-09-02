import puppeteer from 'puppeteer';
const url = process.argv[2];
const b = await puppeteer.launch();
const p = await b.newPage();
await p.setViewport({width:1920,height:1080,deviceScaleFactor:1});
await p.goto(url,{waitUntil:'networkidle0'});
await new Promise(r=>setTimeout(r,1200));
// go to #proof (index 7)
await p.evaluate(()=>{ window.Reveal.slide(7); });
await new Promise(r=>setTimeout(r,500));
const info = await p.evaluate(()=>{
  const s = document.querySelector('.reveal .slides section.present');
  const img = s.querySelector('img');
  if(!img) return {err:'no img'};
  const r = img.getBoundingClientRect();
  return { id:s.id, natW: img.naturalWidth, natH: img.naturalHeight,
           renderW: Math.round(r.width), renderH: Math.round(r.height),
           left: Math.round(r.left), right: Math.round(r.right) };
});
console.log('PROOF flywheel:', JSON.stringify(info));
// also check shear-hook svg (index 17) and disagreement img (index 24)
for(const [idx,label] of [[17,'shear-hook'],[10,'step-memory'],[24,'disagreement']]){
  await p.evaluate((i)=>{ window.Reveal.slide(i); }, idx);
  await new Promise(r=>setTimeout(r,400));
  const x = await p.evaluate(()=>{
    const s = document.querySelector('.reveal .slides section.present');
    const el = s.querySelector('img, svg');
    if(!el) return {err:'none'};
    const r = el.getBoundingClientRect();
    return { tag: el.tagName, renderW: Math.round(r.width), renderH: Math.round(r.height) };
  });
  console.log(`${label}:`, JSON.stringify(x));
}
await b.close();
