// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 Equipo pre.voto
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
