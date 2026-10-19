# Specimen 01 — a website about the agent that built it

A single-page self-portrait of a software engineering agent. Hand-written HTML,
one stylesheet, one small script, no dependencies, no build step. Served from
`dist/`.

## Hero images

All imagery was generated on the machine that serves this page (SDXS, 1-step,
AMD iGPU, ~15 s per plate) after four cloud providers were tried and failed:

| Path | Result |
| --- | --- |
| Local SD 1.5 (GGUF) | `get sd version from file failed` |
| Local SDXS, 4 steps | flat frame |
| Gemini 2.5 Flash Image | HTTP 429 — free-tier image quota 0 |
| OpenAI gpt-image-1.5 | HTTP 429 — `credit_balance_exhausted` |
| OpenRouter | HTTP 402 — $1.00 minimum for image output |
| **Local SDXS, 1 step, CFG 1** | works |

Plates were scored by a vision model against a fixed rubric; the hero (amber
mist, seed 41) scored appeal 8, light 9. Grading (duotone, vignette, grain) is
NumPy/Pillow.

## Plugins applied

- **ponytail 5.2.0** — smallest working change; why there is no framework here.
- **ecc 2.2.3** — `frontend-design-direction`, `frontend-a11y`,
  `make-interfaces-feel-better`, `brand-voice`.
- Remaining installed plugins (unity, clangd-lsp, aws-startup-advisor,
  glm-plan-*, local gamedev) were read and documented in the page's inventory
  section with what was and wasn't applicable.

## Verified

- Rendered in headless Chromium at 320 / 390 / 768 / 1024 / 1440 / 1920 px: no
  horizontal overflow at any width.
- WCAG contrast of hero text measured from painted pixels: 13.0:1 headline.
- Real Tab-press focus ring, reduced-motion honoured, images lazy-load, zero
  third-party requests, HTML parser-clean, AX tree landmarks present.

## Video

`hyperframes/` holds a HyperFrames (HeyGen) composition: 20s, 1920×1080, 30fps
title video for the site — "AURA HARNESS · the machine that built this page".
Rendered copy: `dist/assets/video/aura-harness-intro.mp4` (8.9 MB, h264).

Composition facts: one standalone timeline, four scenes (hero title card with
Ken Burns, three plate crossfades, end card), system fonts only, 11/11 WCAG AA
text checks, `check` passes with 0 errors. Render: beginframe capture, hardware
GPU, 36s wall time.
