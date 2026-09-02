import puppeteer from 'puppeteer';
const b = await puppeteer.launch({args:['--no-sandbox']});
const p = await b.newPage();
p.on('pageerror', e=>console.log('PAGEERROR', e.message));
await p.setViewport({width:1920,height:1080});
await p.goto("file://"+process.argv[2],{waitUntil:'networkidle0'});
await new Promise(r=>setTimeout(r,1600));
const geom = async ()=>p.evaluate(()=>{
  const sec=document.querySelector('section.present');
  const out=[];
  sec.querySelectorAll('.mrow2, .mhead, .mpix, .mtxt, .amat, .agrid, .corr').forEach(el=>{
    const r=el.getBoundingClientRect();
    out.push(el.className.replace(/ (visible|current-fragment|fragment)/g,'')+':'+
      [r.x,r.y,r.width,r.height].map(v=>Math.round(v)).join(','));
  });
  return out.join('|');
});
const sig=[];
for(const fr of [-1,0,1,2]){
  await p.evaluate(f=>Reveal.slide(16,0,f<0?undefined:f), fr);
  await new Promise(r=>setTimeout(r,800));
  sig.push(await geom());
  await p.screenshot({path:`screenshots/s17_${fr<0?'base':fr}.png`});
}
console.log('MOTION', sig.every(s=>s===sig[0]) ? 'none' : 'MOVED');
console.log(sig[3].split('|').join('\n'));
await p.evaluate(()=>Reveal.slide(15,0));
await new Promise(r=>setTimeout(r,900));
await p.screenshot({path:'screenshots/s16A.png'});
console.log('A', await geom());
await b.close();
