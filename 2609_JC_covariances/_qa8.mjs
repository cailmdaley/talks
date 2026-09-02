import puppeteer from 'puppeteer';
const [file, prefix] = process.argv.slice(2);
const b = await puppeteer.launch({args:['--no-sandbox']});
const p = await b.newPage();
p.on('pageerror', e=>console.log('PAGEERROR', e.message));
await p.setViewport({width:1920,height:1080,deviceScaleFactor:1});
await p.goto("file://"+file,{waitUntil:'networkidle0'});
await new Promise(r=>setTimeout(r,1500));
await p.evaluate(()=>Reveal.slide(7,0));
await new Promise(r=>setTimeout(r,600));
for (const v of [0,20,33,70,140]){
  await p.evaluate((v)=>{const i=document.querySelector('section.present input[type=range]'); i.value=v; i.oninput();}, v);
  await new Promise(r=>setTimeout(r,500));
  const out = `${prefix}_thc${v}.png`;
  await p.screenshot({path: out});
  const ov = await p.evaluate(()=>{const sec=document.querySelector('section.present');let w=0,who='';
    sec.querySelectorAll('*').forEach(el=>{if(!el.offsetParent&&el.offsetTop===0)return;const st=getComputedStyle(el);
    if(st.visibility==='hidden'||st.display==='none'||st.opacity==='0')return;let t=0,n=el;
    while(n&&n!==sec){t+=n.offsetTop;n=n.offsetParent;}if(t+el.offsetHeight>w){w=t+el.offsetHeight;who=el.tagName+'.'+el.className;}});
    return {w,who};});
  console.log(out, JSON.stringify(ov));
}
await b.close();
