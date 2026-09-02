import puppeteer from 'puppeteer';
const url = process.argv[2];
const b = await puppeteer.launch();
const p = await b.newPage();
await p.setViewport({width:1920,height:1080,deviceScaleFactor:1});
await p.goto(url,{waitUntil:'networkidle0'});
await new Promise(r=>setTimeout(r,1200));
const n = await p.evaluate(()=> window.Reveal.getTotalSlides());
for(let i=0;i<n;i++){
  await p.evaluate((idx)=>{ window.Reveal.slide(idx); }, i);
  await new Promise(r=>setTimeout(r,400));
  const info = await p.evaluate(()=>{
    const slides = document.querySelector('.reveal .slides');
    const st = getComputedStyle(slides).transform; // matrix(a,...) a = scaleX
    let scale = 1;
    const m = st.match(/matrix\(([^,]+)/); if(m) scale = parseFloat(m[1]);
    const s = document.querySelector('.reveal .slides section.present');
    const r = s.getBoundingClientRect();
    // first text paragraph computed font size
    const para = s.querySelector('div[style*="font-size"], p, li');
    const fs = para ? getComputedStyle(para).fontSize : 'n/a';
    const h2 = s.querySelector('h2');
    const h2fs = h2 ? getComputedStyle(h2).fontSize : 'n/a';
    return { id: s.id||'(none)', scale: scale.toFixed(3),
             rectTop: Math.round(r.top), rectH: Math.round(r.height), rectW: Math.round(r.width),
             cls: s.className, bodyFS: fs, h2FS: h2fs,
             display: getComputedStyle(s).display, justify: getComputedStyle(s).justifyContent };
  });
  console.log(`${String(i).padStart(2,'0')} #${info.id.padEnd(22)} scale=${info.scale} top=${String(info.rectTop).padStart(5)} h=${String(info.rectH).padStart(5)} disp=${info.display.padEnd(5)} just=${info.justify.padEnd(8)} bodyFS=${info.bodyFS.padEnd(7)} h2FS=${info.h2FS}`);
}
await b.close();
