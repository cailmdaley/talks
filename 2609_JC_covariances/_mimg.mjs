import puppeteer from 'puppeteer';
const b = await puppeteer.launch({args:['--no-sandbox']});
const p = await b.newPage();
await p.setViewport({width:1920,height:1080});
await p.goto("file://"+process.argv[2],{waitUntil:'networkidle0'});
await new Promise(r=>setTimeout(r,1500));
for (const [i,f] of [[18,-1],[18,0],[19,-1]]) {
  await p.evaluate((a,c)=>Reveal.slide(a,0,c<0?undefined:c), i, f);
  await new Promise(r=>setTimeout(r,700));
  console.log(i,f, await p.evaluate(()=>{
    const o=[];
    document.querySelectorAll('section.present img, section.present .figone, section.present .figswap, section.present .punchbox').forEach(e=>{
      const r=e.getBoundingClientRect();
      o.push((e.tagName+'.'+e.className).slice(0,40)+' '+Math.round(r.width)+'x'+Math.round(r.height)+' maxh='+getComputedStyle(e).maxHeight);
    });
    return o.join(' | ');
  }));
}
await b.close();
