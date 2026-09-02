import puppeteer from 'puppeteer';
const b = await puppeteer.launch();
const p = await b.newPage();
await p.setViewport({width:1920,height:1080});
await p.goto(process.argv[2],{waitUntil:'networkidle0'});
await new Promise(r=>setTimeout(r,1200));
await p.evaluate(()=>{ Reveal.slide(1); });
await new Promise(r=>setTimeout(r,400));
const info = await p.evaluate(()=>{
  const sec = document.querySelector('#why-cant-we-do-astronomy-here');
  const flex = sec.querySelector('div > div'); // probably the flex container
  const img = sec.querySelector('img');
  function dims(el){ const r=el.getBoundingClientRect(); return {x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height)};}
  const s = getComputedStyle(img);
  return {
    flexRect: flex?dims(flex):null,
    flexInline: flex?flex.getAttribute('style'):null,
    imgRect: dims(img),
    imgHeight: s.height, imgWidth: s.width, imgMaxH: s.maxHeight, imgMaxW: s.maxWidth, imgDisplay: s.display,
    imgParent: img.parentElement.tagName,
    imgParentRect: dims(img.parentElement),
  };
});
console.log(JSON.stringify(info,null,2));
await b.close();
