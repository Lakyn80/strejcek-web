import { resolve } from "node:path";

import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const apiTarget = env.VITE_API_PROXY_TARGET || "http://127.0.0.1:8000";
  const accountingUiSrc = resolve(
    __dirname,
    ".accounting-ui/cz-accounting-module/packages/accounting-ui/src",
  );

  return {
    base: "/accounting/",
    plugins: [react()],
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
