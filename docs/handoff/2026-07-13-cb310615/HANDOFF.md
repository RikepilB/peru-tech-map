# Session — 2026-07-13 — cb310615

## Goal
"Make english and spanish version, then deploy the map with the domain in vercel" — add EN/ES
i18n toggle to Peru Grid, promote the Costa Verde rebrand to the real `index.html`, merge to
master, and deploy to Vercel under `perugrid.com`.

## What was done (concrete one-liners)
- Built EN/ES UI-chrome i18n in `index-costaverde.html`: `window.I18N.{en,es}` dictionary (~30
  keys), `getLang()`/`t()` helpers, `data-i18n*` attributes on all UI chrome, `applyI18N()` DOM
  scan, `#langToggle` button with `localStorage.pg_lang` persistence. Company data (names,
  taglines, funding types) deliberately left untranslated — English category vocabulary kept in
  `<option value>` to match `companies.json`.
- Verified i18n live via browser automation: toggle flips language, persists across reload,
  modal/sidebar/statusbar all translate correctly, company data stays English.
- Promoted `index-costaverde.html` → `index.html` (`cp` + `git rm` of the two prototype files
  `index-costaverde.html`/`index-nazca.html`), deleted stray junk files (`nul`, `` ` ``, `{,+`).
- Committed everything pending on `chore/session-2026-07-08-sync` (companies.json SeguroSimple
  add, DNS/boot-fix handoff docs, i18n, promotion) as `c27eb81` "feat: promote Costa Verde
  rebrand to index.html, add EN/ES toggle".
- Opened PR #1 (`gh pr create`) and merged it to `master` (`gh pr merge 1 --merge
  --delete-branch=false`) — https://github.com/RikepilB/peru-tech-map/pull/1, confirmed
  `state: MERGED`. Local `master` synced (`git pull`).
- Attempted `deploy_to_vercel` (MCP, target `production`, project name `perugrid`, all 3 files
  inlined) — **failed**, see Failed attempts.

## Files changed
- `index.html` — full rewrite: promoted from `index-costaverde.html` (dark Costa Verde theme,
  boot-hang watchdog + `__mapLibReady()` gating from a prior session, now + full EN/ES i18n
  layer). 1110 lines.
- `companies.json` — SeguroSimple entry (from a prior session), 470 lines, unchanged this turn.
- `ticker.json` — unchanged, 17 lines.
- Deleted: `index-costaverde.html`, `index-nazca.html` (superseded prototypes).
- `docs/handoff/HANDOFF.md`, `docs/handoff/2026-07-08-4609ae8d/HANDOFF.md` — DNS/boot-fix
  updates from earlier in this session's lineage, committed alongside the i18n work.

## Failed attempts
- `mcp__claude_ai_Vercel__deploy_to_vercel` (target `production`, name `perugrid`) → **403
  Forbidden**: `"You don't have permission to create a project."` `list_teams` returned `[]`
  (personal account, not a team-scope issue) — the Claude↔Vercel MCP connection itself lacks
  `project:create` permission. Not fixable from this session; needs either (a) user creates an
  empty Vercel project named `perugrid` manually first, then retry deploy against the existing
  project, or (b) user re-authorizes the Vercel integration with broader scope.
- No MCP tool exists in this session's toolset for attaching a custom domain to a Vercel project
  or for importing a GitHub repo as a deploy source — only `deploy_to_vercel` (direct upload) and
  `check_domain_availability_and_price` (buying new domains) are available. Domain attachment
  will need browser automation on the Vercel dashboard once a project exists.

## Next steps
- User to either create an empty Vercel project named `perugrid`, or re-check the Vercel
  integration's permission scope, then retry `deploy_to_vercel` (target `production`) with the
  current `master` content of `index.html` + `companies.json` + `ticker.json`.
- Once deployed: attach `perugrid.com` as a custom domain (Vercel dashboard → Project → Settings
  → Domains) — DNS is already pointed there from a prior session (Spaceship `A @ →
  76.76.21.21`, `CNAME www → cname.vercel-dns.com`, both IN PROPAGATION as of 2026-07-13).
- Verify perugrid.com renders correctly once DNS + Vercel domain verification both complete
  ("Valid Configuration" state).
- Run `/export docs/handoff/2026-07-13-cb310615/transcript.md` (user must run this, not Claude).
- Carried over from prior sessions, still outstanding: user to check
  ridi.pillaca@gmail.com inbox for FormSubmit's one-time activation email; user to decide on
  Paqta (real Lima startup, no confirmed address) and confirm Aviva/MrPink VC exclusions.

## Check-in — 2026-07-14 (taxonomy expansion + landing-view toggles)
New goal this check-in: user supplied two research docs (`Startup Ecosystem Directory
Structure.pdf` — a Gemini research chat proposing a Startup/Ecosystem-Support taxonomy +
landing-view UX; `Coworking Y Cafés En Lima.md` — a Lima coworking/coffeework/library market
report) and asked to read, analyze, and implement the suggested next steps, plus evaluate
adding markitdown as a global skill and Neon DB for the companies data.

- **markitdown skill install BLOCKED.** Scanned `github.com/microsoft/markitdown` with
  SkillSpector per the global supply-chain rule — scored 100/100 CRITICAL ("DO NOT INSTALL"),
  driven by known-CVE transitive deps (Pillow, pdfminer.six, mammoth, requests, lxml, openpyxl,
  pandas, mcp) across its sub-packages. Did not install. Read the PDF/MD directly via the Read
  tool instead (handles PDF natively) — markitdown wasn't actually needed for this task.
- **Neon DB declined again** (user confirmed, consistent with a prior session) — companies.json
  stays the static source of truth. Existing FormSubmit-email-to-manual-merge flow (built in a
  prior session) already covers new-entry submissions without a backend.
- Delivered the two explicit generator prompts from the PDF: a JSON Schema for the
  directory-listing location object (`address` + `coordinates{lat,lng}` + mandatory
  `operating_model` enum, coordinates strictly required only for `On-Site`) and a vanilla-JS
  view-filter state/render pattern (PDF asked for React; adapted to match this project's
  zero-dependency constraint).
- Spawned a background research agent to web-verify ~17 candidate companies the PDF surfaced
  from an unverified AI research chat — 18/18 were real, but several claimed funding stages
  (Netzum "Series A", Juntoz "Series A+") were flagged by the agent as unsubstantiated. Added
  only entries with sourced evidence; skipped or flagged the rest to avoid fabricating data
  (matches this project's existing no-fabrication norm from prior sessions).
- Cross-checked the agent's "already in dataset" claims against the real `companies.json` —
  found the agent was **wrong**: Comunal Coworking (Peru's #1 chain per the coworking doc, ~25%
  market share) was NOT actually in the dataset. Added it.
- `companies.json`: 54 → 69 entries. Added `operating_model: "On-Site"` to all pre-existing
  entries (mechanical, all have real addresses), added `funding.stage: "Seed"` to 5 startups
  with a sourced YC batch already in their tag text (Apurata, Keynua, OlaClick, Kashin, Kurios).
  Added 15 new entries: Comunal Coworking, Worx Coworking, Selina Lima Cowork, BCP Café x Puku
  Puku, Café de Lima, Rutina Café, Biblioteca Nacional del Perú, Biblioteca Municipal Ricardo
  Palma, Sinergia Perú (all sourced from the coworking doc or web-verified with real addresses);
  Prestamype, Leasy, Manzana Verde, Joinnus, LIQUID Venture Studio, Inca Ventures (web-verified
  real + funded, but no confirmed street address — placed with approximate Lima coords + explicit
  "no specific address independently verifiable" note, same pattern already used for Winnipeg
  Capital/Talently/uDocz).
- `index.html`: implemented the PDF's landing-view spec. Default feed = Startup + Consultancy +
  Acquired funding types (zero clicks). Added 3 overlay toggle pills (Show Investors → Fund +
  Incubator types; Show Coworking Areas → Coworking type; Show Non-Profits & Communities →
  Nonprofit type) that blend into the existing feed via OR-filtering rather than replacing it.
  Added matching EN/ES i18n keys, `.barrow.wrap` CSS for the 3-pill row inside the 320px sidebar.
- Verified live in-browser (local `http.server`): syntax-checked all 3 inline `<script>` blocks
  with Node, confirmed 200s on `index.html`/`companies.json`, screenshotted default view (30
  places, Lima) and after clicking "Mostrar Coworkings" (41 places — confirms additive blending,
  not replacement).

## Files changed (this check-in)
- `companies.json` — 54 → 69 entries (see above). Not yet committed/pushed.
- `index.html` — added `viewState`/`typeVisible()` filter logic, 3 toggle-pill buttons in
  `panel-head`, `.barrow.wrap` CSS, `showInvestors`/`showCoworking`/`showNonProfits` i18n keys.
  Not yet committed/pushed.

## Failed attempts (this check-in)
- markitdown install — see above, blocked by SkillSpector CRITICAL score, correctly stopped
  per the global supply-chain rule rather than overridden.
- Did not bulk-assign `funding.stage` to all 54 pre-existing startups — no sourced stage data
  for most of them (e.g. Culqi, Yape, Rappi Perú); guessing would violate the no-fabrication
  norm as much as inventing a company would.

## Next steps (this check-in)
- Companies added this session are **uncommitted** — review before committing (branch, commit
  message, PR per repo rule — never push straight to `master`).
- Add-company modal form doesn't yet collect `operating_model` or the coordinate-fallback layer
  — the JSON schema above defines the contract; wiring it into the actual form UI is unstarted.
- Coworking Y Cafés doc has more entries not yet added (Regus multi-location pricing, WeWork
  plan tiers, Café Sur, Vallejo Librería-Café, Casatomada, Caleta Dolsa, Sofá Café, La Bodega
  Verde, Cafetería de Consumo Mínimo, Biblioteca de Barranco/San Isidro) — curated a
  representative subset only.
- Skipped/flagged candidates needing manual confirmation: Netzum, Juntoz, TuRuta (insufficient
  sourced data), Tekton Labs (its claimed Magdalena del Mar address conflicts with Kurios'
  existing Miraflores entry at the same street number — needs manual disambiguation), Hub UDEP
  (real but Piura-based — outside this project's Lima/Arequipa scope), Phantasia and IMPAQTO
  Capital (WPP subsidiary / Ecuador-HQ'd — likely out of scope), Wynwood House (foreign
  hospitality company, not a tech-ecosystem entity).
- Vercel deploy still blocked from earlier this session (403, see above) — unresolved.
- Run `/export docs/handoff/2026-07-13-cb310615/transcript.md` (user must run this, not Claude).

## Files in this folder
- `HANDOFF.md` — this file
- `snapshot-235350.md` — auto PreCompact snapshot
- `.sid` — session id marker
