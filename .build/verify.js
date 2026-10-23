const { chromium } = require('/home/dusan/node_modules/playwright');
const fs = require('fs');

const BASE = 'http://127.0.0.1:8899/index.html';
const WIDTHS = [320, 390, 768, 1024, 1440, 1920];
const OUT = '/home/dusan/preview-demo/.build/shots';

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({
    executablePath: '/home/dusan/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome',
    args: ['--no-sandbox', '--autoplay-policy=no-user-gesture-required'],
  });
  const results = [];
  const requests = [];

  for (const width of WIDTHS) {
    const ctx = await browser.newContext({
      viewport: { width, height: width < 700 ? 844 : 900 },
      deviceScaleFactor: 1,
      reducedMotion: 'no-preference',
    });
    const page = await ctx.newPage();
    page.on('console', (m) => { if (m.type() === 'error') results.push({ width, console: m.text() }); });
    page.on('response', (r) => { if (r.status() >= 400) requests.push({ width, url: r.url(), status: r.status() }); });
    page.on('requestfailed', (r) => requests.push({ width, url: r.url(), failed: r.failure() }));

    await page.goto(BASE, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1200);

    const metrics = await page.evaluate(() => {
      const de = document.documentElement;
      const video = document.getElementById('heroVideo');
      const h1 = document.getElementById('hero-title');
      const cs = getComputedStyle(h1);
      return {
        scrollWidth: de.scrollWidth,
        clientWidth: de.clientWidth,
        docHeight: de.scrollHeight,
        overflow: de.scrollWidth - de.clientWidth,
        h1Size: cs.fontSize,
        h1Rect: (() => { const r = h1.getBoundingClientRect(); return { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) }; })(),
        fontLoaded: document.fonts.check('500 40px Geist') && document.fonts.check('400 12px "Geist Mono"'),
        revealsIn: document.querySelectorAll('.rv.in').length,
        revealsTotal: document.querySelectorAll('.rv').length,
        video: video ? {
          display: getComputedStyle(video).display,
          duration: video.duration,
          readyState: video.readyState,
          paused: video.paused,
          w: video.videoWidth,
          h: video.videoHeight,
        } : null,
        sections: [...document.querySelectorAll('section[id]')].map((s) => s.id),
        offscreen: [...document.querySelectorAll('body *')]
          .filter((el) => !(el instanceof SVGElement))
          .map((el) => ({ el, r: el.getBoundingClientRect() }))
          .filter(({ r }) => r.width > 0 && (r.right > window.innerWidth + 1 || r.left < -1))
          .slice(0, 8)
          .map(({ el, r }) => ({ tag: el.tagName, cls: el.className && el.className.baseVal !== undefined ? el.className.baseVal : el.className, left: Math.round(r.left), right: Math.round(r.right) })),
      };
    });

    await page.screenshot({ path: `${OUT}/full-${width}.png`, fullPage: true });
    await page.screenshot({ path: `${OUT}/hero-${width}.png` });
    results.push({ width, ...metrics });
    await ctx.close();
  }

  // scroll to the story + audit sections at desktop width for a second look
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await ctx.newPage();
  await page.goto(BASE, { waitUntil: 'networkidle' });
  for (const id of ['story', 'stack', 'specs', 'audit', 'access']) {
    await page.evaluate((x) => document.getElementById(x).scrollIntoView(), id);
    await page.waitForTimeout(900);
    await page.screenshot({ path: `${OUT}/sec-${id}.png` });
  }
  await ctx.close();

  await browser.close();
  fs.writeFileSync(`${OUT}/report.json`, JSON.stringify({ results, requests }, null, 2));
  console.log(JSON.stringify({ results, requests }, null, 2));
})();
