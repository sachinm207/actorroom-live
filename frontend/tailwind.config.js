/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        screenplay: ['"Courier Prime"', 'Courier', 'monospace'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        cinema: {
          950: '#090a0f',
          900: '#11131c',
          800: '#1a1d2d',
          700: '#25293d',
          amber: '#f59e0b',
          cyan: '#06b6d4',
          crimson: '#ef4444'
        }
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.85', transform: 'scale(1.02)' },
        }
      }
    },
  },
  plugins: [],
}
