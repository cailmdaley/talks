import puppeteer from 'puppeteer';
// usage: node _qa.mjs <html> <outdir/prefix> <slideIdx> [maxFrags]
const [file, prefix, idxs, maxF] = process.argv.slice(2);
const b = await puppeteer.launch({args:['--no-sandbox']});
const p = await b.newPage();
p.on('pageerror', e=>console.log('PAGEERROR', e.message));
p.on('console', m=>{ const t=m.text(); if(/error|Error/.test(t)) console.log('CONSOLE', t); });
await p.setViewport({width:1920,height:1080,deviceScaleFactor:1});
await p.goto("file://"+file,{waitUntil:'networkidle0'});
await new Promise(r=>setTimeout(r,1500));
const nf = parseInt(maxF ?? "0");
for (const s of idxs.split(",").map(Number)){
  for (let f=-1; f<=nf; f++){
    await p.evaluate((i,fr)=>{ Reveal.slide(i,0,fr<0?undefined:fr); }, s, f);
    await new Promise(r=>setTimeout(r,700));
    const out = `${prefix}_s${s}_f${f<0?'base':f}.png`;
    await p.screenshot({path: out});
    // overflow in SLIDE coordinates
    const ov = await p.evaluate(()=>{
      const sec = document.querySelector('section.present'); if(!sec) return null;
      let worst = 0, who='';
      sec.querySelectorAll('*').forEach(el=>{
        if(!el.offsetParent && el.offsetTop===0) return;
        const st=getComputedStyle(el); if(st.visibility==='hidden'||st.display==='none'||st.opacity==='0') return;
        let t=0, n=el;
        while(n && n!==sec){ t += n.offsetTop; n = n.offsetParent; }
        const bot = t + el.offsetHeight;
        if(bot>worst){ worst=bot; who=el.tagName+'.'+el.className; }
      });
      return {worst, who};
    });
    console.log(out, JSON.stringify(ov));
  }
}
await b.close();
