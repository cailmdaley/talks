import puppeteer from 'puppeteer';
const url = process.argv[2];
const outDir = process.argv[3];
const tag = process.argv[4] || 's';
const b = await puppeteer.launch();
const p = await b.newPage();
await p.setViewport({width:1920,height:1080,deviceScaleFactor:1});
await p.goto(url,{waitUntil:'networkidle0'});
await new Promise(r=>setTimeout(r,1200));
const n = await p.evaluate(()=> window.Reveal.getTotalSlides());
console.log('total slides', n);
for(let i=0;i<n;i++){
  await p.evaluate((idx)=>{ window.Reveal.slide(idx); }, i);
  await new Promise(r=>setTimeout(r,650));
  // detect vertical overflow on the current slide
  const overflow = await p.evaluate(()=>{
    const s = document.querySelector('.reveal .slides section.present');
    if(!s) return null;
    return { id: s.id||'', scrollH: s.scrollHeight, clientH: s.clientHeight,
             over: s.scrollHeight - s.clientHeight };
  });
  await p.screenshot({path:`${outDir}/${tag}_${String(i).padStart(2,'0')}.png`});
  if(overflow && overflow.over > 4) console.log(`  OVERFLOW slide ${i} (#${overflow.id}): +${overflow.over}px`);
}
await b.close();
console.log('done', tag);
