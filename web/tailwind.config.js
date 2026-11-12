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
          950: '#06090e',
          900: '#0d1117',
          850: '#131922',
          800: '#161b22',
          700: '#21262d',
          600: '#30363d',
          500: '#484f58',
          accent: '#00f0ff',
          neon: '#7928ca',
          surge: '#00ff66',
          warning: '#ffb700',
          danger: '#ff3366',
        }
      },
      fontFamily: {
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
