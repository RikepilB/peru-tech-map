# Costa Verde Map Project: Brand & Design System

## TL;DR
* **Concept:** A digital mapping system blending Lima’s dramatic Costa Verde coastline (cliffs, ocean, urban parks) with a clean, high-performance tech aesthetic.
* **Palette:** Cyber-emerald, deep oceanic slate, and crisp coastal white, accented by high-visibility neon details.
* **Visual Identity:** Geometric topography, minimalist iconography, and structured layouts engineered for clarity and fluid user experiences.

---

## 1. Brand Concept & Vision

The Costa Verde Map Project translates the unique geography of Lima’s Pacific coastline into a highly precise, modern digital interface. It balances the raw, organic energy of the seaside cliffs with structural, data-driven technology.

* **The Natural Aspect:** Deep ocean gradients, sheer grey earth cliffs covered in vegetation, and expansive open horizons.
* **The Tech Aspect:** Vector networks, crisp data overlays, high-contrast UI panels, and seamless interactive telemetry.

This system moves away from typical retro-style maps to create a futuristic, professional platform built for seamless urban navigation and geospatial analysis.

---

## 2. Color Palette

The color system captures the meeting of the Pacific Ocean, coastal greenery, and modern tech infrastructure. It utilizes muted structural tones contrasted with electric highlights for high-readability data displays.

### Primary Brand Colors
* **Cyber Emerald (`#1DA842` / `#05DC60`):** Represents the cliffside parks and paragliding zones. Infused with a neon tech glow for UI accents, button states, and active data paths.
* **Oceanic Slate (`#2B3342` / `#1B222C`):** A dark, deep blue-grey pulled from the Pacific waters on overcast days. Used for main backgrounds, dark-mode panels, and primary text structure.
* **Cliff Shell (`#F4F6F9`):** A crisp, cool off-white that prevents screen glare while keeping layouts sharp, clean, and modern.

### Data & Status Accents
* **Paraglider Coral (`#FF6B6B`):** High-visibility warning indicators, point-of-interest markers, and critical telemetry paths.
* **Lighthouse Beacon (`#FFB400`):** Search highlights, user location focus states, and secondary interactive layers.

---

## 3. Typography & Font System

The typography is built around clean, geometric sans-serif typefaces to ensure readability on digital screens during interactive panning and zooming.

### Primary UI & Display Font: **Inter / Plus Jakarta Sans**
* **Usage:** Headers, map layers, coordinates, data cards.
* **Characteristics:** High x-height, open counters, and exceptional clarity at micro-scales.
* **Scale:**
  * `H1 (Main Titles)`: 22pt / Bold / Tracking: -0.02em
  * `H2 (Section Headers)`: 14pt / SemiBold / Tracking: -0.01em
  * `H3 (Subheadings / Cards)`: 11pt / Medium / Tracking: 0
  * `Body Text`: 10pt / Regular / Line Height: 1.5

### Monospace / Telemetry Font: **JetBrains Mono / SF Mono**
* **Usage:** Latitude/longitude readouts, system status logs, layer distances, and calculated metrics.
* **Characteristics:** Fixed-width design that prevents text shifting during real-time metric updates.

---

## 4. Iconography & Symbols

Icons follow a minimalist, vector-grid approach. Every symbol uses uniform line weights (1.5px or 2px) with open shapes to mirror clean blueprints or heads-up displays (HUD).

* **The Lighthouse (El Faro):** Represents the central command, anchor points, or user primary base locations. Redesigned as a sharp, tiered vertical rectangle with a single horizontal beam symbol.
* **The Paraglider Arc:** Used to symbolize range rings, field of view, coverage zones, or real-time elevation changes.
* **The Cliff Gradient (La Costa):** Parallel topographic line vectors that show terrain elevation shifts, stairs, and access ramps along the coastal wall.
* **The Coast Road (Circuito de Playas):** Clean, dual-line paths with neon illumination to mark highways, fast-routing paths, and traffic vectors.

---

## 5. UI Architecture & Grid System

Adhering to a minimalist, grid-first approach, the user interface acts as a transparent window over the map canvas.

* **Floating Glass Panels:** Modular sidebars and control cards feature subtle background blurs (`backdrop-filter: blur(12px)`) with thin `#2B3342` borders to stay distinct without blocking the terrain.
* **Component Layout:** Left-aligned panels hold primary tools and layer filters. Bottom-right zones contain structural telemetry, zoom controls, and scale legends.
* **Zebra Striping & Lists:** Internal tabular data (e.g., coordinate lists, route stops) utilizes alternating subtle tints to keep data readable without adding heavy grid lines.

---

## 6. Layout & Photographic Philosophy

Visuals combine high-contrast drone perspectives of Lima's coast with neat vector graphics. 

* **Angles:** Ultra-wide, high-angle aerial views emphasize the sharp dividing line between city high-rises and the ocean.
* **Compositions:** Strong diagonal alignments follow the natural curve of the cliffs. This adds motion and energy to the digital layout.
* **Textures:** Smooth sea surfaces contrast with sharp, geometric concrete blocks and organized asphalt lines below.
