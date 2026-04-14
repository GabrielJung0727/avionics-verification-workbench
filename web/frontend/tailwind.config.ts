import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        // engineering-dashboard palette
        navy: {
          950: "#070a14",
          900: "#0a0e1a",
          800: "#0f1422",
          700: "#161c2e",
        },
        graphite: {
          900: "#1a1f2e",
          800: "#222837",
          700: "#2a3142",
          600: "#363d51",
          500: "#4a5266",
        },
        ink: {
          50: "#e8eaed",
          200: "#c2c7d0",
          400: "#8a93a3",
          600: "#5a6273",
        },
        amber: { DEFAULT: "#f59e0b" },
        cyan: { DEFAULT: "#06b6d4" },
        ok: { DEFAULT: "#22c55e" },
        warn: { DEFAULT: "#f97316" },
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      boxShadow: {
        panel: "0 1px 0 rgba(255,255,255,0.04) inset, 0 0 0 1px rgba(255,255,255,0.05)",
      },
      backgroundImage: {
        grid: "linear-gradient(to right, rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(to bottom, rgba(255,255,255,0.04) 1px, transparent 1px)",
      },
      backgroundSize: { grid: "32px 32px" },
    },
  },
  plugins: [],
};

export default config;
