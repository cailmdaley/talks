import puppeteer from 'puppeteer';
// usage: node _mmove.mjs <html> <slideIdx> <maxFrag>
const [file, si, mf] = [process.argv[2], +(process.argv[3]||16), +(process.argv[4]||2)];
const b = await puppeteer.launch({args:['--no-sandbox']});
const p = await b.newPage();
p.on('pageerror', e=>console.log('PAGEERROR', e.message));
await p.setViewport({width:1920,height:1080});
await p.goto("file://"+file,{waitUntil:'networkidle0'});
await new Promise(r=>setTimeout(r,1600));
const geom = async ()=>p.evaluate(()=>{
  const sec=document.querySelector('section.present'); const out=[];
  sec.querySelectorAll('div,svg,img,canvas').forEach(el=>{
    const r=el.getBoundingClientRect();
    out.push(el.className.toString().replace(/ ?(visible|current-fragment|fragment|fade-in|fade-out)/g,'')+':'+
      [r.x,r.y,r.width,r.height].map(v=>Math.round(v)).join(','));
  });
  return out.join('|');
});
const sig=[];
for(let f=-1; f<=mf; f++){
  await p.evaluate((a,c)=>Reveal.slide(a,0,c<0?undefined:c), si, f);
  await new Promise(r=>setTimeout(r,800));
  sig.push(await geom());
}
console.log('slide',si,'MOTION', sig.every(s=>s===sig[0]) ? 'none' : 'MOVED');
if(!sig.every(s=>s===sig[0])){
  const a=sig[0].split('|'), z=sig[sig.length-1].split('|');
  a.forEach((v,i)=>{ if(v!==z[i]) console.log('  ',v,' -> ',z[i]); });
}
await b.close();
