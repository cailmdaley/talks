import puppeteer from 'puppeteer';
// usage: node _shot_opts.mjs <htmlfile> <slideIndex> <out.png> <css...> [--move-cnrs]
const [,, file, slideIdx, out, ...rest] = process.argv;
const moveCnrs = rest.includes('--move-cnrs');
const css = rest.filter(a=>a!=='--move-cnrs').join(' ');
const b = await puppeteer.launch({args:['--no-sandbox']});
const p = await b.newPage();
await p.setViewport({width:1920,height:1080,deviceScaleFactor:1});
await p.goto("file://"+file,{waitUntil:'networkidle0'});
await new Promise(r=>setTimeout(r,1000));
await p.evaluate((i)=>{ window.Reveal && window.Reveal.slide(parseInt(i)); }, slideIdx);
await new Promise(r=>setTimeout(r,700));
if (css) await p.addStyleTag({content: css});
if (moveCnrs) await p.evaluate(()=>{
  const bar=document.querySelector('.reveal .slides section .logo-bar');
  const cnrs=document.querySelector('.reveal .slides section .logo-cnrs');
  const sec=document.querySelector('.reveal .slides section');
  if(cnrs&&sec){ cnrs.remove(); cnrs.className='cnrs-corner-mark'; sec.appendChild(cnrs); }
});
await new Promise(r=>setTimeout(r,500));
await p.screenshot({path: out});
console.log("wrote", out);
await b.close();
