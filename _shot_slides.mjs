import puppeteer from 'puppeteer';
// usage: node shot_slides.mjs <htmlfile> <outprefix> <slideIndexCSV>
const file = process.argv[2];
const outprefix = process.argv[3];
const slides = (process.argv[4] ?? "0").split(",").map(s=>parseInt(s));
const url = "file://" + file;
const b = await puppeteer.launch({args:['--no-sandbox']});
const p = await b.newPage();
await p.setViewport({width:1920,height:1080,deviceScaleFactor:1});
await p.goto(url,{waitUntil:'networkidle0'});
await new Promise(r=>setTimeout(r,1200));
for (const n of slides){
  await p.evaluate((i)=>{ window.Reveal && window.Reveal.slide(i); }, n);
  await new Promise(r=>setTimeout(r,900));
  const out = `${outprefix}_s${n}.png`;
  await p.screenshot({path: out});
  console.log("wrote", out);
}
await b.close();
