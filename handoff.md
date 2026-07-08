# Goal
Rebrand Peru Grid's visual design away from the BUILD416 terminal-console clone toward a
distinct Peru/Andean identity ("Nazca Desert" direction), while keeping data/JS logic intact.
Full session history lives in `docs/handoff/` (this repo's own tree) — this file is a
quick-glance snapshot, not a replacement.

## Current state
Still in the `superpowers:brainstorming` design phase (HARD GATE: no implementation on the real
`index.html` until design approved + spec written). Working-baseline decisions so far: name
stays "Peru Grid"; palette = Nazca Desert (sand `#E8DCC8` bg, rust-red `#8C3B2E` accent,
clay-brown `#2A1E17` ink, tan `#B79C7A` muted); typography = serif display + sans body (drops
Geist Mono); loader = simple fade-in; ticker = keep scrolling reel, reskin only; markers = single
rust-red line-drawn SVG pin. The abstract browser-companion mockup didn't land for the user
("doesn't convince me"), so instead built a real live prototype, `index-nazca.html` — same
MapLibre setup/data as `index.html`, only the skin changed — served at
`http://localhost:8000/index-nazca.html` next to the untouched original at
`http://localhost:8000/` for direct comparison. User's verdict: **"is ok but i will change the
design again"** — accepted as a starting point only, NOT the final locked design.

## Files in flight
None being actively edited right now (session ending). `index-nazca.html` (new file, repo root)
is the current design prototype and will likely change again next session per user's own note.

## Changed
This session: added `index-nazca.html` (new, real live Nazca-reskinned prototype, shares
`companies.json`/`ticker.json` with `index.html` — no data fork). Earlier in this same
multi-day session (already committed/pushed): `index.html`, `companies.json`, `ticker.json` (v2
rebuild to match BUILD416 structure + 53 real Lima/Arequipa entries), `README.md`, `LICENSE`,
`LICENSE-DATA`, `CODEOWNERS`, `.gitignore`, `.github/PULL_REQUEST_TEMPLATE.md`,
`.github/workflows/ci.yml`, `.claude/CLAUDE.md`, `.claude/rules/peru-tech-map-architecture.md`,
`docs/{architecture,decisions,branding}.md` — repo made AI-native via `project-scaffold` and
pushed as public GitHub repo `RikepilB/peru-tech-map`.

## Failed attempts
The browser visual-companion tool (abstract card mockup) didn't work for this user — first they
reported not seeing it at all, then after a real prototype was built instead they said the
mockup approach itself "doesn't convince me." Lesson: for this user, skip the abstract
companion mockup step and go straight to a real live prototype file for visual decisions.

# Next steps
1. Next session: ask what specifically to change about the Nazca Desert prototype (palette?
   typography? marker shape? something else entirely?) before writing
   `docs/superpowers/specs/2026-07-06-rebrand-design.md`. HARD GATE still applies — no edits to
   `index.html`'s real CSS/JS until a design is explicitly approved as final.
2. Outstanding unrelated TODO: wire real `FORM_ENDPOINT` email in `index.html` (and
   `index-nazca.html` if it survives).
