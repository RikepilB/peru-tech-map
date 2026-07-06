# Repository Guidelines

> Shared instruction file read by **Claude Code** and **Codex**. Keep it tool-agnostic;
> Claude-Code-specific workflow lives in `.claude/CLAUDE.md`.

## Project Structure & Module Organization
_TODO: where source, tests, assets, and config live._

## Build, Test, and Development Commands
_TODO: the canonical commands (install / dev / build / lint / typecheck / test)._

## Coding Style & Naming Conventions
_TODO: formatter, indentation, naming. Keep it short and enforce via tooling._

## Testing Guidelines
Tests live in `tests/{unit,integration,e2e}`. Add focused tests near changed logic.
Run lint + typecheck + tests before handing off substantial work.

## Commit & Pull Request Guidelines
Conventional commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`). PRs include the
user-facing change, verification commands, linked issue, and migration/UI notes.

## Security & Configuration
Never commit `.env*`, API keys, OAuth secrets, or uploaded artifacts. Document required
vars in `.env.example`.
