import { defineConfig } from "astro/config";
import svelte from "@astrojs/svelte";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  site: "https://pre.voto",
  output: "static",
  integrations: [svelte()],
  vite: {
    plugins: [tailwindcss()],
  },
});
