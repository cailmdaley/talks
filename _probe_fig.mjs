import puppeteer from 'puppeteer';
const file = process.argv[2]; const idx = parseInt(process.argv[3]);
const b = await puppeteer.launch({args:['--no-sandbox']});
const p = await b.newPage();
await p.setViewport({width:1920,height:1080,deviceScaleFactor:1});
await p.goto("file://"+file,{waitUntil:'networkidle0'});
await new Promise(r=>setTimeout(r,1000));
await p.evaluate(i=>window.Reveal.slide(i), idx);
await new Promise(r=>setTimeout(r,800));
const info = await p.evaluate(()=>{
  const sec = [...document.querySelectorAll('.reveal .slides > section')].find(s=>s.classList.contains('present')) || document.querySelector('.reveal .slides section.present');
  const img = sec?.querySelector('img');
  const r = el => el?(()=>{const b=el.getBoundingClientRect();return {x:Math.round(b.x),y:Math.round(b.y),w:Math.round(b.width),h:Math.round(b.height)};})():null;
  const cs = el => el?(s=>({display:s.display,visibility:s.visibility,opacity:s.opacity,zIndex:s.zIndex,position:s.position,maxHeight:s.maxHeight,height:s.height}))(getComputedStyle(el)):null;
  return {
    secClasses: sec?.className,
    imgSrc: img?.getAttribute('src'),
    imgComplete: img?.complete,
    imgNatural: img?(img.naturalWidth+'x'+img.naturalHeight):null,
    imgRect: r(img),
    imgStyle: cs(img),
    imgClasses: img?.className,
    parentTag: img?.parentElement?.tagName,
    parentClasses: img?.parentElement?.className,
    parentRect: r(img?.parentElement),
    grandTag: img?.parentElement?.parentElement?.tagName,
    grandClasses: img?.parentElement?.parentElement?.className,
  };
});
console.log(JSON.stringify(info,null,2));
await b.close();
