/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Startup Web Palette
        warmBg: "#F7F6F2",        // Soft Warm Off-White
        warmCard: "#FFFFFF",      // Pure White Surface
        warmText: "#102C2B",      // Dark Slate Text
        warmMuted: "#4B6363",     // Cool Gray Secondary Text
        warmBorder: "#E7E9E4",    // Subtle Soft Border

        // Civic Teal Identity
        civicTeal: "#287C73",     // Deep Civic Teal (Primary Signature Accent)
        civicTealHover: "#1F645D",
        civicTealLight: "#E6F4F2",

        // Status Accents
        civicAmber: "#F3B83F",    // Signal Amber
        civicRed: "#D94F4F",      // Alert Red
        civicGreen: "#10B981",    // Emerald Green

        // Authority Dark Command Center Palette
        darkBg: "#0F141C",
        darkSurface: "#161E2E",
        darkCard: "#1F293D",
        darkBorder: "#2D3B54",
        darkText: "#F8FAFC"
      }
    },
  },
  plugins: [],
}
