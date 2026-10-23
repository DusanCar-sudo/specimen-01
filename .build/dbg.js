const { chromium } = require('/home/dusan/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/home/dusan/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome', args:['--no-sandbox'] });
  const p = await (await b.newContext({ viewport:{width:1440,height:900} })).newPage();
  await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'networkidle' });
  await p.evaluate(() => document.getElementById('stack').scrollIntoView());
  await p.waitForTimeout(1500);
  const out = await p.evaluate(() => {
    const q = (s) => { const e=document.querySelector(s); if(!e) return null; const r=e.getBoundingClientRect(); const c=getComputedStyle(e);
      return {x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height),opacity:c.opacity,display:c.display,z:c.zIndex}; };
    return {
      archSvg:q('.arch-svg'), svg:q('.arch-svg svg'), archCopy:q('.arch-copy'), arch:q('#stack'),
      wrap:q('#stack .wrap'), list:q('.arch-list'), revealsIn:document.querySelectorAll('.rv.in').length,
      revealsTotal:document.querySelectorAll('.rv').length,
      svgPaths:document.querySelectorAll('.arch-svg svg *').length
    };
  });
  console.log(JSON.stringify(out,null,1));
  await p.screenshot({path:'shots/dbg-stack.png'});
  await p.evaluate(() => window.scrollBy(0, 500));
  await p.waitForTimeout(1200);
  await p.screenshot({path:'shots/dbg-stack2.png'});
  await b.close();
})();
