import { join, resolve } from "path";

import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv, type UserConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";


export default defineConfig(({ mode }): UserConfig => {

  const env = loadEnv(mode, process.cwd(), "");

  const INPUT_DIR = "./frontend";
  const OUTPUT_DIR = "./frontend/dist";



  const devServerPort = parseInt(env.DJANGO_VITE_DEV_SERVER_PORT) || 5173;

  return {
    // Plugins
    plugins: [tailwindcss(), react()],

    // Alias de résolution
    resolve: {
      alias: {
        "@": resolve(INPUT_DIR, "ts"),
      },
    },

    // Répertoire racine
    root: resolve(INPUT_DIR),

    // Base URL de déploiement
    base: "/static/",

    // Configuration du serveur de développement
    server: {
      host: "0.0.0.0",
      cors: true,
      port: devServerPort, 
      watch: {
        usePolling: true,
      },
    },

    // Configuration du build (production)
    build: {
      manifest: "manifest.json",
      emptyOutDir: true,
      outDir: resolve(OUTPUT_DIR),
      rollupOptions: {
        input: {
          main: join(INPUT_DIR, "ts/main.tsx"),
          css: join(INPUT_DIR, "main.css"),
        },
      },
    },
  };
});
