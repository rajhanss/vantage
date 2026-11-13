# Vantage — Design System

## Identity

Vantage is a security engineering tool. The visual language follows the aesthetic of professional terminal tooling and security dashboards: dark, dense, legible. No gradients. No decorative illustrations. No glassmorphism. Every element earns its place.

---

## Colour Tokens

Defined in `web/src/index.css` as CSS custom properties.

```css
/* Background layers */
--vt-bg-app:    #0a0d0f;   /* Page background */
--vt-bg-card:   #111518;   /* Card / panel surface */
--vt-bg-hover:  #161b1f;   /* Hovered surface */

/* Text */
--vt-text-main: #e8eaed;   /* Primary text */
--vt-text-dim:  #8a9099;   /* Secondary / metadata */

/* Accent */
--vt-accent:         #3b82f6;   /* Primary interactive (blue) */
--vt-accent-hover:   #2563eb;   /* Hovered primary */

/* Semantic */
--vt-success:   #22c55e;   /* Pass / safe */
--vt-warning:   #f59e0b;   /* Partial / caution */
--vt-danger:    #ef4444;   /* Fail / critical */
--vt-muted:     #374151;   /* Disabled / inactive */

/* Border */
--vt-border:    #1e2530;   /* Default border */
--vt-border-active: #3b82f6; /* Focused / selected border */
```

### Semantic usage

| Token | Use |
|-------|-----|
| `--vt-danger` | High / critical severity, attack success |
| `--vt-warning` | Medium severity, partial pass |
| `--vt-success` | Low severity, attack blocked |
| `--vt-accent` | Interactive elements, links, selected state |
| `--vt-text-dim` | Timestamps, labels, metadata, secondary copy |

---

## Typography

```css
font-family: 'Inter', system-ui, -apple-system, sans-serif;
```

### Scale

| Role | Class | Size | Weight |
|------|-------|------|--------|
| Page heading | `text-2xl font-semibold` | 24px | 600 |
| Section heading | `text-lg font-semibold` | 18px | 600 |
| Body | `text-sm` | 14px | 400 |
| Label / metadata | `text-xs font-medium` | 12px | 500 |
| Monospace data | `font-mono text-xs` | 12px | 400 |

### Rules

- No `tracking-wider` on uppercase labels — it reads as AI-generated.
- No `text-4xl` or larger headings in the app shell. This is a tool, not a landing page.
- Monospace (`font-mono`) for all hashes, IDs, ASR values, and code snippets.

---

## Spacing

Tailwind's default scale is used throughout. Key intervals:

| Token | Value | Use |
|-------|-------|-----|
| `p-4` | 16px | Card internal padding |
| `gap-3` | 12px | Inline element gap |
| `gap-6` | 24px | Section gap |
| `mb-6` | 24px | Between major sections |
| `px-6 py-4` | 24px / 16px | Page chrome padding |

---

## Components

### Navbar

- Fixed top, full width.
- Logo + name left, navigation tabs right.
- Active tab: `border-b-2 border-[var(--vt-accent)]`.
- No dropdown menus. All top-level destinations are always visible.

### Buttons

| Variant | Appearance |
|---------|-----------|
| Primary | `bg-[var(--vt-accent)] text-white px-4 py-2 rounded text-sm font-medium` |
| Destructive | `bg-[var(--vt-danger)] text-white …` |
| Ghost | `text-[var(--vt-text-dim)] hover:text-[var(--vt-text-main)] …` |

No pill shapes. `rounded` (4px) only.

### Cards / Panels

```
bg-[var(--vt-bg-card)] border border-[var(--vt-border)] rounded-lg
```

No drop shadows. Border only.

### Tables

- Striped via `even:bg-[var(--vt-bg-hover)]`.
- Header: `text-xs font-medium text-[var(--vt-text-dim)] uppercase`.
- No decorative borders between cells — only horizontal dividers.

### Badges / Severity pills

```css
/* critical */
bg-red-900/40 text-red-400 border border-red-800

/* high */
bg-orange-900/40 text-orange-400 border border-orange-800

/* medium */
bg-yellow-900/40 text-yellow-400 border border-yellow-800

/* low */
bg-green-900/40 text-green-400 border border-green-800
```

Shape: `rounded px-2 py-0.5 text-xs font-medium`. No pill (`rounded-full`).

### Progress bars (ASR)

```
bg-[var(--vt-bg-hover)] rounded-full h-1.5
```

Fill colour derived from severity: danger → warning → success by ASR value.

### Empty states

Plain text in `text-[var(--vt-text-dim)] text-sm`, centered in the container. No illustration. No emoji. One line of copy, one action button if applicable.

### Modal / dialog

```
bg-[var(--vt-bg-card)] border border-[var(--vt-border)] rounded-lg
```

Backdrop: `bg-black/60`. No blur (`backdrop-blur`) — it costs GPU and looks decorative.

---

## Motion

```css
/* Only these transitions are permitted */
transition-colors duration-150 ease-in-out   /* colour changes */
transition-opacity duration-150              /* fade in/out */
```

No `transition-all`. No `animate-bounce`. No `animate-spin` except on genuine loading spinners.

Respects `prefers-reduced-motion`:

```css
@media (prefers-reduced-motion: reduce) {
  * { transition-duration: 0ms !important; }
}
```

---

## Iconography

Lucide React icon set. No emoji as icons. No AI sparkle icons. No decorative illustrations.

Sizes:
- Inline with text: `w-4 h-4`
- Standalone: `w-5 h-5`

---

## Layout

### Shell

```
Navbar (fixed top, h-14)
└── Main content area (pt-14, full viewport height)
    └── Page component (px-6 py-6, max-w-7xl mx-auto)
```

### Responsive breakpoints

| Breakpoint | Columns |
|------------|---------|
| `< 640px` | 1 |
| `640–1024px` | 2 |
| `> 1024px` | 3–4 depending on content density |

Heatmap and comparison views collapse to single-column stacks on mobile. Tables become scrollable horizontally, not reformatted.

---

## Anti-patterns (never use)

- `bg-gradient-to-*` decorative backgrounds
- `backdrop-blur`
- `rounded-full` on anything except avatars and circular icons
- `tracking-wider` on uppercase text
- Emoji as interface icons (`🔥`, `✨`, `🚀`)
- `transition-all`
- `shadow-xl` or larger shadows
- Hardcoded colour values outside token definitions
- `text-5xl` or larger headings in the app shell

---

## Hallmark compliance

All source files pass `sloplint.mjs --tier floor` with `0 FAIL, 0 REFLEX, 0 WARN`.
