/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Bottle-glass ink — the base surface. Deep, cool, almost-black
        // green rather than a generic near-black, so it reads as glass
        // and cellar rather than "dark mode default."
        ink: {
          950: "#0A0F0C",
          900: "#0E1512",
          800: "#141F1A",
          700: "#1B2A23",
          600: "#26392F",
        },
        // Brass / excise-seal accent — used sparingly for verification,
        // primary actions, and the signature seal motif.
        brass: {
          400: "#D9BC72",
          500: "#C8A24A",
          600: "#A9843A",
        },
        // Aged-copper accent for price/discount emphasis — deliberately
        // shifted away from the generic AI terracotta (#D97757).
        copper: {
          400: "#D68A4C",
          500: "#C97C3D",
          600: "#A9642E",
        },
        // Muted sage for eligible/success states — quieter than a
        // stock green, sits well against the ink background.
        sage: {
          400: "#7FA891",
          500: "#5E8C74",
          600: "#4E7D6B",
        },
        rust: {
          400: "#C96B5A",
          500: "#B5533F",
          600: "#9A4433",
        },
        parchment: "#EDEAE2",
      },
      fontFamily: {
        display: ["Fraunces", "ui-serif", "Georgia", "serif"],
        body: ["\"Public Sans\"", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["\"IBM Plex Mono\"", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      boxShadow: {
        seal: "0 1px 0 rgba(200,162,74,0.5), 0 8px 24px -12px rgba(0,0,0,0.6)",
      },
    },
  },
  plugins: [],
};
