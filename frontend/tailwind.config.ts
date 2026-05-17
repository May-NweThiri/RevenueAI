import type { Config } from "tailwindcss"

const config: Config = {
  content: [
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        foreground: "#e8e8ed",
        background: "#0f0f13",
        glass: {
          DEFAULT: "rgba(255, 255, 255, 0.08)",
          border: "rgba(255, 255, 255, 0.12)",
          hover: "rgba(255, 255, 255, 0.12)",
        },
        surface: {
          DEFAULT: "#0f0f13",
          card: "#1a1a22",
          hover: "#24242e",
          border: "#2a2a36",
        },
        accent: {
          DEFAULT: "#6366f1",
          hover: "#818cf8",
          muted: "rgba(99, 102, 241, 0.15)",
        },
        revenue: {
          DEFAULT: "#22c55e",
          up: "#22c55e",
          down: "#ef4444",
        },
      },
      backdropBlur: {
        xs: "2px",
      },
    },
  },
  plugins: [],
}

export default config
