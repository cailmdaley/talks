// Render all main slides in every declared toggle state, plus the window backup.
const fs=require('fs'),path=require('path');
const puppeteer=require('../../node_modules/puppeteer');
const sharp=require('../../node_modules/sharp');
(async()=>{
 const root=path.resolve(__dirname,'../..'),out=path.resolve(__dirname,'../_check/round5');fs.mkdirSync(out,{recursive:true});
 const browser=await puppeteer.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
 const page=await browser.newPage();await page.setViewport({width:1920,height:1080,deviceScaleFactor:1});
 const errors=[],requests=[];page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url())});
 await page.goto('file://'+root+'/_site/2610_GC8_Systematics/index.html',{waitUntil:'networkidle0'});await page.waitForFunction(()=>window.Reveal?.isReady());
 await page.addStyleTag({content:'*,*::before,*::after {transition:none !important;animation:none !important;}'});
 if(!await page.evaluate(()=>document.body.textContent.includes('CSFD brings')))throw Error('Stale build');
 const defaultState=await page.evaluate(()=>House.variant());if(defaultState!=='c1|lensmc|spt|e')throw Error('Wrong default '+defaultState);
 const receipts=[];
 for(const cy of ['c1','c2'])for(const sh of ['lensmc','metacal'])for(const cm of ['spt','act'])for(const mode of ['e','b']){
  const key=[cy,sh,cm,mode].join('_'),captures=[];
  await page.evaluate(([cycle,shear,cmb,mode])=>{House.setVariant('cycle',cycle);House.setVariant('shear',shear);House.setVariant('cmb',cmb);House.setVariant('mode',mode)},[cy,sh,cm,mode]);
  for(const slide of [0,1,2,3,4,5,6,8]){
   await page.evaluate(h=>{Reveal.slide(h,0,-1);House.settle();},slide);await new Promise(r=>setTimeout(r,120));
   await page.evaluate(async()=>{await Promise.all([...document.querySelectorAll('.present img')].map(im=>im.decode()))});
   const name=`${key}_s${slide+1}.png`;await page.screenshot({path:path.join(out,name)});captures.push(name);
   const state=await page.evaluate(()=>({variant:House.variant(),slide:Reveal.getIndices().h,images:[...Reveal.getCurrentSlide().querySelectorAll('img')].map(i=>({ok:i.complete&&i.naturalWidth>0,asset:Object.keys(HouseAssets).find(k=>HouseAssets[k]===i.getAttribute('src')),source:i.getAttribute('data-src-path')})),text:Reveal.getCurrentSlide().innerText}));receipts.push({name,...state});
   if([1,2,3].includes(slide)){
    const effective=slide===2?[cy,sh,cm,'e'].join('|'):[cy,'lensmc','spt','e'].join('|');
    const ok=await page.evaluate(k=>{const i=Reveal.getCurrentSlide().querySelector('img'),alts=JSON.parse(i.getAttribute('data-alt')||'{}'),a=alts[k]||i.getAttribute('data-asset');return i.getAttribute('src')===HouseAssets[a]},effective);
    if(!ok)throw Error('Toggle asset mismatch '+key+' slide '+slide);
   }
  }
  const bufs=await Promise.all(captures.map(f=>sharp(path.join(out,f)).resize(640,360).png().toBuffer()));
  await sharp({create:{width:1920,height:1080,channels:3,background:'#ccc'}}).composite(bufs.map((input,i)=>({input,left:(i%3)*640,top:Math.floor(i/3)*360}))).png().toFile(path.join(out,'contact_'+key+'.png'));
 }
 fs.writeFileSync(path.join(out,'render-receipts.json'),JSON.stringify({defaultState,errors,requests,states:receipts},null,2));
 if(errors.length||requests.length||receipts.some(r=>r.images.some(i=>!i.ok)))throw Error('Render failed');
 console.log(`${receipts.length} states rendered (112 main + 16 window), 16 contact sheets, zero browser errors or network requests.`);await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
