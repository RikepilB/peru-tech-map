# peru-tech-map — Architecture & Workflow

## Shape: static, single-file, zero-dependency

No build step, no bundler, no framework, no backend, no package manager. Three files:

- `index.html` — the entire app (MapLibre GL setup, theming, city switcher, sidebar,
  markers, ticker, add-company modal, loader). All JS is inline in a single `<script>` block.
- `companies.json` — the dataset. Single source of truth for markers, sidebar, and counts.
  Never hardcode a place in `index.html`.
- `ticker.json` — scrolling headline reel, independent of the active city.

Served via any static file server (`python3 -m http.server`). Fetches `companies.json` /
`ticker.json` at runtime, so it must run over `http://`, never opened via `file://`.

## Module boundaries

There are no modules — it's one file by design (see README's "no build step, no framework"
philosophy, inherited from the BUILD416 project this was cloned from). Don't split it into
multiple JS files or add a bundler; that would work against the project's explicit constraint.

## Git workflow

| When | Action |
|---|---|
| Starting a change | Branch: `add/<company-name>` or `fix/<name>` |
| Before merging | CI validates `companies.json`/`ticker.json` are well-formed JSON with required fields |
| Adding a place | Edit `companies.json` only — see README's Data Format section for the schema |

## Key reminders

- **Coordinate guard:** every entry must fall inside its declared city's bbox (Lima or
  Arequipa, see README) — entries outside are skipped at load with a console warning.
- **Marker DOM rule:** the element passed to `new maplibregl.Marker({element})` must carry
  NO css transform/transition/animation on its root — MapLibre writes that element's
  transform every frame; all visuals live on an inner child (`.co-marker`).
- **One accent color** — Solarium green (`#056540`/`#0FA968`). Don't introduce new hues.
- Update this file (not just `docs/architecture.md`) if the shape ever stops being a single
  static file — this is what an agent actually reads to plan a change here.
