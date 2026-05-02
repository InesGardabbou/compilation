/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        neo: {
          bg: '#0a0b10',
          panel: 'rgba(17, 24, 39, 0.7)',
          card: 'rgba(31, 41, 55, 0.6)',
          accent: '#00f0ff',
          primary: '#3b82f6',
          purple: '#8b5cf6',
          danger: '#ef4444',
          success: '#10b981',
          warning: '#f59e0b'
        }
      },
      fontFamily: {
        sans: ['Inter', 'Roboto', 'sans-serif'],
        mono: ['Fira Code', 'monospace']
      },
      backdropBlur: {
        xs: '2px',
      }
    },
  },
  plugins: [],
}
