const { chromium } = require('/home/dusan/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/home/dusan/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome', args:['--no-sandbox'] });
  const p = await (await b.newContext({ viewport:{width:1440,height:900} })).newPage();
  await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'networkidle' });
  await p.addStyleTag({content:'.js .rv{opacity:1!important;transform:none!important;transition:none!important}'});
  const h = await p.evaluate(() => document.documentElement.scrollHeight);
  for (let y = 0; y < h; y += 700) { await p.evaluate((y) => window.scrollTo(0, y), y); await p.waitForTimeout(120); }
  await p.evaluate(() => window.scrollTo(0, 0));
  await p.waitForTimeout(1500);
  await p.screenshot({ path: 'shots/full-1440-forced.png', fullPage: true });
  console.log('height', h);
  await b.close();
})();
