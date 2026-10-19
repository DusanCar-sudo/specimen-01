// Specimen 01 — two small jobs: nav state, honest byte count.
// No scroll reveals: content that is invisible until observed is content a screenshot can lose.
(() => {
  const sections = [...document.querySelectorAll('main section[id]')];
  const links = new Map(
    [...document.querySelectorAll('.masthead nav a')].map(a => [a.getAttribute('href').slice(1), a])
  );

  // Mark the section currently occupying the top half of the viewport.
  if ('IntersectionObserver' in window) {
    const spy = new IntersectionObserver(entries => {
      for (const e of entries) {
        const link = links.get(e.target.id);
        if (!link) continue;
        if (e.isIntersecting) {
          links.forEach(l => l.removeAttribute('aria-current'));
          link.setAttribute('aria-current', 'true');
        }
      }
    }, { rootMargin: '-45% 0px -50% 0px' });

    sections.forEach(s => spy.observe(s));
  }

  // The colophon claims a script size; measure it rather than assert it.
  const entry = performance.getEntriesByType('resource').find(r => r.name.endsWith('app.js'));
  const slot = document.getElementById('script-size');
  if (entry && slot) slot.textContent = `${entry.transferSize || entry.encodedBodySize} bytes, no dependencies`;
})();
