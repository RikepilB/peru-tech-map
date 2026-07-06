# Decisions (ADR log)

> One entry per significant decision. Newest on top. Append-only.

## Template
```
### <YYYY-MM-DD> — <decision title>
- **Context:** why this came up
- **Decision:** what we chose
- **Alternatives:** what we rejected and why
- **Consequences:** what this commits us to
```

### 2026-07-06 — Skipped 6 entities from a user-supplied Lima directory (unverifiable/defunct)
- **Context:** user supplied a ~30-entry "comprehensive directory" of Lima startups/funds/
  accelerators to add. Two research agents fact-checked every entry against SUNAT/RUC registry,
  official sites, Crunchbase/YC/PitchBook, and LinkedIn before adding any pin.
- **Decision:** added 20 entities (see companies.json), skipped 6:
  - **Ovenfo** — no LinkedIn, no Crunchbase, no working domain; only source found was a
    listicle blog reusing generic AI-startup boilerplate across unrelated companies. Likely
    not a real, distinct, active company.
  - **Artificio** — real (press-covered, named founders), but zero verifiable office location
    anywhere (site only lists an email). No pin possible without fabricating coordinates.
  - **Domus AI** — real (Forbes Perú Top 100, StartUp Perú grant recipient), same problem —
    no district/address found anywhere.
  - **Syntax** (usesyntax.com) — was real (Platanus-backed), but its own homepage now reads
    "click here to read what happened with Syntax" — strong shutdown signal.
  - **GoJom** — domain now redirects to a parked-domain sales page; PitchBook lists it
    "Out of Business" (June 2024); LinkedIn shows HQ relocated to Mexico City.
  - **MrPink VC** — real VC fund, but headquartered in Punta del Este, Uruguay, not Lima —
    doesn't belong on a Lima map regardless of Peru-based portfolio companies.
- **Alternatives:** include all of them with a placeholder/city-center pin regardless of
  verifiability (rejected — violates the "no fabricated coordinates" rule); include them with
  no pin at all as a text-only sidebar entry (rejected — breaks the map's core interaction
  model, and the schema has no precedent for a pin-less entry).
- **Consequences:** if a contributor later finds a real, current address for Artificio, Domus
  AI, or a revived Syntax, they can be added properly (see PR template checklist). Ovenfo and
  GoJom should stay excluded unless new evidence surfaces they're real/active again.
- **Lower-confidence entries added anyway (flagged, not skipped):** Talently and uDocz use a
  generic Lima-center coordinate (no confirmed street/district found — will render as a
  co-located, fanned-out pin pair via the existing stacked-pin logic). Winnipeg Capital's
  address is a single low-reliability directory snippet, discarded in favor of a San Isidro
  city-center placeholder. MindQube's own domain now redirects to a "Noobelab" rebrand page —
  added under the MindQube name/description since that's what the source list named, but the
  current operating brand may have changed; verify before treating this as current.
- **New funding.type value:** added `"Fund"` (Salkantay Ventures, Winnipeg Capital, AVP
  Ventures, PECAP) to the existing category set — muted-chip styling, same bucket as
  Startup/Consultancy/Coworking/Incubator/Nonprofit. Updated `index.html`'s
  `MUTED_FUNDING_TYPES`, the add-company modal's category `<select>`, `README.md`, and
  `.github/PULL_REQUEST_TEMPLATE.md` to match.

### 2026-07-06 — Repurpose `funding.type` as a category field
- **Context:** cloned BUILD416's schema, which requires a real VC funding-round `type`
  (Seed/Series A/Public/etc.) per entry. Most Lima/Arequipa entries here are unfunded
  startups, consultancies, coworking spaces, or university incubators — no real funding-round
  data was researched for them, and fabricating one would violate the "no invented facts" rule.
- **Decision:** keep the `funding` object (for chip-rendering compat with the cloned UI code)
  but populate `type` with a category instead: `Startup`, `Consultancy`, `Coworking`,
  `Incubator`, `Nonprofit`, or `Acquired` for the one confirmed acquisition (Dentito). Muted
  chip styling for the first five, green "notable outcome" styling for `Acquired`/`Public`.
- **Alternatives:** invent plausible-sounding funding amounts (rejected — fabrication);
  drop the funding chip entirely (rejected — loses a genuinely useful at-a-glance category cue).
- **Consequences:** the schema diverges from upstream BUILD416's literal meaning of `funding`;
  documented in `README.md`'s Data Format table and `docs/architecture.md` so this isn't
  mistaken for real funding data later.

### 2026-07-06 — No local logo assets; favicon-service fallback only
- **Context:** BUILD416 ships local `assets/logos/*.png` for companies whose favicon doesn't
  render well. Downloading/repackaging third-party company logos wasn't something to do
  without per-file confirmation, and most researched entries don't have a public logo asset
  readily available anyway.
- **Decision:** rely entirely on Google's `s2/favicons` service keyed off each entry's bare
  `domain`, falling back to an initial-letter tile when there's no `domain` at all (several
  Arequipa entries have no confirmed public website).
- **Alternatives:** download and commit logo images per company (rejected — copyright/consent
  and file-download-approval overhead for ~30 images); skip logos/initials entirely (rejected
  — worse UX, no visual differentiation in the sidebar).
- **Consequences:** visual quality depends on Google's favicon service uptime/coverage; a
  future contributor can still add `assets/logos/<name>.png` + a `"logo"` field per-entry if
  they want to override a specific one (the code already supports it).
