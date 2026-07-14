# Peru Grid

[![CI](https://github.com/RikepilB/peru-tech-map/actions/workflows/ci.yml/badge.svg)](https://github.com/RikepilB/peru-tech-map/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](./CONTRIBUTING.md)

An interactive map of startups, cloud consultancies, coworking spaces and incubators across Lima and Arequipa, rendered as a terminal-style operations console. Click a place to fly to it, click its marker for details, switch cities from the sidebar. Live at **[perugrid.com](https://perugrid.com)**.

---

## What It Is

A single self-contained web app with no build step, no framework, no backend. It renders an open-source vector map (MapLibre GL) and overlays a researched dataset of Peruvian tech companies, consultancies, coworking spaces and incubators. The whole thing is three data files plus one HTML file, served as static assets.

**Stack:**
- **[MapLibre GL JS](https://maplibre.org/)** — open-source WebGL map renderer (the open fork of Mapbox GL).
- **[OpenFreeMap](https://openfreemap.org/)** — free vector tile host and base styles. No API key, no usage limits.
- Vector tiles follow the **[OpenMapTiles schema](https://openmaptiles.org/schema/)** (source-layers: `building`, `water`, `transportation`, `place`, `poi`, etc.).
- **[Geist Mono](https://vercel.com/font)** for all UI typography.
- **[FormSubmit](https://formsubmit.co/)** for the "add a company" form (static-site email relay, no server) — **not wired up yet**, see below.

**Design:** monochrome near-black console with Solarium green (`#056540`) as the only accent. Top-down 2D blueprint view by default, with a `[3D]` toggle. Street labels appear only on major roads; default map POIs are hidden so only company markers show.

---

## Repository Layout

```
peru-tech-map/
├── index.html              # The entire app: map, sidebar, city switcher, popovers, form, loader
├── companies.json          # Company dataset — the heart of the project
├── ticker.json             # Scrolling headline ticker
├── README.md               # You are here
├── LICENSE                 # MIT — covers the code
├── LICENSE-DATA            # CC BY 4.0 — covers the datasets
├── CODEOWNERS              # Routes every PR to the maintainer for review
├── CONTRIBUTING.md         # How to add a place, fix data, or change code
├── CODE_OF_CONDUCT.md      # Contributor Covenant 2.1
├── SECURITY.md             # Responsible disclosure
└── .github/
    ├── PULL_REQUEST_TEMPLATE.md
    ├── ISSUE_TEMPLATE/         # Add A Company / Bug Report / Feature Request
    └── workflows/ci.yml        # Validates companies.json/ticker.json on every PR
```

---

## Data Format

### `companies.json`

An array of place objects. This is the file most contributions will touch.

```json
{
  "name": "Culqi",
  "domain": "culqi.com",
  "city": "lima",
  "address": "San Isidro, Lima",
  "lat": -12.0930, "lng": -77.0270,
  "funding": { "type": "Startup" },
  "tag": "Online payment gateway (Credicorp/BCP group) letting businesses accept card payments in-store and online."
}
```

| Field | Required | Notes |
|---|---|---|
| `name` | ✅ | Display name. |
| `city` | ✅ | `"lima"` or `"arequipa"` — drives the city switcher and bbox validation. |
| `lat`, `lng` | ✅ | Decimal degrees. Must fall inside that city's core bbox (see validation below). |
| `funding` | ✅ | Object with `type`. We repurpose BUILD416's funding-round field as a category, since most entries here aren't VC-funded: `Startup`, `Consultancy`, `Coworking`, `Incubator`, `Nonprofit`, `Fund` render as a muted chip; `Acquired` (or `Public`) renders as the green "notable outcome" chip. |
| `domain` | ⬜ | Bare domain (no `https://`, no `www`). Used to fetch the logo and link the website. Omit entirely if unknown — the marker falls back to an initial-letter tile instead of guessing. |
| `address` | ⬜ | Human-readable, for provenance. |
| `tag` | ⬜ | One-sentence description shown in the popover and used as the sidebar's secondary line. |

**Coordinate Validation:** every entry must sit within its city's bounding box —

- Lima: `[-77.20, -12.35]` → `[-76.90, -11.95]`
- Arequipa: `[-71.60, -16.50]` → `[-71.45, -16.30]`

Entries outside their declared city's bbox are skipped at load with a console warning.

### `ticker.json`

An array of headline objects scrolling across the top:

```json
{ "label": "BIOTECH", "text": "Le Qara wins the H&M Foundation Global Change Award for Arequipa-made bio-leather" }
```

Keep `label` short (one or two words, uppercased in the UI) and `text` to a single sentence. Not filtered by city — it's a shared reel across both.

---

## Running It Locally

The app fetches `companies.json` and `ticker.json` at runtime, so it **must be served over HTTP** — opening `index.html` directly with `file://` will fail on CORS. Any static server works:

```bash
python3 -m http.server 8000
# or
npx serve .
```

Then open **http://localhost:8000**.

---

## Known TODOs Before Shipping

- **`FORM_ENDPOINT` in `index.html`** is a placeholder (`https://formsubmit.co/ajax/YOUR_EMAIL_HERE`). The "Add A Company" modal is built but inert until you swap in your own [FormSubmit](https://formsubmit.co/)-verified email — first real submission triggers FormSubmit's one-time verification email.
- Favicon is a self-contained inline SVG (data URI, no file needed). **The social-share image is still a placeholder**: `og:image`/`twitter:image` point to `https://perugrid.com/assets/og-image.jpg`, but that file doesn't exist yet — add a real screenshot/graphic at `assets/og-image.jpg` (1342×896 or similar 3:2 ratio) to make link previews (Slack, Twitter, WhatsApp) show an image instead of nothing.
- No `assets/` folder yet for local company-logo overrides — markers fall back to Google's favicon service or an initial-letter tile, which is enough to ship.

---

## Contributing

Contributions are welcome — especially adding places, fixing coordinates, and correcting categories. **Anyone can open a pull request or issue; all PRs are reviewed and merged by the maintainer.**

See **[CONTRIBUTING.md](./CONTRIBUTING.md)** for the full workflow (branching, validation,
PR checklist), and **[CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)** for community standards.
Found a security issue? See **[SECURITY.md](./SECURITY.md)** instead of opening a public issue.

---

## Credits & Data Sources

Map data © [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors, served via OpenFreeMap. Company data researched and compiled from public sources (company sites, news coverage, university incubator pages). Structure/style adapted from [BUILD416](https://github.com/MapleBudget/toronto-tech-map) by Nelson Lee.

## License

The **code** is [MIT licensed](./LICENSE). The **datasets** (`companies.json`, `ticker.json`) are licensed [CC BY 4.0](./LICENSE-DATA) — standard software licenses don't fit factual data well, so the two are licensed separately. Map base data is © OpenStreetMap contributors under the [ODbL](https://www.openstreetmap.org/copyright); keep the attribution control visible on the map.
