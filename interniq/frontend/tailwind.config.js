/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Space Grotesk"', "sans-serif"],
        body: ['"Manrope"', "sans-serif"],
      },
      colors: {
        brand: {
          ink: "#162335",
          cyan: "#0a7ea4",
          mint: "#77d9c6",
          sand: "#f5ede1",
          coral: "#f0895d",
        },
      },
      boxShadow: {
        panel: "0 20px 35px rgba(22,35,53,0.08)",
      },
    },
  },
  plugins: [],
};
