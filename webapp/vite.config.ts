import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 10939,
    strictPort: true,
    host: true,
    proxy: {
      "/mcp": {
        target: "http://127.0.0.1:10938",
        changeOrigin: true,
      },
      "/health": {
        target: "http://127.0.0.1:10938",
        changeOrigin: true,
      },
    },
  },
});
