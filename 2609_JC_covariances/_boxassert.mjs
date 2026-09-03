// Assert, on EVERY slide and EVERY fragment state, that no ledger box is
// narrower than the equation painted inside it. Engine passed as argv[3].
const eng = process.argv[3] || 'chromium';
let launch, mk;
if (eng === 'webkit') { const {webkit}=await import('playwright'); launch = ()=>webkit.launch();
  mk = async b => b.newPage({viewport:{width:1920,height:1080}}); }
else { const pp=(await import('puppeteer')).default; launch = ()=>pp.launch({args:['--no-sandbox']});
  mk = async b => { const p=await b.newPage(); await p.setViewport({width:1920,height:1080}); return p; }; }
const b = await launch(); const p = await mk(b);
await p.goto('file://'+process.argv[2], {waitUntil:'load'});
await new Promise(r=>setTimeout(r,3000));
const n = await p.evaluate(()=>Reveal.getTotalSlides());
let bad = [];
for (let i=0;i<n;i++){
  for (const f of [-1,0,1,2,3,4,5,6]){
    await p.evaluate(([a,c])=>Reveal.slide(a,0,c<0?undefined:c), [i,f]);
    await new Promise(r=>setTimeout(r,120));
    const r = await p.evaluate(()=>{
      const out=[];
      document.querySelectorAll('section.present .mbox, section.present .corr > div, section.present .eqs > div').forEach(box=>{
        const br=box.getBoundingClientRect();
        box.querySelectorAll('.eq').forEach(e=>{
          const er=e.getBoundingClientRect();
          if(!er.width) return;
          const over = er.right - (br.right - parseFloat(getComputedStyle(box).paddingRight||0));
          if(over > 2) out.push(box.className.split(' ')[0]+':'+Math.round(over));
        });
      });
      return out;
    });
    if(r.length) bad.push(`slide ${i} frag ${f}: overflow ${r.join(',')} px`);
  }
}
console.log(eng.toUpperCase(), bad.length ? 'FAIL\n'+[...new Set(bad)].slice(0,10).join('\n') : 'PASS — no box narrower than its equation');
await b.close();
