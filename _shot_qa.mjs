import puppeteer from 'puppeteer';
const url = process.argv[2];
const outDir = process.argv[3];
const indices = process.argv[4].split(',').map(Number); // 0-based slide indices
const b = await puppeteer.launch();
const p = await b.newPage();
await p.setViewport({width:1920,height:1080,deviceScaleFactor:1});
await p.goto(url,{waitUntil:'networkidle0'});
await new Promise(r=>setTimeout(r,1000));
for(const idx of indices){
  await p.evaluate((i)=>{ window.Reveal.slide(i); }, idx);
  await new Promise(r=>setTimeout(r,700));
  await p.screenshot({path:`${outDir}/slide_${String(idx).padStart(2,'0')}.png`});
}
await b.close();
console.log('done', indices.join(','));
