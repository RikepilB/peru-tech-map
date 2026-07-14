# Contributing to Peru Grid

Thanks for wanting to help map Peru's tech ecosystem. Anyone can open a pull request or
issue — the maintainer reviews and merges everything (see [CODEOWNERS](./CODEOWNERS)).

By participating, you agree to follow the [Code of Conduct](./CODE_OF_CONDUCT.md).

---

## Ways To Contribute

- **Add a place** — a startup, consultancy, coworking space, incubator, fund, or nonprofit
  with a genuine presence in Lima or Arequipa.
- **Fix an entry** — wrong coordinates, stale domain, outdated category.
- **Report a bug** — something broken in the map, sidebar, or add-company flow.
- **Improve the code** — `index.html` is the entire app (no build step, no framework).

No contribution is too small. Typo fixes and single-field corrections are welcome.

---

## Ground Rules

This is a **zero-dependency static site** — `index.html`, `companies.json`, `ticker.json`,
nothing else. PRs that introduce a build step, a framework, or an npm dependency will be
declined regardless of how good the idea is. If you think this constraint needs to change,
open an issue to discuss it first — don't build against it speculatively.

---

## Adding Or Editing A Place

1. **Fork** the repo and create a branch: `add/<company-name>` or `fix/<what-changed>`.
2. Edit `companies.json` directly — see the [Data Format](./README.md#data-format) section
   in the README for the schema and required fields.
3. Validate your JSON before opening a PR:
   ```bash
   python3 -m json.tool companies.json > /dev/null && echo OK
   ```
4. Run the site locally and confirm your pin lands in the right spot:
   ```bash
   python3 -m http.server 8000   # then open http://localhost:8000
   ```
5. Open a PR using the template — fill in the **name, city, coordinates, source**. A source
   link (company site, press release, LinkedIn) speeds up review a lot.

**What gets accepted:**
- ✅ Real companies/places with a genuine, sourceable presence in Lima or Arequipa.
- ✅ Coordinate/detail corrections to existing entries.
- ❌ Entries outside the two cities' bounding boxes (see README).
- ❌ Unverifiable claims, marketing copy, or duplicate entries.

---

## Code / Design Changes

1. Branch off `master` — never commit directly to it.
2. Keep the single-file architecture: everything lives in `index.html`'s inline `<script>`
   and `<style>` blocks. Don't split it into modules or add a bundler.
3. Keep Solarium green (`#056540` / `#0FA968`) as the only accent color.
4. Test locally over HTTP (not `file://` — the app fetches JSON at runtime and needs CORS).
5. Open a PR describing what changed and how you tested it.

---

## Pull Request Process

- CI validates that `companies.json`/`ticker.json` are well-formed JSON and every company
  entry has its required fields. A red CI check blocks merge.
- [CODEOWNERS](./CODEOWNERS) auto-requests the maintainer's review on every PR — nothing
  merges without it.
- Use [Conventional Commits](https://www.conventionalcommits.org/) style for commit
  messages (`feat:`, `fix:`, `docs:`, `chore:`, etc.) where practical.
- Keep PRs focused — one company addition, one bug fix, one feature. Large mixed PRs are
  slower to review.

---

## Reporting Issues

Use the [issue templates](../../issues/new/choose) — pick **Add a company**, **Bug report**,
or **Feature request** depending on what you're filing. For security vulnerabilities, see
[SECURITY.md](./SECURITY.md) instead of opening a public issue.

---

## Questions?

Open a [discussion or issue](../../issues) — no question is too basic.
