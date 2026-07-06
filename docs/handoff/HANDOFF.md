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
    transcript.md             ← optional full /export archive
```

**Rules:** append, never overwrite. Only the father's `## Current state` is replaced each
session. Solved tasks → one concrete one-liner (file / PR / command).

---

## Current state — 2026-07-06

Peru Grid built and working: MapLibre GL + OpenFreeMap map of **53** real Lima/Arequipa places
(startups, cloud consultancies, coworking spaces, incubators, VC funds), city switcher,
terminal-console theme cloned from BUILD416, verified live in Chrome, zero bbox-skip warnings.
Repo made AI-native via `project-scaffold` (ts/npm defaults corrected for this zero-dependency
static site). **In progress (not yet decided):** brainstorming a visual rebrand away from the
BUILD416 clone toward a Peru/Andean identity, keeping the "Peru Grid" name — visual companion
browser tool open, no design locked yet. Not yet a git repo / not pushed. Config TODOs
outstanding: `FORM_ENDPOINT` email, `CODEOWNERS` GitHub handle. Full detail in
`2026-07-06-initial-build/HANDOFF.md`.

---

## Session index (append-only, newest first)

- 2026-07-06-initial-build — Built Peru Grid (53 researched places after a follow-up data
  expansion, Lima+Arequipa), cloned BUILD416 structure/style, ran project-scaffold and fixed
  its ts/npm-default mismatch for this static-site project. Rebrand brainstorm in progress.
  Not yet pushed to git.

<!-- compact-handoff:auto-snapshot -->
