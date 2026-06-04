/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        imdb: '#f5c518',
        darkbg: '#121212',
        darkcard: '#1a1a1a'
      }
    },
  },
  plugins: [],
}