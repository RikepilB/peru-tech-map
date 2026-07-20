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

## Current state — 2026-07-20 (cb310615, part 7)

**FormSubmit activated, live, wired to the hashed endpoint; two real submissions (Orexe,
Tecretail) reviewed and added; a real UI bug (Stage field not showing) found already-fixed
uncommitted, shipping it now.**

- FormSubmit's activation email confirmed real (user clicked "Activate Form"). Fixed the
  underlying issue it existed for: `FORM_ENDPOINT` in `index.html` was posting to the naked
  email `ridi.pillaca@gmail.com` in public client-side JS — swapped for FormSubmit's hash
  endpoint (`formsubmit.co/ajax/bbd1d388bad84c6ba3b9b23d6c784867`) so the real address isn't
  scrapable from page source. Updated `README.md`'s stale "aún no configurado" line to match.
- Two real submissions arrived once the form activated: **Orexe** (orexe.io — web-verified as
  a real remote-first Lima cloud/platform-engineering consultancy, classified `Consultancy`
  not the submitter's self-picked `Startup`, matching this dataset's existing convention) and
  **Tecretail** (tecretail.org — verified real, San Borja-based retail ERP SaaS, founded 2024).
  Both added to `companies.json` with bilingual `tag`/`tag_es` (80 entries total).
- **Found and reverted a real data-corruption bug**: a separate session ("Project Control",
  `docs/handoff/2026-07-18-project-control/`) had mojibake-corrupted this entire father
  `HANDOFF.md` file when it edited it — every em-dash/accented char turned to garbage
  (`ÃƒÆ’Ã‚Â¢...`) via what looks like a UTF-8-as-Latin1 double-encoding round-trip. Reverted to
  the clean version before committing anything; re-added that session's legitimate content
  below with correct encoding by hand (their own per-session `HANDOFF.md` file was NOT
  corrupted, only this shared father file was — worth checking any other tool that writes to
  this file for the same bug before it happens again).
- **User flagged (via screenshot) that the add-company modal's Stage selector never
  appears**, even with Category defaulting to "Startup". Root-caused on the live production
  site: `index.html`'s `catSelect` only toggled `stageField`'s visibility on the dropdown's
  `change` event — never on initial page load, so a user who never touches the Category
  dropdown (it's already "Startup" by default) never sees the Stage field. **This exact fix
  already existed uncommitted in the working tree** (refactored to a named `toggleStage()`
  function with an explicit initial call) — not made by this session, just verified correct
  live via a local server + browser automation (`catSelect.value` = "Startup",
  `stageField` computed `display: block`) and now included in the ship.
- `companies.json`/`ticker.json` still valid JSON; CI green on the last few merges.

**Files changed this check-in (about to commit/ship):** `index.html` (FORM_ENDPOINT hash,
pre-existing stage-field fix + stage-option reorder), `README.md` (FormSubmit status line),
`companies.json` (+Orexe, +Tecretail).

**Still unresolved, flagged repeatedly:** untracked `.claude/skills/*`, `.agents/`, `.codex/`
dirs, and a recurring stray `nul` file — same unresolved cleanup item as parts 5/6.

## Current state — 2026-07-18 (Project Control)

Sesión transversal (no específica de peru-tech-map): se implementó `project-control` como
CLI global local-first, disponible desde Codex, Claude Code, OpenCode y terminales de
Windows. `project-control status -All` actualiza el inventario de las cuatro raíces
registradas (PROYECTOS, workspace, Second Brain y project ledger) y muestra el resumen
global.

Estado verificado: 46 `project_id` únicos, 20 handoffs enlazados y 108 sesiones/exportaciones
Codex deduplicadas. Las vistas viven en `Second Brain/02_Execution/Project_Control/`; el
estado mínimo vive en `C:\Users\a2021\.project-control\`. No se cerraron procesos ni se
eliminaron sesiones.

Mantenimiento temporal instalado: revisión local diaria 22:30 (límite 5 min), inventario
semanal domingo 18:00 (20 min) y desactivación automática 2026-08-01. `cleanup-plan` y
`compact-plan` solo proponen cambios; `apply` exige `-Confirm`.

Uso cotidiano simplificado: el atajo global `pc` permite usar `pc`, `pc recursos`, `pc
semana`, `pc global`, `pc tareas`, `pc salud` y `pc ayuda` sin recordar la interfaz completa.
No hace falta entrar a cada repo: los proyectos se resuelven desde la carpeta actual y `pc
global` revisa todas las raíces registradas.

El centro del Second Brain ahora incluye `02_Execution/Project_Control/CHEATSHEET.md` como
referencia única de rutina, comandos completos, estados y protecciones.

`codex-export` fue corregido para exportar una sesión activa mediante lectura compartida; el
paquete trazable de esta sesión vive en `docs/handoff/2026-07-18-codex-019f64cf81ed/` y
conserva el puntero activo del árbol.

El estado de producto de peru-tech-map en el momento de esa sesión: PR #22 abierto (ya
mergeado desde entonces — ver check-in 2026-07-20 arriba); los cambios de esa sesión no
tocaron `index.html`, `companies.json` ni el deploy.

*(Nota de la sesión 2026-07-20: el texto de esta sección estaba corrupto por un problema de
codificación — reescrito arriba con los acentos correctos a partir del original en
`docs/handoff/2026-07-18-project-control/HANDOFF.md`, que sí quedó íntegro.)*

## Current state — 2026-07-18 (cb310615, part 6)

**Shipped the Phase-1 Spanish-docs translation diff found in part 5 — PR #22, open, not yet
merged: https://github.com/RikepilB/peru-tech-map/pull/22.** `/gsd-ship` was invoked but this
repo has no `.planning/` tree (`phase_found: false`), so shipped manually per the repo's own
branch→PR convention instead: branch `docs/phase1-spanish-internal-docs`, commit `99a0d9c`
(11 translated docs + new `PLAN.md` + handoff updates + session snapshot/transcript files),
pushed, PR opened. Deleted the stray `nul` junk file along the way.

**Next once #22 merges:** flip `index.html`'s `getLang()` (line 109) default to `"es"` —
closes #15, one-liner, not yet made. Then Phase 2 (#16→#18: `tag_es` field + translate 75
company tags) before Phase 3 (#17→#19: taxonomy redesign), per `PLAN.md`'s own dependency
order.

**Still unresolved, flagged twice now:** untracked `.claude/skills/*`, `.agents/`, `.codex/`
dirs sitting in the working tree (look like global skill-sync/tool bootstrap output, not
peru-tech-map deliverables) — need a keep/gitignore/remove decision before they cause noise
in a future PR.

Full detail in `2026-07-13-cb310615/HANDOFF.md` part 6.

## Current state — 2026-07-17 (cb310615, part 5)

**Ran a read-only `/deep-catch-up` this session — no code shipped, but surfaced an
uncommitted Phase-1 translation diff (11 files, 490+/383-) plus a new `PLAN.md` sitting in
the working tree with no branch.** `PLAN.md` (Spanish) lays out 3 phases matching issues
#16-19: Phase 1 (docs+default-lang, in progress uncommitted), Phase 2 (bilingual `tag`
field, not started), Phase 3 (category/subcategory taxonomy, not started, depends on Phase 2
per the plan). Verified by reading code: `index.html`'s `getLang()` (line 109) is still
browser-locale-based (#15 not done), `companies.json` schema unchanged (`tag` single-lang,
`funding.type` flat string — #16-19 not started). All 12 issues (#8-19) confirmed still open
via `gh issue list`. **User was asked to choose next move (ship Phase-1 diff vs. jump to
Phase 2) — answer not yet received when this check-in was written.**

Also flagged, not actioned: a pile of new untracked `.claude/skills/*`, `.agents/`, `.codex/`
dirs (looks like global skill-sync output, not project work) and a stray dead `nul` file —
both need a decision before the next commit touches this working tree.

Full detail in `2026-07-13-cb310615/HANDOFF.md` part 5.

## Current state — 2026-07-14 (cb310615, part 4)

**All outstanding work now tracked as 12 GitHub issues (#8–#19)**, filed via
`/handoff-to-issues` — see that skill's mirrored copy on the repo instead of re-deriving
next-steps from this file's prose. Two are pending big features the user explicitly asked to
start next: **#16→#18** (translate all 75 company `tag` descriptions to Spanish — schema
slice first, then content) and **#17→#19** (redesign categories: `Startup` w/ funding
subcategory Pre-Seed/Seed/Bootstrap/Series A+, plus sibling categories
Incubator/Accelerator/VC/Nonprofit/Consultancy/Coworking — schema+data slice first, then
sidebar filter rework). **#15** (flip product-UI default language to Spanish) is small and
still open, not yet actioned.

**Repo docs are now fully Spanish** — README, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, PR
template, all issue templates (PR #20, merged). Standing rule added to `.claude/CLAUDE.md`:
this is a Peru-focused project, new repo-facing docs get authored in Spanish from the start.
Code/commits/`.claude/` tooling and the product UI's own independent EN/ES toggle are
unaffected — separate concern.

**LIVE at perugrid.com.** The `deploy_to_vercel` MCP tool's 403 (`project:create` permission
gap) was never fixable from the Claude side — worked around by importing the GitHub repo
directly in the Vercel dashboard instead. Project `peru-tech-map` (team
`rikepilbs-projects`) is now GitHub-linked to `master`, with `perugrid.com` +
`www.perugrid.com` attached and SSL verified. **Every future push to `master` auto-deploys**
— no more manual deploy tool needed.

**`companies.json` is 75 entries, all committed.** The 6-entry ONGs/fintech batch from the
prior check-in shipped via PR #3 (merged).

**UI polish shipped (PR #4, merged):** tagline "Where The Builders Are" is now bold
green-bright (was 10px muted gray); desktop sidebar has a collapse toggle (`#panelToggle`,
slides the 320px panel off-screen) so the full map is viewable.

**Open-source readiness shipped (PR #5, merged):** added `CONTRIBUTING.md`,
`CODE_OF_CONDUCT.md`, `SECURITY.md`, structured `.github/ISSUE_TEMPLATE/` (Add A Company /
Bug Report / Feature Request), enabled GitHub Discussions, README badges, and a small GitHub
icon/link in the site UI next to the language toggle. Repo already had LICENSE/CODEOWNERS/
PR-template/CI from earlier sessions. **Not done:** branch-protection rule on `master` — left
for the user to enable in GitHub Settings → Branches.

**`index.html` is the live Costa Verde rebrand with EN/ES i18n, merged to `master`** (PR #1:
https://github.com/RikepilB/peru-tech-map/pull/1). Boot-hang watchdog + `__mapLibReady()`
gating, full EN/ES UI-chrome toggle. Company data (names/taglines/funding types) intentionally
NOT translated.

Full detail in `2026-07-13-cb310615/HANDOFF.md` (both check-ins).

**DNS: Spaceship side done, Vercel side still pending.** Added `A @ → 76.76.21.21` and
`CNAME www → cname.vercel-dns.com` in Spaceship's Advanced DNS for `perugrid.com` (both
ADDED / IN PROPAGATION as of 2026-07-13). Still needed once a Vercel project exists: add
`perugrid.com` as a custom domain (Project → Settings → Domains) to complete the "Valid
Configuration" handshake. Full detail in `2026-07-06-initial-build/HANDOFF.md`, and
`2026-07-08-4609ae8d/HANDOFF.md` (bug-fix + hover-feature + DNS-setup detail).

---

## Session index (append-only, newest first)

- 2026-07-13-cb310615 (2026-07-20 check-in, part 7) — Fixed FormSubmit's exposed-email
  endpoint, added 2 web-verified real submissions (Orexe, Tecretail), shipped a pre-existing
  uncommitted fix for the add-company Stage-field-never-shows bug, and reverted a mojibake
  encoding corruption another session had introduced into this father file.
- 2026-07-18-project-control — Global (non-peru-tech-map-specific) session: built the
  `project-control` CLI + `pc` shortcut, verified inventory across 4 registered roots. Did not
  touch this repo's product code. Its current-state note above was corrupted by an encoding
  bug when first written; rewritten with correct accents in the 2026-07-20 check-in.
- 2026-07-13-cb310615 (2026-07-18 check-in, part 6) — `/gsd-ship` invoked but this repo has no
  `.planning/` tree; shipped manually instead — branched, committed the part-5 Phase-1
  translation diff + `PLAN.md` + handoff files, pushed, opened PR #22 (open, unmerged).
- 2026-07-13-cb310615 (2026-07-17 check-in, part 5) — Read-only `/deep-catch-up`: found an
  uncommitted Phase-1 Spanish-translation diff (11 docs files) and a new `PLAN.md` sitting
  unbranched in the tree, confirmed by code inspection that #15 (default lang) and #16-19
  (i18n descriptions + taxonomy) are genuinely not started, delivered a full briefing, asked
  user to pick the next move — awaiting answer.
- 2026-07-13-cb310615 (2026-07-14 check-in, part 4) — Ran `/handoff-to-issues`: filed 12
  GitHub issues (#8–#19) covering everything left in the tree plus 3 new asks (Spanish
  default, description translation, category/subcategory taxonomy), tracer-bullet sliced
  where big (schema-first issues block their content/UI follow-ups). Translated all
  repo-facing docs (README/CONTRIBUTING/CODE_OF_CONDUCT/SECURITY/PR+issue templates) to
  Spanish and added a standing Spanish-docs rule to `.claude/CLAUDE.md` — PR #20, merged.
- 2026-07-13-cb310615 (2026-07-14 check-in, part 3) — Fixed the Vercel deploy for good:
  worked around the `deploy_to_vercel` tool's unfixable 403 by importing the GitHub repo
  directly in the Vercel dashboard — `perugrid.com` is now live and auto-deploys on every
  push to `master`. Shipped the pending 75-entry `companies.json` batch (PR #3), a more
  prominent tagline + desktop sidebar collapse toggle (PR #4), and a full open-source
  readiness pass — CONTRIBUTING/CoC/SECURITY/issue templates/Discussions/README badges/
  GitHub link in the UI (PR #5).
- 2026-07-13-cb310615 (2026-07-14 check-in, part 2) — Code-reviewed the taxonomy diff (clean),
  shipped it via branch→PR#2→merge to master. Retried Vercel deploy post-merge — confirmed
  durably blocked (403, same `project:create` permission gap). Added 3 user-supplied ONGs/
  Comunidades entries (sourced via WebFetch, placed at named-neighbor coords) and 3 new
  user-supplied startups (correctly deduped 2 of 5 already in the dataset). `companies.json`
  69→75, uncommitted.
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
<!-- Latest auto-snapshot: docs/handoff/2026-07-13-cb310615/snapshot-025657.md -->
## Latest auto snapshot — 2026-07-14T02:56:57.432Z
- Session folder: `docs/handoff/2026-07-13-cb310615/`
- Snapshot file: `docs/handoff/2026-07-13-cb310615/snapshot-025657.md`
- Branch: master
