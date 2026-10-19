# Aura Code — the agent that runs your business with you

Landing page for Aura Code, served from `dist/`. Ported from
`~/lpq-redesign/index.html`, the design direction the user preferred over the
earlier Specimen 01 self-portrait (that page remains in git history — commits
`42fb789`, `84103a8` — under `dist/`).

## Design

- "aura OS" aesthetic: fixed OS menubar with live clock, terminal boot log
  typed out on load, sections presented as windowed panels with title bars,
  fixed status bar at the bottom.
- One HTML file, hand-written CSS, ~40 lines of vanilla JS for the boot log and
  clock. No build step, no dependencies.

## Assets

| Path | Source |
| --- | --- |
| `site-assets/fonts/geist.woff2` | Geist variable, OFL, via jsdelivr `geist@1.3.1` |
| `site-assets/fonts/geist-mono.woff2` | Geist Mono variable, OFL, same source |
| `site-assets/favicon.svg` | Drawn to match the menubar dot |

## Changes from the original

- Asset URLs made relative (`site-assets/...`) so the page works regardless of
  where the preview server roots the site.
- `founder.html` links point at the on-page `#founder` section instead of a
  page that does not exist here.
- Added a visually-hidden `h1`; the original had none.
- Everything else is byte-identical to `~/lpq-redesign/index.html`.

## Verified

- Headless Chromium (Playwright) at 320 / 390 / 768 / 1024 / 1440 / 1920 px:
  zero horizontal overflow at every width.
- Both webfonts load and apply (document.fonts.check passes).
- Boot log completes (~9.5 s) and the menubar clock ticks.
- Server log shows 200s for the page, both fonts and the favicon; no 404s.

Left in place but unreferenced: `assets/` from the Specimen 01 page (app.js,
style.css, images, intro video). Git still has them if they are ever needed.
