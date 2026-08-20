/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      // Same tokens as drunkit-web, on purpose — this is the same
      // platform's back office, not a differently-branded product.
      // A dashboard earns a denser layout, not a different palette.
      colors: {
        ink: {
          950: "#0A0F0C",
          900: "#0E1512",
          800: "#141F1A",
          700: "#1B2A23",
          600: "#26392F",
        },
        brass: {
          400: "#D9BC72",
          500: "#C8A24A",
          600: "#A9843A",
        },
        copper: {
          400: "#D68A4C",
          500: "#C97C3D",
          600: "#A9642E",
        },
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
