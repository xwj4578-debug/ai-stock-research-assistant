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
          primaryHover: "#6A9DFF",
          success: "#22C55E",
          danger: "#EF4444",
          warning: "#F59E0B",
          rise: "#EF4444",
          fall: "#22C55E",
          ai: "#8B5CF6",
          text: "#F9FAFB",
          secondary: "#CBD5E1",
          muted: "#94A3B8",
          cardHover: "#1D2940"
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
