/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#0D8A56",
          dark: "#0A6B42",
          soft: "#E6F6EE",
        },
        secondary: "#10231A",
        accent: "#5F7A6C",
        light: "#EEF6F1",
        paper: "#FAFDFB",
        success: "#0D8A56",
        warn: "#B45309",
      },
      boxShadow: {
        card: "0 12px 40px rgb(16 35 26 / 0.08)",
        soft: "0 6px 24px rgb(16 35 26 / 0.06)",
      },
      fontFamily: {
        display: ["Syne", "ui-sans-serif", "system-ui", "sans-serif"],
        sans: ['"Source Sans 3"', "ui-sans-serif", "system-ui", "sans-serif"],
      },
      backgroundImage: {
        mesh: "radial-gradient(circle at 12% 18%, rgba(13,138,86,0.18), transparent 42%), radial-gradient(circle at 88% 12%, rgba(16,35,26,0.08), transparent 36%), linear-gradient(180deg, #FAFDFB 0%, #E6F6EE 55%, #FAFDFB 100%)",
      },
    },
  },
  plugins: [],
};
