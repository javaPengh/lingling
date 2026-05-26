import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}", "../shared/**/*.ts"],
  theme: {
    extend: {
      colors: {
        ink: "#1f2933",
        mist: "#eef3f8",
        coral: "#e76f51",
        leaf: "#2a9d8f"
      }
    }
  },
  plugins: []
} satisfies Config;
