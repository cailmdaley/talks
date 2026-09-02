import puppeteer from 'puppeteer';
const b = await puppeteer.launch(); const p = await b.newPage();
await p.setViewport({width:1920,height:1080});
await p.goto("file://"+process.argv[2],{waitUntil:'networkidle0'});
await new Promise(r=>setTimeout(r,1000));
await p.evaluate(()=>window.Reveal&&window.Reveal.slide(5));
await new Promise(r=>setTimeout(r,600));
const info = await p.evaluate(()=>{
  const r=e=>e?(()=>{const b=e.getBoundingClientRect();const c=getComputedStyle(e);return{rect:[Math.round(b.x),Math.round(b.y),Math.round(b.width),Math.round(b.height)],pos:c.position,top:c.top,bottom:c.bottom,right:c.right,vis:c.visibility,op:c.opacity,txt:(e.textContent||'').trim().slice(0,20)}})():null;
  const sn=document.querySelector('.reveal .slide-number');
  const lg=document.querySelector('.slide-logo, img.slide-logo, .reveal .slide-logo');
  return {slideNumber:r(sn), logo:r(lg)};
});
console.log(JSON.stringify(info,null,2));
await b.close();
