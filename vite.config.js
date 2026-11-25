import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [tailwindcss()],

  // django-vite préfixe également les ressources de développement
  // avec STATIC_URL ; Vite doit donc servir les deux modes sous /static/.
  base: "/static/",

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
});
