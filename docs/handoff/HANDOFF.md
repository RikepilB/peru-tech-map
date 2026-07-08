# peru-tech-map — Handoff (father)

**Read this first.** Whole-project handoff. Freshest state on top, then an append-only
index of every session folder. Nothing here is ever deleted — full prose lives in each
session's own `HANDOFF.md`; this file is the map.

## How this works (tree of context)

```
docs/handoff/
  HANDOFF.md                  ← this file (father): rolling current state + session index
  .current-session            ← pointer: active session folder name (used by the hooks)
  _meta/TEMPLATE.md           ← per-session template
  <YYYY-MM-DD>-<name>/        ← one immutable folder per session
    HANDOFF.md                ← session digest: goal · done · files · failed · next
    transcript.md              ← optional full /export archive
```

**Rules:** append, never overwrite. Only the father's `## Current state` is replaced each
session. Solved tasks → one concrete one-liner (file / PR / command).

---

## Current state — 2026-07-08

Peru Grid built and working: MapLibre GL + OpenFreeMap map of **53** real Lima/Arequipa places,
city switcher, verified live, zero bbox-skip warnings. Public GitHub repo `RikepilB/peru-tech-map`.

**Rebrand status: Nazca Desert abandoned; Costa Verde v2 (dark branding + company-building
highlighting) is the live prototype under review.** First Costa Verde pass over-corrected the
Nazca "desert" bug by deleting the base-layer recolor entirely, leaving a generic light
stock-liberty look with no branding. User feedback (side-by-side screenshots): wanted the real
dark futuristic branding back (like the original BUILD416 clone) AND every indexed company's
building visually differentiated from the rest of the skyline. Redid the basemap recolor with
distinct hue/lightness bands this time (navy bg, slate-blue buildings, neon-emerald glowing
major roads, teal water — no more monochrome-family mistake), and added a new feature: every
company's real building footprint gets a bold solid-emerald highlight (2D fill + 3D extrusion),
computed via `queryRenderedFeatures` at each company's coordinate, refreshed live as the map
pans/zooms. Verified correct via direct MapLibre state introspection after some false alarms
caused by requestAnimationFrame-throttled stale screenshots in the automated test browser (same
known quirk as the original 2026-07-06 session's 3D-animation note — not a real bug either
time). **Not yet approved as final** — user asked to check it live in their own browser tab.
HARD GATE still applies, no edits to the real `index.html` yet. Local dev server intentionally
left running (port 8000). Only outstanding config TODO carried over: `FORM_ENDPOINT` email.
Full detail in `2026-07-06-initial-build/HANDOFF.md` (both 2026-07-08 continuation sections).

---

## Session index (append-only, newest first)

- 2026-07-08 (continuation of 2026-07-06-initial-build) — Diagnosed Nazca Desert's
  contrast-killing base-layer recolor bug, abandoned that direction, designed + built Costa
  Verde v1 (`index-costaverde.html`, terrain left fully untouched). User flagged v1 as
  over-corrected — too generic/no branding, no way to spot company buildings — so redid the
  basemap recolor with a proper dark futuristic palette (distinct hue/lightness bands this
  time) and added a new always-on company-building-highlight feature (real building footprint
  under each company glows emerald). Verified correct via direct MapLibre API state checks
  after ruling out rAF-throttled stale screenshots as a false alarm. Awaiting user's live
  approval before promoting to `index.html`.
- 2026-07-06-initial-build — Built Peru Grid (53 researched places, Lima+Arequipa), cloned
  BUILD416 structure/style, ran project-scaffold (fixed ts/npm-default mismatch), pushed as
  public GitHub repo `RikepilB/peru-tech-map`. Nazca Desert rebrand direction locked via
  brainstorming skill; real live prototype `index-nazca.html` built and reviewed, accepted as
  working baseline only (not final) — session closed by user.

<!-- compact-handoff:auto-snapshot -->
<!-- Latest auto-snapshot: docs/handoff/2026-07-08-4609ae8d/snapshot-052823.md -->
## Latest auto snapshot — 2026-07-08T05:28:23.777Z
- Session folder: `docs/handoff/2026-07-08-4609ae8d/`
- Snapshot file: `docs/handoff/2026-07-08-4609ae8d/snapshot-052823.md`
- Branch: master
