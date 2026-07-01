import { fileURLToPath, URL } from "node:url";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// https://vite.dev/config/
export default defineConfig({
	plugins: [react(), tailwindcss()],
	resolve: {
		alias: {
			"@": fileURLToPath(new URL("./src", import.meta.url)),
		},
	},
	server: {
		port: 5173,
		// Proxy API calls to the backend so the session cookie is same-origin (no CORS in dev).
		proxy: {
			"/api": {
				target: "http://127.0.0.1:8080",
				changeOrigin: true,
			},
		},
	},
});
