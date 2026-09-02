import puppeteer from 'puppeteer';
const [file, prefix] = process.argv.slice(2);
const b = await puppeteer.launch({args:['--no-sandbox']});
const p = await b.newPage();
p.on('pageerror', e=>console.log('PAGEERROR', e.message));
await p.setViewport({width:1920,height:1080,deviceScaleFactor:1});
await p.goto("file://"+file,{waitUntil:'networkidle0'});
await new Promise(r=>setTimeout(r,1500));
const ov = async () => p.evaluate(()=>{const sec=document.querySelector('section.present');let w=0,who='';
  sec.querySelectorAll('*').forEach(el=>{if(el.tagName.startsWith('MJX-ASSISTIVE'))return;
  if(!el.offsetParent&&el.offsetTop===0)return;const st=getComputedStyle(el);
  if(st.visibility==='hidden'||st.display==='none'||st.opacity==='0')return;let t=0,n=el;
  while(n&&n!==sec){t+=n.offsetTop;n=n.offsetParent;}if(t+el.offsetHeight>w){w=t+el.offsetHeight;who=el.tagName+'.'+el.className;}});
  // overlap check: cost badge vs every ledger cell
  const cost=sec.querySelector('.cost'); let clash='none';
  if(cost && cost.textContent.trim()){ const c=cost.getBoundingClientRect();
    sec.querySelectorAll('.eqs > div').forEach(d=>{const r=d.getBoundingClientRect();
      if(!(r.right<c.left||r.left>c.right||r.bottom<c.top||r.top>c.bottom)) clash=d.querySelector('.nm').textContent;});}
  return {w,who,clash};});
for (const mi of [0,1,2]) {
  await p.evaluate(i=>{Reveal.slide(6,0); const b=document.querySelectorAll('section.present .pick button'); b[i].click();}, mi);
  for (let f=-1; f<=2; f++){
    await p.evaluate((fr)=>{Reveal.slide(6,0,fr<0?undefined:fr);}, f);
    await new Promise(r=>setTimeout(r,600));
    const out=`${prefix}_m${mi}_f${f<0?'base':f}.png`;
    await p.screenshot({path:out});
    console.log(out, JSON.stringify(await ov()));
  }
}
await b.close();
