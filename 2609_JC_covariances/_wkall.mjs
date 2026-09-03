import { webkit } from 'playwright';
const [file, prefix, idxs, maxF] = process.argv.slice(2);
const b = await webkit.launch(); const p = await b.newPage({viewport:{width:1920,height:1080}});
p.on('pageerror', e=>{ if(!/Config/.test(e.message)) console.log('PAGEERROR', e.message); });
await p.goto('file://'+file,{waitUntil:'load'}); await p.waitForTimeout(2500);
for (const s of idxs.split(',').map(Number)) for (let f=-1; f<=+maxF; f++){
  await p.evaluate(([i,fr])=>Reveal.slide(i,0,fr<0?undefined:fr),[s,f]); await p.waitForTimeout(600);
  const r = await p.evaluate(()=>{
    const sec=document.querySelector('section.present'); const sr=sec.getBoundingClientRect();
    const sc=sr.width/1920;
    let worst=0; const boxes=[];
    sec.querySelectorAll('*').forEach(el=>{
      const st=getComputedStyle(el); if(st.visibility==='hidden'||st.display==='none'||+st.opacity===0) return;
      if(el.closest('.fragment:not(.visible)')) return;
      const r=el.getBoundingClientRect(); if(!r.width||!r.height) return;
      worst=Math.max(worst,(r.bottom-sr.top)/sc);
      // text leaves: elements whose direct text is non-empty, plus mjx-container, img, canvas, svg
      const direct=[...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim());
      if(direct||/^(MJX-CONTAINER|IMG|CANVAS)$/.test(el.tagName)||(el.tagName==='svg'&&!el.closest('mjx-container')))
        boxes.push({t:el.tagName+'.'+(el.className.baseVal??el.className)+':'+(el.textContent||'').trim().slice(0,25),x:r.left,y:r.top,r:r.right,b:r.bottom,el});
    });
    const hits=[];
    for(let i=0;i<boxes.length;i++)for(let j=i+1;j<boxes.length;j++){
      const a=boxes[i],c=boxes[j]; if(a.el.contains(c.el)||c.el.contains(a.el)) continue;
      const ox=Math.min(a.r,c.r)-Math.max(a.x,c.x), oy=Math.min(a.b,c.b)-Math.max(a.y,c.y);
      if(ox>4&&oy>4) hits.push(a.t+' × '+c.t+` (${ox|0}x${oy|0})`);
    }
    return {worst:Math.round(worst),hits:hits.slice(0,6),n:hits.length};
  });
  const out=`${prefix}_s${s}_f${f<0?'base':f}.png`; await p.screenshot({path:out});
  console.log(out, r.worst, r.n?JSON.stringify(r.hits):'');
}
await b.close();
