import puppeteer from 'puppeteer';
const file = process.argv[2];
const b = await puppeteer.launch({args:['--no-sandbox']});
const p = await b.newPage();
await p.setViewport({width:1920,height:1080,deviceScaleFactor:1});
await p.goto("file://"+file,{waitUntil:'networkidle0'});
await new Promise(r=>setTimeout(r,1500));
async function probe(id){
  await p.evaluate((sid)=>{ const i=[...document.querySelectorAll('section')].findIndex(s=>s.id===sid); window.Reveal.slide(i); }, id);
  await new Promise(r=>setTimeout(r,700));
  return await p.evaluate((sid)=>{
    const sec=document.getElementById(sid);
    const cs=getComputedStyle(sec);
    const r=sec.getBoundingClientRect();
    const kids=[...sec.children].filter(c=>c.getBoundingClientRect().height>0);
    const first=kids[0]?.getBoundingClientRect();
    const last=kids[kids.length-1]?.getBoundingClientRect();
    const img=sec.querySelector('img');
    const ir=img?img.getBoundingClientRect():null;
    return {id:sid, scale:window.Reveal.getScale(), display:cs.display, justify:cs.justifyContent,
      secTop:Math.round(r.top), secH:Math.round(r.height),
      contentTop:first?Math.round(first.top):null, contentBottom:last?Math.round(last.bottom):null,
      imgH:ir?Math.round(ir.height):null, imgBottom:ir?Math.round(ir.bottom):null,
      overflow: last && r.height ? Math.round(last.bottom - (r.top + r.height)) : null};
  }, id);
}
console.log(JSON.stringify(await probe('pitch'),null,1));
console.log(JSON.stringify(await probe('step-memory'),null,1));
await b.close();
