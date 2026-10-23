const { chromium } = require('/home/dusan/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/home/dusan/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome', args:['--no-sandbox'] });
  const out = {};
  for (const width of [390, 768, 1440]) {
    const p = await (await b.newContext({ viewport:{width,height:900} })).newPage();
    await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'networkidle' });
    await p.addStyleTag({content:'.js .rv{opacity:1!important;transform:none!important;transition:none!important}'});
    out[width] = await p.evaluate(() => {
      const box = (el) => { const r = el.getBoundingClientRect(); return {x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height)}; };
      const beats = [...document.querySelectorAll('.beat')].map((el) => ({
        id: el.id,
        fig: box(el.querySelector('.beat-fig')),
        copy: box(el.querySelector('.beat-copy')),
        img: (() => { const i = el.querySelector('img'); return { complete: i.complete, nw: i.naturalWidth, nh: i.naturalHeight, box: box(i) }; })(),
        captionOverflow: (() => { const f = el.querySelector('figcaption'); return f.scrollWidth - f.clientWidth; })(),
      }));
      const clipped = [...document.querySelectorAll('h1,h2,h3,p,dd,figcaption,.i-data,.mono-sm')]
        .filter((el) => el.scrollWidth > el.clientWidth + 2 && getComputedStyle(el).overflow !== 'visible')
        .map((el) => ({ tag: el.tagName, cls: el.className, sw: el.scrollWidth, cw: el.clientWidth }));
      const over = [...document.querySelectorAll('.beat-copy, .beat-fig, .data, .spec-side, .term, .thesis-grid, .arch-copy')]
        .filter((el) => el.scrollWidth > el.clientWidth + 2)
        .map((el) => ({ cls: el.className, sw: el.scrollWidth, cw: el.clientWidth }));
      const archText = [...document.querySelectorAll('.arch-svg svg text')].map((t) => {
        const r = t.getBoundingClientRect(); const s = t.closest('svg').getBoundingClientRect();
        return { txt: t.textContent.slice(0, 28), x: Math.round(r.x - s.x), right: Math.round(r.right - s.x), top: Math.round(r.y - s.y), bottom: Math.round(r.bottom - s.y) };
      }).filter((t) => t.x < -1 || t.right > 1320 || t.top < 0 || t.bottom > 640);
      return { beats, clipped, over, archText, docH: document.documentElement.scrollHeight };
    });
    await p.close();
  }
  await b.close();
  console.log(JSON.stringify(out, null, 1));
})();
