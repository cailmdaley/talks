import puppeteer from 'puppeteer';
const file = process.argv[2];
const b = await puppeteer.launch({args:['--no-sandbox']});
const p = await b.newPage();
await p.setViewport({width:1920,height:1080,deviceScaleFactor:1});
await p.goto("file://"+file,{waitUntil:'networkidle0'});
await p.evaluate(()=>{ window.Reveal && window.Reveal.slide(5); });
await new Promise(r=>setTimeout(r,5000)); // let the METR iframe load
await p.screenshot({path:"26_CNRS_RisingTalents/screenshots/qa-rework/metr_zoom.png"});
await b.close(); console.log("done");
