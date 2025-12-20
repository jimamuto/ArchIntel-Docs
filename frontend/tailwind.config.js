module.exports = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        background: "#060608",
        foreground: "#FFFFFF",

        aurora: {
          bg: "#060608",
          card: "#0F0F13",
          border: "#232329",
          muted: "#8A8F98",
          pink: "#FF71D4",
          purple: "#B26EF7",
          cyan: "#5DE6FA",
          input: "#1A1A20", // Added explicit input color
        },

        card: {
          DEFAULT: "#0F0F13",
          foreground: "#FFFFFF",
        },
        popover: {
          DEFAULT: "#0F0F13",
          foreground: "#FFFFFF",
        },
        primary: {
          DEFAULT: "#B26EF7",
          foreground: "#FFFFFF",
        },
        secondary: {
          DEFAULT: "#1A1A20",
          foreground: "#FFFFFF",
        },
        muted: {
          DEFAULT: "#141419",
          foreground: "#8A8F98",
        },
        accent: {
          DEFAULT: "#1A1A20",
          foreground: "#FFFFFF",
        },
        destructive: {
          DEFAULT: "#EF4444",
          foreground: "#FFFFFF",
        },
        border: "#232329",
        input: "#1A1A20",
        ring: "#B26EF7",
      },
      borderRadius: {
        lg: "8px",
        md: "6px",
        sm: "4px",
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'conic-gradient': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'glow-conic': 'conic-gradient(from 180deg at 50% 50%, #2a8af6 0deg, #a853ba 180deg, #e92a67 360deg)',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      boxShadow: {
        'glow': '0 0 20px -5px rgba(178, 110, 247, 0.4)', // Aurora purple glow
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
      },
      animation: {
        spotlight: "spotlight 2s ease .2s 1 forwards",
        shimmer: "shimmer 2s linear infinite",
        scroll: "scroll 20s linear infinite",
        "pulse-glow": "pulse-glow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
      keyframes: {
        spotlight: {
          "0%": { opacity: 0, transform: "translate(-72%, -62%) scale(0.5)" },
          "100%": { opacity: 1, transform: "translate(-50%,-40%) scale(1)" },
        },
        shimmer: {
          from: { backgroundPosition: "0 0" },
          to: { backgroundPosition: "-200% 0" },
        },
        scroll: {
          to: { transform: "translate(calc(-50% - 0.5rem))" },
        },
        "pulse-glow": {
          "0%, 100%": { opacity: 1 },
          "50%": { opacity: .5 },
        }
      }
    },
  },
  plugins: [],
}
