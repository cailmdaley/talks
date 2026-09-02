import puppeteer from 'puppeteer';
const b = await puppeteer.launch(); const p = await b.newPage();
await p.setViewport({width:1720,height:560,deviceScaleFactor:1});
await p.goto("file:///tmp/svgview.html",{waitUntil:'networkidle0'});
await new Promise(r=>setTimeout(r,1500));
await p.screenshot({path:'/tmp/timeline_check.png'});
await b.close(); console.log('done');
