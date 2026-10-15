---
name: Pulse Insights
colors:
  surface: '#0b1326'
  surface-dim: '#0b1326'
  surface-bright: '#31394d'
  surface-container-lowest: '#060e20'
  surface-container-low: '#131b2e'
  surface-container: '#171f33'
  surface-container-high: '#222a3d'
  surface-container-highest: '#2d3449'
  on-surface: '#dae2fd'
  on-surface-variant: '#c7c4d7'
  inverse-surface: '#dae2fd'
  inverse-on-surface: '#283044'
  outline: '#908fa0'
  outline-variant: '#464554'
  surface-tint: '#c0c1ff'
  primary: '#c0c1ff'
  on-primary: '#1000a9'
  primary-container: '#8083ff'
  on-primary-container: '#0d0096'
  inverse-primary: '#494bd6'
  secondary: '#d0bcff'
  on-secondary: '#3c0091'
  secondary-container: '#571bc1'
  on-secondary-container: '#c4abff'
  tertiary: '#4cd7f6'
  on-tertiary: '#003640'
  tertiary-container: '#009eb9'
  on-tertiary-container: '#002f38'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e1e0ff'
  primary-fixed-dim: '#c0c1ff'
  on-primary-fixed: '#07006c'
  on-primary-fixed-variant: '#2f2ebe'
  secondary-fixed: '#e9ddff'
  secondary-fixed-dim: '#d0bcff'
  on-secondary-fixed: '#23005c'
  on-secondary-fixed-variant: '#5516be'
  tertiary-fixed: '#acedff'
  tertiary-fixed-dim: '#4cd7f6'
  on-tertiary-fixed: '#001f26'
  on-tertiary-fixed-variant: '#004e5c'
  background: '#0b1326'
  on-background: '#dae2fd'
  surface-variant: '#2d3449'
typography:
  display-lg:
    fontFamily: Space Grotesk
    fontSize: 56px
    fontWeight: '700'
    lineHeight: 64px
    letterSpacing: -0.03em
  display-lg-mobile:
    fontFamily: Space Grotesk
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-xl:
    fontFamily: Space Grotesk
    fontSize: 40px
    fontWeight: '600'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Space Grotesk
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.015em
  headline-lg:
    fontFamily: Space Grotesk
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Space Grotesk
    fontSize: 22px
    fontWeight: '500'
    lineHeight: 30px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Space Grotesk
    fontSize: 18px
    fontWeight: '500'
    lineHeight: 26px
    letterSpacing: 0em
  body-lg:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
    letterSpacing: -0.005em
  body-md:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
    letterSpacing: 0em
  body-sm:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0.01em
  metric-stat:
    fontFamily: Space Grotesk
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 38px
    letterSpacing: -0.02em
  label-md:
    fontFamily: Geist
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Geist
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.04em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1.25rem
  gutter-sm: 0.75rem
  gutter-lg: 1.5rem
  margin: 2rem
  margin-sm: 1rem
  margin-lg: 3rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

The brand targets product leaders, data engineers, and executive operators who demand signal over noise. The aesthetic bridges Modern Corporate precision with refined Glassmorphism, evoking a focused, high-clarity environment akin to a physical aerospace or financial command deck operating at night.

Visual characteristics center on:
- Deep, immersive dark canvases that reduce visual fatigue during prolonged analytical sessions.
- Luminous, deliberate violet and indigo focal points indicating primary interaction paths and current system state.
- Ultra-fine micro-borders that articulate complex structural grids without visual weight.
- Controlled frosted backdrops to establish soft dimensional hierarchy over rich data graphics.

## Colors

The palette relies on a base of midnight slate layered with electric spectral accents tuned specifically for legibility against dark surfaces:

- **Primary (`#6366F1` / Electric Indigo):** Anchors core actions, focused indicators, and primary visual metrics.
- **Secondary (`#8B5CF6` / Vivid Violet):** Used for analytical transitions, secondary highlights, active navigation paths, and complementary data series.
- **Tertiary (`#06B6D4` / Spectral Cyan):** Reserved for technical data marks, real-time pulse triggers, and informational callouts.
- **Neutral (`#0F172A` / Midnight Slate):** Forms the foundational canvas, establishing the deep dark environment.

### Data Visualization Accents
- **Success & Positive Trends:** Emerald (`#10B981`)
- **Warning & At-Risk Thresholds:** Amber (`#F59E0B`)
- **Critical & Negative Divergence:** Rose Crimson (`#F43F5E`)
- **Supplementary Series:** Cyan (`#06B6D4`) and Violet (`#8B5CF6`)

### Dark Mode Surface Tiers
- **Canvas Base:** `#090D16`
- **Surface Layer 1 (Base Cards):** `#0F172A` at 70% opacity with backdrop blur
- **Surface Layer 2 (Elevated Panels):** `#1E293B` at 65% opacity
- **Border Subtle:** `rgba(255, 255, 255, 0.08)`
- **Border Focus/Active:** `rgba(99, 102, 241, 0.45)`

## Typography

The pairing combines the technological geometry of **Space Grotesk** for headings and metric displays with the neutral utility of **Geist** for dense analytical interfaces, labels, and analytical tables.

- Apply `metric-stat` to major numeric counters and dashboard tiles, pairing with tabular lining figures (`font-variant-numeric: tabular-nums`) for clean vertical scanning.
- Use uppercase styling exclusively with `label-sm` for table headers, metadata badges, and chart axis descriptors.
- Ensure high typographic hierarchy by reserving Space Grotesk strictly for high-impact milestones, section titles, and numerical aggregates.

## Layout & Spacing

This design system uses a 12-column fluid grid system across desktop viewports, transitioning through an 8-column configuration on tablets to a single- or dual-column vertical flow on mobile screens.

### Grid & Breakpoints
- **Desktop (1280px+):** 12 columns, `margin-lg` (3rem), `gutter-lg` (1.5rem). Primary analytics panels occupy 8 or 9 columns; filter sidebars and real-time event logs occupy 3 or 4 columns.
- **Tablet (768px – 1279px):** 8 columns, `margin` (2rem), `gutter` (1.25rem). Metric cards reflow to 2x2 grids; secondary sidebars collapse into slide-out panels.
- **Mobile (<768px):** 4 columns or single-column stack, `margin-sm` (1rem), `gutter-sm` (0.75rem). KPI counters compress horizontally into scrolling segments.

### Spacing Rules
- Apply `space-xs` and `space-sm` for inline metadata grouping, badge padding, and icon-to-label offsets.
- Internal card padding standardizes at `space-md` for compact dense widgets and `space-lg` for primary chart surfaces.
- Use `space-xl` for sectional transitions within analytical workspaces.

## Elevation & Depth

Visual hierarchy relies on a combination of subtle surface luminescence, semi-transparent frosted planes, and razor-thin borders rather than heavy drop shadows.

### Layering Strategy
1. **Canvas (Level 0):** Flat `#090D16` base layer, unlit.
2. **Standard Panels & Widgets (Level 1):** Translucent fill (`rgba(15, 23, 42, 0.72)`), backed by a `12px` Gaussian backdrop blur. Framed by a 1px solid stroke of `rgba(255, 255, 255, 0.08)`.
3. **Elevated Drawers & Flyouts (Level 2):** Fill of `rgba(30, 41, 59, 0.85)` with `16px` backdrop blur, a top-edge highlight stroke of `rgba(255, 255, 255, 0.16)`, and a diffused ambient shadow (`0 20px 40px -15px rgba(0, 0, 0, 0.65)`).
4. **Modals & Command Palettes (Level 3):** Fill of `rgba(15, 23, 42, 0.95)`, framed by `rgba(99, 102, 241, 0.35)` with an ambient violet-tinted glow (`0 24px 64px -12px rgba(99, 102, 241, 0.2)`).

### Micro-Border Definition
Card structures never use drop shadows to communicate edges. Instead, use a dual-layer inner border technique: an outer `1px` stroke of `rgba(255, 255, 255, 0.07)` combined with an optional inner top-line gradient fade (`rgba(255, 255, 255, 0.12)` down to transparent) to emulate subtle bevel illumination.

## Shapes

The design system maintains a structured, architectural aesthetic characterized by crisp, restrained rounding (`roundedness: 1`):

- **Default UI Containers & Cards:** `0.25rem` (4px) to `0.5rem` (8px) corner radius, preserving high data density without visual softness.
- **Buttons, Inputs, and Badges:** `0.25rem` (4px) corner radius to reinforce a technical, engineered feel.
- **Pill Exception:** Status indicators (active live pings, numerical metric increments) use full circular rounding solely to designate operational state badges.

## Components

### Buttons
- **Primary:** Background of `#6366F1` with an inner 1px highlight stroke (`rgba(255, 255, 255, 0.2)`). White label text, medium weight. On hover: shifts toward `#4F46E5` with an ambient glow (`0 0 16px rgba(99, 102, 241, 0.4)`).
- **Secondary:** Surface background `rgba(255, 255, 255, 0.04)`, bordered by `rgba(255, 255, 255, 0.12)`. Hover shifts to `rgba(255, 255, 255, 0.08)` and border becomes `rgba(255, 255, 255, 0.2)`.
- **Ghost:** Transparent background with subtle label color; applies `rgba(255, 255, 255, 0.05)` fill on hover.

### Chips & Badges
- **Status Indicators:** Micro-pills rendered with `space-xs` vertical and `space-sm` horizontal padding. Composed of an ultra-low opacity tinted background (10% tint of accent color), 1px matched border (25% opacity), and a vibrant 6px circular dot (e.g., Emerald for stable, Amber for degraded, Cyan for streaming).
- **Filter Tags:** Rectangular (4px radius) with subtle close icons. Surface tinted to `#1E293B`, border `rgba(255, 255, 255, 0.08)`.

### Form Controls
- **Input Fields:** Background `rgba(15, 23, 42, 0.6)` with a 1px border of `rgba(255, 255, 255, 0.1)`. Height of 36px for high density. On focus: border shifts to `#6366F1`, accompanied by a subtle 2px soft ring of `rgba(99, 102, 241, 0.2)`.
- **Checkboxes & Radios:** 16px square/circle with `1px` border of `rgba(255, 255, 255, 0.2)`. Checked state activates an indigo fill (`#6366F1`) with crisp white check/pip graphics.

### Cards & Analytical Widgets
- Default to frosted base surfaces (`rgba(15, 23, 42, 0.7)`), surrounded by 1px micro-borders (`rgba(255, 255, 255, 0.07)`).
- Card headers strictly divide content using a bottom rule of `1px solid rgba(255, 255, 255, 0.05)` accompanied by `space-sm` bottom spacing.
- Chart tooltips employ Surface Layer 2 with sharp 4px radius and high-contrast numerical readouts.

### Data Tables
- Header row utilizes `label-sm` in all-caps, with an understated baseline stroke (`1px solid rgba(255, 255, 255, 0.08)`).
- Row hover produces a unified `rgba(99, 102, 241, 0.04)` wash across cells.
- Numbers and numerical delta tags use tabular alignment (`text-align: right`) to guarantee visual comparison accuracy across rows.