import { resolve } from "node:path";

import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const apiTarget = env.VITE_API_PROXY_TARGET || "http://127.0.0.1:8000";
  const accountingUiSrc = resolve(
    __dirname,
    ".accounting-ui/cz-accounting-module/packages/accounting-ui/src",
  );

  return {
    base: "/accounting/",
    plugins: [
      react(),
      VitePWA({
        registerType: "autoUpdate",
        includeAssets: ["pvm-deal-logo.png", "pwa-icon-192.png", "pwa-icon-512.png", "offline.html"],
        manifest: {
          name: "PVM Deal Accounting",
          short_name: "PVM Accounting",
          description: "Fakturace a účetní administrativa PVM-Deal",
          theme_color: "#111827",
          background_color: "#0f172a",
          display: "standalone",
          start_url: "/accounting/",
          scope: "/",
          lang: "cs",
          icons: [
            {
              src: "pwa-icon-192.png",
              sizes: "192x192",
              type: "image/png",
              purpose: "any",
            },
            {
              src: "pwa-icon-512.png",
              sizes: "512x512",
              type: "image/png",
              purpose: "any",
            },
            {
              src: "pwa-icon-512.png",
              sizes: "512x512",
              type: "image/png",
              purpose: "maskable",
            },
          ],
        },
        workbox: {
          navigateFallback: "/accounting/index.html",
          navigateFallbackDenylist: [/^\/api\//],
          globPatterns: ["**/*.{js,css,html,ico,png,svg,woff2,webmanifest}"],
          maximumFileSizeToCacheInBytes: 3 * 1024 * 1024,
          runtimeCaching: [
            {
              urlPattern: ({ url }) => url.pathname.startsWith("/api/"),
              handler: "NetworkOnly",
            },
            {
              urlPattern: ({ url }) => url.pathname.includes("/pdf"),
              handler: "NetworkOnly",
            },
          ],
        },
        devOptions: {
          enabled: false,
        },
      }),
    ],
    resolve: {
      alias: {
        "@cz-accounting/accounting-ui": resolve(accountingUiSrc, "index.ts"),
      },
      dedupe: ["react", "react-dom"],
    },
    server: {
      port: 5174,
      proxy: {
        "/api": {
          target: apiTarget,
          changeOrigin: true,
        },
      },
    },
    build: {
      outDir: "dist",
      emptyOutDir: true,
    },
  };
});
