<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright (c) 2026 Equipo pre.voto -->
<script lang="ts">
  import { Sun, Moon } from "lucide-svelte";

  let isDark = $state(false);

  $effect(() => {
    const stored = localStorage.getItem("prevoto-theme");
    if (stored) {
      isDark = stored === "dark";
    } else {
      isDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    }
  });

  function toggle() {
    isDark = !isDark;
    document.documentElement.classList.toggle("dark", isDark);
    localStorage.setItem("prevoto-theme", isDark ? "dark" : "light");
  }
</script>

<button
  onclick={toggle}
  class="p-1.5 rounded-md text-ink-soft hover:text-ink hover:bg-paper-warm transition-colors"
  aria-label={isDark ? "Cambiar a modo claro" : "Cambiar a modo oscuro"}
>
  {#if isDark}
    <Sun size={18} />
  {:else}
    <Moon size={18} />
  {/if}
</button>
