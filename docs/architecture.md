# Architecture

> System patterns, module boundaries, and trade-offs. Keep this authoritative; the agent
> reads it to plan changes. Human-facing mirror of `.claude/rules/peru-tech-map-architecture.md`
> — keep both in sync.

## Overview
Single static HTML file (`index.html`) + two JSON data files (`companies.json`, `ticker.json`).
No build step, no framework, no backend, no package manager. MapLibre GL JS renders the map;
OpenFreeMap serves the vector tiles. Cloned in structure/style from
[BUILD416](https://github.com/MapleBudget/toronto-tech-map), extended with a Lima/Arequipa
city switcher.

## Modules & boundaries
There are no modules — everything lives inline in `index.html`'s one `<script>` block, by
design (see the project's "no build step, no framework" constraint). Logical sections inside
that script: map init + theming → building/3D setup → company loading + bbox guard → marker
rendering (with spiderfy fan-out for stacked coords) → sidebar → ticker → status bar → add-
company modal (FormSubmit, not yet wired to a real email) → terminal-boot loader.

## Data flow
1. `map.on("load")` fires → base style gets dark-themed, POI labels hidden, road labels
   filtered to major roads only.
2. `companies.json` is fetched once into `ALL_COMPANIES`; `ticker.json` is fetched
   independently and rendered as a scrolling reel (not city-filtered).
3. `applyCity(city)` filters `ALL_COMPANIES` to the active city, bbox-guards each entry
   (console-warns and skips anything outside that city's box), rebuilds markers + sidebar,
   and refits the camera (`maxBounds`/`minZoom`/home position) for that city.
4. Clicking a sidebar row or a marker calls `selectCompany(i, fly)` — flies the camera,
   opens a themed popup, and highlights both the marker and its sidebar row in sync.

## Trade-offs & constraints
- **No fabricated funding data.** Most entries aren't VC-funded, so `funding.type` is
  repurposed as a category (`Startup`/`Consultancy`/`Coworking`/`Incubator`/`Nonprofit`) rather
  than a real funding round — documented in the README's Data Format section.
- **No local logo assets.** Markers use Google's favicon service keyed off `domain`, falling
  back to an initial-letter tile when `domain` is absent — avoids bundling/copying third-party
  logo images.
- **Add-company form is inert.** `FORM_ENDPOINT` in `index.html` is a placeholder; needs a
  real FormSubmit-verified email before that feature goes live.
