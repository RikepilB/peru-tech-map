Map Project: Storybook UI BriefThis document serves as the system source of truth for UI layout agents and code generation tools. It structures the brand concept from watermarked_img_18090315783402885778.png into exact component states, typography hierarchies, and asset tokens following the bold, structured grid presentation style seen in image_fa34a6.jpg.1. Core Tokens & Global SettingsJSON{
  "project": "Costa Verde Map UI System",
  "theme": "Dark Tech / Minimalist Grid",
  "layout_rules": {
    "grid_unit": "8px",
    "border_radius": "12px",
    "backdrop_blur": "12px",
    "border_weight": "1.5px"
  },
  "color_palette": {
    "background_main": "#1B222C",
    "panel_bg": "rgba(43, 51, 66, 0.65)",
    "panel_border": "#2B3342",
    "cyber_emerald": "#1DA842",
    "neon_teal": "#05DC60",
    "paraglider_coral": "#FF6B6B",
    "lighthouse_beacon": "#FFB400",
    "text_primary": "#F4F6F9"
  }
}
2. Component Specifications (Storybook Categories)Category A: Typography SystemAgents must enforce the following hierarchy strictly. Do not use random sizes or weights outside this token set.Display Title (font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700;)H1: Size 22pt | Tracking: -0.02em | Case: Uppercase alternateH2: Size 14pt | Tracking: -0.01em | Case: Sentence caseData Readouts (font-family: 'JetBrains Mono', monospace; font-weight: 500;)Telemetry_Label: Size 11pt | Color: #05DC60Coordinates: Size 10pt | Tracking: 0 | Strips trailing whitespace.Category B: Iconography & Asset InventoryWhen embedding system marks or rendering graphics inside panels, agents must use these verbatim filenames and keys:Symbol / Graphic KeyAsset Implementation TargetAssociated Asset Referencelogo_costaverdeHeader Branding Elementwatermarked_img_18090315783402885778.pngicon_lighthouseAnchor / Control Center POIwatermarked_img_18090315783402885778.pngicon_paragliderCoverage Area / Range Indicatorwatermarked_img_18090315783402885778.pngmap_concept_topoTopographic Data Layer Cardwatermarked_img_18090315783402885778.pnglayout_inspirationDark Mode Grid Architectureimage_fa34a6.jpgCategory C: UI Component StatesUse these declarative states for generating button, list, or panel styles.1. Floating Glass Panel (.panel-map-control)Background: rgba(43, 51, 66, 0.65)Border: 1.5px solid #2B3342Backdrop Filter: blur(12px)Layout: Vertical flex container, 16px internal padding.2. Active Telemetry Stream (.data-row-active)Text Color: #F4F6F9Accent Signal: Left-side indicator bar using #05DC60 (Neon Teal).Behavior: Alternating zebra-striping rows using rgba(27, 34, 44, 0.4) on even items.3. Warning / Critical POI Marker (.marker-critical)Color Token: #FF6B6B (Paraglider Coral)UI Asset: Embedded icon_paraglider path vector.Interaction State: Pulsing animation on focus indicator.3. Layout Architecture ConstraintsAgents rendering layout code must follow these three rules:Strict Grid Toggles: Map view must cover 100% viewport width and height. UI control modules sit exclusively on an absolute floating layer aligned to an 8px grid structure.High-Contrast Dividers: When rendering tabular data lists inside cards, use thin 1px horizontal lines colored #2B3342 instead of heavy colored blocks.No Text Shifting: All readouts monitoring real-time telemetry variables must utilize fixed-width layout metrics to ensure numeric strings remain pixel-locked during fast rendering refreshes.

TL;DR
The Shift: Moving away from a purely sans-serif layout to introduce high-contrast, editorial serif pairs that mimic the dramatic scale of Lima's cliffs.

The Concept: High-end geospatial data visualization. Merging technical screen indicators with luxury editorial formatting.

Primary Pair: Playfair Display (or Bodoni FLF) for primary branding, structural headers, and spatial titles; JetBrains Mono for coordinates and real-time telemetry.

Updated design.md Brief for Layout Agents
This file has been updated to integrate a high-end typography structure, drawing contrasting inspiration from luxury editorial serifs seen in image_fa3f4e.jpg and image_fa3f50.jpg, alongside the micro-geometry of tech fonts in image_fa3f8c.png.

JSON
{
  "project": "Costa Verde Map UI System",
  "theme": "Editorial Tech / Luxury Geographic Grid",
  "typography_philosophy": "High-contrast structural collision. We utilize dramatic, high-fashion serifs to represent the towering cliffs and prestige of the Costa Verde, paired tightly with strict monospace variables for tech accuracy."
}
Category A: Typography System
Agents must deprecate standard sans-serif fonts for main interfaces and adopt the following multi-class typographic pairing:

1. Editorial Branding & Structural Headers
Font Selection: Playfair Display (or Bodoni FLF / The Seasons as referenced in image_fa3f4e.jpg)

Style: Bold Italic or Regular High-Contrast Serif

Usage: Platform main logo, major geographic zone overlays, primary section titles.

CSS Rule:

CSS
h1.brand-title {
  font-family: 'Playfair Display', 'Bodoni FLF', serif;
  font-weight: 700;
  letter-spacing: -0.03em;
  text-transform: none;
}
2. Secondary Slab / Structured Subheaders
Font Selection: Sánchez (As referenced for creative legibility in image_fa3f4e.jpg)

Style: Regular Slab Serif

Usage: Component card titles, telemetry panel labels, map filter category titles.

Intent: Provides an anchor between high-luxury serif headers and mechanical data arrays.

3. Real-Time Telemetry & Geospatial Output
Font Selection: JetBrains Mono (or Nano Light / Geo Light from image_fa3f8c.png)

Style: Monospace (Light or Medium)

Usage: Latitude, longitude, elevation metrics, scale legends, status logs.

CSS Rule:

CSS
.telemetry-readout {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 300;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
Category B: Visual Mapping Grid
+-----------------------------------------------------------------------+
|  [COSTA VERDE] (Playfair Display Bold - High Luxury Editorial)         |
|  El Faro Anchor // Telemetry System v2.06                            |
+-----------------------------------------------------------------------+
|                                                                       |
|   [ PANEL: ZONA DE VUELO ] (Sánchez Slab Serif Subheading)             |
|   -----------------------------------------------------------------   |
|   ALTITUDE: 148m          LAT: -12.1287                               |
|   SPEED:    24 knots      LON: -77.0315                               |
|   [JetBrains Mono - Fixed Width Data Blocks]                          |
|                                                                       |
+-----------------------------------------------------------------------+
Category C: Component Refinements for Agents
Header Module (.ui-header-main): Must align the brand title using a raw serif aesthetic over a dark background canvas. This creates a high-end interface that makes geospatial mapping look like an premium editorial dashboard.

Data Labels (.label-mono-mini): Use tracking adjustments (letter-spacing: 0.1em) to maintain perfect structural balance alongside high-end serif titles. No sans-serif fillers should be utilized.