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
        disaster: {
          dark: '#0a0f1d',
          card: '#111827',
          surface: '#1e293b',
          border: '#334155',
          critical: '#ef4444',
          warning: '#f59e0b',
          info: '#3b82f6',
          safe: '#10b981',
          accent: '#06b6d4'
        }
      },
      fontFamily: {
        sans: ['Inter', 'Outfit', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
