# Skills (project manifest)

**Hybrid model:** this project does **not** copy skills in. It uses your **global** skills at
`~/.claude/skills/` (they evolve fast — copying would freeze them). This file is the index of
which ones matter here + how to add a project-local one.

## Global skills that apply here
- `catch-up` — fast orientation at session start (reads the handoff tree + git).
- `deep-catch-up` — deep audit (codebase map + risks + plan). Opt-in; token-heavy.
- `handoff-context` — record a session into `docs/handoff/` (append-only).
- `project-scaffold` — re-run scaffolding, `--inventory` (prune report), `--publish`.
- _add the ones you actually use; see `project-scaffold --inventory` for the full annotated list._

## Add a project-local skill
Create `.claude/skills/<name>/SKILL.md` (folder name must equal the frontmatter `name:`).
Project skills override global ones of the same name. Commit them — they are part of the prompt.
