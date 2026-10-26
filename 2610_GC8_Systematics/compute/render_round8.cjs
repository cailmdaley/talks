// Step through slide 5 with real key presses (fragment events run), screenshot each step and one step back.
const fs=require('fs'),path=require('path');
const puppeteer=require('../../node_modules/puppeteer');
(async()=>{
 const root=path.resolve(__dirname,'../..'),out=path.resolve(__dirname,'../_check/round8');fs.mkdirSync(out,{recursive:true});
 const browser=await puppeteer.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
 const page=await browser.newPage();await page.setViewport({width:1920,height:1080});
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto('file://'+root+'/_site/2610_GC8_Systematics/index.html',{waitUntil:'networkidle0'});await page.waitForFunction(()=>window.Reveal?.isReady());
 await page.addStyleTag({content:'*,*::before,*::after {transition:none !important;animation:none !important;}'});
 await page.evaluate(()=>Reveal.slide(4,0,-1));
 const shot=async n=>{await new Promise(r=>setTimeout(r,200));const s=await page.evaluate(()=>({v:House.variant(),f:Reveal.getIndices().f,vis:[...Reveal.getCurrentSlide().querySelectorAll('img')].filter(i=>getComputedStyle(i).opacity!=='0'&&getComputedStyle(i).visibility!=='hidden').map(i=>i.getAttribute('data-src-path')||i.getAttribute('src').slice(0,40))}));console.log(n,JSON.stringify(s));await page.screenshot({path:path.join(out,n+'.png')});};
 await shot('s0');for(const n of ['s1','s2','s3']){await page.keyboard.press('ArrowRight');await shot(n);}
 await page.keyboard.press('ArrowLeft');await page.keyboard.press('ArrowLeft');await shot('back_s1');
 console.log('errors',errors);await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
