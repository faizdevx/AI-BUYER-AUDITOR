/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#050716',
          900: '#080C24',
          850: '#0D1038',
          800: '#131748',
          750: '#171D54',
          700: '#1C2263',
          600: '#2A338E',
          500: '#3D49B8',
        },
        crimson: {
          DEFAULT: '#E63946',
          dark: '#B81D2A',
          bright: '#FF2A3B',
          muted: '#9E2A34',
        },
        posterPink: {
          DEFAULT: '#F5A9B8',
          light: '#FDDCE3',
          dim: '#E090A1',
        },
        paper: '#F1F4FA',
        subtle: '#8C97B8',
      },
      fontFamily: {
        sans: ['Geist', 'Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"Geist Mono"', '"JetBrains Mono"', 'monospace'],
      },
      letterSpacing: {
        tighter3: '-0.08em',
        tighter2: '-0.05em',
        tighter1: '-0.03em',
        widest3: '0.3em',
      },
      lineHeight: {
        ultra: '0.80',
        tightest: '0.86',
      }
    },
  },
  plugins: [],
};
