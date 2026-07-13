# Session — 2026-07-08 — 4609ae8d

## Goal
Wrap up the Costa Verde rebrand session: get pending work committed/pushed, fix reported
bugs in `index-costaverde.html` (highlight scope + latency), confirm data completeness, wire
the add-company form, and scope out deploying to perugrid.com on Vercel.

## What was done (concrete one-liners)
- Added a hover differentiator to the company-building highlight in `index-costaverde.html`:
  idle state now a subtle dim green tint (was a loud always-on solid block), hover brightens to
  a bold emerald pop via MapLibre `feature-state` + cursor:pointer, using real per-building ids
  on the highlight GeoJSON sources.
- Found + fixed a real bug that silently blocked the highlight (and all buildings) from ever
  rendering at the zoom users actually use: base style's `building` layer capped at
  `maxzoom:14`, but clicking a company flies to zoom 16 — extended via
  `map.setLayerZoomRange("building", 13, 24)`.
- Found + fixed a MapLibre validation bug: `fill-extrusion-opacity` doesn't support
  feature-state/data expressions — was throwing inside `addLayer` on every load, silently
  preventing `co-buildings-3d-highlight` from ever being added (console error, no thrown JS
  exception up the stack). Fixed by keeping 3D opacity constant, driving hover off
  `fill-extrusion-color` only.
- Verified live: idle-dim + hover-bright + hover-clear states confirmed via screenshots and
  direct `feature-state`/`queryRenderedFeatures` checks in both 2D (default) and 3D (toggle)
  modes; zero console errors after fixes.
- Explored Spaceship Domain Manager for `perugrid.com` (read-only, no settings changed):
  Nameservers & DNS (default Spaceship nameservers), Domain Contacts (registrant set, WHOIS
  private), Privacy (private + contact-form email protection), URL redirect (not configured),
  Email forwarding (not configured). Domain is idle, not yet pointed at any deploy.
- Committed + pushed all pending session work (Costa Verde docs/prototype, handoff tree) on
  branch `chore/session-2026-07-08-sync` (never pushed to `master` directly, per repo rule) →
  https://github.com/RikepilB/peru-tech-map/pull/new/chore/session-2026-07-08-sync
- Deleted stray `nul` junk file (broken shell-redirect artifact, not real content).
- Excluded 16 third-party `.claude/skills/*` folders (7.5MB) from the commit — user's call,
  unrelated to this repo's own code.
- Confirmed repo/domain state: GitHub repo already exists (`RikepilB/peru-tech-map`); Spaceship
  account has one domain, `perugrid.com`, already registered; no Vercel project linked yet
  (`.vercel/project.json` absent, no teams).
- Root-caused and fixed the "all buildings glow" bug in `index-costaverde.html`: (1) base
  `building-3d`/`building` fill colors were too light against the `#0F1621` bg, so every
  building read as "lit" by contrast alone — darkened the ramp (`#1E2530`→`#3A4557`); (2)
  `queryRenderedFeatures` sometimes returns a generalized block-scale MultiPolygon instead of a
  real building footprint (OpenFreeMap tile data gap) — added a `isBuildingSizedGeometry` size
  guard (~150m cap) so only real single-building geometry gets pushed into the highlight
  sources. Verified via direct MapLibre state introspection + zoomed screenshots (Culqi's real
  59m-height footprint correctly highlighted; no more citywide glow).
- Fixed the reported latency/slowness: debounced `refreshCompanyBuildingHighlights()` (was
  recomputing on every single `idle` tick during pan/zoom/3D-toggle, now 120ms debounce).
- Confirmed `companies.json` completeness: 53 entries (38 Lima + 15 Arequipa), matches the
  original research count — no other source list to diff against.
- Wired `FORM_ENDPOINT` in `index-costaverde.html` to `ridi.pillaca@gmail.com` (user's explicit
  choice: plain endpoint, not hashed) and removed the "not wired up yet" dev TODO note.
- Live-tested the add-company flow end-to-end in the browser (dropped a pin, filled a
  clearly-labeled TEST submission, got the "SUBMITTED" success state — fetch resolved `ok`).
  FormSubmit requires a one-time activation click on first use to a new email; reminded user to
  check inbox.
- Declined to build a Neon DB-backed add-company backend — user explicitly chose to keep the
  FormSubmit-email + manual-merge flow instead, since a real backend would break this repo's
  documented zero-dependency static-site rule.

## Files changed
- `index-costaverde.html` — darkened building base colors, added building-size geometry guard,
  debounced highlight refresh, wired `FORM_ENDPOINT`, removed dev TODO note. Later same session:
  added hover feature-state to both highlight layers, fixed `building` layer maxzoom cap, fixed
  invalid `fill-extrusion-opacity` data expression on the 3D highlight layer.
- `companies.json` — added SeguroSimple (real Lima address, geocoded via OSM Nominatim); did
  NOT add Aviva (Mexico-City-based, not Peru), Paqta (real Lima startup, no confirmed address),
  MrPink VC (Uruguay/Buenos Aires-based) — all three cross-checked against
  `docs/🚀 Prominent Tech Startups & Small.md` and excluded to avoid fabricated data.
- `docs/handoff/HANDOFF.md`, `docs/handoff/2026-07-06-initial-build/HANDOFF.md` — updated in a
  prior turn this session (branding-restored + highlight-feature recap).
- Committed on branch `chore/session-2026-07-08-sync`: `Map Project Storybook U.md`,
  `docs/design.md`, `docs/Gemini_Generated_Image_vel0pcvel0pcvel0.png`,
  `docs/plans/2026-07-06-costa-verde-rebrand-design.md`, `handoff.md` (root, stale/legacy —
  left as-is, not cleaned up), `index-costaverde.html`, `index-nazca.html`, handoff tree files.

## Failed attempts
- First diagnosis of the highlight bug assumed it was purely a contrast/color problem; only
  after re-testing found a second, bigger cause (oversized generalized polygons from the vector
  tile data) — needed direct source-data inspection (`getSource(...)._data.features`), not just
  screenshots, to catch it.
- Repeated premature JS state checks immediately after `navigate`/`jumpTo` returned stale/zeroed
  results (e.g. `COMPANIES.length: 0`, missing sources) because the map's `load` event hadn't
  fired yet — not a real bug, just checked too early; needed longer waits + hard-reload
  (`ctrl+shift+r`) to rule out browser-cache staleness.
- Simulating hover via `map.fire('mousemove', {point:{x,y}})` gave false negatives/positives —
  a plain `{x,y}` object isn't a real MapLibre `Point`, so `queryRenderedFeatures` misbehaved.
  Fixed by dispatching a real DOM `MouseEvent` on the canvas with `clientX/clientY`, or using the
  `computer` tool's own hover action (whose coordinate space is the screenshot resolution, not
  the page's CSS-pixel space — the two aren't 1:1 here, cost a few misfires before spotting it).

## Check-in — 2026-07-09
Session resumed after a gap; no new substantive work done (only `/remote-control` and
`/handoff-context` invocations, no code/data changes). Tree confirmed already current from the
prior update. Everything below still stands.

## Check-in — 2026-07-13
Set up `perugrid.com` DNS in Spaceship to point at Vercel (browser automation via
`/chrome`, on Spaceship's Advanced DNS page for perugrid.com). Domain had zero existing
records (no parking records to purge, unlike the article's assumption). Added:
- `A @ → 76.76.21.21` (Default record group) — status ADDED / IN PROPAGATION.
- `CNAME www → cname.vercel-dns.com` (Custom group 1) — status ADDED / IN PROPAGATION.
Hit UI friction: the host-field editor rejected direct overwrite/backspace-then-type in a
couple of attempts ("Invalid host value" on stray leftover chars) — fixed by clicking the
field, `End`, repeated `Backspace`, then typing the clean value. No Vercel-side project
step done yet (no `.vercel/project.json` in repo — project not linked/created there this
session).

## Check-in — 2026-07-13 (part 2)
`/gsd-ship` was invoked but this repo has no `.planning/` GSD project (no ROADMAP/PLAN/
VERIFICATION artifacts) — asked user, redirected to "test the page" instead of forcing GSD
structure onto a zero-dependency static site.
- Reproduced a real bug live: `index-costaverde.html` hung forever at "MOUNTING COMPANY
  GRID… 0%" on a fresh load, no error, no console output — a genuinely silent infinite hang.
- Root-caused via direct browser instrumentation (fetch-and-recompile the live script,
  page-global diagnostic log array to dodge the console-read tool's page-load timing race,
  cache-busted URLs to rule out stale-file confusion from repeated same-URL navigations):
  the page had two `<script defer>` tags (MapLibre GL from unpkg CDN, then the app) and
  relied on `defer` ordering alone to guarantee the library loaded before the app used it.
  When unpkg had a hiccup, the browser silently skipped the failed `defer` script (spec
  behavior — no error, no retry), leaving `maplibregl` `undefined` when the app called
  `new maplibregl.Map(...)`, freezing the loader forever with zero feedback.
- Fixed in `index-costaverde.html`: wrapped the app script in `bootApp()`, gated it behind
  `window.__mapLibReady()` (fires immediately if the library's already loaded, or waits for
  its real `onload` event) instead of trusting script order; added an automatic jsDelivr
  CDN fallback on unpkg `onerror`; added a boot watchdog (15s timeout, `window.onerror`,
  `unhandledrejection`) that shows a visible "BOOT FAILED" message + Reload button instead
  of an infinite silent freeze, for ANY future failure cause, not just this one.
- Verified with 4 independent fresh (cache-busted) reloads — all rendered the full map (39
  Lima companies, sidebar, ticker) within ~4-6s, `map.loaded()` confirmed `true` each time.
- Discovered as a side effect: repeated navigations to the exact same `localhost:8000` URL
  in one browser tab can silently serve a stale cached document (`document.lastModified`
  lagging behind the real file's mtime) even after local edits — a local dev-server/browser
  caching quirk, not a site bug; cache-busting query params (`?cb=...`) reliably bypass it.
  Not expected to affect real Vercel production traffic (different cache-control behavior).

## Next steps
- User to review the fixed `index-costaverde.html` live at `http://localhost:8000/index-costaverde.html`,
  including the new hover-differentiator effect on company buildings.
- User to check `ridi.pillaca@gmail.com` inbox for FormSubmit's one-time activation email and
  confirm it.
- User to decide on Paqta (real Lima startup, no confirmed address — add with approximate coords
  or skip) and confirm Aviva/MrPink VC exclusions are correct.
- Vercel side still pending: create/link a Vercel project for this repo, add `perugrid.com` as
  a custom domain in Project → Settings → Domains, then hit Refresh there to confirm
  "Valid Configuration" once DNS propagates (Spaceship side is done — A + CNAME records added,
  see check-in above).
- Once approved: promote `index-costaverde.html` → `index.html` for the actual deploy.
- Boot-hang fix (`bootApp()` + `__mapLibReady()` + jsDelivr fallback + boot watchdog) is
  applied but uncommitted on `chore/session-2026-07-08-sync` — asked user whether to commit;
  awaiting go-ahead.
- Open a PR for branch `chore/session-2026-07-08-sync` if/when user wants it merged.
- Run `/export docs/handoff/2026-07-08-4609ae8d/transcript.md` (I can't run this myself).

## Files in this folder
- `HANDOFF.md` — this file (curated digest)
- `snapshot-052823.md` — auto PreCompact snapshot
- `transcript.md` — full `/export` of the session (not yet captured)
