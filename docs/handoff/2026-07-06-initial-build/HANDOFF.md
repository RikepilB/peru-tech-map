# Session — 2026-07-06 — initial-build

## Goal
Build Peru Grid: an interactive MapLibre GL map of real startups/tech-consultancies/coworking/
incubators in Lima and Arequipa, then restructure it to match the reference repo layout of
[MapleBudget/toronto-tech-map](https://github.com/MapleBudget/toronto-tech-map) (BUILD416),
and make the repo itself AI-native via `project-scaffold`.

## What was done
- Researched 33 real entities (18 Lima, 15 Arequipa) via two parallel web-search agents —
  includes Manantial Tecnológico (real AWS/Oracle cloud partner) as specifically requested.
- Built v1: `index.html` + `data.json`, own dark-theme design, city switcher, 3D toggle,
  sidebar sync, coordinate guard — verified live in Chrome.
- Fetched the actual BUILD416 repo (README, index.html, companies.json, ticker.json, LICENSE,
  LICENSE-DATA, CODEOWNERS, .gitignore, PR template) via `gh api` to clone its real structure
  rather than guess from the blog post alone.
- Rebuilt as v2 to match BUILD416 exactly: `companies.json` (renamed from `data.json`, BUILD416
  schema with `funding.type` repurposed as a category — see `docs/decisions.md`), `ticker.json`,
  terminal-console UI (Solarium green monochrome), city switcher added on top of the clone,
  `README.md`/`LICENSE`/`LICENSE-DATA`/`CODEOWNERS`/`.gitignore`/`.github/PULL_REQUEST_TEMPLATE.md`.
- Verified live: dark theme, ticker, city switch (Lima 18 ↔ Arequipa 15, zero bbox-skip
  warnings), sidebar↔marker↔popup sync, pin fan-out, favicon-service logos with initial-letter
  fallback. 3D `easeTo` animation didn't visibly complete in the automated browser tab
  (traced to rAF throttling on that tab, not a code bug — `map.jumpTo` reached the target
  instantly and the layer-visibility swap logic fired correctly).
- Ran `project-scaffold` (`--lang ts`) to make the repo AI-native: `.claude/CLAUDE.md`,
  `AGENTS.md`, `opencode.json`, `docs/{architecture,decisions,branding}.md`, this handoff tree,
  `.github/ISSUE_TEMPLATE.md` + `workflows/ci.yml`, `.claude/rules/`, `.claude/agents/`,
  `.claude/commands/`. 5 files skipped as already-existing (README, LICENSE, etc.) — idempotent.
- Fixed the scaffold's generic `--lang ts` mismatch for a zero-dependency static site:
  rewrote `ci.yml` (was pnpm/npm build pipeline — replaced with JSON-validation checks),
  rewrote `.claude/rules/peru-tech-map-architecture.md` (was assuming `src/<domain>/` modules
  — replaced with the actual single-file shape), filled `.claude/CLAUDE.md`'s package-manager
  TODO, filled `docs/branding.md` and `docs/architecture.md`, added two ADR entries to
  `docs/decisions.md` (funding-type repurposing, no-local-logos decision).
- User supplied a ~30-entry "comprehensive Lima directory" (AI/SaaS startups, VC funds,
  accelerators) to cross-reference against the map. Two research agents fact-checked every
  entry (SUNAT/RUC registry, official sites, Crunchbase/YC/PitchBook). Added 20 verified new
  Lima entries (companies.json now 38 Lima + 15 Arequipa = 53 total); skipped 6 unverifiable/
  defunct ones (Ovenfo, Artificio, Domus AI, Syntax, GoJom, MrPink VC) — full rationale in
  `docs/decisions.md`. Added a new `"Fund"` funding.type category (Salkantay Ventures, Winnipeg
  Capital, AVP Ventures, PECAP) — updated `index.html`'s MUTED_FUNDING_TYPES set, the
  add-company modal's category select, README, and PR template to match. Updated ticker.json's
  STAT line (33→53) and added a YC-alumni headline. Verified live: 38 Lima places, zero
  bbox-skip warnings.
- Now mid-brainstorm (in progress, not yet decided) on a visual rebrand — user wants to move
  away from the BUILD416 terminal-console clone toward a distinct Peru/Andean visual identity,
  keeping the "Peru Grid" name. Using `superpowers:brainstorming` skill + visual companion
  browser tool (server started, `.superpowers/brainstorm/` — add to `.gitignore` before commit).
  No design decisions made yet as of this note.

## Files changed
- `index.html`, `companies.json`, `ticker.json` (core app)
- `README.md`, `LICENSE`, `LICENSE-DATA`, `CODEOWNERS`, `.gitignore`, `.github/PULL_REQUEST_TEMPLATE.md`
- `.claude/CLAUDE.md`, `.claude/rules/peru-tech-map-architecture.md`, `.github/workflows/ci.yml`
  (all hand-edited after scaffold to fit a static-site project, not the ts/npm default)
- `docs/architecture.md`, `docs/decisions.md`, `docs/branding.md` (filled from scaffold TODOs)
- Everything else project-scaffold generated (`.claude/agents/`, `.claude/commands/`,
  `.claude/rules/common/`, `.claude/rules/typescript/`, `AGENTS.md`, `opencode.json`,
  `.mcp.json`, `.env.example`, `tests/{unit,integration,e2e}/.gitkeep`) — left as scaffold
  defaults, mostly inert for this project (no real tests/secrets to speak of yet).

## Failed attempts
None outright failed — the only wrinkle was the 3D-toggle animation not visibly completing
in the automated test browser (see above); confirmed non-fatal via `jumpTo` + layer-state checks.

## Next steps
1. **In progress:** finish the visual-rebrand brainstorm (Peru/Andean identity direction picked;
   color palette/typography/component treatment still being decided via the visual companion)
   → design doc → writing-plans → implementation.
2. Configure `FORM_ENDPOINT` in `index.html` with a real FormSubmit-verified email (currently
   `YOUR_EMAIL_HERE` placeholder) before the "Add A Company" modal is live.
3. Confirm the real GitHub handle for `CODEOWNERS` (currently placeholder `@ridi.pillaca`).
4. Decide whether to `git init` + push this as its own repo (the scaffold's `--publish` flag
   can do this) — not done yet, no `git` history exists for this project.
5. Optional: spot-check the 3D toggle's smooth animation in a normal (non-automated) browser tab.
6. Optional: add real `assets/logos/*.png` overrides for any entry whose favicon doesn't render
   well, per `docs/decisions.md`'s no-local-logos-yet decision.
7. Optional: manually verify Artificio/Domus AI addresses (real companies, just no locatable
   office found) if a contributor turns up a district/street later.

## Files in this folder
- HANDOFF.md — this digest
- transcript.md — full /export (if captured)
- snapshot-*.md — auto git-snapshots (PreCompact hook)
