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

## Current state — 2026-07-13

Peru Grid built and working: MapLibre GL + OpenFreeMap map of **54** real Lima/Arequipa places
(added SeguroSimple this session; Aviva/Paqta/MrPink VC cross-checked against the reference doc
and excluded — wrong city or no confirmed address), city switcher, verified live, zero
bbox-skip warnings. Public GitHub repo `RikepilB/peru-tech-map`. All prior session work (Costa
Verde docs/prototype, handoff tree) committed + pushed on branch `chore/session-2026-07-08-sync`
(never pushed to `master` directly, per repo rule) — not yet merged/PR'd. Newest changes (hover
differentiator + companies.json update) still uncommitted on that branch.

**Rebrand status: Costa Verde v3 — highlight/latency bugs fixed, hover differentiator added,
two more real bugs found + fixed, still under review.** Company-building highlight now has a
subtle idle tint + a bright emerald hover pop (MapLibre feature-state), not just an always-on
solid block. Adding the hover feature surfaced two pre-existing bugs that were silently blocking
the highlight from ever showing at the zoom users actually use: (1) the base style's `building`
layer capped at `maxzoom:14`, but clicking a company flies to zoom 16 — extended the layer's
zoom range; (2) `fill-extrusion-opacity` doesn't support MapLibre feature-state expressions,
which was silently failing `addLayer` for the 3D highlight every load (console error, no crash)
— fixed by keeping 3D opacity constant and driving hover off color only. Both verified fixed via
live screenshots + direct feature-state checks in 2D and 3D modes, zero console errors. Also
surveyed the Spaceship Domain Manager for `perugrid.com` (read-only): default nameservers,
WHOIS private, no URL redirect or email forwarding configured yet — domain is idle, ready
whenever a deploy is approved.

**Not yet approved as final** — user is reviewing the fixed version live before any promotion.
HARD GATE still applies, no edits to the real `index.html` yet. Local dev server intentionally
left running (port 8000). Deploy target: Vercel + Spaceship domain `perugrid.com` (only domain
on the account, already registered).

**Boot-hang bug found + fixed (uncommitted).** `index-costaverde.html` had a real, reproducible
silent-hang bug: it trusted `<script defer>` ordering to guarantee MapLibre GL (from unpkg CDN)
loaded before the app used it — when unpkg hiccupped, the browser silently skipped the failed
defer script (spec behavior, no error), leaving `maplibregl` undefined and the loader frozen
forever at "MOUNTING COMPANY GRID… 0%" with zero feedback. Fixed: app now waits for an explicit
`window.__mapLibReady()` signal instead of trusting script order, auto-retries once from jsDelivr
on unpkg failure, and a new boot watchdog shows a visible error + Reload button on any future
failure (thrown error, rejected promise, or 15s timeout) instead of hanging silently. Verified
across 4 independent fresh reloads. Uncommitted on `chore/session-2026-07-08-sync` — awaiting
user go-ahead to commit.

**DNS: Spaceship side done, Vercel side pending.** Added `A @ → 76.76.21.21` and
`CNAME www → cname.vercel-dns.com` in Spaceship's Advanced DNS for `perugrid.com` (both
ADDED / IN PROPAGATION as of 2026-07-13). Still needed: create/link a Vercel project for this
repo and add `perugrid.com` as a custom domain there (Project → Settings → Domains) to
complete the "Valid Configuration" handshake — not done yet, no `.vercel/project.json` in repo.
Full detail in `2026-07-06-initial-build/HANDOFF.md` (2026-07-08 continuation sections) and
`2026-07-08-4609ae8d/HANDOFF.md` (this continuation's bug-fix + hover-feature + DNS-setup
detail).

---

## Session index (append-only, newest first)

- 2026-07-08-4609ae8d (2026-07-13 check-in, part 2) — Reproduced and root-caused a real silent
  boot-hang bug in `index-costaverde.html` (unpkg `defer`-script race left `maplibregl`
  undefined with zero error). Fixed with an explicit `__mapLibReady()` gate, jsDelivr CDN
  fallback, and a boot watchdog that surfaces any future failure instead of hanging silently.
  Verified across 4 fresh reloads. Uncommitted, awaiting user go-ahead.
- 2026-07-08-4609ae8d (2026-07-13 check-in) — Set up `perugrid.com` DNS in Spaceship for the
  Vercel deploy: added `A @ → 76.76.21.21` and `CNAME www → cname.vercel-dns.com` (both IN
  PROPAGATION). No existing records to purge (domain was clean). Vercel-side project
  creation/domain-add still pending.
- 2026-07-08-4609ae8d — Committed/pushed all pending Costa Verde work on branch
  `chore/session-2026-07-08-sync` (excluded 16 unrelated third-party `.claude/skills/*`
  folders). Found + fixed two real bugs the user caught live in `index-costaverde.html`: the
  company-building highlight was lighting up every building (base color too light + oversized
  generalized tile polygons counted as real footprints — added a size guard), and the page felt
  slow (debounced the highlight recompute). Cross-checked `companies.json` against a reference
  doc: added SeguroSimple (54 total), excluded Aviva/Paqta/MrPink VC (wrong city or no confirmed
  address). Wired `FORM_ENDPOINT` to the user's email and live-tested the add-company flow
  end-to-end. Added a hover differentiator to the building highlight (idle dim tint, bright
  emerald on hover via feature-state) and fixed two real bugs it surfaced: a `building` layer
  maxzoom cap blocking all buildings above zoom 14, and an invalid `fill-extrusion-opacity` data
  expression silently failing the 3D highlight layer. Surveyed the Spaceship Domain Manager for
  `perugrid.com` (read-only, nothing configured). Scoped the Vercel + `perugrid.com` deploy but
  did not execute it — user chose to review the fix live first. User explicitly declined a Neon
  DB backend for add-company, keeping the zero-dependency static-site architecture.
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
<!-- Latest auto-snapshot: docs/handoff/2026-07-08-4609ae8d/snapshot-041419.md -->
## Latest auto snapshot — 2026-07-09T04:14:19.229Z
- Session folder: `docs/handoff/2026-07-08-4609ae8d/`
- Snapshot file: `docs/handoff/2026-07-08-4609ae8d/snapshot-041419.md`
- Branch: chore/session-2026-07-08-sync
