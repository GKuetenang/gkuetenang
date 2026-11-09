import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";

export default defineConfig(({ command }) => ({
  plugins: [tailwindcss()],

  // Les chemins sont différents en développement
  // et après compilation pour Django.
  base: command === "build" ? "/static/" : "/",

  server: {
    host: "127.0.0.1",
    port: 5173,
    strictPort: true,
    cors: {
      origin: [
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://127.0.0.1:8001",
        "http://localhost:8001",
      ],
    },
  },

  build: {
    manifest: true,
    outDir: "static",
    assetsDir: "vite-assets",
    emptyOutDir: false,

    rollupOptions: {
      input: "frontend/main.js",
    },
  },
}));