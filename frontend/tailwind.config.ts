import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: {
          DEFAULT: "#F4F5F7",
          raised: "#FFFFFF",
        },
        ink: {
          DEFAULT: "#12181F",
          muted: "#5B6672",
          faint: "#8A94A0",
        },
        line: {
          DEFAULT: "#DFE3E8",
          strong: "#C4CAD2",
        },
        signal: {
          DEFAULT: "#0B6E7A",
          hover: "#095A64",
          soft: "#E4F1F2",
        },
        gain: {
          DEFAULT: "#1E7B45",
          soft: "#E4F3E9",
        },
        loss: {
          DEFAULT: "#B23A2E",
          soft: "#FBEBE9",
        },
        warn: {
          DEFAULT: "#9A6B12",
          soft: "#FBF1DE",
        },
      },
      fontFamily: {
        display: ["var(--font-display)", "sans-serif"],
        sans: ["var(--font-sans)", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      borderRadius: {
        sm: "3px",
        DEFAULT: "4px",
        md: "6px",
        lg: "8px",
      },
      boxShadow: {
        none: "none",
        panel: "0 1px 2px 0 rgb(18 24 31 / 0.04)",
      },
      keyframes: {
        shimmer: {
          "0%": { backgroundPosition: "-400px 0" },
          "100%": { backgroundPosition: "400px 0" },
        },
      },
      animation: {
        shimmer: "shimmer 1.4s ease-in-out infinite",
      },
    },
  },
};
export default config;

