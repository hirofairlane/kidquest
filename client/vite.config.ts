import { defineConfig } from "vite";

// The Phaser view layer is bundled here; the pure engine has no Phaser/Vite coupling.
export default defineConfig({
  base: "./",
  build: {
    target: "es2020",
    outDir: "dist",
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: { phaser: ["phaser"] },
      },
    },
  },
  server: {
    host: "0.0.0.0",
    port: 5273,
  },
});
