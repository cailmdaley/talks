// Render every four-axis toggle / main-slide fragment state, and contact sheets.
const fs=require('fs'),path=require('path');
const puppeteer=require('../../node_modules/puppeteer');
const sharp=require('../../node_modules/sharp');
(async()=>{
 const root=path.resolve(__dirname,'../..'),out=path.resolve(__dirname,'../_check/round4');fs.mkdirSync(out,{recursive:true});
 const browser=await puppeteer.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
 const page=await browser.newPage();await page.setViewport({width:1920,height:1080,deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));await page.goto('file://'+root+'/_site/2610_GC8_Systematics/index.html',{waitUntil:'networkidle0'});await page.waitForFunction(()=>window.Reveal?.isReady());
 await page.addStyleTag({content:'*,*::before,*::after {transition:none !important;animation:none !important;}'});
 if(!await page.evaluate(()=>document.body.textContent.includes('Rewindowing explains 77%')))throw Error('Stale build: ladder missing');
 const receipts=[];
 for(const cy of ['c1','c2'])for(const sh of ['lensmc','metacal'])for(const cm of ['spt','act'])for(const mode of ['e','b']){
  const key=[cy,sh,cm,mode].join('_');let captures=[];
  await page.evaluate(([cycle,shear,cmb,mode])=>{House.setVariant('cycle',cycle);House.setVariant('shear',shear);House.setVariant('cmb',cmb);House.setVariant('mode',mode)},[cy,sh,cm,mode]);
  for(const [slide,steps] of [[0,1],[1,1],[2,3],[3,2],[4,2]])for(let step=0;step<steps;step++){
   await page.evaluate(([h,f])=>{Reveal.slide(h,0,f-1);House.settle();},[slide,step]);await new Promise(r=>setTimeout(r,110));
   await page.evaluate(async()=>{await Promise.all([...document.querySelectorAll('.present img')].map(im=>im.decode().catch(()=>{})))});
   const name=`${key}_s${slide+1}_f${step}.png`;await page.screenshot({path:path.join(out,name)});captures.push(name);
   const state=await page.evaluate(()=>({variant:House.variant(),slide:Reveal.getIndices().h,fragment:Reveal.getIndices().f,images:[...Reveal.getCurrentSlide().querySelectorAll('img')].map(i=>({ok:i.complete&&i.naturalWidth>0,asset:i.getAttribute('data-asset')})),text:Reveal.getCurrentSlide().innerText}));receipts.push({name,...state});
  }
  const bufs=await Promise.all(captures.map(f=>sharp(path.join(out,f)).resize(640,360).png().toBuffer()));
  await sharp({create:{width:1920,height:1080,channels:3,background:'#ccc'}}).composite(bufs.map((input,i)=>({input,left:(i%3)*640,top:Math.floor(i/3)*360}))).png().toFile(path.join(out,'contact_'+key+'.png'));
 }
 fs.writeFileSync(path.join(out,'render-receipts.json'),JSON.stringify({errors,states:receipts},null,2));
 if(errors.length||receipts.some(r=>r.images.some(i=>!i.ok)))throw Error('render failed');
 console.log(`${receipts.length} states rendered, 16 contact sheets, ${errors.length} browser errors.`);await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
