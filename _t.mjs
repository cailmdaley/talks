import puppeteer from 'puppeteer';
const b=await puppeteer.launch(); const p=await b.newPage();
p.on('pageerror',e=>{if(!/Config/.test(e.message))console.log('PAGEERR',e.message);});
p.on('console',m=>{if(m.type()==='error')console.log('CONSOLE',m.text().slice(0,200));});
await p.setViewport({width:1920,height:1080});
await p.goto(process.argv[2],{waitUntil:'networkidle0'});
await new Promise(r=>setTimeout(r,3000));
await p.evaluate(()=>window.Reveal.slide(1));
await new Promise(r=>setTimeout(r,2000));
for(let i=0;i<8;i++){
  const st=await p.evaluate(()=>({cap:document.getElementById('nka-cap').textContent,
    f:Reveal.getIndices().f,
    eqs:[0,1,2,3,4,5,6].map(i=>{const e=document.getElementById('eq'+i);
      return e.style.display==='none'?'-':(e.className==='on'?'ON':'dim');}).join('')}));
  console.log(i,'f='+st.f, st.eqs, '|', st.cap);
  if(i<7){ await p.keyboard.press('ArrowRight'); await new Promise(r=>setTimeout(r,800)); }
}
// decoupling sanity: does M^-1 Ctil land on C?
const dec = await p.evaluate(()=>{
  // read the drawn teal dots vs the true curve is hard; instead recompute via the page's DOM
  const dots=document.querySelectorAll('#svgB circle');
  return dots.length;
});
console.log('decoupled dots drawn at step 7 view:', dec);
// kernel drag + vary readout at two locations
for (const k of [30, 78]) {
  const r = await p.evaluate((kk)=>{
    const svg=document.getElementById('svgC'); const rect=svg.getBoundingClientRect();
    const x = rect.left + rect.width*(kk-1)/(250-1);
    svg.dispatchEvent(new PointerEvent('pointerdown',{clientX:x,clientY:rect.top+40,bubbles:true,pointerId:1}));
    svg.dispatchEvent(new PointerEvent('pointerup',{bubbles:true,pointerId:1}));
    return null;
  }, k);
  await new Promise(r=>setTimeout(r,500));
  const t = await p.evaluate(()=>Array.from(document.querySelectorAll('#svgC text')).map(t=>t.textContent).join(' || '));
  console.log('k0='+k, '->', t);
}
await b.close();
