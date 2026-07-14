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

## Current state — 2026-07-14 (cb310615)

**Taxonomy expansion + landing-view toggles built, UNCOMMITTED.** Following two research docs
(Startup Ecosystem Directory Structure taxonomy + a Lima coworking market report), `index.html`
now defaults to a Startups+Consultancies feed with 3 overlay toggle pills (Show Investors /
Show Coworking Areas / Show Non-Profits & Communities) that blend into the feed rather than
replace it — verified live via browser automation (30 → 41 places on toggle, additive not
destructive). `companies.json` grew 54 → 69 entries: added `operating_model` to all existing
entries, `funding.stage` to 5 sourced YC-batch startups, and 15 new web-verified entries
(notably Comunal Coworking — Peru's #1 chain, was missing entirely). markitdown was evaluated
for PDF conversion but SkillSpector scored it CRITICAL (100/100) — not installed; Read tool
handled the PDF fine without it. Full detail in `2026-07-13-cb310615/HANDOFF.md`.

**`index.html` is the live Costa Verde rebrand with EN/ES i18n, merged to `master`** (prior
check-in this session — PR #1: https://github.com/RikepilB/peru-tech-map/pull/1). Boot-hang
watchdog + `__mapLibReady()` gating, full EN/ES UI-chrome toggle. Company data
(names/taglines/funding types) intentionally NOT translated.

**Deploy to Vercel still BLOCKED — 403 Forbidden creating project.** `deploy_to_vercel` MCP call
(target `production`, name `perugrid`, full file upload) failed:
`"You don't have permission to create a project."` `list_teams` returned empty (personal
account, not a team-scope issue) — the Claude↔Vercel MCP connection itself lacks
`project:create` permission. Needs user to either create an empty Vercel project named
`perugrid` manually first (then retry deploy against the existing project), or re-authorize the
Vercel integration with broader scope. No MCP tool exists for attaching a custom domain or
importing a GitHub repo as a deploy source — domain attachment will need browser automation on
the Vercel dashboard once a project exists.

**DNS: Spaceship side done, Vercel side still pending.** Added `A @ → 76.76.21.21` and
`CNAME www → cname.vercel-dns.com` in Spaceship's Advanced DNS for `perugrid.com` (both
ADDED / IN PROPAGATION as of 2026-07-13). Still needed once a Vercel project exists: add
`perugrid.com` as a custom domain (Project → Settings → Domains) to complete the "Valid
Configuration" handshake. Full detail in `2026-07-06-initial-build/HANDOFF.md`, and
`2026-07-08-4609ae8d/HANDOFF.md` (bug-fix + hover-feature + DNS-setup detail).

---

## Session index (append-only, newest first)

- 2026-07-13-cb310615 (2026-07-14 check-in) — Read + analyzed two research docs (Startup
  Ecosystem taxonomy PDF, Lima coworking market report). SkillSpector-scanned markitdown for
  install (CRITICAL, blocked). Web-verified 17 candidate companies via background agent, added
  15 sourced entries + fixed a real gap (Comunal Coworking, #1 in the market, was missing).
  `companies.json` 54→69. Built the landing-view default (Startups+Consultancies) + 3 overlay
  toggle pills (Investors/Coworking/Non-Profits) in `index.html`, verified live. Declined Neon
  DB again (static JSON stays source of truth). Work uncommitted — pending review.
- 2026-07-13-cb310615 — Added full EN/ES UI-chrome i18n to the Costa Verde rebrand (toggle
  button, `I18N` dict, `localStorage` persistence; company data left untranslated). Promoted
  `index-costaverde.html` → `index.html`, committed everything pending, opened + merged PR #1 to
  `master`. Attempted Vercel deploy (`deploy_to_vercel`) — blocked by a 403 (MCP connection
  lacks `project:create` permission); domain attachment and actual deploy still pending user
  action.
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
<!-- Latest auto-snapshot: docs/handoff/2026-07-13-cb310615/snapshot-235350.md -->
## Latest auto snapshot — 2026-07-13T23:53:50.680Z
- Session folder: `docs/handoff/2026-07-13-cb310615/`
- Snapshot file: `docs/handoff/2026-07-13-cb310615/snapshot-235350.md`
- Branch: master
