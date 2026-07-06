# CLAUDE.md — how Claude Code operates in this repo

Rulebook, five sections: **Role → Style → Constraints → Workflow → Quality.**

## 1. Role

Claude Code maintains peru-tech-map, a zero-dependency static site (one `index.html` plus two JSON data files) — it edits data and inline code directly, with no build tooling to run.

Loaded automatically at session start. Local overrides go in `CLAUDE.local.md` (gitignored,
repo root). This file itself lives in `.claude/` on purpose — keeps AI-operating instructions
out of the root listing; `opencode.json`/`AGENTS.md` already point here explicitly.

## 2. Style

- **Rules live in `.claude/rules/`** — `common/` + `typescript/` + `peru-tech-map-architecture.md`
  (this project's own module boundaries — see below). Guardrails (what must never happen)
  are `common/coding-rules.md` + `common/review-checklist.md`.

### Always-on coding-time skills
These apply to every change, not just one lifecycle stage — invoke via the `Skill` tool when
installed globally:
- **`ponytail`** — forces the simplest/laziest solution that actually works (YAGNI); reach
  for it before adding an abstraction, dependency, or speculative flexibility.
- **`caveman`** — terse output mode for status/progress chatter; never compresses code,
  commits, or security-relevant text.
- **`headroom`** — compresses bulky tool output/logs before they enter context; use the
  hardened wrapper only, never the bare CLI.

## 3. Constraints (never do)

- **Package manager:** none. Zero-dependency static site — one `index.html`, `companies.json`,
  `ticker.json`, no build step, no bundler, no framework. Don't introduce one.
- **Git:** never push directly to the default branch. Branch → PR → merge. Conventional commits.
- **Secrets:** never commit `.env*`, tokens, keys. Use `.env.example` for required vars.

## 4. Workflow

### Orientation
- Start a session with the `catch-up` skill (reads `docs/handoff/HANDOFF.md` + git).
- Record finished work with the `handoff-context` skill (append-only — never overwrite).

### Architecture
Module boundaries, entry points, data flow: [`.claude/rules/peru-tech-map-architecture.md`](rules/peru-tech-map-architecture.md)
(archetype: **monolith** — regenerate with a different `--archetype` if this project's
shape changes). Keep `docs/architecture.md` as the human-facing mirror; keep both in sync.

## 5. Quality (before delivering)

- **Tests:** none in the TDD/unit-test sense. CI gate validates the two JSON data files are
  well-formed and every `companies.json` entry has its required fields.

## Branding & product framing
_TODO: fill `docs/branding.md` (name/tagline/voice/audience) and the problem/solution framing
in `README.md` before this repo is considered "documented."_
