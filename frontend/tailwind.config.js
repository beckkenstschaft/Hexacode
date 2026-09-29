/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        snapdragon: {
          blue: "#3253DC",
          "blue-hover": "#2843B8",
          "blue-light": "#E8ECFA",
          navy: "#0B1A4F",
          "navy-light": "#152A6B",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      spacing: {
        "18": "4.5rem",
        "88": "22rem",
      },
    },
  },
  plugins: [],
};