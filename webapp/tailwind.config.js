/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        radarr: { DEFAULT: "#e5a00d", dim: "#8b6910" },
        sonarr: { DEFAULT: "#00b4d8", dim: "#0a6b80" },
        lidarr: { DEFAULT: "#9b59b6", dim: "#5c3470" },
        prowlarr: { DEFAULT: "#e74c3c", dim: "#8b2d24" },
        readarr: { DEFAULT: "#2ecc71", dim: "#1a7a42" },
        overseerr: { DEFAULT: "#ff6b35", dim: "#994020" },
        bazarr: { DEFAULT: "#f1c40f", dim: "#8b7208" },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      animation: {
        "fade-in": "fadeIn 0.3s ease-out",
        "slide-up": "slideUp 0.3s ease-out",
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
};
