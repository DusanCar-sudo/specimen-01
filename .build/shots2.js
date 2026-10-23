const { chromium } = require('/home/dusan/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/home/dusan/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome', args:['--no-sandbox'] });
  const ctx = await b.newContext({ viewport:{width:1440,height:900}, deviceScaleFactor:1 });
  const p = await ctx.newPage();
  await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'networkidle' });
  await p.addStyleTag({content:'.js .rv{opacity:1!important;transform:none!important;transition:none!important}.top{position:absolute!important}'});
  await p.evaluate(() => document.getElementById('story').scrollIntoView());
  await p.waitForTimeout(1600);
  const beats = await p.$$('.beat');
  await beats[0].screenshot({path:'shots/beat1.png'});
  await beats[1].screenshot({path:'shots/beat2.png'});
  await beats[3].screenshot({path:'shots/beat4.png'});
  const term = await p.$('.term'); await term.screenshot({path:'shots/term.png'});
  const spec = await p.$('.spec-table'); await spec.screenshot({path:'shots/spec.png'});
  await p.evaluate(() => document.getElementById('stack').scrollIntoView());
  await p.waitForTimeout(2200);
  const arch = await p.$('.arch-svg'); await arch.screenshot({path:'shots/arch.png'});
  // mobile beat
  const m = await (await b.newContext({ viewport:{width:390,height:844} })).newPage();
  await m.goto('http://127.0.0.1:8899/index.html', { waitUntil:'networkidle' });
  await m.addStyleTag({content:'.js .rv{opacity:1!important;transform:none!important;transition:none!important}.top{position:absolute!important}'});
  await m.evaluate(() => document.getElementById('story').scrollIntoView());
  await m.waitForTimeout(1400);
  const mb = await m.$$('.beat'); await mb[0].screenshot({path:'shots/m-beat1.png'});
  await b.close();
})();
