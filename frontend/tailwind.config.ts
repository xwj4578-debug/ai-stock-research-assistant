import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}", "./types/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        workspace: {
          bg: "#0B1020",
          panel: "#111827",
          card: "#172033",
          border: "#263244",
          primary: "#4F8BFF",
          success: "#22C55E",
          danger: "#EF4444",
          warning: "#F59E0B",
          text: "#F9FAFB",
          muted: "#9CA3AF"
        }
      },
      boxShadow: {
        terminal: "0 20px 80px rgba(0, 0, 0, 0.35)"
      }
    }
  },
  plugins: []
};

export default config;
