// frontend/vite.config.js
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  // zachováváme tvůj base
  base: process.env.VITE_BASE_PATH || "/",
  server: {
    host: true,
    port: 5173,
    // v devu přesměruj /api na gunicorn (Flask) na 127.0.0.1:5000
    proxy: {
      "/api": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
        secure: false,
      },
    },
  },
  build: {
    outDir: "dist",
  },
});
