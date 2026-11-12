/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        vantage: {
          950: 'var(--vt-bg-canvas)',
          900: 'var(--vt-bg-surface)',
          850: 'var(--vt-bg-surface-elevated)',
          800: 'var(--vt-bg-surface-muted)',
          700: 'var(--vt-border-subtle)',
          600: 'var(--vt-border-strong)',
          500: 'var(--vt-text-muted)',
          accent: 'var(--vt-accent-primary)',
          surge: 'var(--vt-signal-positive)',
          warning: 'var(--vt-signal-warning)',
          danger: 'var(--vt-signal-danger)',
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
