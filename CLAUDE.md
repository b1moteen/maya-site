# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Single-page marketing/ticketing site for the show «Майя Великолепная» (Russian-language content). Static, no build step, no package manager, no tests, no linter. Deployed via GitHub Pages from the repo root (`.nojekyll` present; see `README.md` for deploy and custom-domain steps and the pre-launch checklist).

Run locally by opening `index.html` in a browser, or `python3 -m http.server` in the repo root (needed if testing autoplay video behaviour). The directory is not a git repository.

## Architecture

Everything lives in `index.html` (~200 lines, very long minified-style lines): one `<style>` block (line ~11–120), the markup of sections (hero → about → "Вы увидите" → gallery → exhibition → team → video → reviews → dates → price → footer/modal/lightbox), and one inline `<script>` at the bottom. Media is in `assets/` (`photo-NN.jpg`, `hero-video.mp4`, `evening-video.mp4`), referenced by relative path. Fonts (Prata, Jost) load from Google Fonts.

Key points that span the file:

- **Theming**: CSS custom properties on `:root` (`--bg`, `--ink`, `--red`, …) with dark values duplicated in two places — the `prefers-color-scheme: dark` media query (guarded by `:not([data-theme="light"])`) and `:root[data-theme="dark"]`. Change dark colors in both.
- **Data-driven booking UI** (script): `days` (date ISO + status `''` / `'low'` / `'out'`) renders both the date rows (`#rows`) and the modal `<select id="sel">`; `T` (name, description, price) renders ticket counters (`#tks`), with quantities in `q[]` and total via `calc()`. Ticket prices are also hardcoded in the "Билеты" markup section, so changing prices means editing `T` **and** that block. The `D` array near the top of the script is unused leftover.
- **Buy flow**: any element with `data-buy` (optionally `data-i` = day index) opens the modal via `open()`. The "Оформить" handler (`#go`) is a stub — it only shows a confirmation text; no order is sent anywhere.
- **Interactions**: scroll-reveal via `.rv` + IntersectionObserver adding `.in`; the "Вы увидите" block cycles `.act` items and `.sa img` in sync (5s timer, hover/click to select); hero video and the evening video (auto-play/pause on visibility, sound toggle `#snd`); 3D tilt on `#arch` and custom cursor `#cur`; lightbox (`data-ph` → `P` map to `photo-16/17/18`).
- Reviews (`#rev`) are placeholder/invented text and must be replaced with real ones before launch (per README).
