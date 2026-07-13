# Costa Verde rebrand — design (approved 2026-07-08)

Supersedes the Nazca Desert direction (`index-nazca.html`, kept for reference only).
Inspiration: `docs/design.md`, `Map Project Storybook U.md`, `docs/Gemini_Generated_Image_vel0pcvel0pcvel0.png`.

## Root cause fixed
`index-nazca.html`'s `themeBaseLayers()` recolored water/land/building fills to near-identical
sand tones, killing contrast → real terrain read as flat desert; `building-3d` extrusion ramp
(`#D8C9A8`→`#A38E6C`) blended into that same background, so 3D buildings looked "gone" even when
toggled on.

## Decisions
1. **Map terrain: untouched.** New prototype clones the real `index.html` (clean base — natural
   `openfreemap/liberty` tiles, working 3D buildings). No base-layer recolor loop. Costa Verde
   styling applies only to floating UI chrome (header, sidebar, controls, statusbar, ticker,
   modal, loader, markers).
2. **Typography:** Plus Jakarta Sans (headers/labels/UI) + JetBrains Mono (coordinates/status/
   data), replacing Geist Mono everywhere. Rejected the storybook doc's later editorial-serif
   (Playfair Display + Sánchez) pivot — sans+mono matches the reference image and is lower risk.
3. **Accent color:** single accent, swapped Solarium green (`#056540`/`#0FA968`) → Cyber Emerald
   (`#1DA842`/`#05DC60`). Dropped design.md's coral/amber status accents to keep the
   architecture rule ("one accent color") intact.
4. **File:** new sibling `index-costaverde.html`. `index.html` untouched until this prototype is
   approved as final (hard gate, per brainstorming skill).

## Tokens
```
--bg:       #1B222C   (was #070A08)
--panel:    rgba(43,51,66,0.65)   (glass, was solid #0C110D)
--line:     #2B3342   (was #16281D)
--green:        #1DA842   (was #056540)
--green-bright: #05DC60   (was #0FA968)
--text:     #F4F6F9   (was #D6E2D8)
--muted:    #7C8794   (was #6B7A6E)
--sans:     'Plus Jakarta Sans', system-ui, sans-serif   (new)
--mono:     'JetBrains Mono', ui-monospace, monospace    (was Geist Mono)
--radius:   12px   (new — was 0)
--blur:     12px
```

## Components touched
- `.brand`, `.ctl`/`#toggle3d`, `#panel`, `.modal`, `.loader`: square → `border-radius:12px`,
  solid bg → glass (`var(--panel)` + `backdrop-filter:blur(12px)`), border 1.5px.
- `.panel-head h1`, `.modal-head h2`, `.brand`: font-family → `--sans` (was mono everywhere;
  mono now reserved for actual telemetry per storybook rule).
- `.statusbar`/`.ticker`: keep existing blur, retint to new tokens, keep mono (correct — these
  are the telemetry surfaces).
- `.co-marker`, `.co .logo`: recolor ring/border to emerald, shape unchanged.

## Not touched
Data files, JS logic (company loading, city switcher, marker positioning math), add-company
modal fields — visual layer only.
