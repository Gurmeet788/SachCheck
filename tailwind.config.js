/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          dark: '#0a0f1d',
          navy: '#0f172a',
          slate: '#1e293b',
          border: '#334155',
          teal: '#0d9488',
          'teal-light': '#14b8a6',
          'teal-bright': '#2dd4bf',
          'teal-soft': '#ccfbf1',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
