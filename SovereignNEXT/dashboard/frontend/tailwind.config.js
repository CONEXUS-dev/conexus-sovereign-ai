/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        sovereign: {
          bg: '#0a0f1a',
          surface: '#111827',
          border: '#1f2937',
          accent: '#6366f1',
          regulated: '#22c55e',
          oscillating: '#f59e0b',
          drifting: '#ef4444',
          stuck: '#6b7280',
          saturated: '#a855f7',
        },
      },
      fontFamily: {
        serif: ['Crimson Text', 'Georgia', 'serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
