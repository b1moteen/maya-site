# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Single-page marketing/ticketing site for the show «Майя Великолепная» (Russian-language content). Static, no build step, no package manager, no tests, no linter. Deployed via GitHub Pages from the repo root (`.nojekyll` present; see `README.md` for deploy and custom-domain steps and the pre-launch checklist).

Run locally by opening `index.html` in a browser, or `python3 -m http.server` in the repo root (needed if testing autoplay video behaviour).

## Architecture

Everything lives in `index.html` (very long minified-style lines): one `<style>` block, the markup of sections (hero → about → gallery → exhibition → team → video → reviews → dates → price → footer/lightbox), and one inline `<script>` at the bottom. Media is in `assets/` (`photo-NN.jpg`, `hero-video.mp4`, `evening-video.mp4`, `evening-poster.jpg`, `qr-tickets.png`), referenced by relative path (`photo-02…06` and `photo-15` are currently unused). Fonts (Prata, Jost) load from Google Fonts. A CSP `<meta>` in `<head>` whitelists only self + Google Fonts; new external resources must be added there.

Key points that span the file:

- **Theming**: CSS custom properties on `:root` (`--bg`, `--ink`, `--red`, …) with dark values duplicated in two places — the `prefers-color-scheme: dark` media query (guarded by `:not([data-theme="light"])`) and `:root[data-theme="dark"]`. Change dark colors in both.
- **Dates** (script): `days` (date ISO + status `''` / `'low'`) renders the date rows (`#rows`). Prices are static markup only (range "От 2 500 ₽ до 5 000 ₽" in "Билеты"). The `D` array near the top of the script is unused leftover, as is the `.tag` CSS rule.
- **Buy flow**: no modal/counters. Every `a[data-buy]` (header, hero, exhibition, video, ticket cards, mobile `.bar`, rows from the script) is a plain link to the icetickets.ru event page (`target=_blank`, `rel="noopener noreferrer"`); the same URL is behind the QR in the footer (`.qr`, `assets/qr-tickets.png`).
- **Interactions**: scroll-reveal via `.rv` + IntersectionObserver adding `.in`; hero video and the evening video `#v2` (9:16, poster `evening-poster.jpg`, auto-play/pause on visibility, sound toggle `#snd`); custom cursor `#cur`; lightbox (`data-ph` → `P` map to `photo-16/17/18`; `.treas .ph` cards are keyboard-accessible).
- **Photos** have no arches/frames: they fade into the background via CSS masks (`.arch` radial, `.gm img`/`.ex img`/`.rail figure` linear). All `<img>` carry width/height and `loading="lazy"` (hero: `fetchpriority="high"`).
- **Background sketches** (`#sk`, SVG `<symbol>`s `sk-fan`/`sk-pt` right after `<body>`): fixed layer at `z-index:-1`; color from `--ink`, opacity from `--sko` (light .09 / dark .12 — set in all three theme places). `.pane` has no backdrop-filter so sketches show through panels.
- Reviews (`#rev`) are placeholder/invented text and must be replaced with real ones before launch (per README).
