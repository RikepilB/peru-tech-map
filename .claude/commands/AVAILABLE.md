# Available commands (not installed by default)

The scaffold copied a **curated subset** into `.claude/commands/`:
`plan`, `tdd`, `code-review`, `verify`, `refactor-clean`, `e2e`, `update-docs`.

Everything below exists in your template but was **not** copied — add on demand by
copying `template/.claude/commands/<name>.md` into `.claude/commands/`.

| Command | Use case |
|---|---|
| `/build-fix` | Fix a failing build / type errors with minimal diffs. |
| `/checkpoint` | Snapshot session state as a recoverable checkpoint. |
| `/claw` | Project-specific automation entrypoint (review before use). |
| `/eval` | Run an evaluation harness over a skill/output. |
| `/evolve` | Iteratively improve a skill/prompt from feedback. |
| `/go-review` | Go-language code review pass. |
| `/go-test` | Generate/run Go tests. |
| `/instinct-export` | Export learned 'instincts' / preferences. |
| `/instinct-import` | Import learned 'instincts' / preferences. |
| `/instinct-status` | Show current 'instinct' state. |
| `/learn-eval` | Evaluate a learning/tutoring run. |
| `/learn` | Tutoring mode — diagnose then teach (also a global skill). |
| `/multi-backend` | Fan out backend work across parallel agents. |
| `/multi-execute` | Execute a multi-agent plan. |
| `/multi-frontend` | Fan out frontend work across parallel agents. |
| `/multi-plan` | Plan work for multi-agent execution. |
| `/multi-workflow` | Orchestrate a multi-step multi-agent workflow. |
| `/orchestrate` | General multi-agent orchestration entrypoint. |
| `/pm2` | Manage long-running dev processes via pm2. |
| `/python-review` | Python-language code review pass. |
| `/sessions` | List/manage prior sessions. |
| `/setup-pm` | Set up the process manager (pm2) for the project. |
| `/skill-create` | Scaffold a new skill (skill-creator flow). |
| `/test-coverage` | Report/raise test coverage. |
| `/update-codemaps` | Regenerate codemaps/docs of the codebase. |

> Tip: run `node scaffold.mjs --inventory` for a usage-ranked view of skills,
> commands, and plugins — including never-used items worth pruning.
