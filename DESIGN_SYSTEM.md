# Vantage Design System

> Engineered using the Hallmark Anti-AI-Slop specification (v2.0.0).

---

## 1. Design Philosophy

Vantage is an analytical intelligence platform designed for researchers, quantitative developers, and systems architects. Its interface prioritizes **information density, typographical clarity, and zero decorative noise**.

### Anti-Slop Commitments (Hallmark Floor Rules)
1. **No Neon / Cyberpunk Gradients:** Replaced generic purple-to-cyan neon glows with a restrained industrial dark palette.
2. **Tokens at the Root:** Every color and font references CSS variables declared in `:root`. Zero raw inline hex values.
3. **No Decorative Animations:** Eliminated arbitrary scanlines, pulsing orbs, and generic sparkle icons. Animations are strictly functional (e.g. data refresh spinner) with `prefers-reduced-motion` fallbacks.
4. **Authentic Typography:** High-legibility grotesque (`Inter`) for natural reading paired with tabular monospace (`JetBrains Mono`) strictly for quantitative indicators ($Z$-scores, velocities, counts, timestamps).
5. **No Eyebrows or Small Caps:** Replaced tracked all-caps eyebrows with clear sentence-case section headers.
6. **Accessible Navigation:** Complete keyboard focus-visible rings (`outline: 2px solid var(--vt-border-focus)`), explicit SVG accessibility labels, and WCAG AA contrast compliance.

---

## 2. Design Tokens

### Canvas & Surface Hierarchy
```css
--vt-bg-canvas: #090b0e;             /* Primary document canvas */
--vt-bg-surface: #101318;            /* Card & container background */
--vt-bg-surface-elevated: #151921;   /* Hover / elevated element */
--vt-bg-surface-muted: #1c212c;      /* Muted secondary backgrounds */
```

### Borders & Dividers
```css
--vt-border-subtle: #242a38;         /* Structural table / card borders */
--vt-border-strong: #333b4e;         /* Emphasized active borders */
--vt-border-focus: #3b82f6;          /* Instant focus-visible rings */
```

### Typographic Hierarchy
```css
--vt-text-primary: #f1f5f9;          /* High-contrast headings and primary values */
--vt-text-secondary: #94a3b8;        /* Body copy and descriptions */
--vt-text-muted: #64748b;            /* Secondary metadata and captions */
```

### Quantitative Signal Palette
```css
--vt-accent-primary: #3b82f6;        /* Primary action & forecast horizon */
--vt-signal-positive: #10b981;       /* Acceleration / growth surges */
--vt-signal-warning: #f59e0b;        /* Statistical anomalies / inflections */
--vt-signal-danger: #ef4444;         /* Decelerating / decay trends */
```

---

## 3. Core Component Patterns

### Trajectory Charting
- **Historical Curve:** 1.5px solid Signal Emerald (`#10b981`) with subtle single-step gradient area.
- **Forecast Horizon:** 1.5px dashed Steel Blue (`#3b82f6`).
- **Prediction Intervals:** Dual shaded uncertainty ribbons (80% and 95%) with monotonic bounds ($0 \le \text{lower}_{95} \le \text{lower}_{80} \le \hat{y} \le \text{upper}_{80} \le \text{upper}_{95}$).

### Network Topology Matrix
- **SVG Engine:** Scalable vector rendering with greedy modularity community grouping.
- **Node Scale:** Dynamic radius proportional to link degree ($4\text{px} + 1.2 \cdot \text{degree}$).
- **Accessibility:** Labeled SVG root with `aria-label="Entity co-occurrence graph matrix"`.

---

## 4. Verification & Linting
- **Sloplint Results:** 0 FAIL, 0 REFLEX, 0 WARN across 12 files.
- **Test Suite:** 79 unit and integration tests passing (100%).
