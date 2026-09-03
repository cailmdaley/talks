import { webkit } from 'playwright';
// usage: node _wk.mjs <html> <prefix> <slideIdx,...> [frag]
const [file, prefix, idxs, fr] = process.argv.slice(2);
const b = await webkit.launch();
const p = await b.newPage({viewport:{width:1920,height:1080}});
p.on('pageerror', e=>console.log('PAGEERROR', e.message));
await p.goto('file://'+file, {waitUntil:'load'});
await p.waitForTimeout(2500);
for (const s of idxs.split(',').map(Number)) {
  await p.evaluate(([i,f])=>Reveal.slide(i,0,f<0?undefined:f), [s, fr===undefined?-1:+fr]);
  await p.waitForTimeout(900);
  const out = `${prefix}_s${s}.png`;
  await p.screenshot({path: out});
  // measure every ledger box against the equation inside it
  const m = await p.evaluate(()=>{
    const o=[];
    document.querySelectorAll('section.present .mbox, section.present .corr.big > div').forEach(el=>{
      const br=el.getBoundingClientRect();
      let w=0;
      el.querySelectorAll('.eq').forEach(e=>{
        const r=e.getBoundingClientRect(); w=Math.max(w, r.right-br.left);
      });
      o.push({box:Math.round(br.width), needs:Math.round(w),
              over:Math.round(w-br.width)});
    });
    return o;
  });
  console.log(out, JSON.stringify(m));
}
await b.close();
