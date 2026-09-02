import puppeteer from 'puppeteer';
const deckUrl="http://127.0.0.1:4004/project-file/local/Users/cd280747/Documents/projects/talks/_site/26_CNRS_RisingTalents/26_CNRS_RT_1_general.html";
// Use a 16:9-ish wide short frame like a report embed
const wrapper=`<!doctype html><html><head><style>html,body{margin:0}.deck-frame{width:1000px;height:563px;border:0;display:block}</style></head><body><iframe class="deck-frame" src="${deckUrl}" allowfullscreen></iframe></body></html>`;
const b=await puppeteer.launch({args:['--no-sandbox']});
const p=await b.newPage();
await p.setViewport({width:1000,height:600,deviceScaleFactor:1});
await p.setContent(wrapper,{waitUntil:'networkidle2',timeout:30000}).catch(()=>{});
await new Promise(r=>setTimeout(r,3500));
const deck=p.frames().find(f=>f.url().includes('26_CNRS_RT_1_general'));
const n=await deck.evaluate(()=>window.Reveal.getTotalSlides());
const vh=await deck.evaluate(()=>window.innerHeight);
console.log('deck frame innerHeight:', vh, 'totalSlides:', n);
const rows=[];
for(let i=0;i<n;i++){
  await deck.evaluate((idx)=>window.Reveal.slide(idx),i);
  await new Promise(r=>setTimeout(r,150));
  const info=await deck.evaluate(()=>{
    const sec=document.querySelector('.reveal .slides section.present');
    const r=sec.getBoundingClientRect();
    const h2=sec.querySelector('h2'); const hr=h2?h2.getBoundingClientRect():null;
    return {id:sec.id, secTop:Math.round(r.top), secBot:Math.round(r.bottom), secH:Math.round(r.height), h2Top:hr?Math.round(hr.top):null, h2Bot:hr?Math.round(hr.bottom):null};
  });
  rows.push({i,...info});
}
console.table(rows);
await b.close();
